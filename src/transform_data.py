from pathlib import Path
import pandas as pd
import json

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

LOCAL_PATH = Path("../data") / "bronze_data.json"
columns_names_to_rename = {
    "requestId": "request_id",
    "executionId": "execution_id",
    "data.source": "source",
    "data.type": "type",
    "data.url": "url",
    "data.requestUrl": "request_url",
    "data.extractedAt": "extracted_at",
    "data.query": "query",
    "data.totalResults": "total_results",
    "data.primaryResults": "primary_results",
    "data.page": "page",
    "data.resultsPerPage": "results_per_page",
    "data.offset": "offset",
    "data.nextPage": "next_page",
    "data.nextPageUrl": "next_page_url",
    #data.items columns will be normalized separately
}

def create_dataframe(local_path: str) -> pd.DataFrame:
    #logging.info("Creating DataFrame from the JSON file...")
    path = local_path

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with open(path) as f:
        data = json.load(f)

    df = pd.json_normalize(data)
    #logging.info(f"\nDataFrame created with {len(df)} row(s)")
    return df


def normalize_data_items_columns(df: pd.DataFrame) -> pd.DataFrame:
    df_exploded = df.explode('data.items').reset_index(drop=True)

    df_data_items = pd.json_normalize(df_exploded['data.items'])
    
    '''if 'aggregateRating' in df_data_items:
        df_data_items = df_data_items.drop(columns=['aggregateRating'])'''

    df_data_items = df_data_items.rename(columns={
        'url': 'data_items_url',
        'imageUrl': 'data_items_imageUrl',
        'sku': 'data_items_sku',
        'categoryId': 'data_items_categoryId',
        'domainId': 'data_items_domainId',
        'name': 'data_items_name',
        'condition': 'data_items_condition',
        'currency': 'data_items_currency',
        'currencyRaw': 'data_items_currencyRaw',
        'price': 'data_items_price',
        'highlight': 'data_items_highlight',
        'isBestSeller': 'data_items_isBestSeller',
        'isPowerSeller': 'data_items_isPowerSeller',
        'powerSellerStatusTitle': 'data_items_powerSellerStatusTitle',
        'ean': 'data_items_ean',
        'sellerId': 'data_items_sellerId',
        'sellerName': 'data_items_sellerName',
        'sellerCity': 'data_items_sellerCity',
        'sellerState': 'data_items_sellerState',
        'sellerCountry': 'data_items_sellerCountry',
        'aggregateRating.rating': 'data_items_aggregateRating_rating',
        'aggregateRating.reviewCount': 'data_items_aggregateRating_reviewCount',
        'aggregateRating': 'aggregateRating'
    })

    df = pd.concat([df_exploded, df_data_items], axis=1)
    logging.info(f"\nNormalized 'data.items' column - {len(df.columns)} columns")
    return df
