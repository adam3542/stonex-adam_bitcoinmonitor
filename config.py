# Webhook Configuration
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

WEBHOOK_URL = os.getenv('WEBHOOK_URL', '') 

# Determine whether to run in Docker based on environment variables
IS_DOCKER = os.getenv('IS_DOCKER', 'false').lower() == 'true'

# File path configuration
DATA_DIRS = {
    'prompts': 'prompts',       
    'responses': 'responses',
    'advices': 'advices', 
    'records': 'investment_records',
    'debug': 'debug_logs',
    'data': 'data',
    'reports': 'reports'
}

# Market sentiment indicator configuration
MARKET_SENTIMENT = {
    'fear_greed_url': 'https://api.alternative.me/fng/',
    'ahr999_url': 'https://dncapi.flink1.com/api/v2/index/arh999?code=bitcoin&webp=1',
    'btc_price_url': 'https://api.binance.com/api/v3/klines',
}

# DeepSeek AI Configuration
DEEPSEEK_AI = {
    'api_url': os.getenv('DEEPSEEK_API_URL', 'https://openrouter.ai/api/v1/chat/completions'),
    'key_url': os.getenv('DEEPSEEK_KEY_URL', 'https://apopenrouter.ai/api/v1/key'),
    'model': os.getenv('DEEPSEEK_MODEL', 'deepseek/deepseek-r1:free'),
    'temperature': 0,
    'max_tokens': 16000,
    'top_p': 1.0,
    'stream': False
}
