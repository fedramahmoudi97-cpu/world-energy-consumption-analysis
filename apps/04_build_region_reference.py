"""Rebuild the project's small geographic reference using standard Python.

Run inside the existing Docker container (no extra packages needed):
  docker compose exec spark python3 /opt/spark/apps/04_build_region_reference.py

Input: outputs/geography_scope_review_draft.csv
Source: the English geographic hierarchy on the official UN M49 page.
Outputs: a cached source HTML, its dated SHA256 metadata, and
         outputs/geography_candidate_region_reference.csv.

The existing file in data/ is not overwritten. This script creates geographic
metadata; it does not perform energy analysis or establish country eligibility.
The energy calculations and data profiling in the project use PySpark.
"""

import argparse
import csv
import hashlib
import json
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path


SOURCE_URL = "https://unstats.un.org/unsd/methodology/m49/"


class M49TableParser(HTMLParser):
    """Read HTML table rows, including the UN's geographic parent identifiers."""

    def __init__(self):
        super().__init__()
        self.tables = []
        self.table = None
        self.row = None
        self.cell = None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.table = []
        elif self.table is not None and tag == "tr":
            self.row = {"attrs": dict(attrs), "cells": []}
        elif self.row is not None and tag in ("td", "th"):
            self.cell = []

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.cell is not None:
            self.row["cells"].append(" ".join("".join(self.cell).split()))
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.table.append(self.row)
            self.row = None
        elif tag == "table" and self.table is not None:
            self.tables.append(self.table)
            self.table = None


def load_source(output_dir):
    """Download once; subsequent runs use the same saved reference snapshot."""
    html_path = output_dir / "un_m49_source.html"
    metadata_path = output_dir / "un_m49_source_metadata.json"

    if html_path.exists() != metadata_path.exists():
        raise ValueError("The source HTML and its metadata must be kept together.")

    if not html_path.exists():
        print(f"Downloading official reference: {SOURCE_URL}")
        with urllib.request.urlopen(SOURCE_URL, timeout=60) as response:
            content = response.read()
        metadata = {
            "source_url": SOURCE_URL,
            "retrieved_date": datetime.now(timezone.utc).date().isoformat(),
            "sha256": hashlib.sha256(content).hexdigest(),
        }
        html_path.write_bytes(content)
        metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    else:
        content = html_path.read_bytes()
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    if metadata["source_url"] != SOURCE_URL:
        raise ValueError("Cached source URL does not match the intended reference.")
    if hashlib.sha256(content).hexdigest() != metadata["sha256"]:
        raise ValueError("Cached UN source has changed; check its SHA256 metadata.")
    return content.decode("utf-8-sig"), metadata


def build_lookup(html):
    parser = M49TableParser()
    parser.feed(html)
    # Select the English hierarchy by content, not by table position.
    matches = [table for table in parser.tables if any(
        row["attrs"].get("data-tt-id") == "001"
        and row["cells"] and row["cells"][0] == "World"
        for row in table)]
    if len(matches) != 1:
        raise ValueError("Cannot uniquely identify the English UN geographic table.")

    nodes = {}
    lookup = {}
    for row in matches[0]:
        node_id = row["attrs"].get("data-tt-id")
        if not node_id:
            continue
        if node_id in nodes:
            raise ValueError(f"Duplicate geographic node: {node_id}")
        nodes[node_id] = row
        cells = row["cells"]
        if len(cells) >= 3 and len(cells[2]) == 3 and cells[2].isupper():
            if cells[2] in lookup:
                raise ValueError(f"Duplicate reference ISO code: {cells[2]}")
            lookup[cells[2]] = row
    if not lookup:
        raise ValueError("The reference contains no usable ISO codes.")
    return nodes, lookup


