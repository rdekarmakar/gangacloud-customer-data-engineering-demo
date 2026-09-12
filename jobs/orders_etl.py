from pathlib import Path
from shutil import which

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


EXPECTED_ROWS = [
    ("ai", 1, 1500),
    ("cloud", 2, 2000),
    ("data", 3, 4700),
]


def main() -> None:
    if which("java") is None:
        raise RuntimeError(
            "Java is required to run this PySpark demo, but `java` was not found "
            "on PATH. Install a JDK and rerun `make validate`."
        )

    repo_root = Path(__file__).resolve().parents[1]
    input_path = repo_root / "data" / "input" / "orders.csv"
    output_path = repo_root / "data" / "output" / "orders_by_category_parquet"

    spark = (
        SparkSession.builder.master("local[*]")
        .appName("GangaCloudOrdersETLDemo")
        .getOrCreate()
    )

    try:
        orders_df = spark.read.csv(
            str(input_path),
            header=True,
            inferSchema=True,
        )

        result_df = (
            orders_df.filter(F.col("status") == "success")
            .groupBy("category")
            .agg(
                F.count("*").cast("long").alias("successful_order_count"),
                F.sum("amount").cast("long").alias("total_success_amount"),
            )
            .select("category", "successful_order_count", "total_success_amount")
            .orderBy("category")
        )

        result_df.write.mode("overwrite").parquet(str(output_path))

        actual_rows = [
            (
                row["category"],
                row["successful_order_count"],
                row["total_success_amount"],
            )
            for row in spark.read.parquet(str(output_path)).orderBy("category").collect()
        ]

        if actual_rows != EXPECTED_ROWS:
            raise ValueError(
                "Validation failed. "
                f"Expected {EXPECTED_ROWS}, but got {actual_rows}."
            )

        print("Validation passed.")
        print("GangaCloud Data Engineering Workspace demo completed successfully.")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
