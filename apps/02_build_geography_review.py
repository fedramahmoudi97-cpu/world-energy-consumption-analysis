"""Build a DRAFT geography review; retain every input entity.

Run from the project PowerShell terminal:
  docker compose exec spark /opt/spark/bin/spark-submit /opt/spark/apps/02_build_geography_review.py

Input: outputs/geography_year_inventory.csv (created by 01_scope_inventory.py).
Output: outputs/geography_scope_review_draft.csv.
Rerunning replaces only this generated draft. Keep manual decisions in a
separate file so they are not overwritten by a rerun.

The explicit name lists come from inspection of the 306-label reference
inventory, not from an authoritative geographic classification service.
All classifications are draft. A candidate is NOT a final inclusion, a
sovereignty determination, or evidence of complete energy/GDP data.
"""

import csv
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

INPUT_PATH = Path("/opt/spark/outputs/geography_year_inventory.csv")
OUTPUT_PATH = Path("/opt/spark/outputs/geography_scope_review_draft.csv")

AGGREGATE_NAMES = [
    "ASEAN (Ember)",
    "Africa",
    "Africa (EI)",
    "Africa (Ember)",
    "Africa (Shift)",
    "Asia",
    "Asia & Oceania (EIA)",
    "Asia (Ember)",
    "Asia Pacific (EI)",
    "Asia and Oceania (Shift)",
    "Australia and New Zealand (EIA)",
    "CIS (EI)",
    "Central & South America (EIA)",
    "Central America (EI)",
    "Central and South America (Shift)",
    "EU28 (Shift)",
    "Eastern Africa (EI)",
    "Eurasia (EIA)",
    "Eurasia (Shift)",
    "Europe",
    "Europe (EI)",
    "Europe (Ember)",
    "Europe (Shift)",
    "European Union (27)",
    "European Union (EIA)",
    "G20 (Ember)",
    "G7 (Ember)",
    "High-income countries",
    "IEO - Africa (EIA)",
    "IEO - Middle East (EIA)",
    "IEO OECD - Europe (EIA)",
    "Latin America and Caribbean (Ember)",
    "Low-income countries",
    "Lower-middle-income countries",
    "Mexico, Chile, and other OECD Americas (EIA)",
    "Middle Africa (EI)",
    "Middle East (EI)",
    "Middle East (EIA)",
    "Middle East (Ember)",
    "Middle East (Shift)",
    "Non-OECD (EI)",
    "Non-OECD (EIA)",
    "Non-OPEC (EI)",
    "Non-OPEC (EIA)",
    "North America",
    "North America (EI)",
    "North America (Ember)",
    "North America (Shift)",
    "OECD (EI)",
    "OECD (EIA)",
    "OECD (Ember)",
    "OECD (Shift)",
    "OECD - Asia And Oceania (EIA)",
    "OECD - Europe (EIA)",
    "OECD - North America (EIA)",
    "OPEC (EI)",
    "OPEC (EIA)",
    "OPEC (Shift)",
    "OPEC - Africa (EIA)",
    "OPEC - South America (EIA)",
    "Oceania",
    "Oceania (Ember)",
    "Other Non-OECD - America (EIA)",
    "Other Non-OECD - Asia (EIA)",
    "Other Non-OECD - Europe and Eurasia (EIA)",
    "Persian Gulf (EIA)",
    "Persian Gulf (Shift)",
    "South America",
    "South Korea and other OECD Asia (EIA)",
    "South and Central America (EI)",
    "U.S. Pacific Islands (EIA)",
    "U.S. Territories (EIA)",
    "United States Pacific Islands (Shift)",
    "United States Territories (Shift)",
    "Upper-middle-income countries",
    "Western Africa (EI)",
    "World"
]

HISTORICAL_REVIEW_NAMES = [
    "Czechoslovakia",
    "East Germany (EIA)",
    "West Germany (EIA)",
    "Serbia and Montenegro",
    "USSR",
    "Yugoslavia",
    "Netherlands Antilles"
]

