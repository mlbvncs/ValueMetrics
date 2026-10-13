import logging
import os

import pandas as pd
import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

p = Path(__file__).parent.resolve().parent
Path(p / 'logs').mkdir(parents=True, exist_ok=True)

format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
filename_path = Path(p / 'logs' / 'logs.log')
logging.basicConfig(format=format, filename=filename_path, encoding='utf-8', level=logging.INFO)
logger = logging.getLogger(__name__)

def extracting_data(page: int) -> pd.DataFrame:
    '''if not os.environ('API_KEY'):
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
        pass'''
    return 0

def main():
    return 0

'''if __name__ == '__main__':
    main()'''