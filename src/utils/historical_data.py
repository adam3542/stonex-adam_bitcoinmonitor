import asyncio
import os
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

from collectors import BTCPriceCollector, AHR999Collector, FearGreedCollector

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HistoricalDataCollector:
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.data_file = os.path.join(data_dir, "historical_data.json")
        
        os.makedirs(data_dir, exist_ok=True)
        
        self.btc_collector = BTCPriceCollector(data_dir)
        self.ahr999_collector = AHR999Collector(data_dir)
        self.fng_collector = FearGreedCollector(data_dir)
    
    async def collect_historical_data(self, days=180) -> Dict[str, Any]:
        
        btc_task = asyncio.create_task(self.btc_collector.get_price_history(days))
        ahr_task = asyncio.create_task(self.ahr999_collector.get_ahr999_history(days))
        fng_task = asyncio.create_task(self.fng_collector.get_fear_greed_history(days))
        
        btc_history = await btc_task
        ahr_history = await ahr_task
        fng_history = await fng_task
        
        historical_data = {
            "btc_price": btc_history,
            "ahr999": ahr_history,
            "fear_greed": fng_history,
            "last_updated": int(time.time())
        }
        
        self.save_historical_data(historical_data)
        
        return historical_data
    
    def save_historical_data(self, data: Dict[str, Any]) -> bool:
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            return False
    
    def load_historical_data(self) -> Optional[Dict[str, Any]]:
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return data
            else:
                return None
        except Exception as e:
            return None
    
    def merge_historical_data(self, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
        if not old_data:
            return new_data
        
        if not new_data:
            return old_data
        
        merged_data = {}
        
        if "btc_price" in old_data and "btc_price" in new_data:
            old_btc = {item["date"]: item for item in old_data["btc_price"]} if old_data.get("btc_price") else {}
            new_btc = {item["date"]: item for item in new_data["btc_price"]} if new_data.get("btc_price") else {}
            old_btc.update(new_btc)
            merged_data["btc_price"] = list(old_btc.values())
            merged_data["btc_price"].sort(key=lambda x: x["timestamp"], reverse=True)
        else:
            merged_data["btc_price"] = new_data.get("btc_price", old_data.get("btc_price", []))
        
        if "ahr999" in old_data and "ahr999" in new_data:
            old_ahr = {item["date"]: item for item in old_data["ahr999"]} if old_data.get("ahr999") else {}
            new_ahr = {item["date"]: item for item in new_data["ahr999"]} if new_data.get("ahr999") else {}
            old_ahr.update(new_ahr)
            merged_data["ahr999"] = list(old_ahr.values())
            merged_data["ahr999"].sort(key=lambda x: x["timestamp"], reverse=True)
        else:
            merged_data["ahr999"] = new_data.get("ahr999", old_data.get("ahr999", []))
        
        if "fear_greed" in old_data and "fear_greed" in new_data:
            old_fng = {item["date"]: item for item in old_data["fear_greed"]} if old_data.get("fear_greed") else {}
            new_fng = {item["date"]: item for item in new_data["fear_greed"]} if new_data.get("fear_greed") else {}
            old_fng.update(new_fng)
            merged_data["fear_greed"] = list(old_fng.values())
            merged_data["fear_greed"].sort(key=lambda x: x["timestamp"], reverse=True)
        else:
            merged_data["fear_greed"] = new_data.get("fear_greed", old_data.get("fear_greed", []))
        
        merged_data["last_updated"] = int(time.time())
        
        return merged_data
    
    async def update_historical_data(self, force=False) -> Dict[str, Any]:
        old_data = self.load_historical_data()
        
        if not old_data or force:
            return await self.collect_historical_data()
        
        last_updated = old_data.get("last_updated", 0)
        current_time = int(time.time())
        if (current_time - last_updated) >= 12 * 60 * 60:
            new_data = await self.collect_historical_data()
            return self.merge_historical_data(old_data, new_data)
        else:
            return old_data