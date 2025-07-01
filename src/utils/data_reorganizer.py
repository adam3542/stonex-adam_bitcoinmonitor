import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_historical_data(file_path: str) -> Dict[str, Any]:
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        else:
            return {}
    except Exception as e:
        return {}

def reorganize_by_date(data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    if not data:
        return {}
    
    btc_price_data = data.get('btc_price', [])
    ahr999_data = data.get('ahr999', [])
    fear_greed_data = data.get('fear_greed', [])
    
    daily_data = {}
    
    for item in btc_price_data:
        date = item.get('date')
        if not date:
            continue
            
        if date not in daily_data:
            daily_data[date] = {'date': date}
            
        daily_data[date]['price'] = item.get('price')
        # daily_data[date]['market_cap'] = item.get('market_cap')
        # daily_data[date]['volume'] = item.get('volume')
        # daily_data[date]['btc_timestamp'] = item.get('timestamp')
    
    for item in ahr999_data:
        date = item.get('date')
        if not date:
            continue
            
        if date not in daily_data:
            daily_data[date] = {'date': date}
            
        daily_data[date]['ahr999'] = item.get('ahr999')
        # for field in ['ma200', 'price_ma_ratio', 'ahr999_signal']:
        #     if field in item:
        #         daily_data[date][field] = item.get(field)
        # daily_data[date]['ahr999_timestamp'] = item.get('timestamp')
    
    for item in fear_greed_data:
        date = item.get('date')
        if not date:
            continue
            
        if date not in daily_data:
            daily_data[date] = {'date': date}
            
        daily_data[date]['fear_greed_value'] = item.get('value')
        # daily_data[date]['fear_greed_classification'] = item.get('classification')
        # daily_data[date]['fear_greed_timestamp'] = item.get('timestamp')
    
    return daily_data

def save_daily_data(daily_data: Dict[str, Dict[str, Any]], file_path: str) -> bool:
    try:
        data_list = list(daily_data.values())
        data_list.sort(key=lambda x: x['date'])
        
        complete_data = {
            "data": data_list,
            "count": len(data_list),
            # "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "description": "Daily combined BTC price, AHR999 index and Fear & Greed index data"
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(complete_data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        return False

def reorganize_data(input_file: str, output_file: str) -> bool:

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    historical_data = load_historical_data(input_file)
    if not historical_data:
        return False
    
    daily_data = reorganize_by_date(historical_data)
    if not daily_data:
        return False
    
    success = save_daily_data(daily_data, output_file)
    if success:
        return True
    else:
        return False
