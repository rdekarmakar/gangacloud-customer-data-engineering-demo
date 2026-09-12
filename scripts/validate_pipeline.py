import os
import sys
from pathlib import Path

import boto3
import psycopg
from botocore.config import Config


EXPECTED_ROWS = [
    ("ai", 1, 1500),
    ("cloud", 2, 2000),
    ("data", 3, 4700),
]
OBJECT_KEY = "orders/curated/category_summary/category_summary.parquet"


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
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def required(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    load_dotenv(repo_root / ".env")

    bucket = required("MINIO_BUCKET")
    s3 = boto3.client(
        "s3",
        endpoint_url=required("MINIO_ENDPOINT"),
        aws_access_key_id=required("MINIO_ROOT_USER"),
        aws_secret_access_key=required("MINIO_ROOT_PASSWORD"),
        region_name="us-east-1",
        config=Config(
            connect_timeout=5,
            read_timeout=15,
            retries={"max_attempts": 2},
            s3={"addressing_style": "path"},
        ),
    )
    try:
        s3.head_bucket(Bucket=bucket)
        s3.head_object(Bucket=bucket, Key=OBJECT_KEY)
    except Exception as exc:
        raise RuntimeError(
            f"MinIO validation failed for s3://{bucket}/{OBJECT_KEY}."
        ) from exc

    try:
        with psycopg.connect(
            host="127.0.0.1",
            port=5432,
            dbname=required("POSTGRES_DB"),
            user=required("POSTGRES_USER"),
            password=required("POSTGRES_PASSWORD"),
            connect_timeout=5,
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT to_regclass('public.category_order_summary')")
                if cursor.fetchone()[0] is None:
                    raise RuntimeError(
                        "PostgreSQL table is missing: category_order_summary"
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
            "PostgreSQL validation failed. Check that the stack is healthy and "
            "the .env credentials match the container."
        ) from exc

    if postgres_rows != EXPECTED_ROWS:
        raise ValueError(
            "PostgreSQL rows differ from the expected result. "
            f"Expected {EXPECTED_ROWS}, got {postgres_rows}."
        )

    print("GangaCloud end-to-end pipeline validation passed.")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Pipeline validation failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
