import json
import logging
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv(Path(__file__).resolve().parent.parent / "config" / ".env")
API_URL = "https://api.geckoapi.com.br/v1/extract"
PAGE_URL = "https://lista.mercadolivre.com.br/celulares-e-telefones"
keyword = "celulares e telefones"
page = 1

def extract_gecko_api(api_url: str, page_url: str, keyword: str, page: int) -> dict:
    try:
        response = requests.post(
            api_url,
            headers={"Authorization": f"Bearer {os.getenv('API_KEY')}"},
            json={
                "target": "mercadolivre.com.br",
                "type": "plp",
                "url": page_url,
                "page": page,
                "keyword": keyword,
            },
            timeout=30,
        )
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        return {}

    if response.status_code != 200:
        logger.error(f"Request failed with status code: {response.status_code}")
        return {}

    data = response.json()

    if not data:
        logger.warning("Response JSON is empty")
        return {}

    output_path = 'data/gecko_data.json'
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)

    logger.info(f"Response saved to {output_path}")
    return data

extract_gecko_api(API_URL, PAGE_URL, keyword, page)