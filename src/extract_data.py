import json
import os
from math import ceil
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / "config" / ".env")

API_URL = "https://api.geckoapi.com.br/v1/extract"
PAGE_URL = "https://lista.mercadolivre.com.br/celulares-e-telefones"
KEYWORD = "celulares e telefones"

import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_gecko_api(api_url: str, page_url: str, keyword: str, page: int) -> dict:
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("API_KEY not set")

    try:
        response = requests.post(
            api_url,
            headers={"Authorization": f"Bearer {api_key}"},
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
        raise ValueError(f"Request failed: {e}") from e

    if response.status_code != 200:
        raise ValueError(f"Request failed with status code: {response.status_code}")

    data = response.json()

    if "data" not in data or "items" not in data["data"]:
        raise ValueError("Response missing data/items")

    return data


def main() -> None:
    first_page = extract_gecko_api(API_URL, PAGE_URL, KEYWORD, 1)
    total_pages = ceil(first_page["data"]["totalResults"] / first_page["data"]["resultsPerPage"])

    responses = [first_page] 
    for page in range(2, total_pages + 1):
        page_response = extract_gecko_api(API_URL, PAGE_URL, KEYWORD, page)
        responses.append(page_response) 

    output_path = Path("data") / "bronze_data.json"
    output_dir = output_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(responses, f, indent=4, ensure_ascii=False)

    logger.info(f"Response saved to {output_path}")


if __name__ == "__main__":
    main()