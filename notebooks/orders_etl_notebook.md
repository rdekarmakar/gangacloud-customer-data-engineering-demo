# Orders ETL Notebook

This notebook-style walkthrough mirrors `jobs/orders_etl.py` for the M28.2 GangaCloud Data Engineering Workspace demo.

## Cell 1: Create a Local PySpark Session

```python
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = (
    SparkSession.builder.master("local[*]")
    .appName("GangaCloudOrdersETLNotebook")
    .getOrCreate()
)
```

## Cell 2: Define Paths

```python
repo_root = Path.cwd()
input_path = repo_root / "data" / "input" / "orders.csv"
output_path = repo_root / "data" / "output" / "orders_by_category_parquet"
```

## Cell 3: Read Orders CSV

```python
orders_df = spark.read.csv(
    str(input_path),
    header=True,
    inferSchema=True,
)

orders_df.show()
orders_df.printSchema()
```

## Cell 4: Filter Successful Orders

```python
successful_orders_df = orders_df.filter(F.col("status") == "success")
successful_orders_df.show()
```

## Cell 5: Aggregate by Category

```python
result_df = (
    successful_orders_df.groupBy("category")
    .agg(
        F.count("*").cast("long").alias("successful_order_count"),
        F.sum("amount").cast("long").alias("total_success_amount"),
    )
    .select("category", "successful_order_count", "total_success_amount")
    .orderBy("category")
)

result_df.show()
```

## Cell 6: Write Parquet

```python
result_df.write.mode("overwrite").parquet(str(output_path))
```

## Cell 7: Read Parquet Back

```python
parquet_df = spark.read.parquet(str(output_path)).orderBy("category")
parquet_df.show()
```

## Cell 8: Validate Expected Result

```python
expected_rows = [
    ("ai", 1, 1500),
    ("cloud", 2, 2000),
    ("data", 3, 4700),
]

actual_rows = [
    (
        row["category"],
        row["successful_order_count"],
        row["total_success_amount"],
    )
    for row in parquet_df.collect()
]

if actual_rows != expected_rows:
    raise ValueError(f"Validation failed. Expected {expected_rows}, but got {actual_rows}.")

print("Validation passed.")
print("GangaCloud Data Engineering Workspace demo completed successfully.")
```

## Cell 9: Stop Spark

```python
spark.stop()
```
