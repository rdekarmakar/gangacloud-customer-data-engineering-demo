import os
import sys
from pathlib import Path
from shutil import which

import boto3
import psycopg
from botocore.config import Config
from pyspark.sql import SparkSession
from pyspark.sql import functions as F


EXPECTED_ROWS = [
    ("ai", 1, 1500),
    ("cloud", 2, 2000),
    ("data", 3, 4700),
]
OBJECT_KEY = "orders/curated/category_summary/category_summary.parquet"
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS category_order_summary (
    category TEXT PRIMARY KEY,
    successful_order_count BIGINT NOT NULL,
    total_success_amount BIGINT NOT NULL
)
"""


def load_dotenv(path: Path) -> None:
    if not path.is_file():
        raise RuntimeError(
            f"Environment file not found: {path}. Copy .env.example to .env first."
        )

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


def require_environment() -> dict[str, str]:
    names = (
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "MINIO_ROOT_USER",
        "MINIO_ROOT_PASSWORD",
        "MINIO_ENDPOINT",
        "MINIO_BUCKET",
    )
    missing = [name for name in names if not os.environ.get(name)]
    if missing:
        raise RuntimeError(
            "Missing required environment variables: " + ", ".join(missing)
        )
    return {name: os.environ[name] for name in names}


def minio_client(config: dict[str, str]):
    return boto3.client(
        "s3",
        endpoint_url=config["MINIO_ENDPOINT"],
        aws_access_key_id=config["MINIO_ROOT_USER"],
        aws_secret_access_key=config["MINIO_ROOT_PASSWORD"],
        region_name="us-east-1",
        config=Config(
            connect_timeout=5,
            read_timeout=15,
            retries={"max_attempts": 2},
            s3={"addressing_style": "path"},
        ),
    )


def main() -> None:
    if which("java") is None:
        raise RuntimeError(
            "Java is required to run this PySpark pipeline, but `java` was not "
            "found on PATH. Install a JDK and rerun `make pipeline-run`."
        )

    repo_root = Path(__file__).resolve().parents[1]
    load_dotenv(repo_root / ".env")
    config = require_environment()
    input_path = repo_root / "data" / "input" / "orders.csv"
    output_path = Path(
        os.getenv(
            "PIPELINE_OUTPUT_PATH",
            str(repo_root / "data" / "output" / "platform_etl" / "category_summary"),
        )
    )

    spark = (
        SparkSession.builder.master("local[*]")
        .appName("GangaCloudOrdersPlatformETL")
        .getOrCreate()
    )

    try:
        orders_df = spark.read.csv(str(input_path), header=True, inferSchema=True)
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

        actual_rows = [
            (
                row["category"],
                row["successful_order_count"],
                row["total_success_amount"],
            )
            for row in result_df.collect()
        ]
        if actual_rows != EXPECTED_ROWS:
            raise ValueError(
                f"Spark validation failed. Expected {EXPECTED_ROWS}, got {actual_rows}."
            )

        result_df.coalesce(1).write.mode("overwrite").parquet(str(output_path))
    finally:
        spark.stop()

    parquet_parts = sorted(output_path.glob("part-*.parquet"))
    if len(parquet_parts) != 1:
        raise RuntimeError(
            f"Expected one generated Parquet part in {output_path}, "
            f"but found {len(parquet_parts)}."
        )

    s3 = minio_client(config)
    try:
        s3.head_bucket(Bucket=config["MINIO_BUCKET"])
        s3.upload_file(
            str(parquet_parts[0]),
            config["MINIO_BUCKET"],
            OBJECT_KEY,
        )
        s3.head_object(Bucket=config["MINIO_BUCKET"], Key=OBJECT_KEY)
    except Exception as exc:
        raise RuntimeError(
            "MinIO upload or verification failed. Ensure the stack is healthy and "
            "run `make storage-init`."
        ) from exc

    try:
        with psycopg.connect(
            host=os.getenv("POSTGRES_HOST", "127.0.0.1"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            dbname=config["POSTGRES_DB"],
            user=config["POSTGRES_USER"],
            password=config["POSTGRES_PASSWORD"],
            connect_timeout=5,
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(CREATE_TABLE_SQL)
                cursor.execute("DELETE FROM category_order_summary")
                cursor.executemany(
                    """
                    INSERT INTO category_order_summary (
                        category,
                        successful_order_count,
                        total_success_amount
                    ) VALUES (%s, %s, %s)
                    """,
                    actual_rows,
                )
                cursor.execute(
                    """
                    SELECT category, successful_order_count, total_success_amount
                    FROM category_order_summary
                    ORDER BY category
                    """
                )
                postgres_rows = cursor.fetchall()
    except psycopg.Error as exc:
        raise RuntimeError(
            "PostgreSQL load or read-back failed. Ensure the stack is healthy and "
            "the .env credentials match the running container."
        ) from exc

    if postgres_rows != EXPECTED_ROWS:
        raise ValueError(
            "PostgreSQL validation failed. "
            f"Expected {EXPECTED_ROWS}, got {postgres_rows}."
        )

    print("Validation passed.")
    print("MinIO Parquet object verified.")
    print("PostgreSQL result verified.")
    print("GangaCloud end-to-end Data Engineering pipeline completed successfully.")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"GangaCloud end-to-end pipeline failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
