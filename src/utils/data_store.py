import json
import os
from datetime import datetime

class DataStore:
    def __init__(self):
        self.data_file = "data/last_data.json"
        self.history_file = "data/history.txt"  
        self.ensure_data_dir()
    
    def ensure_data_dir(self):
        try:
            data_dir = os.path.dirname(self.data_file)
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
            else:
                print(f"Data directory already exists: {data_dir}")
        except Exception as e:
            print(f"Failed to create data directory: {str(e)}")
    
    def get_last_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    if self.validate_data(data):
                        return data
            return None
        except Exception as e:
            return None
    
    def save_data(self, ethena_data, market_data):
        try:
            data = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'ethena': None,
                'market': {
                    'btc': {
                        'price': market_data.get('btc_price')
                    },
                    'sentiment': {
                        'ahr999': market_data.get('ahr999'),
                        'fear_greed': market_data.get('fear_greed')
                    }
                }
            }

            print("\nSaved data content:")
            print("="*50)
            print(f"Time: {data['timestamp']}\n")            

            if data['market']['btc']['price'] is not None:
                print("BTC Data:")
                print(f"💰 BTC Price: ${data['market']['btc']['price']:,.2f}\n")
            else:
                print("BTC data: None\n")
            
            if data['market']['sentiment']['ahr999'] is not None:
                print(f"📉 AHR999 Index: {data['market']['sentiment']['ahr999']:.4f}")
            else:
                print("📉 AHR999 Index: None")
                
            if data['market']['sentiment']['fear_greed'] is not None:
                print(f"😱 Fear and Greed Index: {data['market']['sentiment']['fear_greed']}")
            else:
                print("😱 Fear and Greed Index: None")
            print("="*50)
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.save_to_history_file(data)
            
            return True
        except Exception as e:
            print(f"Failed to save data: {str(e)}")
            return False
    
    def save_to_history_file(self, data):
        try:
            timestamp = data['timestamp']
            record_lines = [
                f"===== {timestamp} ====="
            ]
            
            if data['market']['btc']['price'] is not None:
                record_lines.append(f"BTC: ${data['market']['btc']['price']:,.0f}")
            else:
                record_lines.append("BTC: No data")
            
            if data['market']['sentiment']['ahr999'] is not None:
                record_lines.append(f"AHR999: {data['market']['sentiment']['ahr999']:.2f}")
            else:
                record_lines.append("AHR999: No data")
            
            if data['market']['sentiment']['fear_greed'] is not None:
                record_lines.append(f"Fear and Greed: {data['market']['sentiment']['fear_greed']}")
            else:
                record_lines.append("Fear and Greed: No data")
            
            record_lines.append("=" * 30)
            record_text = "\n".join(record_lines) + "\n\n"
            
            existing_content = ""
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                f.write(record_text + existing_content)
            
            return True
        except Exception as e:
            print(f"Failed to save history: {str(e)}")
            return False
    
    def validate_data(self, data):
        try:
            required_fields = {
                'timestamp': str,
                'market': dict
            }
            
            for field, field_type in required_fields.items():
                if field not in data:
                    print(f"Missing required field(s): {field}")
                    return False
                if not isinstance(data[field], field_type):
                    print(f"Field type error for {field}: expected {field_type}, got {type(data[field])}")
                    return False
            return True
        except Exception as e:
            print(f"Data format validation failed: {str(e)}")
            return False
    
    def calculate_changes(self, old_data, new_data):
        if not old_data:
            return None
        
        changes = {}
        
        if 'market' in old_data and 'market' in new_data:
            market_changes = {}
            
            if ('btc' in old_data['market'] and 'btc' in new_data['market'] and
                'price' in old_data['market']['btc'] and 'price' in new_data['market']['btc'] and
                old_data['market']['btc']['price'] is not None and new_data['market']['btc']['price'] is not None):
                old_price = float(old_data['market']['btc']['price'])
                new_price = float(new_data['market']['btc']['price'])
                change_pct = ((new_price - old_price) / old_price) * 100
                market_changes['btc'] = {
                    'price': {
                        'old': old_price,
                        'new': new_price,
                        'change_pct': change_pct
                    }
                }
            
            if 'sentiment' in old_data['market'] and 'sentiment' in new_data['market']:
                sentiment_changes = {}
                for key in ['ahr999', 'fear_greed']:
                    if (key in old_data['market']['sentiment'] and 
                        key in new_data['market']['sentiment'] and
                        old_data['market']['sentiment'][key] is not None and 
                        new_data['market']['sentiment'][key] is not None):
                        old_val = float(old_data['market']['sentiment'][key])
                        new_val = float(new_data['market']['sentiment'][key])
                        sentiment_changes[key] = {
                            'old': old_val,
                            'new': new_val
                        }
                if sentiment_changes:
                    market_changes['sentiment'] = sentiment_changes
            
            if market_changes:
                changes['market'] = market_changes
        
        return changes if changes else None 