SPECIAL_REVIEW_REASONS = {
    "Antarctica": "Review suitability for country-level population and economic comparisons.",
    "Kosovo": "Missing ISO code in this snapshot; review separately rather than excluding for missing code.",
    "Wake Island (EIA)": "Review separately reported area and possible overlap with the Shift series.",
    "Wake Island (Shift)": "Review separately reported area and possible overlap with the EIA series.",
    "Hawaiian Trade Zone (EIA)": "Review the source-specific geographic definition and possible overlap with other entities."
}

def main():
    if not INPUT_PATH.is_file():
        raise FileNotFoundError(f"Run 01_scope_inventory.py first: {INPUT_PATH}")

    spark = SparkSession.builder.appName("Energy - Draft Geography Review").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    try:
        inventory = (spark.read.option("header", True)
                     .option("inferSchema", False)
                     .option("mode", "FAILFAST").csv(str(INPUT_PATH)))
        required = {"country", "iso_code", "first_year", "last_year", "row_count",
                    "distinct_years", "years_present_2000_2018"}
        missing = required - set(inventory.columns)
        if missing:
            raise ValueError(f"Missing input columns: {sorted(missing)}")
        if inventory.filter(F.col("country").isNull()).limit(1).count():
            raise ValueError("An entity name is missing; review the input.")
        if inventory.groupBy("country").count().filter("count > 1").limit(1).count():
            raise ValueError("Multiple inventory rows share a name; review before classifying.")

        name = F.col("country")
        is_aggregate = name.isin(AGGREGATE_NAMES)
        historical_review = name.isin(HISTORICAL_REVIEW_NAMES)
        special_review = name.isin(list(SPECIAL_REVIEW_REASONS))
        has_code = F.coalesce(F.length(F.trim(F.col("iso_code"))) > 0, F.lit(False))

        category = (F.when(is_aggregate, "aggregate")
                    .when(historical_review, "historical_or_combined_entity_review")
                    .when(special_review, "special_entity_review")
                    .when(has_code, "coded_geography_candidate")
                    .otherwise("unclassified_review"))

        reason = (F.when(is_aggregate,
                         "Named global, regional, economic or multi-area aggregate; keep outside country sample.")
                  .when(historical_review,
                        "Review historical or combined-area definition and overlap with successor entities."))
        for entity, explanation in SPECIAL_REVIEW_REASONS.items():
            reason = reason.when(name == entity, explanation)
        reason = (reason.when(has_code,
                              "Code present; verify geographic definition, territory overlap and analysis-specific coverage.")
                  .otherwise("No explicit rule matched; review manually. Missing code is not an exclusion rule."))

        review = (inventory
                  .withColumn("draft_geography_class", category)
                  .withColumn("proposed_scope_status",
                              F.when(is_aggregate, "exclude_from_country_sample")
                              .when(historical_review | special_review | ~has_code, "manual_review")
                              .otherwise("candidate_only"))
                  .withColumn("classification_reason", reason)
                  .withColumn("period_row_status",
                              F.when(F.col("years_present_2000_2018").cast("int") == 19,
                                     "all_19_year_rows_present")
                              .otherwise("incomplete_period_rows"))
                  .withColumn("measurement_coverage_status", F.lit("not_assessed_here"))
                  .withColumn("review_status", F.lit("draft_pending_review"))
                  .orderBy("country"))

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        # Export the small summary to one Excel-friendly CSV; calculations use Spark.
        with OUTPUT_PATH.open("w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=review.columns)
            writer.writeheader()
            written = 0
            for row in review.toLocalIterator():
                writer.writerow(row.asDict())
                written += 1

        print(f"\nDraft saved: {OUTPUT_PATH}")
        print(f"Geographic entities retained: {written}")
        review.groupBy("draft_geography_class", "proposed_scope_status").count().orderBy(
            "draft_geography_class").show(truncate=False)
        print("Draft only: no final sample selected and no energy/GDP coverage inferred.")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
