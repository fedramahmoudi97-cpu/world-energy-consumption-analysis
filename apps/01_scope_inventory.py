import csv
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

DATA_PATH = "/opt/spark/data/World Energy Consumption.csv"
OUTPUT_PATH = Path("/opt/spark/outputs/geography_year_inventory.csv")

spark = (
    SparkSession.builder
    .appName("Energy - Geography and Year Inventory")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

try:
    raw = (
        spark.read
        .option("header", True)
        .option("inferSchema", False)
        .option("mode", "FAILFAST")
        .csv(DATA_PATH)
    )

    df = raw.select(
        "country",
        "iso_code",
        F.col("year").cast("int").alias("year")
    )

    if df.filter(F.col("year").isNull()).limit(1).count():
        raise ValueError("Missing or invalid year found; review before continuing.")

    inventory = (
        df.groupBy("country", "iso_code")
        .agg(
            F.min("year").alias("first_year"),
            F.max("year").alias("last_year"),
            F.count("*").alias("row_count"),
            F.countDistinct("year").alias("distinct_years"),
            F.countDistinct(
                F.when(F.col("year").between(2000, 2018), F.col("year"))
            ).alias("years_present_2000_2018")
        )
        .orderBy("country", "iso_code")
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=inventory.columns)
        writer.writeheader()

        for row in inventory.toLocalIterator():
            writer.writerow(row.asDict())

    print(f"\nInventory saved to: {OUTPUT_PATH}")
    inventory.show(10, truncate=False)

finally:
    spark.stop()