import os
import json
import numpy as np
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TrendAnalyzer:
    def __init__(self, historical_data=None):
        self.historical_data = historical_data
        self.analysis_period = 180
    
    def set_historical_data(self, historical_data):
        self.historical_data = historical_data
    
    def analyze_btc_price_trend(self):

        if not self.historical_data or "btc_price" not in self.historical_data:
            return {
                "status": "error",
                "message": "No BTC historical price data available for analysis"
            }
        
        btc_data = self.historical_data["btc_price"]
        
        btc_data = sorted(btc_data, key=lambda x: x.get("timestamp", 0), reverse=True)
        
        btc_data = btc_data[:self.analysis_period]
        
        if not btc_data:
            return {
                "status": "error",
                "message": "BTC price data is empty"
            }
        
        prices = [item.get("price", 0) for item in btc_data if "price" in item]
        dates = [item.get("date", "") for item in btc_data if "date" in item]
        
        if len(prices) < 7:
            return {
                "status": "error",
                "message": f"Insufficient BTC price data: only {len(prices)} days available; at least 7 days of data required"
            }
        
        current_price = prices[0]
        avg_7d = np.mean(prices[:7]) if len(prices) >= 7 else None
        avg_30d = np.mean(prices[:30]) if len(prices) >= 30 else None
        avg_90d = np.mean(prices[:90]) if len(prices) >= 90 else None
        
        price_change_1d = ((current_price / prices[1]) - 1) * 100 if len(prices) > 1 else 0
        price_change_7d = ((current_price / prices[6]) - 1) * 100 if len(prices) > 6 else 0
        price_change_30d = ((current_price / prices[29]) - 1) * 100 if len(prices) > 29 else 0
        
        volatility_7d = (np.std(prices[:7]) / np.mean(prices[:7]) * 100) if len(prices) >= 7 else 0
        volatility_30d = (np.std(prices[:30]) / np.mean(prices[:30]) * 100) if len(prices) >= 30 else 0
        
        trend_7d = "Increase" if price_change_7d > 0 else "Decrease"
        trend_30d = "Increase" if price_change_30d > 0 else "Decrease"
        
        rsi = self._calculate_rsi(prices, 14) if len(prices) >= 14 else None
        
        min_price = min(prices)
        max_price = max(prices)
        price_percentile = ((current_price - min_price) / (max_price - min_price) * 100) if max_price > min_price else 50
        

        recent_lows = sorted(prices[:30])[:5]
        recent_highs = sorted(prices[:30], reverse=True)[:5]
        
        support_level = sum(recent_lows) / len(recent_lows)
        resistance_level = sum(recent_highs) / len(recent_highs)
        
        return {
            "status": "success",
            "current_price": current_price,
            "avg_7d": avg_7d,
            "avg_30d": avg_30d,
            "avg_90d": avg_90d,
            "price_change_1d": price_change_1d,
            "price_change_7d": price_change_7d,
            "price_change_30d": price_change_30d,
            "volatility_7d": volatility_7d,
            "volatility_30d": volatility_30d,
            "trend_7d": trend_7d,
            "trend_30d": trend_30d,
            "rsi_14d": rsi,
            "price_percentile": price_percentile,
            "support_level": support_level,
            "resistance_level": resistance_level,
            "latest_date": dates[0] if dates else None
        }
    
    def analyze_sentiment_trends(self):
        
        if not self.historical_data:
            return {
                "status": "error",
                "message": "No historical data available for analysis"
            }
        
        ahr999_analysis = self._analyze_ahr999()
        
        fear_greed_analysis = self._analyze_fear_greed()
        
        return {
            "status": "success" if ahr999_analysis["status"] == "success" or fear_greed_analysis["status"] == "success" else "error",
            "ahr999": ahr999_analysis,
            "fear_greed": fear_greed_analysis
        }
    
    def _analyze_ahr999(self):
        if not self.historical_data or "ahr999" not in self.historical_data:
            return {
                "status": "error",
                "message": "No historical data for the AHR999 index available for analysis"
            }
        
        ahr_data = self.historical_data["ahr999"]
        
        ahr_data = sorted(ahr_data, key=lambda x: x.get("timestamp", 0), reverse=True)
        
        ahr_data = ahr_data[:self.analysis_period]
        
        if not ahr_data:
            return {
                "status": "error",
                "message": "AHR999 index data is empty"
            }
        
        ahr_values = [item.get("ahr999", 0) for item in ahr_data if "ahr999" in item]
        dates = [item.get("date", "") for item in ahr_data if "date" in item]
        
        if len(ahr_values) < 7:
            return {
                "status": "error",
                "message": f"Insufficient AHR999 index data: only {len(ahr_values)} days available; at least 7 days of data required"
            }
        
        current_ahr = ahr_values[0]
        avg_7d = np.mean(ahr_values[:7]) if len(ahr_values) >= 7 else None
        avg_30d = np.mean(ahr_values[:30]) if len(ahr_values) >= 30 else None
        
        ahr_change_1d = ((current_ahr / ahr_values[1]) - 1) * 100 if len(ahr_values) > 1 else 0
        ahr_change_7d = ((current_ahr / ahr_values[6]) - 1) * 100 if len(ahr_values) > 6 else 0
        ahr_change_30d = ((current_ahr / ahr_values[29]) - 1) * 100 if len(ahr_values) > 29 else 0
        
        trend_7d = "Increase" if ahr_change_7d > 0 else "Decrease"
        trend_30d = "Increase" if ahr_change_30d > 0 else "Decrease"
        
        min_ahr = min(ahr_values)
        max_ahr = max(ahr_values)
        ahr_percentile = ((current_ahr - min_ahr) / (max_ahr - min_ahr) * 100) if max_ahr > min_ahr else 50
        
        market_state = "Unknown"
        if current_ahr < 0.45:
            market_state = "Extremely undervalued"
        elif current_ahr < 0.75:
            market_state = "Undervalued"
        elif current_ahr < 1.0:
            market_state = "Lower Bound of Fair Value Range"
        elif current_ahr < 1.25:
            market_state = "Upper Bound of Fair Value Range"
        elif current_ahr < 1.5:
            market_state = "Overvalued"
        else:
            market_state = "Extremely Overvalued"
        
        return {
            "status": "success",
            "current_value": current_ahr,
            "avg_7d": avg_7d,
            "avg_30d": avg_30d,
            "change_1d": ahr_change_1d,
            "change_7d": ahr_change_7d,
            "change_30d": ahr_change_30d,
            "trend_7d": trend_7d,
            "trend_30d": trend_30d,
            "percentile": ahr_percentile,
            "market_state": market_state,
            "latest_date": dates[0] if dates else None
        }
    
    def _analyze_fear_greed(self):
        if not self.historical_data or "fear_greed" not in self.historical_data:
            return {
                "status": "error",
                "message": "No historical data for the Fear & Greed Index available for analysis"
            }
        
        fg_data = self.historical_data["fear_greed"]
        
        fg_data = sorted(fg_data, key=lambda x: x.get("timestamp", 0), reverse=True)
        
        fg_data = fg_data[:self.analysis_period]
        
        if not fg_data:
            return {
                "status": "error",
                "message": "Fear & Greed Index data is empty"
            }
        
        fg_values = [item.get("value", 0) for item in fg_data if "value" in item]
        fg_classes = [item.get("value_classification", "") for item in fg_data if "value_classification" in item]
        dates = [item.get("date", "") for item in fg_data if "date" in item]
        
        if len(fg_values) < 7:
            return {
                "status": "error",
                "message": f"Insufficient Fear & Greed Index data: only {len(fg_values)} days available; at least 7 days of data required"
            }
        
        current_fg = fg_values[0]
        current_class = fg_classes[0] if fg_classes else "未知"
        avg_7d = np.mean(fg_values[:7]) if len(fg_values) >= 7 else None
        avg_30d = np.mean(fg_values[:30]) if len(fg_values) >= 30 else None
        
        fg_change_1d = current_fg - fg_values[1] if len(fg_values) > 1 else 0
        fg_change_7d = current_fg - fg_values[6] if len(fg_values) > 6 else 0
        fg_change_30d = current_fg - fg_values[29] if len(fg_values) > 29 else 0
        
        trend_7d = "Increase" if fg_change_7d > 0 else "Decrease"
        trend_30d = "Increase" if fg_change_30d > 0 else "Decrease"
        
        market_mood = current_class
        
        if fg_change_7d > 10:
            mood_change = "Significant improvement in sentiment"
        elif fg_change_7d > 5:
            mood_change = "Slight improvement in sentiment"
        elif fg_change_7d < -10:
            mood_change = "Significant deterioration in sentiment"
        elif fg_change_7d < -5:
            mood_change = "Slight deterioration in sentiment"
        else:
            mood_change = "Sentiment relatively stable"
        
        return {
            "status": "success",
            "current_value": current_fg,
            "current_class": current_class,
            "avg_7d": avg_7d,
            "avg_30d": avg_30d,
            "change_1d": fg_change_1d,
            "change_7d": fg_change_7d,
            "change_30d": fg_change_30d,
            "trend_7d": trend_7d,
            "trend_30d": trend_30d,
            "market_mood": market_mood,
            "mood_change": mood_change,
            "latest_date": dates[0] if dates else None
        }
    
    def _calculate_rsi(self, prices, window=14):
        if len(prices) < window + 1:
            return None
        
        deltas = np.diff(prices[::-1])
        
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[:window])
        avg_loss = np.mean(losses[:window])

        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def generate_investment_advice(self):
        
        price_analysis = self.analyze_btc_price_trend()
        if price_analysis["status"] == "error":
            return {
                "status": "error",
                "message": f"Unable to generate investment recommendation: {price_analysis['message']}"
            }
        
        sentiment_analysis = self.analyze_sentiment_trends()
        if sentiment_analysis["status"] == "error":
            logger.warning("Market sentiment analysis failed; generating recommendations based on price data only.")
        
        advice = {
            "status": "success",
            "price_based": self._get_price_based_advice(price_analysis),
            "formatted_output": ""
        }
        
        if sentiment_analysis["status"] == "success":
            if "ahr999" in sentiment_analysis and sentiment_analysis["ahr999"]["status"] == "success":
                advice["ahr999_based"] = self._get_ahr999_based_advice(sentiment_analysis["ahr999"])
            
            if "fear_greed" in sentiment_analysis and sentiment_analysis["fear_greed"]["status"] == "success":
                advice["fear_greed_based"] = self._get_fear_greed_based_advice(sentiment_analysis["fear_greed"])
        
        advice["overall"] = self._get_overall_advice(advice)
        
        advice["formatted_output"] = self._format_advice_output(price_analysis, sentiment_analysis, advice)
        
        return advice
    
    def _get_price_based_advice(self, price_analysis):
        current_price = price_analysis["current_price"]
        
        if price_analysis["trend_30d"] == "Increase" and price_analysis["trend_7d"] == "Decrease":
            if price_analysis["price_change_7d"] > 10:
                return {
                    "action": "Wait or slightly reduce position",
                    "reason": "Price has surged rapidly in the short term, potential risk of pullback",
                    "confidence": "Medium"
                }
            else:
                return {
                    "action": "Hold",
                    "reason": "Price is maintaining a stable upward trend",
                    "confidence": "Medium"
                }
        elif price_analysis["trend_30d"] == "Increase" and price_analysis["trend_7d"] == "Decrease":
            if price_analysis["price_change_7d"] < -7:
                return {
                    "action": "Buy the dip (small position)",
                    "reason": "Short-term pullback but medium-term trend is upward; potential buying opportunity",
                    "confidence": "Medium"
                }
            else:
                return {
                    "action": "Hold",
                    "reason": "Minor short-term pullback; medium-term trend remains upward",
                    "confidence": "Medium"
                }
        elif price_analysis["trend_30d"] == "Decrease" and price_analysis["trend_7d"] == "Increase":
            return {
                "action": "Cautious hold",
                "reason": "Could be a short-term rebound within a medium-term downtrend",
                "confidence": "Low"
            }
        else:
            if price_analysis["price_change_30d"] < -20:
                return {
                    "action": "Cautious small buy",
                    "reason": "After a sharp decline, the price may be bottoming out",
                    "confidence": "Low"
                }
            else:
                return {
                    "action": "Wait and see",
                    "reason": "Price is in a downtrend; wait for signs of stabilization",
                    "confidence": "Medium"
                }
    
    def _get_ahr999_based_advice(self, ahr999_analysis):

        current_ahr = ahr999_analysis["current_value"]
        market_state = ahr999_analysis["market_state"]
        
        if market_state == "Extremely Undervalued":
            return {
                "action": "Buy aggressively",
                "reason": f"AHR999 index ({current_ahr:.3f}) indicates the market is extremely undervalued",
                "confidence": "High"
            }
        elif market_state == "Undervalued":
            return {
                "action": "Buy regularly",
                "reason": f"AHR999 index ({current_ahr:.3f}) indicates the market is undervalued",
                "confidence": "Medium-High"
            }
        elif market_state == "Lower Bound of Fair Value Range":
            return {
                "action": "Buy slightly",
                "reason": f"AHR999 index ({current_ahr:.3f}) indicates the market is near the lower bound of fair value",
                "confidence": "Medium"
            }
        elif market_state == "Upper Bound of Fair Value Range":
            return {
                "action": "Hold",
                "reason": f"AHR999 index ({current_ahr:.3f}) indicates the market is near the upper bound of fair value",
                "confidence": "Medium"
            }
        elif market_state == "Overvalued":
            return {
                "action": "Slightly reduce position",
                "reason": f"AHR999 index ({current_ahr:.3f}) indicates the market is overvalued",
                "confidence": "Medium-High"
            }
        else:
            return {
                "action": "Aggressively reduce position",
                "reason": f"AHR999 index ({current_ahr:.3f}) indicates the market is extremely overvalued",
                "confidence": "High"
            }
    
    def _get_fear_greed_based_advice(self, fear_greed_analysis):

        current_fg = fear_greed_analysis["current_value"]
        market_mood = fear_greed_analysis["market_mood"]
        
        if market_mood == "Extreme Fear":
            return {
                "action": "Gradually buy",
                "reason": f"Fear & Greed Index ({current_fg}) indicates extreme fear, which is usually a buying opportunity",
                "confidence": "Medium-High"
            }
        elif market_mood == "Fear":
            return {
                "action": "Buy slightly",
                "reason": f"Fear & Greed Index ({current_fg}) indicates market fear",
                "confidence": "Medium"
            }
        elif market_mood == "Neutral":
            return {
                "action": "Hold",
                "reason": f"Fear & Greed Index ({current_fg}) indicates neutral market sentiment",
                "confidence": "Medium"
            }
        elif market_mood == "Greed":
            return {
                "action": "Hold cautiously",
                "reason": f"Fear & Greed Index ({current_fg}) indicates market greed",
                "confidence": "Medium"
            }
        else:  # Extreme Greed
            return {
                "action": "Consider reducing position",
                "reason": f"Fear & Greed Index ({current_fg}) indicates extreme greed — caution advised",
                "confidence": "Medium-High"
            }
    
    def _get_overall_advice(self, advice_dict):

        actions = []
        reasons = []
        confidence_levels = {"Low": 1, "Medium": 2, "Medium-High": 3, "High": 4}
        
        if "price_based" in advice_dict:
            actions.append(advice_dict["price_based"]["action"])
            reasons.append(advice_dict["price_based"]["reason"])
            price_confidence = confidence_levels.get(advice_dict["price_based"]["confidence"], 2)
        else:
            price_confidence = 0
        
        if "ahr999_based" in advice_dict:
            actions.append(advice_dict["ahr999_based"]["action"])
            reasons.append(advice_dict["ahr999_based"]["reason"])
            ahr_confidence = confidence_levels.get(advice_dict["ahr999_based"]["confidence"], 2)
        else:
            ahr_confidence = 0
        
        if "fear_greed_based" in advice_dict:
            actions.append(advice_dict["fear_greed_based"]["action"])
            reasons.append(advice_dict["fear_greed_based"]["reason"])
            fg_confidence = confidence_levels.get(advice_dict["fear_greed_based"]["confidence"], 2)
        else:
            fg_confidence = 0
        
        action_weights = {}
        for i, action in enumerate(actions):
            confidence = [price_confidence, ahr_confidence, fg_confidence][i]
            if action in action_weights:
                action_weights[action] += confidence
            else:
                action_weights[action] = confidence
        
        if not action_weights:
            final_action = "Wait and see"
            final_reason = "Insufficient data to provide a clear recommendation"
            final_confidence = "Low"
        else:
            final_action = max(action_weights.items(), key=lambda x: x[1])[0]
            
            relevant_reasons = []
            for i, action in enumerate(actions):
                if action == final_action:
                    relevant_reasons.append(reasons[i])
            
            final_reason = "Comprehensive analysis:" + "；".join(relevant_reasons)
            
            max_weight = max(action_weights.values())
            if max_weight >= 7:
                final_confidence = "High"
            elif max_weight >= 5:
                final_confidence = "Medium-High"
            elif max_weight >= 3:
                final_confidence = "Medium"
            else:
                final_confidence = "Low"
        
        return {
            "action": final_action,
            "reason": final_reason,
            "confidence": final_confidence
        }
    
    def _format_advice_output(self, price_analysis, sentiment_analysis, advice):

        output = []
        
        output.append("=============== BTC Investment Analysis Report ===============")
        output.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        output.append("【💰 Price Information")
        if price_analysis["status"] == "success":
            latest_date = price_analysis.get("latest_date", "Unknown")
            output.append(f"Latest data date: {latest_date}")
            output.append(f"Current price: ${price_analysis['current_price']:,.2f}")
            output.append(f"7-day average: ${price_analysis['avg_7d']:,.2f}")
            output.append(f"30-day average: ${price_analysis['avg_30d']:,.2f}")
            output.append(f"90-day average: ${price_analysis['avg_90d']:,.2f}")
            output.append(f"24h change: {price_analysis['price_change_1d']:.2f}%")
            output.append(f"7d change: {price_analysis['price_change_7d']:.2f}%")
            output.append(f"30d change: {price_analysis['price_change_30d']:.2f}%")
            output.append(f"7-day volatility: {price_analysis['volatility_7d']:.2f}%")
            output.append(f"30-day volatility: {price_analysis['volatility_30d']:.2f}%")
            
            if price_analysis.get("rsi_14d") is not None:
                output.append(f"14-day RS: {price_analysis['rsi_14d']:.2f}")
            
            output.append(f"Support level: ${price_analysis['support_level']:,.2f}")
            output.append(f"Resistance level: ${price_analysis['resistance_level']:,.2f}")
            output.append(f"Current price is at the {price_analysis['price_percentile']:.2f} percentile of the {self.analysis_period}-day range")
        else:
            output.append(f"Unable to retrieve price information: {price_analysis.get('message', 'Unknown error')}")
        output.append("")
        
        output.append("【💭 Market Sentiment Indicators】")
        if sentiment_analysis["status"] == "success":

            if "ahr999" in sentiment_analysis and sentiment_analysis["ahr999"]["status"] == "success":
                ahr = sentiment_analysis["ahr999"]
                output.append("AHR999 Index:")
                output.append(f"   Current value: {ahr['current_value']:.3f} ({ahr['market_state']})")
                output.append(f"  7-day average: {ahr['avg_7d']:.3f}")
                output.append(f"  30-day average: {ahr['avg_30d']:.3f}")
                output.append(f"  7-day trend: {ahr['trend_7d']} ({ahr['change_7d']:.2f}%)")
                output.append(f"  30-day trend: {ahr['trend_30d']} ({ahr['change_30d']:.2f}%)")
                output.append(f"  Historical percentile: {ahr['percentile']:.2f}%")
                output.append("")
            
            if "fear_greed" in sentiment_analysis and sentiment_analysis["fear_greed"]["status"] == "success":
                fg = sentiment_analysis["fear_greed"]
                output.append("Fear & Greed Index:")
                output.append(f"   Current value: {fg['current_value']} ({fg['current_class']})")
                output.append(f"  7-day average: {fg['avg_7d']:.2f}")
                output.append(f"  30-day average: {fg['avg_30d']:.2f}")
                output.append(f"  7-day trend: {fg['trend_7d']} ({fg['change_7d']:.2f})")
                output.append(f"  30-day trend: {fg['trend_30d']} ({fg['change_30d']:.2f})")
                output.append(f"  Market sentiment: {fg['market_mood']}")
                output.append(f"  Sentiment change: {fg['mood_change']}")
                output.append("")
        else:
            output.append(f"Unable to retrieve market sentiment indicators: {sentiment_analysis.get('message', 'Unknown error')}")
            output.append("")
        
        output.append("【💡 Investment Recommendations")
        
        if "price_based" in advice:
            pb = advice["price_based"]
            output.append(f"Based on price analysis: {pb['action']} (Confidence: {pb['confidence']})")
            output.append(f"  Reason: {pb['reason']}")
        
        if "ahr999_based" in advice:
            ab = advice["ahr999_based"]
            output.append(f"Based on AHR999 Index: {ab['action']} (Confidence: {ab['confidence']})")
            output.append(f"  Reason: {ab['reason']}")
        
        if "fear_greed_based" in advice:
            fb = advice["fear_greed_based"]
            output.append(f"Based on Fear & Greed Index: {fb['action']} (Confidence: {fb['confidence']})")
            output.append(f"  Reason: {fb['reason']}")
        
        output.append("")
        
        if "overall" in advice:
            ov = advice["overall"]
            output.append("Overall Recommendation:")
            output.append(f"  Action: {ov['action']}")
            output.append(f"  Reason: {ov['reason']}")
            output.append(f"  Confidence: {ov['confidence']}")
        
        output.append("\n======================= End of Report ======================")
        
        return "\n".join(output) 