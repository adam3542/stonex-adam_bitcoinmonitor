import os
import sys
import json
import asyncio
import logging
import platform
from datetime import datetime

from webhook import send_message_async

src_dir = os.path.join(os.path.dirname(__file__), 'src')
sys.path.append(src_dir)

from config import DATA_DIRS
from src.utils.historical_data import HistoricalDataCollector
from src.utils.trend_analyzer import TrendAnalyzer
from src.utils.data_reorganizer import reorganize_data

from src.ai.advisor import DeepseekAdvisor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('crypto_monitor.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

os.makedirs("reports", exist_ok=True)

async def generate_analysis_report(force_update=False):
    logger.info("Start generating analysis report...")
    
    os.makedirs(DATA_DIRS['data'], exist_ok=True)
    
    collector = HistoricalDataCollector(data_dir=DATA_DIRS['data'])
    
    if force_update:
        logger.info("Force update of historical data...")
        historical_data = await collector.collect_historical_data()
    else:
        logger.info("Check and update historical data...")
        historical_data = await collector.update_historical_data()
    
    if not historical_data:
        logger.error("Failed to obtain historical data and unable to generate analysis report")
        return False
    
    btc_count = len(historical_data.get("btc_price", []))
    ahr_count = len(historical_data.get("ahr999", []))
    fg_count = len(historical_data.get("fear_greed", []))
    
    logger.info(f"Historical data obtained: BTC price ({btc_count} pieces), AHR999 index ({ahr_count} pieces), Fear and Greed index ({fg_count} pieces)")
    
    analyzer = TrendAnalyzer(historical_data)
    
    advice = analyzer.generate_investment_advice()
    
    if advice.get("status") == "error":
        logger.error(f"Failed to generate investment advice: {advice.get('message', 'Unknown error')}")
        return False
    
    report = advice.get("formatted_output", "")
    
    push_message = "🔔 BTCInvestment advice analysis report\n\n"
    push_message += f"{report}"
    
    await send_message_async(push_message)
    
    report_file = f"{DATA_DIRS['reports']}/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    
    logger.info(f"The analysis report has been saved to: {report_file}")
    
    print("\n" + report)
    
    return True, report_file

async def get_ai_investment_advice():
    print("=== AI Investment Advisor (DeepSeek R1) ===\n")
    
    data_file = "data/daily_data.json"
    if not os.path.exists(data_file):
        print("Error: The integrated data file was not found.")
        return
    
    advisor = DeepseekAdvisor()
    
    months = 6
    print(f"analyze data from the last {months} ​​months")
    
    max_retries = 2
    retry_delay = 2.0
    
    try:
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if isinstance(data, list):
                print("Note: Preparing data format for AI processing...")
                wrapped_data = {"responses": data}
                
                temp_file = data_file + ".temp"
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(wrapped_data, f, ensure_ascii=False, indent=2)
                
                data_file = temp_file
                print("The data format has been adjusted, continue processing...")
        except Exception as e:
            logger.warning(f"Error reading data file: {str(e)}")
            print(f"warn: Error reading data file: {str(e)}，")
        
        print("\nGetting AI investment advice, please wait...\n")
        print(f"Configured maximum number of retries: {max_retries}, retry interval: {retry_delay} seconds")
        
        advice = advisor.get_investment_advice(
            data_file=data_file, 
            months=months, 
            max_retries=max_retries, 
            retry_delay=retry_delay
        )
        
        if advice:
            print("\nSuccessfully Obtain AI Investment Advice:")
            print(advice)
            
            push_message = "🤖 AI investment advisor advice\n\n"
            push_message += f"{advice}"
            
            await send_message_async(push_message)
        else:
            print("Error: Failed to obtain AI investment advice")
            print("Possible reasons: API server connection problem, invalid API key, or request timeout")
            print("Tips: Check network connection, API key settings and server status")
    
    except KeyError as e:
        logger.error(f"Error occurred during investment advice processing: {str(e)}")
        print(f"Error: Required data keys are missing during AI investment advice processing '{str(e)}'")
        
        if str(e) == "'responses'":
            print("\nTip: DeepseekAdvisor requires the 'responses' field. Your JSON data structure may need to be adjusted。")
            print("Suggested format: { \"responses\": [ ... your data array ... ] }")
    
    except Exception as e:
        logger.error(f"Error in processing AI investment advice: {str(e)}")
        print(f"Error: {str(e)}")    
        print("Try to get detailed error information...")
        import traceback
        error_details = traceback.format_exc()
        logger.debug(error_details)
        print(f"Error details are recorded in the log file")

async def main():

    try:

        print("\n====== Cryptocurrency Monitoring System ======")
        print("Support analysis: BTC price, AHR999 index and fear and greed index")

        print("Checking for data updates, please wait...\n")
        
        try:
            await generate_analysis_report(force_update=False)
        except Exception as e:
            logger.error(f"Error generating analysis report: {str(e)}")
            print(f"Error generating analysis report: {str(e)}")
        
        try:
            data_dir = DATA_DIRS['data']
            input_file = os.path.join(data_dir, "historical_data.json")
            output_file = os.path.join(data_dir, "daily_data.json")
            
            os.makedirs(data_dir, exist_ok=True)
            
            if not os.path.exists(input_file):
                logger.error(f"The input file does not exist: {input_file}")
                print(f"Error: The input file does not exist: {input_file}")
                return 1
            
            print("Integrating data into a date-organized format...\n")
            success = reorganize_data(input_file, output_file)
            
            if success:
                print(f"Data integration successful! Data files organized by date have been generated: {output_file}")
                print(f"Data file processing completed: {output_file}\n")
            else:
                print("Data integration failed, please check the log for details\n")
        except Exception as e:
            print(f"Errors during data integration: {str(e)}")
            logger.error(f"Errors during data integration: {str(e)}")
        
        try:
            print("AI investment advice being generated...\n")
            await get_ai_investment_advice()
        except Exception as e:
            logger.error(f"Errors in generating AI investment advice: {str(e)}")
            print(f"Errors in generating AI investment advice: {str(e)}")
        
        print("\nProcessing completed, program exits")

    except KeyboardInterrupt:
        print("\nThe program was interrupted by the user")
        return 1
    except Exception as e:
        logger.error(f"Program execution error: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        return 1

    return 0

if __name__ == "__main__":

    exit_code = asyncio.run(main())
    sys.exit(exit_code) 
