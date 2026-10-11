"""Record proposed geography rules and the current review evidence.

Place in apps, then run from the project PowerShell terminal:
  docker compose exec spark python3 /opt/spark/apps/06_record_geography_policy.py

Standard Python is sufficient: this step documents policy and reads small
review tables; it does not calculate energy indicators or run a new selection.
The rules are explicit analytical proposals, NOT machine-discovered facts,
UN selection requirements, or group-approved decisions.

Inputs: outputs/geography_candidate_scope_review.csv,
        outputs/geography_scope_review_draft.csv,
        outputs/geography_exception_decisions_proposed.csv,
        outputs/un_m49_source.html and un_m49_source_metadata.json.
Output: outputs/geography_policy_proposed.md (readable in VS Code).
Existing inputs, scope_rules.md, and earlier decisions are never modified.
"""

import argparse
import csv
import hashlib
import json
from pathlib import Path

POLICY_VERSION = '0.1-proposed'
UN_URL = 'https://unstats.un.org/unsd/methodology/m49/'
OWID_URL = 'https://github.com/owid/energy-data'

# Explicit proposed project methodology. References support the context;
# they do not prescribe or approve our sample-selection policy.
RULES = [
    ('G01', 'Unit of observation',
     'Use one separately reported country or area in one year. Preserve the original '
     'dataset name and ISO field. Do not describe all candidate areas as independent '
     'countries. If areas are included, label the reported sample as countries and areas.',
     'Project proposal; UN M49 countries-or-areas terminology [R1].'),
    ('G02', 'Country and territory eligibility',
     'Do not include or exclude an area solely because it is a territory, has an ISO '
     'code, or matches M49. Inclusion in an analysis requires a documented statistical '
     'area, adequate geographic consistency for that analysis, and the required valid '
     'measurements. Unresolved geography remains pending and cannot be marked eligible.',
     'Project proposal informed by the limits of M49 [R1].'),
    ('G03', 'Aggregates and double counting',
     'Keep World, continents, income groups and other multi-area aggregates outside '
     'the entity-level comparison sample. They may be separately labelled benchmarks. '
     'Never add such an aggregate to its constituents. A sum of selected entities is '
     'a selected-sample sum, not automatically a global total.',
     'Project proposal; existing script-02 inventory; OWID aggregate documentation [R2].'),
    ('G04', 'Parent-area overlap and matching denominators',
     'Check the source definitions for the specific indicator and years before jointly '
     'using a country total and a separately reported associated area. Political '
     'association alone neither proves nor rules out statistical overlap. Do not sum '
     'overlapping observations or treat an unresolved parent/area pair as independent '
     'observations in pooled analysis. Compare energy, population and GDP only when '
     'their geographic coverage is compatible. If unresolved, hold the affected '
     'entity-analysis combination pending; do not fabricate a subtraction or merge.',
     'Project comparability rule; source-specific evidence must still be documented.'),
    ('G05', 'Historical entities and changing boundaries',
     'Keep predecessor and successor series separate. Do not concatenate or sum them '
     'to invent a continuous country series. A current name, code or a full set of '
     'year rows does not establish stable historical boundaries. Require a documented '
     'consistent series or an explicitly justified restriction of the period; otherwise '
     'hold the affected trend comparison pending. Existing exception proposals stay separate.',
     'Project proposal; UN M49 historical changes [R1].'),
    ('G06', 'Regional grouping',
     'Use the saved M49 hierarchy as a fixed statistical grouping for this project. '
     'Preserve region, subregion and intermediate region as distinct levels. This '
     'reference is not a historical boundary concordance. Blank intermediate region '
     'can be legitimate and is not an exclusion criterion.',
     'Project use of the M49 hierarchy [R1]; cached source and its metadata.'),
    ('G07', 'Unmatched regional codes',
     'Keep unmatched entities and flag them. Taiwan remains a separate dataset entity '
     'with its original TWN code; this step does not assign a region, replace its code, '
     'merge it with another entity, or exclude it. A later mapping must identify its '
     'source and be explicitly labelled as a project mapping. A missing region blocks '
     'region-based grouping until resolved, but does not by itself prevent other analyses.',
     'Project handling rule; observed unmatched row and UN M49 FAQ [R1].'),
    ('G08', 'Period and measurement coverage',
     'Keep 2000-2018 as the proposed period until the required measurements are checked. '
     'Row availability is not measurement completeness. An entity with fewer than 19 '
     'year rows cannot enter a complete 19-year panel unchanged, but may qualify for '
     'an explicitly defined shorter-period or endpoint analysis. Do not equate blanks '
     'with zeros, infer independence dates from data availability, or backfill values '
     'merely to make an entity eligible.',
     'Project proposal; script-05 evidence and pending Person-4 coverage assessment.'),
    ('G09', 'Existing exceptions',
     'Retain the separately recorded historical/special exceptions in the audit trail. '
     'Carry forward their proposed decisions and reasons without upgrading them to '
     'approved decisions. Kosovo is not rejected solely for a missing ISO field. '
     'Changing an exception proposal requires explicit documented review.',
     'Project exception table generated/verified by script 03.'),
    ('G10', 'Final selection and responsibilities',
     'Final eligibility requires geographic suitability AND analysis-specific valid '
     'joint measurement coverage. Fedra prepares geography/period recommendations; '
     'Person 2 confirms definitions and units; Person 3 addresses structure, cleaning '
     'and calculation methods; Person 4 assesses joint coverage. The group agrees on '
     'the final scope. Report each analysis sample and its exclusions. No eligibility '
     'decision is automatically approved by running this script.',
     'Proposed project workflow and the agreed preparation roles.'),
]


