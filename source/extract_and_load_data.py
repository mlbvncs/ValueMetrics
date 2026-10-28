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
from dotenv import load_dotenv, set_key

p = Path(__file__).parent.resolve().parent
Path(p / 'logs').mkdir(parents=True, exist_ok=True)

format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
filename_path = Path(p / 'logs' / 'extract_and_load_data.log')
logging.basicConfig(format=format, filename=filename_path, encoding='utf-8', level=logging.INFO)
logger = logging.getLogger(__name__)

env = p / '.env'
env.touch()
load_dotenv(dotenv_path=env)

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
            timeout=(10, 120)
        )
        response.raise_for_status()

        data = response.json()

        if data.get('notFound') is True:
            logger.error("notFound=true: entity not found")
            raise ValueError("notFound=true: entity not found")

        logger.info(f"Page {page} extracted from GeckoAPI")
        return data
    except Exception as e:
        logger.error(f"Error occurred while trying to extract page {page} from GeckoAPI: {e}")
        raise

def extract_data():
    logger.info("Fetching page 1")

    data = extract_data_model(1)
    all_pages = [data]

    total_pages = math.ceil(data["data"]["totalResults"] / data["data"]["resultsPerPage"])
    for i in range(2, total_pages + 1):
        logger.info(f"Fetching page {i}")
        data = extract_data_model(i)
        all_pages.append(data)

    logger.info("All pages have been obtained from GeckoAPI")
    return all_pages

def upload_data(data, date_time_str, key=None):
    if key is None:
        key = f"bronze/mercadolivre/celulares-e-telefones/{date_time_str}/bronze_data.json"

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
        logger.info("bronze_data.json uploaded to Amazon S3")
    except Exception as e:
        logger.error(f"Error occurred while uploading file to Amazon S3: {e}")
        raise

date_time_obj = datetime.now(ZoneInfo('America/Sao_Paulo'))
date_time_str = date_time_obj.strftime('%Y-%m-%dT%H-%M-%S')
set_key(dotenv_path=env, key_to_set="EXTRACT_DATETIME", value_to_set=date_time_str)
def main():
    upload_data(extract_data(), date_time_str)

if __name__ == '__main__':
    main()