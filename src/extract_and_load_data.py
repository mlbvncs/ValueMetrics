import json
import logging
import math
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import boto3
import pandas as pd
import requests
from dotenv import load_dotenv

p = Path(__file__).parent.resolve().parent
Path(p / 'logs').mkdir(parents=True, exist_ok=True)

format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
filename_path = Path(p / 'logs' / 'extract_and_load_data.log')
logging.basicConfig(format=format, filename=filename_path, encoding='utf-8', level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(dotenv_path=p / 'config' / '.env')

def extract_data_model(page: int) -> pd.DataFrame:
    if not os.getenv('API_KEY'):
        logger.error("API_KEY is not set in the environment variables.")
        raise TypeError("Expected string for API_KEY, received None (API_KEY is not set in the environment variables).")

    try:
        response = requests.post(
            "https://api.geckoapi.com.br/v1/extract",
            headers={"Authorization": f"Bearer {os.environ['API_KEY']}"},
            json={
                "url": "https://lista.mercadolivre.com.br/iphone-15-pro-max",
                "target": "mercadolivre.com.br",
                "type": "plp",
                "page": page
            },
            timeout = 30
        )
        return response.json()
    except Exception as e:
        logger.error(f"Error occurred while extracting data: {e}")
        raise

def extract_data():
    data = extract_data_model(1)
    all_pages = [data]

    total_pages = math.ceil(data["data"]["totalResults"] / data["data"]["resultsPerPage"])
    for i in range(2, total_pages + 1):
        data = extract_data_model(i)
        all_pages.append(data)

    return all_pages

def upload_data(data, key=None):
    if key is None:
        key = f"bronze/mercadolivre/celulares-e-telefones/{datetime.now(ZoneInfo('America/Sao_Paulo'))}/bronze_data.json"

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
        s3_client.put_object(
            Bucket=os.getenv('S3_BUCKET_NAME'),
            Key=key,
            Body=json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')
        )
    except Exception as e:
        logger.error(f"Error occurred while uploading file: {e}")
        raise

def main():
    upload_data(extract_data())

if __name__ == '__main__':
    main()