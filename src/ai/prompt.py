import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Union

from config import DATA_DIRS

logger = logging.getLogger(__name__)

def get_investment_advice_template(current_date: str, last_position: int = 0, 
                                  last_cost_basis: str = "No position yet", 
                                  last_action: str = "First time position building advice", 
                                  data_json: str = "", 
                                  total_budget: float = 1000.0) -> str:

    current_invested = (last_position / 100) * total_budget
    available_cash = total_budget - current_invested
    
    return f"""You are my professional Bitcoin investment advisor, with deep expertise in cryptocurrency market analysis and rigorous risk management capabilities。 Based on current market data ({current_date}), please provide a comprehensive analysis and specific actionable investment recommendations。

# TL;DR (Core Summary)
Please provide a core summary of 50 words or less at the beginning, including：
- Current market status：【Bull market/Bear market/Choppy market】
- Investment Decisions：【Increase/reduce/full position/clear position/hold】
- Key reasons：【Main supporting reasons】

Current Portfolio Status:
- Total investment budget：${total_budget:.0f}
- Current Bitcoin positions:{last_position}% (Invested${current_invested:.0f})
- Available cash：${available_cash:.0f}
- Current cost basis: {last_cost_basis}
- Risk Preference: Medium (Willing to accept reasonable volatility, but requires that the maximum drawdown does not exceed 30%)
- Investment cycle: medium to long term (6-18 months)

Last investment advice: {last_action}

Please analyze the market conditions based on the following historical data and provide clear operational (trading/investment) recommendations.

Here is the historical market data (JSON format):
{data_json}

Please provide a comprehensive analysis and precise recommendations according to the following structure:

I、Market Cycle Analysis (within 150 characters):
[Analyze the current market cycle position (accumulation phase / uptrend phase / distribution phase / downtrend phase), key support and resistance levels, the significance of the AHR999 indicator and the Fear & Greed Index, as well as the overall market sentiment. Provide a clear judgment on whether the market is currently in a bull or bear phase. Use only the provided data for your analysis。]

II、Technical Indicator Interpretation
1. Price Trends:[Analyze BTC's recent price trends, moving average system status, and trading volume changes]
2. Market valuation:[Interpret the current meanings of the AHR999 and Fear & Greed Index, and explain their levels relative to historical data]
3. Cycle Phase：[Based on the existing data, determine the current market cycle phase and identify signals indicating a bull-to-bear or bear-to-bull transition]

III、Investment Decision Recommendations
1. Position Adjustment：[Use clear keywords such as "Increase position / Decrease position / Full position / Clear position / Hold," specifying exact percentage and amount adjustments, accurate to 5%]
2. Entry/Exit Price Levels：[Provide clear price ranges, including ideal entry points and price ranges for phased buying/selling]
3. Stop-Loss Settings:[Specify explicit stop-loss price and conditions for re-entry after stop-loss triggers]
4. Profit Targets：[Set short-term (1-3 months) and mid-term (3-6 months) target prices and the strategy after reaching these targets]

IV、Position Management Tracking and Profit Calculation
Last recommendation：{last_action}
Current recommendation: [Core content of new advice, using standard decision keywords]
Position change: [Position percentage change after executing advice, from {last_position}% to what]
Fund allocation：
- Currently invested：${current_invested:.0f} ({last_position}%)
- Amount for this operation：$XXX
- Invested after operation：$XXX (XX%)
- Remaining available cash：$XXX

Cost Basis Calculation：
- Current cost basis：{last_cost_basis}
- New trade price：$XXX
- Average cost after operation：$XXX

Expected Returns Calculation：
- Short-term target profit:$XXX (+XX%)
- Mid-term target profit:$XXX (+XX%)
- Total portfolio return rate：XX%

V. Risk Analysis
[List 2-3 observed market risk factors based on provided data, each within 50 words, with concrete mitigation measures]
1. [Primary risk 1 and countermeasures]
2. [Primary risk 2 and countermeasures]
3. [Optional risk 3 and countermeasures]

VI. Key Future Observation Indicators
[List 3 indicators or price levels to watch closely, each with explicit thresholds, significance, trigger conditions, and actionable recommendations after triggers]
1. [Key indicator 1: threshold, meaning, action after trigger]
2. [Key indicator 2: threshold, meaning, action after trigger]
3. [Key indicator 3: threshold, meaning, action after trigger]

VII. Structured Decision Data 
```json
{{
  "date": "{current_date}",
  "market_state": "ull Market / Bear Market / choppy Market",
  "decision_keyword": "Increase Position / Decrease Position / Full Position / Clear Position / Hold",
  "position": number,
  "position_change": "Increase / Decrease / Maintain X%",
  "action": "Buy / Sell / Hold / Clear",
  "entry_price": "Price range or specific value",
  "stop_loss": number,
  "target_short": number,
  "target_mid": number,
  "cost_basis": number,
  "portfolio": {{
    "total_budget": {total_budget},
    "current_invested": number,
    "available_cash": number,
    "operation_amount": number
  }},
  "profit_calculation": {{
    "short_term_profit": number,
    "mid_term_profit": number,
    "short_term_return_pct": "percentage",
    "mid_term_return_pct": "percentage",
    "portfolio_return_pct": "percentage"
  }},
  "market_cycle": "Accumulation / Uptrend / Distribution / Downtrend",
  "risks": ["Risk 1", "Risk 2", "Risk 3"],
  "key_levels": ["Level 1", "Level 2", "Level 3"]
}}
```

Important Notes:
1. Provide a TL;DR summary at the beginning clearly stating bull/bear status and decision keyword
2. Present detailed analysis in six sections before the JSON decision data
3. Position adjustments must use standard keywords: Increase Position / Decrease Position / Full Position / Clear Position / Hold
4. All monetary calculations must be based on the total investment budget ${total_budget:.0f}
5. Include specific profit calculations in both USD and percentages
6. All suggestions must be based solely on provided data; do not reference unprovided indicators or info
7. Provide concrete, actionable strategies rather than vague advice
8. Consider current position status and cost basis in recommendations
9. Use clear numerical values and percentages; avoid ambiguous statements
10. Ensure every risk factor has a corresponding mitigation strategy
11. Historical data comparisons must specify exact values and timestamps
"""