def geographic_path(row, nodes):
    # Example: Nigeria -> Western Africa -> Sub-Saharan Africa -> Africa -> World.
    # Reverse this path and omit World to obtain the official hierarchy levels.
    path = []
    seen = set()
    while row["attrs"].get("data-tt-parent-id"):
        parent = row["attrs"]["data-tt-parent-id"]
        if parent in seen:
            raise ValueError("Cycle in the source geographic hierarchy.")
        seen.add(parent)
        row = nodes[parent]
        if row["cells"][1] != "001":
            path.append(row["cells"][0])
    path.reverse()
    if not 2 <= len(path) <= 3:
        raise ValueError(f"Unexpected geographic hierarchy: {path}")
    return path


def main():
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--project-root", type=Path,
                      default=Path(__file__).resolve().parent.parent)
    root = args.parse_args().project_root
    output_dir = root / "outputs"
    input_path = output_dir / "geography_scope_review_draft.csv"
    output_path = output_dir / "geography_candidate_region_reference.csv"

    # 1. Select the candidate entities from our previously generated inventory.
    with input_path.open(encoding="utf-8-sig", newline="") as file:
        candidates = [row for row in csv.DictReader(file)
                      if row["draft_geography_class"] == "coded_geography_candidate"]
    if not candidates:
        raise ValueError("No candidates found in the draft geography review.")
    if len({row["country"] for row in candidates}) != len(candidates):
        raise ValueError("Candidate country names are not unique.")
    if len({row["iso_code"] for row in candidates}) != len(candidates):
        raise ValueError("Candidate ISO codes are not unique.")

    # 2. Obtain and parse the official reference snapshot.
    html, metadata = load_source(output_dir)
    nodes, lookup = build_lookup(html)

    # 3. Match on ISO codes. Keep every original candidate, including unmatched ones.
    results = []
    unmatched = []
    for candidate in sorted(candidates, key=lambda row: row["country"]):
        code = candidate["iso_code"]
        match = lookup.get(code)
        result = {
            "country": candidate["country"],
            "iso_code": code,
            "reference_country_or_area_name": "",
            "reference_m49_code": "",
            "region": "",
            "subregion": "",
            "intermediate_region": "",
            "region_match_status": "manual_mapping_pending",
            "reference_scheme": "UN M49 geographic hierarchy; current reference applied as a fixed grouping, not a historical boundary concordance",
            "reference_url": SOURCE_URL,
            "reference_retrieved_date": metadata["retrieved_date"],
            "scope_status": "candidate_only_pending_geographic_and_measurement_review",
            "review_note": "Region assignment does not establish sovereign status, non-overlapping statistical boundaries, or energy/GDP coverage. Original dataset name and code are unchanged.",
        }
        if match:
            path = geographic_path(match, nodes)
            result.update(
                reference_country_or_area_name=match["cells"][0],
                reference_m49_code=match["cells"][1],
                region=path[0], subregion=path[1],
                intermediate_region=path[2] if len(path) == 3 else "",
                region_match_status="exact_iso_alpha3_match",
            )
        else:
            unmatched.append((candidate["country"], code))
            result["review_note"] = "No exact ISO match in this reference. Preserve the dataset entity and review manually; do not infer its region or delete it."
            if code == "TWN":
                # Explicit project note based on the M49 FAQ, not an inferred match.
                result["review_note"] = "TWN has no standalone row in the main M49 table. Preserve Taiwan as a separate dataset entity; do not delete or merge with China. M49 FAQ permits statistical numeric code 158. A separate documented project mapping is pending; blank region is not an exclusion decision."
        results.append(result)

    # 4. Save the reproducible result separately from the file already in data/.
    if len(results) != len(candidates):
        raise ValueError("The mapping unexpectedly changed the number of entities.")
    with output_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)

    print(f"Candidates retained: {len(results)}")
    print(f"Exact ISO matches: {len(results) - len(unmatched)}")
    print(f"Unmatched entities: {unmatched}")
    print(f"Reference SHA256: {metadata['sha256']}")
    print(f"Saved: {output_path}")
    print("Geographic metadata only: no final sample or measurement coverage inferred.")


if __name__ == "__main__":
    main()
