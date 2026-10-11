"""Combine candidate geography, year availability and regional reference in Spark.

Run in the project's PowerShell terminal:
  docker compose exec spark /opt/spark/bin/spark-submit /opt/spark/apps/05_build_candidate_scope_review.py

Inputs (unchanged):
  outputs/geography_scope_review_draft.csv -- produced by script 02
  data/geography_candidate_region_reference.csv -- produced by script 04,
      then copied from outputs to data with PowerShell
Output:
  outputs/geography_candidate_scope_review.csv

Purpose: prepare ONE review table for the existing coded candidates. The 12
exceptions remain in their separate table; they are not silently discarded.
This script does NOT classify sovereignty, resolve territorial overlap, check
measurement coverage, select a final sample, or change the proposed period.
Flags below are deterministic review prompts, not inclusion/exclusion decisions.
Do not manually edit this generated table; record group decisions separately.
"""

import csv
from pathlib import Path

from pyspark.sql import SparkSession, functions as F

ROOT = Path('/opt/spark')
REVIEW = ROOT / 'outputs/geography_scope_review_draft.csv'
REFERENCE = ROOT / 'data/geography_candidate_region_reference.csv'
OUTPUT = ROOT / 'outputs/geography_candidate_scope_review.csv'
KEYS = ['country', 'iso_code']
YEAR_COLUMNS = ['first_year', 'last_year', 'row_count', 'distinct_years',
                'years_present_2000_2018']
REGION_COLUMNS = ['reference_country_or_area_name', 'reference_m49_code',
                  'region', 'subregion', 'intermediate_region',
                  'region_match_status', 'reference_scheme', 'reference_url',
                  'reference_retrieved_date', 'review_note']


def read_table(spark, path, required):
    if not path.is_file():
        raise ValueError(f'Missing input: {path}')
    frame = (spark.read.option('header', True).option('inferSchema', False)
             .option('mode', 'FAILFAST').csv(str(path)))
    missing = set(required) - set(frame.columns)
    if missing:
        raise ValueError(f'Missing columns in {path.name}: {sorted(missing)}')
    return frame


def validate_keys(frame, label):
    for key in KEYS:
        if frame.filter(F.col(key).isNull() | (F.trim(F.col(key)) == '')).limit(1).count():
            raise ValueError(f'Missing {key}: {label}')
        if frame.groupBy(key).count().filter(F.col('count') > 1).limit(1).count():
            raise ValueError(f'Duplicate {key}: {label}; review before joining.')


def save_or_verify(frame):
    # This small reference table is exported as a single CSV after Spark's join.
    rows = [{k: '' if v is None else str(v) for k, v in row.asDict().items()}
            for row in frame.orderBy('country').toLocalIterator()]
    if OUTPUT.exists():
        with OUTPUT.open(encoding='utf-8-sig', newline='') as handle:
            old = csv.DictReader(handle)
            if old.fieldnames != frame.columns or list(old) != rows:
                raise ValueError('Existing output differs and was preserved. '
                                 'Review input or policy changes before replacing it.')
        print(f'VERIFIED (existing file preserved): {OUTPUT}')
    else:
        with OUTPUT.open('x', encoding='utf-8-sig', newline='') as handle:
            writer = csv.DictWriter(handle, fieldnames=frame.columns)
            writer.writeheader()
            writer.writerows(rows)
        print(f'CREATED: {OUTPUT}')


def main():
    spark = SparkSession.builder.appName('Energy - Candidate Scope Review').getOrCreate()
    spark.sparkContext.setLogLevel('WARN')
    try:
        review = read_table(spark, REVIEW, KEYS + YEAR_COLUMNS + ['draft_geography_class'])
        candidates = (review.filter(F.col('draft_geography_class') == 'coded_geography_candidate')
                      .select(*(KEYS + YEAR_COLUMNS)))
        reference = read_table(spark, REFERENCE, KEYS + REGION_COLUMNS).select(
            *(KEYS + REGION_COLUMNS))
        candidate_count = candidates.count()
        if candidate_count == 0:
            raise ValueError('No coded candidates found in the geography review.')
        validate_keys(candidates, REVIEW.name)
        validate_keys(reference, REFERENCE.name)
        # Compare complete name/code pairs so outdated reference copies fail visibly.
        if (candidates.join(reference, KEYS, 'left_anti').limit(1).count()
                or reference.join(candidates, KEYS, 'left_anti').limit(1).count()):
            raise ValueError('Candidate name/code pairs differ between the inputs. '
                             'Check that data contains the intended script-04 output.')
        for column in YEAR_COLUMNS:
            candidates = candidates.withColumn(column, F.col(column).cast('int'))
            if candidates.filter(F.col(column).isNull()).limit(1).count():
                raise ValueError(f'Missing or invalid integer: {column}')
        if candidates.filter(~F.col('years_present_2000_2018').between(0, 19)).limit(1).count():
            raise ValueError('Year coverage outside the expected 0-19 range.')

        result = (candidates.join(reference, KEYS, 'left')
                  .withColumn('proposed_period_start', F.lit(2000))
                  .withColumn('proposed_period_end', F.lit(2018))
                  .withColumn('year_row_review',
                      F.when(F.col('years_present_2000_2018') == 19,
                             F.lit('all_19_year_rows_present_values_not_assessed'))
                       .otherwise(F.lit('incomplete_year_rows_review_analysis_period')))
                  .withColumn('region_mapping_review',
                      F.when(F.col('region_match_status') == 'exact_iso_alpha3_match',
                             F.lit('matched_geographic_metadata_only'))
                       .otherwise(F.lit('separate_documented_mapping_required')))
                  .withColumn('geographic_definition_review',
                              F.lit('pending_country_area_definition_and_overlap_review'))
                  .withColumn('measurement_coverage_review',
                              F.lit('pending_analysis_specific_joint_coverage'))
                  .withColumn('final_sample_status', F.lit('not_selected_candidate_only')))
        if result.count() != candidate_count:
            raise ValueError('The join changed the candidate count.')
        save_or_verify(result)
        print(f'Candidates retained: {candidate_count}')
        print('Candidates with incomplete year rows in 2000-2018:')
        result.filter(F.col('years_present_2000_2018') < 19).select(
            'country', 'iso_code', 'years_present_2000_2018').orderBy('country').show(truncate=False)
        print('Candidates requiring a separate regional mapping:')
        result.filter(F.col('region_mapping_review') == 'separate_documented_mapping_required').select(
            'country', 'iso_code', 'region_match_status').show(truncate=False)
        print('No final sample selected. Twelve exceptions remain in their separate review file.')
        print('Geographic eligibility and joint measurement coverage still require review.')
    finally:
        spark.stop()


if __name__ == '__main__':
    main()
