from pyspark.sql import SparkSession

DATA_PATH = "/opt/spark/data/World Energy Consumption.csv"

spark = (
    SparkSession.builder
    .appName("Energy - Environment Check")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

try:
    df = (
        spark.read
        .option("header", True)
        .option("inferSchema", False)
        .option("mode", "FAILFAST")
        .csv(DATA_PATH)
    )

    print("\n=== Environment Check ===")
    print(f"Spark version: {spark.version}")
    print(f"Spark master: {spark.sparkContext.master}")
    print(f"Rows: {df.count():,}")
    print(f"Columns: {len(df.columns)}")

    df.select("country", "year", "iso_code").show(5, truncate=False)

finally:
    spark.stop()