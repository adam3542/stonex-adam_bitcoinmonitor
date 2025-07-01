from collectors.base_collector import BaseDataCollector
import logging
from datetime import datetime
import time
import os
from config import MARKET_SENTIMENT

logger = logging.getLogger(__name__)

class BTCPriceCollector(BaseDataCollector):
    def __init__(self, data_dir="data"):
        super().__init__(data_dir)
        self.btc_history_file = "btc_price_history.json"
        self.api_url = MARKET_SENTIMENT['btc_price_url']
    
    async def get_price_history(self, days=180):
        logger.info(f"Fetching {days} days of BTC historical price data...")
        
        btc_data = self.load_from_json(self.btc_history_file)
        if btc_data and len(btc_data) > 0:
            latest_time = max(int(item.get("timestamp", 0)) for item in btc_data)
            current_time = int(time.time() * 1000)
            if (current_time - latest_time) < 24 * 60 * 60 * 1000:
                logger.info(f"Using cached BTC historical price data; latest data timestamp: {datetime.fromtimestamp(latest_time/1000)}")
                return btc_data
            else:
                logger.info(f"Cached data has expired; latest data timestamp: {datetime.fromtimestamp(latest_time/1000)}")
        
        try:
            params = {
                "symbol": "BTCUSDT",
                "interval": "1d",
                "limit": min(days, 1000)
            }
            
            data = await self.fetch_data(self.api_url, params)
            
            if data and isinstance(data, list):
                logger.info(f"Successfully retrieved {len(data)} entries of BTC historical price data")
                
                btc_history = []
                for item in data:
                    try:
                        timestamp = int(item[0])
                        close_price = float(item[4])
                        
                        btc_history.append({
                            "timestamp": timestamp,
                            "date": datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d'),
                            "price": close_price
                        })
                    except (IndexError, ValueError) as e:
                        logger.error(f"Error parsing BTC price data: {str(e)}, Data: {item}")
                
                btc_history.sort(key=lambda x: x["timestamp"], reverse=True)
                
                self.save_to_json(btc_history, self.btc_history_file)
                
                return btc_history
            else:
                logger.error("Failed to retrieve BTC historical price data")
                return self.load_from_json(self.btc_history_file) or []
        except Exception as e:
            logger.error(f"Exception occurred while fetching BTC historical price data: {str(e)}")
            return self.load_from_json(self.btc_history_file) or [] 