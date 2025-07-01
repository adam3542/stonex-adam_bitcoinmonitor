import os
import json
import uuid
import yaml
import logging
import requests
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

from config import DEEPSEEK_AI, DATA_DIRS

from ai.prompt import (
    get_investment_advice_template, 
    prepare_investment_advice_params,
    save_prompt_for_debug,
    extract_json_from_text
)

logger = logging.getLogger(__name__)

class DeepseekAPI:
    
    def __init__(self, api_key: str = None, api_url: str = None):
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        self.api_url = api_url or DEEPSEEK_AI['api_url']
        self.key_url = DEEPSEEK_AI['key_url']
    
    def validate_api_key(self) -> bool:
        return bool(self.api_key)
    
    def chat_completion(self, 
                        messages: List[Dict[str, str]], 
                        model: str = None,
                        temperature: float = None,
                        max_tokens: int = None,
                        top_p: float = None,
                        stream: bool = None,
                        max_retries: int = 2,
                        retry_delay: float = 2.0,
                        **kwargs) -> Optional[Dict[str, Any]]:

        if not self.validate_api_key():
            self.api_key = self.get_api_key(max_retries=max_retries, retry_delay=retry_delay)

        if not self.api_key:
            logger.warning("DeepSeek API key is not set, please provide it via environment variable DEEPSEEK_API_KEY or initialization parameter")
            return None

        payload = {
            "model": model or DEEPSEEK_AI['model'],
            "messages": messages,
            "temperature": temperature if temperature is not None else DEEPSEEK_AI['temperature'],
            "max_tokens": max_tokens if max_tokens is not None else DEEPSEEK_AI['max_tokens'],
            "top_p": top_p if top_p is not None else DEEPSEEK_AI['top_p'],
            "stream": stream if stream is not None else DEEPSEEK_AI['stream']
        }
        
        payload.update(kwargs)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        retries = 1
        while retries <= max_retries:
            try:
                logger.info(f"Calling DeepSeek API, model: {payload['model']}, number of attempts: {retries}/{max_retries}")
                response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
                
                if response.status_code == 200:
                    logger.info("DeepSeek API call succeeded")
                    return response.json()
                elif response.status_code == 429:
                    logger.warning(f"The API call is restricted (429), waiting to retry...")
                    retries += 1
                    if retries <= max_retries:
                        wait_time = retry_delay * (2 ** (retries - 1))
                        logger.info(f"Wait {wait_time} seconds before trying again...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"The maximum number of retries has been reached and the API call failed: {response.status_code} - {response.text}")
                        return None
                elif response.status_code >= 500:
                    logger.warning(f"Server error ({response.status_code}), try again...")
                    retries += 1
                    if retries <= max_retries:
                        wait_time = retry_delay * (2 ** (retries - 1))
                        logger.info(f"Wait {wait_time} seconds before trying again...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"The maximum number of retries has been reached and the API call failed: {response.status_code} - {response.text}")
                        return None
                else:
                    logger.error(f"API call failed: {response.status_code} - {response.text}")
                    return None
            
            except requests.exceptions.Timeout:
                logger.warning("API request timed out, try again...")
                retries += 1
                if retries <= max_retries:
                    wait_time = retry_delay * (2 ** (retries - 1))
                    logger.info(f"Wait {wait_time} seconds before trying again...")
                    time.sleep(wait_time)
                else:
                    logger.error("The maximum number of retries has been reached and the API request has timed out.")
                    return None
            except requests.exceptions.ConnectionError:
                logger.warning("API connection error, try again...")
                retries += 1
                if retries <= max_retries:
                    wait_time = retry_delay * (2 ** (retries - 1))
                    logger.info(f"Wait {wait_time} seconds before trying again...")
                    time.sleep(wait_time)
                else:
                    logger.error("The maximum number of retries has been reached and the API connection has failed.")
                    return None
            except requests.exceptions.RequestException as e:

                logger.error(f"API request exception: {str(e)}")
                retries += 1
                if retries <= max_retries:
                    wait_time = retry_delay * (2 ** (retries - 1))
                    logger.info(f"Wait {wait_time} seconds before trying again...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"The maximum number of retries has been reached and the API request has failed: {str(e)}")
                    return None
            except Exception as e:
                logger.error(f"Error calling DeepSeek API: {str(e)}")
                retries += 1
                if retries <= max_retries:
                    wait_time = retry_delay * (2 ** (retries - 1))
                    logger.info(f"Wait {wait_time} seconds before trying again...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"The maximum number of retries has been reached and an unknown error has occurred: {str(e)}")
                    return None
        
        return None
    
    def generate_text(self, prompt: str, max_retries: int = 2, retry_delay: float = 2.0, **kwargs) -> Optional[str]:

        messages = [{"role": "user", "content": prompt}]
        response = self.chat_completion(messages, max_retries=max_retries, retry_delay=retry_delay, **kwargs)
        
        if response:
            
            self.save_response_to_file(response)
            
            try:
                content = response["choices"][0]["message"]["content"]
                return content
            except (KeyError, IndexError) as e:
                logger.error(f"Error parsing API response: {str(e)}")
                return None
        
        return None
    
    def generate_investment_advice(self, data_json: str, last_advice: Dict = None, max_retries: int = 2, retry_delay: float = 2.0, **kwargs) -> Optional[str]:

        current_date = kwargs.pop('current_date', None)
        if not current_date:
            current_date = datetime.now().strftime('%Y-%m-%d')
        

        params = prepare_investment_advice_params(current_date, last_advice)
        
        prompt = get_investment_advice_template(
            current_date=params["current_date"],
            last_position=params["last_position"],
            last_cost_basis=params["last_cost_basis"],
            last_action=params["last_action"],
            data_json=data_json
        )
        
        save_prompt_for_debug(prompt)
        
        return self.generate_text(prompt, max_retries=max_retries, retry_delay=retry_delay, **kwargs)
    
    def save_investment_record(self, recommendation: str, data_json: str = None, **kwargs) -> Dict[str, Any]:

        records_dir = kwargs.get('records_dir', DATA_DIRS['records'])
        os.makedirs(records_dir, exist_ok=True)
        

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        record_id = f"BTI-{timestamp}"
        
        advice_data = extract_json_from_text(recommendation) or {}
        
        record = {
            "id": record_id,
            "timestamp": timestamp,
            "date": datetime.now().strftime('%Y-%m-%d'),
            "recommendation": recommendation,
            "advice_data": advice_data,
            "metadata": kwargs
        }
        
        filename = f"{record_id}.json"
        filepath = os.path.join(records_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Investment advice records saved: {filepath}")
        return {"record_id": record_id, "advice_data": advice_data}


    def get_api_key(self, max_retries: int = 2, retry_delay: float = 2.0) -> str:
        
        headers = {
            "client_id": str(uuid.uuid4())
        }
        retries = 1
        while retries <= max_retries:
            try:
                response = requests.get(self.key_url, headers=headers, params={}, timeout=60)
                content_type = response.headers["Content-Type"]
                if response.status_code == 200:
                    if content_type.startswith("application/json"):
                        response = json.loads(response.text)
                    elif content_type.startswith("application/yaml"):
                        response = yaml.load(response.text, Loader=yaml.Loader)
                    return response["key"]
                else:
                    return None
            except Exception as e:
                retries += 1
                if retries <= max_retries:
                    wait_time = retry_delay * (2 ** (retries - 1))
                    time.sleep(wait_time)
        return None

    def load_investment_record(self, record_id: str, records_dir: str = None) -> Optional[Dict[str, Any]]:

        if records_dir is None:
            records_dir = DATA_DIRS['records']
            
        filepath = os.path.join(records_dir, f"{record_id}.json")
        
        if not os.path.exists(filepath):
            logger.error(f"Log file not found: {filepath}")
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                record = json.load(f)
            return record
        except Exception as e:
            logger.error(f"Failed to load record: {str(e)}")
            return None
    
    def load_latest_investment_record(self, records_dir: str = None) -> Optional[Dict[str, Any]]:

        records_dir = DATA_DIRS['records']
            
        if not os.path.exists(records_dir):
            logger.warning(f"The record directory does not exist: {records_dir}")
            return None, None
        
        try:
            files = [f for f in os.listdir(records_dir) if f.startswith('BTI-') and f.endswith('.json')]
            if not files:
                logger.info(f"No investment advice record found in the directory: {records_dir}")
                return None, None
            
            files.sort(reverse=True)
            latest_file = files[0]
            record_id = latest_file.split('.')[0] 
            
            record = self.load_investment_record(record_id, records_dir)
            if record:
                logger.info(f"Successfully loaded the latest investment advice record: {record_id}")
                return record, record_id
            else:
                return None, None
        except Exception as e:
            logger.error(f"Error finding latest record: {str(e)}")
            return None, None
    
    def generate_and_save_investment_advice(self, data_json: str, last_record_id: str = None, debug: bool = False, 
                                 max_retries: int = 2, retry_delay: float = 2.0, **kwargs) -> Dict[str, Any]:

        last_advice = None
        
        if not last_record_id:
            logger.info("No last record ID provided, trying to automatically load the latest record")
            last_record, last_record_id = self.load_latest_investment_record()
        else:
            logger.info(f"Loading the specified last investment advice: {last_record_id}")
            last_record = self.load_investment_record(last_record_id)
        
        if last_record:
            if "advice_data" in last_record and last_record["advice_data"]:
                last_advice = last_record["advice_data"]
                logger.info(f"Successfully loaded last recommended data: Positions {last_advice.get('position', 'N/A')}%")
            elif "recommendation" in last_record:
                last_advice = extract_json_from_text(last_record["recommendation"])
                if last_advice:
                    logger.info(f"Reparse last suggested data from text: Positions {last_advice.get('position', 'N/A')}%")
        else:
            logger.info("No previous record found, the first investment suggestion will be generated")
        
        advice = self.generate_investment_advice(
            data_json, 
            last_advice=last_advice, 
            max_retries=max_retries,
            retry_delay=retry_delay,
            **kwargs
        )
        
        if not advice:
            logger.error("Generating investment advice fails, even after retries")
            return {"success": False, "error": "Failed to generate investment advice, please check API connection and configuration"}
        
        try:
            result = self.save_investment_record(
                recommendation=advice,
                data_json=data_json,
                last_record_id=last_record_id,
                user_settings=kwargs.get('user_settings', {})
            )
            
            return {
                "success": True,
                "advice": advice,
                "record_id": result["record_id"],
                "advice_data": result["advice_data"]
            }
        except Exception as e:
            logger.error(f"Error saving investment advice record: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            
            return {
                "success": True,
                "advice": advice,
                "record_id": f"temp-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "advice_data": extract_json_from_text(advice) or {},
                "save_error": str(e)
            }

    def save_response_to_file(self, response):
        try:
            responses_dir = os.path.join(DATA_DIRS['responses'])
            os.makedirs(responses_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"response_{timestamp}.json"
            file_path = os.path.join(responses_dir, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(response, f, ensure_ascii=False, indent=2)
                  
            logger.info(f"AI original response saved to: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving AI response: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            return False
