import os
import sys
from pathlib import Path

import boto3
import psycopg
from botocore.config import Config
from botocore.exceptions import ClientError


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
        print(f"MinIO bucket already exists: {bucket}")
    except ClientError as exc:
        error_code = str(exc.response.get("Error", {}).get("Code", ""))
        status_code = exc.response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        if error_code in {"404", "NoSuchBucket", "NotFound"} or status_code == 404:
            s3.create_bucket(Bucket=bucket)
            print(f"Created MinIO bucket: {bucket}")
        else:
            raise RuntimeError(f"Unable to inspect MinIO bucket {bucket}.") from exc
    except Exception as exc:
        raise RuntimeError(
            "Unable to connect to MinIO. Check that the Docker stack is healthy."
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
                cursor.execute(CREATE_TABLE_SQL)
        print("PostgreSQL table is ready: category_order_summary")
    except psycopg.Error as exc:
        raise RuntimeError(
            "Unable to initialize PostgreSQL. Check that the Docker stack is "
            "healthy and the .env credentials match the container."
        ) from exc

    print("GangaCloud storage initialization completed successfully.")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Storage initialization failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
