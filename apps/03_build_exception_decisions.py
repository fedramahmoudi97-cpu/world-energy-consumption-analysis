#!/usr/bin/env python3
"""Reproduce the proposed geography exceptions and the raw-file checksum.

Place this file in DS8003Project-energy/apps.
Run from the project's PowerShell terminal:
  docker compose exec spark python3 /opt/spark/apps/03_build_exception_decisions.py

Inputs:
  data/World Energy Consumption.csv (the agreed, unchanged snapshot)
  outputs/geography_scope_review_draft.csv (created by script 02)
Outputs:
  outputs/geography_exception_decisions_proposed.csv
  outputs/dataset_checksum.csv

Evidence counts are recomputed from the RAW DATA, not copied from an old output.
PROPOSED_RULES below records editorial/analytical judgments from the initial
review. These are proposals pending group review, NOT decisions inferred by
Python and NOT classifications downloaded from the UN. The reference URLs are
citations for further review; this script does not fetch those web pages.

This small reference-building step uses Python's standard library, not PySpark.
A nonempty cell (including '0') counts as present. Numeric validity, common
coverage across variables and final sample eligibility are NOT tested here.
An existing CSV is verified by its parsed contents; a differing file is never
overwritten. This protects any subsequent group edits.
"""
import argparse
import csv
import hashlib
from pathlib import Path

EXPECTED_SHA256 = '00cd4b34da817f8cdb3af3558424be0d122aeea328156cf2d1f948e2158e48d7'
START_YEAR, END_YEAR = 2000, 2018
MEASURES = [
    'primary_energy_consumption', 'energy_per_capita', 'population', 'gdp',
    'fossil_fuel_consumption', 'renewables_consumption', 'renewables_share_energy',
]

# Explicit proposed policy rules; revise through group review, not silently.
# The snapshot and period are fixed because these reasons refer to that evidence.
PROPOSED_RULES = {'Antarctica': {'proposed_decision': 'exclude_from_main_country_comparisons',
                'reason': 'Non-comparable geographic unit for the proposed country-level '
                          'study; population, per-capita energy, GDP and energy-mix measures '
                          'are absent in the proposed period. Primary energy alone does not '
                          'establish eligibility for the main sample.',
                'geographic_reference': ''},
 'Czechoslovakia': {'proposed_decision': 'exclude_from_2000_2018_sample',
                    'reason': 'No rows in the proposed period. Keep historical entity separate '
                              'from Czechia and Slovakia; do not concatenate automatically.',
                    'geographic_reference': 'https://unstats.un.org/unsd/methodology/m49/'},
 'East Germany (EIA)': {'proposed_decision': 'exclude_from_2000_2018_sample',
                        'reason': 'No rows in the proposed period. Do not combine this '
                                  'historical series automatically with Germany.',
                        'geographic_reference': 'https://unstats.un.org/unsd/methodology/m49/'},
 'Hawaiian Trade Zone (EIA)': {'proposed_decision': 'exclude_from_2000_2018_sample',
                               'reason': 'No rows in the proposed period; the series ends in '
                                         '1986. No need to resolve its exact historical '
                                         'geographic definition for this period.',
                               'geographic_reference': ''},
 'Kosovo': {'proposed_decision': 'retain_for_analysis_specific_review',
            'reason': 'Do not exclude solely because iso_code is missing. Primary and '
                      'per-capita energy exist for part of the period; GDP and the selected '
                      'fossil/renewable measures are absent. Not eligible for a common '
                      'complete 2000-2018 five-analysis sample under these variables. A '
                      'narrower total/per-capita comparison may be considered after '
                      'source-definition and geographic-overlap review; retain the original '
                      'blank ISO field.',
            'geographic_reference': 'https://unstats.un.org/unsd/methodology/m49/'},
 'Netherlands Antilles': {'proposed_decision': 'exclude_pending_geographic_harmonization',
                          'reason': 'Historical combined territory with a documented 2010 '
                                    'geographic change. Rows continuing to 2021 do not prove '
                                    'consistent boundaries. Exclude from the proposed main '
                                    'sample unless source definitions and harmonization are '
                                    'justified; GDP and energy-mix measures are also absent in '
                                    '2000-2018.',
                          'geographic_reference': 'https://unstats.un.org/unsd/methodology/m49/'},
 'Serbia and Montenegro': {'proposed_decision': 'exclude_combined_entity_from_main_sample',
                           'reason': 'Combined historical entity with only six rows in the '
                                     'proposed period, ending in 2005. Keep separate from '
                                     'Serbia and Montenegro; no automatic joining of '
                                     'predecessor and successor series.',
                           'geographic_reference': 'https://unstats.un.org/unsd/methodology/m49/'},
 'USSR': {'proposed_decision': 'exclude_historical_entity_from_main_sample',
          'reason': 'Historical combined entity. Although 19 year rows and GDP values exist, '
                    'primary energy is absent throughout 2000-2018. Do not treat these rows as '
                    'a contemporary country or infer energy-GDP feasibility from row presence.',
          'geographic_reference': 'https://unstats.un.org/unsd/methodology/m49/'},
 'Wake Island (EIA)': {'proposed_decision': 'exclude_from_main_country_comparisons',
                       'reason': 'Source-specific area series. Primary energy exists, but '
                                 'population, per-capita energy, GDP and energy-mix measures '
                                 'are absent in the proposed period. Do not count the EIA and '
                                 'Shift labels as two countries.',
                       'geographic_reference': ''},
 'Wake Island (Shift)': {'proposed_decision': 'exclude_from_main_country_comparisons',
                         'reason': 'Source-specific area series with 17 year rows; selected '
                                   'primary energy, per-capita, GDP and energy-mix measures '
                                   'are absent. Do not count the Shift and EIA labels as two '
                                   'countries.',
                         'geographic_reference': ''},
 'West Germany (EIA)': {'proposed_decision': 'exclude_from_2000_2018_sample',
                        'reason': 'No rows in the proposed period. Do not combine this '
                                  'historical series automatically with Germany.',
                        'geographic_reference': 'https://unstats.un.org/unsd/methodology/m49/'},
 'Yugoslavia': {'proposed_decision': 'exclude_from_2000_2018_sample',
                'reason': 'No rows in the proposed period. Do not concatenate the historical '
                          'series with successor entities.',
                'geographic_reference': 'https://unstats.un.org/unsd/methodology/m49/'}}


