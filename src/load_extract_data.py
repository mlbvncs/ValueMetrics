import logging
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import boto3
import botocore
from botocore.exceptions import ClientError
from dotenv import load_dotenv

archive_p = Path(__file__).parent.resolve().parent

format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
filename_path = Path(archive_p / 'logs' / 'load_data.log')
logging.basicConfig(format=format, filename=filename_path, encoding='utf-8', level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(dotenv_path=archive_p / 'config' / '.env')
LOCAL_PATH = Path(archive_p / 'data' / 'bronze_data.json')
FILENAME = LOCAL_PATH.name

def upload_file(file_name, object_name=None):
    if object_name is None:
        object_name = f"bronze/mercadolivre/celulares-e-telefones/{datetime.now(ZoneInfo('America/Sao_Paulo'))}/{FILENAME}"

    if not os.getenv('S3_BUCKET_NAME'):
        logger.error("S3_BUCKET_NAME is not set in the environment variables.")
        raise TypeError("Expected string for S3_BUCKET_NAME, received None (S3_BUCKET_NAME is not set in the environment variables).")

    if not os.getenv('AWS_ACCESS_KEY_ID'):
        logger.error("AWS_ACCESS_KEY_ID is not set in the environment variables.")
        raise TypeError("Expected string for AWS_ACCESS_KEY_ID, received None (AWS_ACCESS_KEY_ID is not set in the environment variables).")

    if not os.getenv('AWS_SECRET_ACCESS_KEY'):
        logger.error("AWS_SECRET_ACCESS_KEY is not set in the environment variables.")
        raise TypeError("Expected string for AWS_SECRET_ACCESS_KEY, received None (AWS_SECRET_ACCESS_KEY is not set in the environment variables).")

    try:
        s3_client = boto3.client('s3')
        s3_client.upload_file(file_name, os.getenv('S3_BUCKET_NAME'), object_name)
    except Exception as e:
        logger.error(f"Error occurred while uploading file: {e}")
        raise

def main():
    upload_file(LOCAL_PATH)

    return 0

if __name__ == '__main__':
    main()