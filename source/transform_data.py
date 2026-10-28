import io
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import boto3
import pandas as pd
from dotenv import load_dotenv, set_key

p = Path(__file__).parent.resolve().parent
Path(p / 'logs').mkdir(parents=True, exist_ok=True)

format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
filename_path = Path(p / 'logs' / 'transform_data.log')
logging.basicConfig(format=format, filename=filename_path, encoding='utf-8', level=logging.INFO)
logger = logging.getLogger(__name__)

env = p / '.env'
load_dotenv(dotenv_path=env)

drop_columns = [
    'requestId', 'executionId', 'data.source', 'data.type', 'data.url', 
    'data.requestUrl', 'data.query', 'data.totalResults', 'data.primaryResults', 
    'data.page', 'data.resultsPerPage', 'data.offset', 'data.nextPage', 
    'data.nextPageUrl', 'data.items', 'aggregateRating'
]
columns_to_rename = {
    'url': 'url',
    'sku': 'sku',
    'data.extractedAt': 'extracted_at',
    'imageUrl': 'image_url',
    'categoryId': 'category_id',
    'domainId': 'domain_id',
    'name': 'name',
    'condition': 'condition',
    'currency': 'currency',
    'currencyRaw': 'currency_raw',
    'price': 'price',
    'highlight': 'highlight',
    'isBestSeller': 'is_best_seller',
    'isPowerSeller': 'is_power_seller',
    'powerSellerStatusTitle': 'power_seller_status_title',
    'ean': 'ean',
    'sellerId': 'seller_id',
    'sellerName': 'seller_name',
    'sellerCity': 'seller_city',
    'sellerState': 'seller_state',
    'sellerCountry': 'seller_country',
    'aggregateRating.rating': 'rating',
    'aggregateRating.reviewCount': 'review_count',
}

def extract_data():
    if not os.getenv('EXTRACT_DATETIME'):
        logger.error("EXTRACT_DATETIME is not set in the environment variables.")
        raise TypeError("Expected string for EXTRACT_DATETIME, received None (EXTRACT_DATETIME is not set in the environment variables).")

    try:
        s3_client = boto3.client(
            's3', 
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), 
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        response = s3_client.get_object(
            Bucket=os.getenv('S3_BUCKET_NAME'), 
            Key=f"bronze/mercadolivre/celulares-e-telefones/{os.getenv('EXTRACT_DATETIME')}/bronze_data.json"
        )
        data = json.loads(response['Body'].read().decode('utf-8'))
        logger.info("bronze_data.json obtained from Amazon S3")
        return data
    except Exception as e:
        logger.error(f"Error occurred while extracting data from Amazon S3: {e}")
        raise

def create_dataframe() -> pd.DataFrame:
    data = extract_data()
    df = pd.json_normalize(data)

    return df

#1
def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    df_data_items = df.explode('data.items', ignore_index=True)
    df_items = pd.json_normalize(df_data_items['data.items'])
    df = pd.concat(
        [df_data_items, df_items],
        axis=1
    )
    
    return df

#2
def drop_unnecessary(df: pd.DataFrame, drop_columns: list) -> pd.DataFrame:
    df = df.drop(drop_columns, axis=1)
    
    return df

#3
def rename_columns(df: pd.DataFrame, columns_to_rename: dict) -> pd.DataFrame:
    for key, value in columns_to_rename.items():
        df.rename(columns={key: value}, inplace=True)

    return df

#4
def convert_type(df: pd.DataFrame) -> pd.DataFrame:
    df['extracted_at'] = pd.to_datetime(df['extracted_at'], errors='coerce').dt.tz_convert('America/Sao_Paulo')
    df = df.astype(
            {
                "url": "string", 
                "image_url": "string", 
                "sku": "string",
                "category_id": "string",
                "domain_id": "string",
                "name": "string",
                "condition": "string",
                "currency": "string",
                "currency_raw": "string",
                "price": "Float64",
                "highlight": "string",
                "is_best_seller": "boolean",
                "is_power_seller": "boolean",
                "power_seller_status_title": "string",
                "rating": "Float64",
                "review_count": "Float64",
                "ean": "string",
                "seller_id": "string",
                "seller_name": "string",
                "seller_city": "string",
                "seller_state": "string",
                "seller_country": "string"
            }
        )

    return df

#5
def treat_outliers(df: pd.DataFrame) -> pd.DataFrame:
    #price
    df = df.dropna(subset='price', ignore_index=True)
    #rating
    df.loc[(df['rating'] < 1) | (df['rating'] > 5), 'rating'] = 0

    return df

#6

#7
def treat_identification_columns(df: pd.DataFrame) -> pd.DataFrame:
    #unique
    df.drop_duplicates(subset=['url', 'sku'], inplace=True, ignore_index=True)
    other_columns = [col for col in df.columns if col not in ['url', 'sku']]
    df = df.reindex(columns=['url', 'sku'] + other_columns)
    
    return df

def upload_data(df, upload_date_time_str, key=None):
    if key is None:
        key = f"silver/mercadolivre/celulares-e-telefones/{upload_date_time_str}/silver_data.parquet"

    try:
        parquet_buffer = io.BytesIO()
        df.to_parquet(parquet_buffer, engine='pyarrow', index=False)

        s3_client = boto3.client('s3')
        s3_client.put_object(
            Bucket=os.getenv('S3_BUCKET_NAME'),
            Key=key,
            Body=parquet_buffer.getvalue()
        )
        logger.info("silver_data.parquet uploaded to Amazon S3")
    except Exception as e:
        logger.error(f"Error occurred while uploading file to Amazon S3: {e}")
        raise

upload_date_time_obj = datetime.now(ZoneInfo('America/Sao_Paulo'))
upload_date_time_str = upload_date_time_obj.strftime('%Y-%m-%dT%H-%M-%S')
set_key(dotenv_path=env, key_to_set="TRANSFORM_DATETIME", value_to_set=upload_date_time_str)
def main():
    df = create_dataframe()
    df = normalize_df(df)
    df = drop_unnecessary(df, drop_columns)
    df = rename_columns(df, columns_to_rename)
    df = convert_type(df)
    df = treat_outliers(df)

    df = treat_identification_columns(df)
    upload_data(df, upload_date_time_str)

if __name__ == '__main__':
    main()