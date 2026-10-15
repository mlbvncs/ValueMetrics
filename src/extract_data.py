import logging
import math
import os
import json

import pandas as pd
import requests
from dotenv import load_dotenv
from pathlib import Path

p = Path(__file__).parent.resolve().parent
Path(p / 'logs').mkdir(parents=True, exist_ok=True)

format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
filename_path = Path(p / 'logs' / 'extract_data.log')
logging.basicConfig(format=format, filename=filename_path, encoding='utf-8', level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(dotenv_path=p / 'config' / '.env')

def extracting_data(page: int) -> pd.DataFrame:
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

def main():
    Path(p / 'data').mkdir(parents=True, exist_ok=True)

    data = extracting_data(1)
    all_pages = [data]

    total_pages = math.ceil(data["data"]["totalResults"] / data["data"]["resultsPerPage"])
    for i in range(2, total_pages + 1):
         data = extracting_data(i)
         all_pages.append(data)

    with Path(p / 'data' / 'bronze_data.json').open('w', encoding='utf-8') as f:
            json.dump(all_pages, f, indent=2, ensure_ascii=False)

    return 0

if __name__ == '__main__':
    main()