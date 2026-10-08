import json
import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

LOCAL_PATH = Path("../data") / "bronze_data.json"
columns_names_to_drop = [
    'requestId', 'executionId', 'data.source', 'data.type', 
    'data.url', 'data.requestUrl', 'data.query', 'data.totalResults', 
    'data.primaryResults', 'data.page', 'data.resultsPerPage', 'data.offset', 
    'data.nextPage', 'data.nextPageUrl', 'data.items', 'categoryId', 'domainId', 'currency',
    'currencyRaw', 'aggregateRating'
]
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
    logger.info("Creating DataFrame from the JSON file...")
    path = local_path

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with open(path) as f:
        data = json.load(f)

    df = pd.json_normalize(data)
    logger.info(f"DataFrame created with {len(df)} row(s)")
    return df


def normalize_data_items_columns(df: pd.DataFrame) -> pd.DataFrame:
    df_exploded = df.explode('data.items').reset_index(drop=True)

    df_data_items = pd.json_normalize(df_exploded['data.items'])
    
    df = pd.concat(
        [df_exploded.drop(columns="data.items"), df_data_items],
        axis=1,
    )

    logger.info(f"\nNormalized 'data.items' column - {len(df.columns)} columns")
    return df

def drop_columns(df: pd.DataFrame, columns_to_drop: list) -> pd.DataFrame:
    df = df.drop(columns=columns_to_drop, errors='ignore')

    logger.info(f"\nDropped columns - {len(columns_to_drop)} columns dropped")
    return df 