def prepare_investment_advice_params(current_date: Optional[str] = None, 
                                   last_advice: Optional[Dict] = None,
                                   total_budget: float = 1000.0) -> Dict[str, Any]:

    if not current_date:
        current_date = datetime.now().strftime('%Y-%m-%d')
    
    params = {
        "current_date": current_date,
        "last_position": 0,
        "last_cost_basis": "No position opened yet",
        "last_action": "Initial Position Entry Recommendation",
        "total_budget": total_budget
    }
    
    if last_advice:
        params["last_position"] = last_advice.get("position", 0)
        params["last_cost_basis"] = last_advice.get("cost_basis", "No position opened yet")
        
        last_decision = last_advice.get("decision_keyword", "Open a position")
        last_entry_price = last_advice.get("entry_price", "N/A")
        last_stop_loss = last_advice.get("stop_loss", "N/A")
        
        params["last_action"] = f"{last_decision} to {params['last_position']}%, entry price at {last_entry_price}, stop-loss set at {last_stop_loss}"
    
    return params

def calculate_portfolio_metrics(current_position: int, current_cost_basis: float,
                              new_position: int, new_price: float,
                              total_budget: float = 1000.0) -> Dict[str, Any]:

    current_invested = (current_position / 100) * total_budget
    new_invested = (new_position / 100) * total_budget
    operation_amount = new_invested - current_invested
    
    if new_position > 0:
        if current_position > 0:
            total_btc_old = current_invested / current_cost_basis if current_cost_basis > 0 else 0
            total_btc_new = abs(operation_amount) / new_price if operation_amount != 0 else 0
            
            if operation_amount > 0:
                new_cost_basis = (current_invested + abs(operation_amount)) / (total_btc_old + total_btc_new)
            else:
                new_cost_basis = current_cost_basis
        else:
            new_cost_basis = new_price
    else:
        new_cost_basis = 0
    
    return {
        "current_invested": current_invested,
        "new_invested": new_invested,
        "operation_amount": operation_amount,
        "available_cash": total_budget - new_invested,
        "new_cost_basis": new_cost_basis,
        "operation_type": "Increase Position" if operation_amount > 0 else "Decrease Position" if operation_amount < 0 else "Hold"
    }

def save_prompt_for_debug(prompt: str) -> str:
    prompts_dir = DATA_DIRS['prompts']
    os.makedirs(prompts_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f"prompt_{timestamp}.txt"
    
    prompt_path = os.path.join(prompts_dir, filename)
    
    with open(prompt_path, 'w', encoding='utf-8') as f:
        f.write(prompt)
    
    logger.info(f"Saved prompt to: {prompt_path}")
    return prompt_path

def extract_json_from_text(text: str) -> Optional[Dict]:
    import re
    import json
    
    json_match = re.search(r'```json\s*({[\s\S]*?})\s*```', text)
    if not json_match:
        return None
        
    try:
        json_str = json_match.group(1)
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {str(e)}")
        return None 