def read_csv(path, required):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        if len(fields) != len(set(fields)):
            raise ValueError(f'Duplicate column names: {path}')
        missing = set(required) - set(fields)
        if missing:
            raise ValueError(f'Missing columns in {path}: {sorted(missing)}')
        return list(reader)


def verify_or_write(path, rows):
    """Preserve existing work; verify values independently of CSV formatting."""
    fields = list(rows[0])
    text_rows = [{k: str(v) for k, v in row.items()} for row in rows]
    if path.exists():
        existing = read_csv(path, fields)
        # PowerShell emits uppercase hashes; both cases mean the same SHA-256.
        if path.name == 'dataset_checksum.csv':
            for row in existing:
                row['Hash'] = row['Hash'].lower()
        if existing != text_rows:
            raise ValueError(
                f'Existing file differs and was preserved: {path}. '
                'Review the differences before replacing any group decisions. '
                'Use --output-dir with an empty folder to inspect a fresh rebuild.'
            )
        print(f'VERIFIED (existing file preserved): {path.name}')
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f'CREATED: {path.name}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=Path,
                        default=Path(__file__).resolve().parent.parent)
    parser.add_argument('--output-dir', type=Path, default=None,
                        help='Optional separate directory for comparing a rebuild.')
    args = parser.parse_args()
    root = args.project_root.resolve()
    output_dir = args.output_dir.resolve() if args.output_dir else root / 'outputs'
    raw_path = root / 'data' / 'World Energy Consumption.csv'
    review_path = root / 'outputs' / 'geography_scope_review_draft.csv'

    digest = hashlib.sha256()
    with raw_path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    actual_hash = digest.hexdigest()
    if actual_hash != EXPECTED_SHA256:
        raise ValueError('Raw dataset differs from the reviewed snapshot. '
                         'Reassess the proposed rules before using another version.')

    review = read_csv(review_path, ['country', 'iso_code', 'proposed_scope_status'])
    exceptions = [r for r in review if r['proposed_scope_status'] == 'manual_review']
    names = [r['country'] for r in exceptions]
    if len(names) != len(set(names)) or set(names) != set(PROPOSED_RULES):
        raise ValueError('The manual-review list changed or contains duplicates. '
                         'Review the explicit proposed rules first.')
    by_name = {r['country']: r for r in exceptions}
    observed = {name: {} for name in names}
    seen_names = set()
    raw = read_csv(raw_path, ['country', 'iso_code', 'year'] + MEASURES)
    for row in raw:
        name = row['country']
        if name not in observed:
            continue
        seen_names.add(name)
        if row['iso_code'] != by_name[name]['iso_code']:
            raise ValueError(f'ISO mismatch between raw and review: {name}')
        year = int(row['year'])
        if START_YEAR <= year <= END_YEAR:
            if year in observed[name]:
                raise ValueError(f'Duplicate country-year: {name}, {year}')
            observed[name][year] = row
    if seen_names != set(names):
        raise ValueError('A review entity is missing from the raw dataset.')

    results = []
    for name in sorted(names):
        years = observed[name]
        rule = PROPOSED_RULES[name]
        result = {
            'country': name,
            'iso_code': by_name[name]['iso_code'],
            'review_status': 'proposed_pending_group_review',
            'proposed_decision': rule['proposed_decision'],
            'applies_to': 'Proposed main country comparison, 2000-2018; raw data retained',
            'reason': rule['reason'],
            'period_start': START_YEAR,
            'period_end': END_YEAR,
            'year_rows_present': len(years),
        }
        for measure in MEASURES:
            result[measure + '_nonempty_years'] = sum(
                bool(row[measure].strip()) for row in years.values()
            )
        result.update({
            'primary_energy_years_present': ';'.join(
                str(year) for year in sorted(years)
                if years[year]['primary_energy_consumption'].strip()
            ),
            'evidence_method': 'Targeted check of 12 exceptions using Python csv; counts are nonempty original cells, not numeric-validity or full joint-coverage checks. Zero is retained as an observed value.',
            'dataset_sha256': actual_hash,
            'data_evidence_file': 'World Energy Consumption.csv; geography_scope_review_draft.csv',
            'geographic_reference': rule['geographic_reference'],
            'remaining_action': 'Group review; Person 4 to confirm analysis-specific joint coverage. Review source boundaries/overlap before any country-level inclusion.',
        })
        results.append(result)

    verify_or_write(output_dir / 'geography_exception_decisions_proposed.csv', results)
    verify_or_write(output_dir / 'dataset_checksum.csv', [{
        'File': raw_path.name, 'Algorithm': 'SHA256', 'Hash': actual_hash,
    }])
    print(f'Exceptions reviewed: {len(results)}; period: {START_YEAR}-{END_YEAR}')
    print('Evidence recomputed. All decisions remain proposed pending group review.')
    print('Raw data and the scope-review input were not modified.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, csv.Error) as exc:
        raise SystemExit(f'ERROR: {exc}')
