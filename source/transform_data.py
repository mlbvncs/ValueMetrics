import io
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import boto3
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from dotenv import set_key

p = Path(__file__).parent.resolve().parent
Path(p / 'logs').mkdir(parents=True, exist_ok=True)

format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
filename_path = Path(p / 'logs' / 'transform_data.log')
logging.basicConfig(format=format, filename=filename_path, encoding='utf-8', level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(dotenv_path=p / '.env')

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
    

    if not os.getenv('S3_BUCKET_NAME'):
        logger.error("S3_BUCKET_NAME is not set in the environment variables.")
        raise TypeError("Expected string for S3_BUCKET_NAME, received None (S3_BUCKET_NAME is not set in the environment variables).")

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

def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    df_data_items = df.explode('data.items', ignore_index=True)
    df_items = pd.json_normalize(df_data_items['data.items'])
    df = pd.concat(
        [df_data_items, df_items],
        axis=1
    )

    return df

def drop_unnecessary(df: pd.DataFrame, drop_columns: list) -> pd.DataFrame:
    df_drop = df.drop(drop_columns, axis=1)
    return df_drop

def standard_dataextractedat(df: pd.DataFrame) -> pd.DataFrame:
    df['data.extractedAt'] = pd.to_datetime(df['data.extractedAt'])
    df['data.extractedAt'] = df['data.extractedAt'].dt.tz_convert('America/Sao_Paulo')

    return df

def treat_identification_columns(df: pd.DataFrame) -> pd.DataFrame:
    #nulls and empty strings
    df = df.replace(r'^\s*$', np.nan, regex=True)
    df = df.dropna(subset=['url', 'sku'], ignore_index=True)
    #unique
    df.drop_duplicates(subset=['url', 'sku'], inplace=True, ignore_index=True)

    other_columns = [col for col in df.columns if col not in ['url', 'sku']]
    df = df.reindex(columns=['url', 'sku'] + other_columns)
    
    return df

def impute_values(df: pd.DataFrame) -> pd.DataFrame:
    df.loc[df['highlight'].isna(), 'highlight'] = 'Sem destaque'

    return df

def treat_outliers(df: pd.DataFrame) -> pd.DataFrame:
    #price
    df = df.dropna(subset='price', ignore_index=True)

    #aggregateRating.rating
    df.loc[(df['aggregateRating.rating'] < 1) | (df['aggregateRating.rating'] > 5), 'aggregateRating.rating'] = np.nan

    return df

def rename_columns(df: pd.DataFrame, columns_to_rename: dict) -> pd.DataFrame:
    for key, value in columns_to_rename.items():
        df.rename(columns={key: value}, inplace=True)

    return df

def upload_data(df, upload_date_time_str, key=None):
    if not os.getenv('EXTRACT_DATETIME'):
        logger.error("EXTRACT_DATETIME is not set in the environment variables.")
        raise TypeError("Expected string for EXTRACT_DATETIME, received None (EXTRACT_DATETIME is not set in the environment variables).")

    if not os.getenv('S3_BUCKET_NAME'):
        logger.error("S3_BUCKET_NAME is not set in the environment variables.")
        raise TypeError("Expected string for S3_BUCKET_NAME, received None (S3_BUCKET_NAME is not set in the environment variables).")
    
    if key is None:
        key = f"silver/mercadolivre/celulares-e-telefones/{upload_date_time_str}/silver_data.parquet"

    if not os.getenv('AWS_ACCESS_KEY_ID'):
        logger.error("AWS_ACCESS_KEY_ID is not set in the environment variables.")
        raise TypeError("Expected string for AWS_ACCESS_KEY_ID, received None (AWS_ACCESS_KEY_ID is not set in the environment variables).")

    if not os.getenv('AWS_SECRET_ACCESS_KEY'):
        logger.error("AWS_SECRET_ACCESS_KEY is not set in the environment variables.")
        raise TypeError("Expected string for AWS_SECRET_ACCESS_KEY, received None (AWS_SECRET_ACCESS_KEY is not set in the environment variables).")

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
env = '.env'
set_key(dotenv_path=env, key_to_set="TRANSFORM_DATETIME", value_to_set=upload_date_time_str)
def main():
    df = create_dataframe()
    df = normalize_df(df)
    df = drop_unnecessary(df, drop_columns)
    df = standard_dataextractedat(df)
    df = treat_identification_columns(df)
    df = impute_values(df)
    df = treat_outliers(df)
    df = rename_columns(df, columns_to_rename)
    upload_data(df, upload_date_time_str)

if __name__ == '__main__':
    main()