def read_csv(path, required):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        missing = set(required) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f'{path.name}: missing columns {sorted(missing)}')
        rows = list(reader)
    if not rows:
        raise ValueError(f'Empty input: {path.name}')
    names = [r['country'] for r in rows]
    if len(names) != len(set(names)):
        raise ValueError(f'Duplicate entity names: {path.name}')
    return rows


def cell(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')


def build_document(folder):
    candidates = read_csv(folder / 'geography_candidate_scope_review.csv',
                          ['country', 'iso_code', 'years_present_2000_2018',
                           'region_match_status', 'reference_retrieved_date',
                           'proposed_period_start', 'proposed_period_end', 'final_sample_status'])
    inventory = read_csv(folder / 'geography_scope_review_draft.csv',
                         ['country', 'iso_code', 'draft_geography_class', 'proposed_scope_status'])
    exceptions = read_csv(folder / 'geography_exception_decisions_proposed.csv',
                          ['country', 'review_status', 'proposed_decision', 'reason',
                           'dataset_sha256', 'period_start', 'period_end'])
    metadata = json.loads((folder / 'un_m49_source_metadata.json').read_text(encoding='utf-8'))
    source_hash = hashlib.sha256((folder / 'un_m49_source.html').read_bytes()).hexdigest()
    if metadata['source_url'] != UN_URL or metadata['sha256'] != source_hash:
        raise ValueError('M49 source and metadata do not match.')
    if {r['reference_retrieved_date'] for r in candidates} != {metadata['retrieved_date']}:
        raise ValueError('Candidate reference date differs from the cached source date.')
    expected_pairs = {(r['country'], r['iso_code']) for r in inventory
                      if r['draft_geography_class'] == 'coded_geography_candidate'}
    if {(r['country'], r['iso_code']) for r in candidates} != expected_pairs:
        raise ValueError('Candidate list differs from the script-02 review.')
    if {r['country'] for r in exceptions} != {
            r['country'] for r in inventory if r['proposed_scope_status'] == 'manual_review'}:
        raise ValueError('Exception list differs from the script-02 review.')
    if any(r['final_sample_status'] != 'not_selected_candidate_only' for r in candidates):
        raise ValueError('Candidate decisions changed; reconcile the policy before proceeding.')
    if any(r['review_status'] != 'proposed_pending_group_review' for r in exceptions):
        raise ValueError('Exception approval status changed; reconcile before proceeding.')
    if any((r['proposed_period_start'], r['proposed_period_end']) != ('2000', '2018')
           for r in candidates) or any((r['period_start'], r['period_end']) != ('2000', '2018')
                                      for r in exceptions):
        raise ValueError('The proposed period changed; revise the policy first.')
    hashes = {r['dataset_sha256'] for r in exceptions}
    if len(hashes) != 1:
        raise ValueError('Exceptions refer to different dataset snapshots.')
    partial = [r for r in candidates if int(r['years_present_2000_2018']) < 19]
    unmatched = [r for r in candidates if r['region_match_status'] != 'exact_iso_alpha3_match']
    aggregates = sum(r['draft_geography_class'] == 'aggregate' for r in inventory)
    lines = [
        '# Proposed geographic scope policy', '',
        f'Policy version: {POLICY_VERSION}',
        'Status: proposed for group review; no final sample approved.', '',
        'This document supplements the existing scope_rules.md draft. It does not '
        'overwrite that file or replace analysis-specific coverage checks. The rules '
        'are explicit project choices recorded in script 06; counts and exception '
        'details below are read from the existing project outputs.', '',
        '## Proposed rules', '',
    ]
    for rule_id, title, text, basis in RULES:
        lines.extend([f'### {rule_id} - {title}', '', text, '', f'Basis: {basis}', ''])
    lines.extend([
        '## Current evidence (not final eligibility)', '',
        f'- Initial geographic labels: {len(inventory)}.',
        f'- Aggregate labels in the existing draft: {aggregates}.',
        f'- Coded candidates retained: {len(candidates)}.',
        f'- Historical/special exceptions kept separately: {len(exceptions)}.',
        f'- Candidates with all 19 year rows: {len(candidates) - len(partial)}.',
        f'- Candidates with incomplete year rows: {len(partial)}.',
        f'- Exact M49 matches: {len(candidates) - len(unmatched)}.',
        f'- Unresolved regional mappings: {len(unmatched)}.', '',
        '### Incomplete year rows', '',
        '| Dataset name | ISO code | Years present, 2000-2018 |',
        '| --- | --- | --- |',
    ])
    lines.extend('| ' + ' | '.join(cell(r[k]) for k in
                 ['country', 'iso_code', 'years_present_2000_2018']) + ' |'
                 for r in sorted(partial, key=lambda r: r['country']))
    lines.extend(['', '### Unresolved regional mappings', ''])
    lines.extend(f"- {r['country']} ({r['iso_code']}): preserve; apply G07."
                 for r in sorted(unmatched, key=lambda r: r['country']))
    lines.extend(['', '### Existing exception proposals (unchanged)', '',
                  '| Dataset name | Proposed decision | Recorded reason |',
                  '| --- | --- | --- |'])
    lines.extend('| ' + ' | '.join(cell(r[k]) for k in
                 ['country', 'proposed_decision', 'reason']) + ' |'
                 for r in sorted(exceptions, key=lambda r: r['country']))
    lines.extend([
        '', '## Outstanding evidence and next decision', '',
        'This step records the policy; it has not audited every candidate boundary or '
        'resolved every associated-area overlap. In step 7, use indicator/source '
        'definitions and coverage results to resolve the entity-analysis cases that '
        'could enter the sample. For each unresolved case, retain the original name/code '
        'and record the affected indicator, years, evidence URL/version, proposed '
        'handling, reason and review status. Apply approved rules through code; '
        'do not patch generated CSV cells manually.', '',
        'Until then, all candidates retain their pending status. The policy does not '
        'turn the list of 217 candidates into 217 confirmed countries.', '',
        '## References and provenance', '',
        f'- [R1] UN Statistics Division, M49 methodology, hierarchy, historical changes '
        f'and FAQ: {UN_URL}',
        f'- Saved M49 retrieval date: {metadata["retrieved_date"]}.',
        f'- Saved M49 HTML SHA256: {source_hash}.',
        f'- [R2] OWID energy-data documentation: {OWID_URL}. Consulted 2026-10-07 '
        'for general source/aggregate context only. Its current documentation is NOT '
        'proof of indicator definitions or area coverage in our older Kaggle snapshot.',
        f'- Dataset SHA256 recorded in the exception evidence: {next(iter(hashes))}. '
        'Script 03 performs the raw-file hash check; this documentation step reads its record.',
        '- Policy rules, candidate scope review and exception proposals are project '
        'materials, not official UN inclusion decisions.', '',
    ])
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=Path,
                        default=Path(__file__).resolve().parent.parent)
    folder = parser.parse_args().project_root / 'outputs'
    text = build_document(folder)
    target = folder / 'geography_policy_proposed.md'
    if target.exists():
        if target.read_text(encoding='utf-8') != text:
            raise ValueError('Existing policy differs and was preserved. '
                             'Review the changes before replacing the document.')
        print(f'VERIFIED (existing file preserved): {target}')
    else:
        with target.open('x', encoding='utf-8', newline='\n') as handle:
            handle.write(text)
        print(f'CREATED: {target}')
    print(f'Proposed rules recorded: {len(RULES)}')
    print('No candidate or exception status changed. Group review remains pending.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, csv.Error) as exc:
        raise SystemExit(f'ERROR: {exc}')
