"""Record a provisional scope, without selecting countries or assessing coverage.

Place this script in apps. Run from the project PowerShell terminal:
docker compose exec spark python3 /opt/spark/apps/07_record_proposed_scope.py

Inputs: the three review CSVs and geography_policy_proposed.md in outputs.
Output: outputs/proposed_scope_countries_timeframes.md.
Uses standard Python only. Does not modify inputs or create an analysis dataset.
The methodological proposals below are human choices, not inferred findings.
"""
import argparse
import csv
import hashlib
from pathlib import Path


def read_rows(path, required):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        missing = set(required) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f'{path.name}: missing columns {sorted(missing)}')
        rows = list(reader)
    names = [r['country'] for r in rows]
    if not rows or any(not name.strip() for name in names) or len(names) != len(set(names)):
        raise ValueError(f'{path.name}: empty input, blank names or duplicate names.')
    return rows


def build_document(folder):
    candidate_path = folder / 'geography_candidate_scope_review.csv'
    inventory_path = folder / 'geography_scope_review_draft.csv'
    exception_path = folder / 'geography_exception_decisions_proposed.csv'
    policy_path = folder / 'geography_policy_proposed.md'
    candidates = read_rows(candidate_path, ['country', 'iso_code',
        'years_present_2000_2018', 'proposed_period_start', 'proposed_period_end',
        'final_sample_status', 'region_match_status'])
    inventory = read_rows(inventory_path, ['country', 'iso_code',
        'draft_geography_class', 'proposed_scope_status'])
    exceptions = read_rows(exception_path, ['country', 'review_status',
        'period_start', 'period_end', 'dataset_sha256'])
    policy = policy_path.read_text(encoding='utf-8')
    if not policy.strip() or not all(f'### G{i:02d} - ' in policy for i in range(1, 11)):
        raise ValueError('Expected the ten-rule policy from step 06; review the policy input.')
    pairs = {(r['country'], r['iso_code']) for r in candidates}
    expected = {(r['country'], r['iso_code']) for r in inventory
                if r['draft_geography_class'] == 'coded_geography_candidate'}
    if pairs != expected:
        raise ValueError('Candidate keys differ from the geography inventory.')
    if {r['country'] for r in exceptions} != {r['country'] for r in inventory
            if r['proposed_scope_status'] == 'manual_review'}:
        raise ValueError('Exception names differ from the geography inventory.')
    if any(r['final_sample_status'] != 'not_selected_candidate_only' for r in candidates):
        raise ValueError('Candidate status changed; reconcile the scope before proceeding.')
    if any(r['review_status'] != 'proposed_pending_group_review' for r in exceptions):
        raise ValueError('Exception status changed; reconcile before proceeding.')
    if any((r['proposed_period_start'], r['proposed_period_end']) != ('2000', '2018')
           for r in candidates) or any((r['period_start'], r['period_end']) != ('2000', '2018')
                                      for r in exceptions):
        raise ValueError('Input periods differ from the proposed 2000-2018 period.')
    years = [int(r['years_present_2000_2018']) for r in candidates]
    if any(n < 0 or n > 19 for n in years):
        raise ValueError('Invalid count of years within 2000-2018.')
    hashes = {r['dataset_sha256'].lower() for r in exceptions}
    if len(hashes) != 1 or any(len(h) != 64 or any(c not in '0123456789abcdef' for c in h) for h in hashes):
        raise ValueError('Invalid or inconsistent dataset hash in exception evidence.')
    aggregates = sum(r['draft_geography_class'] == 'aggregate' for r in inventory)
    full = sum(n == 19 for n in years)
    matched = sum(r['region_match_status'] == 'exact_iso_alpha3_match' for r in candidates)
    lines = [
        '# Proposed scope regarding countries and timeframes', '',
        'Status: provisional for group review; no final country list or analysis sample approved.', '',
        '## Draft wording for the proposal', '',
        'The project proposes to examine energy consumption and the energy mix across '
        'countries and areas over 2000-2018, using the fixed World Energy Consumption '
        'dataset snapshot. The unit of observation is a separately reported country or '
        'area in a year. Inclusion will require suitable geographic comparability and '
        'valid observations for the variables and years needed by each analysis. '
        'Aggregate labels will be excluded from entity-level comparisons and used only '
        'as separately identified benchmarks where appropriate. Historical entities '
        'will not be automatically joined to successor series. The final sample and '
        'any justified changes to the timeframe will be agreed after reviewing variable '
        'definitions, geographic consistency and analysis-specific joint data coverage. '
        'Findings will describe the observed sample and associations, without claiming '
        'causal effects or automatic global representativeness.', '',
        '## Basis and limits of the current evidence', '',
        f'- Geographic labels reviewed: {len(inventory)}; aggregate labels: {aggregates}.',
        f'- Coded candidate countries/areas: {len(candidates)}; separately reviewed exceptions: {len(exceptions)}.',
        f'- Candidates with all 19 year rows: {full}; with fewer year rows: {len(candidates) - full}.',
        f'- Exact regional reference matches: {matched}; unresolved mappings: {len(candidates) - matched}.',
        '- These are inventory counts, not counts of eligible countries or complete measurements.',
        '- The 2000-2018 interval is a working proposal. This step does not establish that it is the optimal or feasible interval for every analysis.',
        '- A reference match does not establish sovereignty, stable historical boundaries or compatible indicator coverage.', '',
        '## Proposed selection and timeframe rules', '',
        '1. Apply the detailed geography rules in geography_policy_proposed.md. Preserve original names and codes; retain raw data and the exception audit trail.',
        '2. Confirm compatible source definitions and geographic coverage for energy, population and GDP. Resolve affected boundary/overlap cases before admitting them to an analysis.',
        '3. For annual trends, assess measurements across the required years. For endpoint changes, assess both endpoints and comparability; do not silently apply endpoint-only eligibility to annual trends.',
        '4. Compare total and per-capita rankings using the same eligible entities and reference year. Comparisons between analyses must state any sample differences.',
        '5. Decide between a common sample and explicitly reported analysis-specific samples after the joint-coverage review. No completeness percentage or minimum sample size is imposed by this script.',
        '6. If coverage is inadequate, consider a justified shorter common period or analysis-specific period with the group. Do not fill missing values with zero or splice historical series to force eligibility.',
        '7. Keep regional summaries conditional on resolved mappings and compatible coverage. Do not add aggregates to their constituent entities or label selected-sample totals as global totals.', '',
        '## Decisions still open and responsible contributors', '',
        '| Decision | Evidence needed | Contributor | Status |',
        '| --- | --- | --- | --- |',
        '| Geographic eligibility of affected cases | Indicator/year-specific boundaries, overlap and source evidence | Fedra with Person 2 | Pending |',
        '| Indicator definitions and units | Documentation applicable to the actual dataset snapshot | Person 2 | Pending |',
        '| Valid measurements and calculation rules | Structural checks, duplicate handling and agreed calculation methods | Person 3 | Pending |',
        '| Feasible entities and years for each of the five analyses | Valid joint coverage of all required variables | Person 4 | Pending |',
        '| Final period, sample strategy and list of entities | Reconciliation of the evidence above | Group | Pending |', '',
        'The pending labels mean that confirmation is not incorporated into this document; '
        'they do not assert that other members have not started their work. This step '
        'does not repeat their coverage calculations. Record each final inclusion/exclusion '
        'with its analysis, years, reason and evidence when the group resolves these decisions.', '',
        '## Reproducibility', '',
        'Generated by apps/07_record_proposed_scope.py. Counts are calculated from the '
        'existing review tables; the proposed methodology and draft wording are explicit '
        'text in the script. This is a scope document, not a new selection dataset. '
        'The script checks input structure and consistency, but does not independently '
        'verify all underlying source definitions or the raw dataset.', '',
        f'- Dataset SHA256 recorded in exception evidence: {next(iter(hashes))}.',
        '- Input file SHA256 values at generation:',
    ]
    for path in (candidate_path, inventory_path, exception_path, policy_path):
        lines.append(f'  - {path.name}: {hashlib.sha256(path.read_bytes()).hexdigest()}')
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=Path,
                        default=Path(__file__).resolve().parent.parent)
    folder = parser.parse_args().project_root / 'outputs'
    document = build_document(folder)
    target = folder / 'proposed_scope_countries_timeframes.md'
    if target.exists():
        if target.read_text(encoding='utf-8') != document:
            raise ValueError('Existing scope differs and was preserved. Review changes before replacing it.')
        print(f'VERIFIED (existing file preserved): {target}')
    else:
        with target.open('x', encoding='utf-8', newline='\n') as handle:
            handle.write(document)
        print(f'CREATED: {target}')
    print('Scope status: PROPOSED; final sample and timeframe remain pending.')
    print('No input files, candidate decisions or exception decisions changed.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, csv.Error) as exc:
        raise SystemExit(f'ERROR: {exc}')
