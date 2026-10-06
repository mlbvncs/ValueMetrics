import os
from datetime import date
from pathlib import Path

import boto3
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / "config" / ".env")
LOCAL_PATH = Path("data") / "gecko_data.json"
BUCKET = os.environ["S3_BUCKET_NAME"]


def upload_to_s3(local_path: Path, bucket: str, key: str) -> None:
    s3 = boto3.client("s3")
    s3.upload_file(str(local_path), bucket, key)


def main() -> None:
    today = date.today().isoformat()
    key = f"bronze/mercadolivre/celulares-e-telefones/{today}/gecko_data.json"
    upload_to_s3(LOCAL_PATH, BUCKET, key)
    print(f"Uploaded to s3://{BUCKET}/{key}")


if __name__ == "__main__":
    main()