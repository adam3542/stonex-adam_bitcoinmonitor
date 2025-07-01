import aiohttp
import json
import os
import logging
import traceback
from datetime import datetime
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseDataCollector:

    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    async def fetch_data(self, url, params=None):            
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                    async with session.get(url, params=params, timeout=30) as response:
                        if response.status == 200:
                            return await response.json()
                        else:
                            logger.error(f"Request failed, status code: {response.status}, URL: {url}")
                            return None
        except Exception as e:
            logger.error(f"Error fetching data: {url}, Error: {str(e)}")
            logger.debug(traceback.format_exc())
            return None
    
    def save_to_json(self, data, filename):
        file_path = os.path.join(self.data_dir, filename)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Data has been saved to: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save data: {str(e)}")
            return False
    
    def load_from_json(self, filename):

        file_path = os.path.join(self.data_dir, filename)
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                logger.info(f"Data loaded from {file_path}")
                return data
            else:
                logger.warning(f"File does not exist: {file_path}")
                return None
        except Exception as e:
            logger.error(f"Failed to load data: {str(e)}")
            return None
    
    def is_data_expired(self, data, timestamp_key="last_updated", hours=24):
        if not data or timestamp_key not in data:
            return True
            
        last_updated = data[timestamp_key]
        current_time = int(time.time())
        return (current_time - last_updated) >= hours * 60 * 60 