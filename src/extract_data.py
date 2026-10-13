import logging
import os

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def extracting_data(page: int) -> pd.DataFrame:
    if not os.environ('API_KEY'):
        logger.critical("API_KEY is not set in the environment variables.")
        raise

    try:
        response = requests.post(
            "https://api.geckoapi.com.br/v1/extract",
            headers={"Authorization": f"Bearer {os.environ('API_KEY')}"},
            json={
                "url": "https://lista.mercadolivre.com.br/iphone-15-pro-max",
                "target": "mercadolivre.com.br",
                "type": "plp",
                "page": page
            },
            timeout = 30
        )
    except:
        pass