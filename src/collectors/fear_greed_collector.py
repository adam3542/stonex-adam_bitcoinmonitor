from collectors.base_collector import BaseDataCollector
import logging
from datetime import datetime, timedelta
import time
from config import MARKET_SENTIMENT
logger = logging.getLogger(__name__)

class FearGreedCollector(BaseDataCollector):

    def __init__(self, data_dir="data"):
        super().__init__(data_dir)
        self.fng_history_file = "fng_history.json"
        self.api_url = MARKET_SENTIMENT['fear_greed_url']
        
        if "?" in self.api_url:
            self.api_url += "&limit=0"
        else:
            self.api_url += "?limit=0"
    
    async def get_fear_greed_history(self, days=180):   
        fng_data = self.load_from_json(self.fng_history_file)
        if fng_data and "data" in fng_data and len(fng_data["data"]) > 0:
            try:
                latest_time = int(fng_data["data"][0]["timestamp"])
                current_time = int(time.time())
                if (current_time - latest_time) < 24 * 60 * 60:
                    logger.info(f"Using cached historical data for the Fear & Greed Index; latest data timestamp: {datetime.fromtimestamp(latest_time)}")
                    return self.format_fng_data(fng_data, days)
                else:
                    logger.info(f"Cached data has expired. Fetching updated historical data for the Fear & Greed Index")
            except (KeyError, IndexError, TypeError) as e:
                logger.error(f"Failed to verify Fear & Greed (FNG) data timestamp: {str(e)}")
        
        try:
            data = await self.fetch_data(self.api_url)
            
            if data and "data" in data:
                logger.info(f"Successfully retrieved {len(data['data'])} entries of Fear & Greed Index historical data")
                
                self.save_to_json(data, self.fng_history_file)
                
                return self.format_fng_data(data, days)
            else:
                logger.error("Failed to retrieve Fear & Greed Index historical data")
                raw_data = self.load_from_json(self.fng_history_file)
                if raw_data:
                    return self.format_fng_data(raw_data, days)
                return []
        except Exception as e:
            logger.error(f"Exception occurred while fetching Fear & Greed Index historical data: {str(e)}")
            
            raw_data = self.load_from_json(self.fng_history_file)
            if raw_data:
                return self.format_fng_data(raw_data, days)
            return []
    
    def format_fng_data(self, data, days=180):
        if not data or "data" not in data:
            return []
        
        formatted_data = []
        today = datetime.now()
        past_date = today - timedelta(days=days)
        
        for item in data["data"]:
            try:
                timestamp = int(item["timestamp"])
                date_obj = datetime.fromtimestamp(timestamp)
                
                if date_obj >= past_date:
                    formatted_data.append({
                        "timestamp": timestamp,
                        "date": date_obj.strftime('%Y-%m-%d'),
                        "value": int(item["value"]),
                        "value_classification": item["value_classification"]
                    })
            except (KeyError, ValueError) as e:
                logger.error(f"Error formatting Fear & Greed Index data: {str(e)}, Data: {item}")
        
        formatted_data.sort(key=lambda x: x["timestamp"], reverse=True)
        return formatted_data 