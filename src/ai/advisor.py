import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union


from ai.deepseek import DeepseekAPI


from config import DATA_DIRS


logger = logging.getLogger(__name__)

class DeepseekAdvisor:
    
    def __init__(self, api_key: str = None, api_url: str = None):
        self.api = DeepseekAPI(api_key=api_key, api_url=api_url)
        
        self.advice_dir = os.path.join(DATA_DIRS['advices'])
        os.makedirs(self.advice_dir, exist_ok=True)
        
        logger.info("DeepSeek Advisor initialization completed")
    
    def get_investment_advice(self, data_file: str, months: int = 3, last_record_id: str = None, 
                            debug: bool = False, max_retries: int = 2, retry_delay: float = 2.0, **kwargs) -> Optional[str]:
       
        filtered_data = self._prepare_data_for_ai(data_file, months)
        if not filtered_data:
            logger.error("Failed to prepare data for AI analysis")
            return None
            
        data_json = json.dumps(filtered_data, ensure_ascii=False)
        
        logger.info(f"Start generating investment recommendations using data from the last {months} ​​months...")
        
        try:
            result = self.api.generate_and_save_investment_advice(
                data_json=data_json,
                last_record_id=last_record_id,
                debug=debug,
                max_retries=max_retries,
                retry_delay=retry_delay,
                **kwargs
            )
            
            if result.get("success"):
                advice = result.get("advice")
                
                self._save_advice_to_file(advice)
                
                logger.info(f"Successfully generated investment proposals")
                return advice
            else:
                error = result.get("error", "Unknown error")
                logger.error(f"Failed to generate investment proposal: {error}")
                return None
                
        except Exception as e:
            logger.error(f"Error when calling AI API to generate investment advice: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            return None
    
    def _prepare_data_for_ai(self, data_file: str, months: int) -> List[Dict]:
        try:
            if not os.path.exists(data_file):
                logger.error(f"The data file does not exist: {data_file}")
                return []
                
            with open(data_file, 'r', encoding='utf-8') as f:
                file_content = f.read()
                
            try:
                all_data = json.loads(file_content)
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {e}")
                logger.debug(f"File content preview: {file_content[:200]}...")
                return []
               
            if not isinstance(all_data, list):
                logger.error(f"Data format error: {type(all_data).__name__}")

                if isinstance(all_data, dict) and 'data' in all_data and isinstance(all_data['data'], list):
                    all_data = all_data['data']
                    logger.info("Extracting array of data from dictionary")
                else:
                    try:
                        if isinstance(all_data, str):
                            all_data = json.loads(all_data)
                            if isinstance(all_data, list):
                                logger.info("Successfully parsed the string into a data list")
                            else:
                                logger.error("After parsing, it is still not a list type")
                                return []
                        else:
                            return []
                    except:
                        return []
            
            if all_data and not all(isinstance(item, dict) for item in all_data):
                logger.error("Data format error: Not all items in the list are dictionary types")
                return []
            
            today = datetime.today()
            start_date = (today - timedelta(days=30 * months)).strftime('%Y-%m-%d')
            
            filtered_data = []
            for item in all_data:
                if not isinstance(item, dict):
                    continue
                    
                date_str = item.get('date')
                if not date_str or not isinstance(date_str, str):
                    continue
                    
                if date_str >= start_date:
                    filtered_data.append(item)
            
            if not filtered_data:
                logger.warning(f"No data found starting from {start_date}")

                filtered_data = all_data[:min(100, len(all_data))]
                logger.info(f"Return all available data (up to 100 records)")
            
            filtered_data.sort(key=lambda x: x.get('date', ''), reverse=True)
            
            return filtered_data
            
        except Exception as e:
            logger.error(f"Errors in preparing data for AI analysis: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            return []
    
    def _save_advice_to_file(self, advice: str) -> bool:
        try:

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"advice_{timestamp}.md"
            filepath = os.path.join(self.advice_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(advice)
            
            logger.info(f"Investment advice has been saved to: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving investment proposal to file: {str(e)}")
            return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    advisor = DeepseekAdvisor()
    advice = advisor.get_investment_advice("data/daily_data.json")
    if advice:
        print("\n========== Summary of AI Investment Advice ==========")
        print(advice)
        print("=====================================================\n") 