# BTC daily monitoring indicator analysis and AI investment advice

Analyze BTC price, AHR999 index, and Fear & Greed index based on historical data, and provide buy/sell recommendations。

## Features

- ✅ Fetch and save BTC historical price data
- ✅ Fetch and parse AHR999 index historical data
- ✅ Fetch Fear & Greed index historical data
- ✅ Analyze market trends based on 6 months of historical data
- ✅ Generate comprehensive investment advice reports integrating multiple indicators
- ✅ Consolidate multiple data sources by date into a unified JSON format
- ✅ Use Deepseek R1 AI model to offer advanced investment analysis suggestions

## NEW UPDATES
- ✅ Proxy configuration for fetchers
- ✅ Persists historical data to csv files ('csv' directory)
- ✅ Sends telegram notification with report / prompt results

Proxy configuration:
1) Line 43 in config.py, set your proxy URL as 'http://host:port' or 'http://user:pass@host:port' with authentication

Telegram notification set-up:
1) Open Telegram
2) Message '/newbot' to @BotFather
3) Choose a name and username for your new bot by responding to BotFather.
4) Note down your token to access the HTTP API:
  <img width="440" height="141" alt="image" src="https://github.com/user-attachments/assets/fc41684c-5baa-4077-addd-4138ee290d7b" />

6) Search for your bot username on Telegram and start the chat, type '/start' followed by 'hello'
7) In your browser URL, enter: https://api.telegram.org/bot<YOUR-TOKEN>/getUpdates, this will give you your chat history and chat id with your new bot, note down the chat id:
   <img width="291" height="29" alt="image" src="https://github.com/user-attachments/assets/9dc17ee8-a40e-4c28-8d1d-01a0859cf63e" />

8) 
