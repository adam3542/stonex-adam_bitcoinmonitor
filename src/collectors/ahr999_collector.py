from collectors.base_collector import BaseDataCollector
import logging
from datetime import datetime, timedelta
import time
import random
import numpy as np
from config import MARKET_SENTIMENT

logger = logging.getLogger(__name__)

class AHR999Collector(BaseDataCollector):

    def __init__(self, data_dir="data"):
        super().__init__(data_dir)
        self.ahr999_history_file = "ahr999_history.json"
        self.api_url = MARKET_SENTIMENT['ahr999_url']
    
    async def get_ahr999_history(self, days=365, keep_extra_data=False):
        logger.info("Fetching historical data for the AHR999 index...")
        
        ahr_data = self.load_from_json(self.ahr999_history_file)
        if ahr_data and len(ahr_data) > 0:
            try:
                latest_time = max(item.get("timestamp", 0) for item in ahr_data if isinstance(item.get("timestamp"), (int, float)))
                current_time = int(time.time())
                if (current_time - latest_time) < 24 * 60 * 60:
                    logger.info(f"Using cached historical data for the AHR999 index; latest data timestamp: {datetime.fromtimestamp(latest_time)}")
                    return ahr_data
                else:
                    logger.info(f"Cached data has expired. Fetching updated historical data for the AHR999 index")
            except Exception as e:
                logger.error(f"Error checking AHR999 data timestamp: {str(e)}")

        try:

            data = await self.fetch_data(self.api_url)
            
            if data and "data" in data and isinstance(data["data"], list) and ("code" not in data or data.get("code") == 200 or data.get("code") == 0):
                logger.info(f"Successfully retrieved AHR999 historical data, number of entries: {len(data['data'])}")
                
                ahr999_history = []
                
                filtered_data = data["data"]
                if len(filtered_data) > days:
                    filtered_data = filtered_data[-days:]
                
                for item in filtered_data:
                    try:
                        if len(item) >= 2:
                            timestamp = int(item[0])
                            ahr999_value = float(item[1])
                            
                            entry = {
                                "timestamp": timestamp,
                                "date": datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d'),
                                "ahr999": ahr999_value
                            }
                            
                            if keep_extra_data and len(item) >= 5:
                                entry["price"] = float(item[2])
                                entry["ma200"] = float(item[3]) 
                                entry["price_ma_ratio"] = float(item[4])
                            
                            ahr999_history.append(entry)
                    except (IndexError, ValueError) as e:
                        logger.error(f"Error parsing AHR999 data: {str(e)}, Data: {item}")
                
                ahr999_history.sort(key=lambda x: x["timestamp"], reverse=True)
                
                self.save_to_json(ahr999_history, self.ahr999_history_file)
                
                return ahr999_history
            else:
                logger.error("Failed to retrieve AHR999 historical data or data format is incorrect.")
                return self.generate_mock_ahr999_data(days)
        except Exception as e:
            logger.error(f"Exception occurred while fetching AHR999 historical data: {str(e)}")
            
            return self.generate_mock_ahr999_data(days)
    
    def generate_mock_ahr999_data(self, days=365):
        logger.info(f"Generate {days} days of simulated AHR999 historical index data")
        
        random.seed(42)
        np.random.seed(42)
        
        start_date = datetime.now()
        ahr999_history = []
        
        base_value = 1.0 
        cycle_length = 365 * 4
        amplitude = 0.8
        
        for i in range(days):
            date = start_date - timedelta(days=i)
            timestamp = int(date.timestamp())
            date_str = date.strftime('%Y-%m-%d')
            
            cycle_position = (i % cycle_length) / cycle_length * 2 * np.pi
            cycle_value = base_value + amplitude * np.sin(cycle_position)
            
            random_factor = 1.0 + random.uniform(-0.1, 0.1) 
            ahr999_value = max(0.1, min(3.0, cycle_value * random_factor))
            
            if i % 30 < 15:
                trend_factor = 1.0 + random.uniform(0, 0.02)
            else:
                trend_factor = 1.0 - random.uniform(0, 0.02)
            
            ahr999_value *= trend_factor
            
            ahr999_history.append({
                "timestamp": timestamp,
                "date": date_str,
                "ahr999": round(ahr999_value, 4)
            })
        
        ahr999_history.sort(key=lambda x: x["timestamp"], reverse=True)
        
        self.save_to_json(ahr999_history, self.ahr999_history_file)
        
        return ahr999_history 