##### Load packages ---------------------------------------------------------------------------------------

# Import Coinbase-related packages
import cbpro
import coinbase
from coinbase.wallet.client import Client
from coinbase.wallet.model import APIObject

# Import other packages
#import matplotlib
#matplotlib.use("TKAgg")
import matplotlib.dates
from matplotlib.ticker import StrMethodFormatter
from matplotlib import pyplot
import dateutil.parser as dp
from numpy import linspace
from numpy import argmax
from numpy import argmin
from pandas import *
import datetime
from datetime import timedelta
import seaborn
import math
import time
import json
import requests
import re





##### Get price data --------------------------------------------------------------------------------------

# Create function to pull price data for a given timeframe
# Possible timeframes: 1hr, 1d (default), 1 wk, 1m, 3m, 6m, 1yr, max
# Note: Coinbase historical data may be incomplete
def getPriceSeries(tFrame, currency):

    # Set end of timeframe
    tEnd = round(time.time())

    # Set beginning of timeframe and data granularity
    if tFrame == "1hr":
        tStart = tEnd - 3600
        gran = 60
    elif tFrame == "1d":
        tStart = tEnd - 86400
        gran = 300
    elif tFrame == "1wk":
        tStart = tEnd - 86400*7 
        gran = 3600
    elif tFrame == "1m":
        tStart = tEnd - 86400*30
        gran = 21600
    elif tFrame == "3m":
        tStart = tEnd - 86400*30*3
        gran = 21600
    elif tFrame == "6m":
        tStart = tEnd - 86400*30*6
        gran = 21600
    elif tFrame == "1yr":
        tStart = tEnd - 86400*365
        gran = 21600
    elif tFrame == "max":
        tStart = 1375660800
        gran = 86400

    # Activate public client
    p_client = cbpro.PublicClient()
    
    # Set number of blocks since there is a 300-point limit per block
    nBlocks = ((tEnd - tStart)/gran + 2)/300
    
    # Set currency conversion string
    ccs = currency + "-USD"
    
    # Define internal function to convert timestamp to ISO format
    def tsToISO(ts):
        tz = datetime.datetime.now().astimezone().tzinfo
        return datetime.datetime.fromtimestamp(ts, tz).isoformat()
    
    # Pull data from CoinbasePro API
    if nBlocks <= 1:    
        isodate0 = tsToISO(tStart)
        isodate1 = tsToISO(tEnd)
        data = p_client.get_product_historic_rates(ccs, granularity = gran,
                                                   start = isodate0, end = isodate1)
        data = DataFrame(data, columns = ["timestamp", "open", "high", "low", "close", "volume"])
        data = data.sort_values(by = "timestamp")
    else:
        for i in range(1, math.ceil(nBlocks) + 1):
            if i == 1:
                isodate0 = tsToISO(tStart)
                isodate1 = tsToISO(tStart + gran*300)
                data = p_client.get_product_historic_rates(ccs, granularity = gran,
                                                           start = isodate0, end = isodate1)
                data = DataFrame(data, columns = ["timestamp", "open", "high", "low", "close", "volume"])
                data = data.sort_values(by = "timestamp")
            else:
                if i > 1 and i < nBlocks:
                    isodate0 = tsToISO(tStart + (i - 1)*gran*300)
                    isodate1 = tsToISO(tStart + i*gran*300)
                elif i > nBlocks:
                    isodate0 = tsToISO(tStart + (i - 1)*gran*300)
                    isodate1 = tsToISO(tEnd)
                newdat = p_client.get_product_historic_rates(ccs, granularity = gran,
                                                             start = isodate0, end = isodate1)
                newdat = DataFrame(newdat, columns = ["timestamp", "open", "high", "low", "close", "volume"])
                newdat = newdat.sort_values(by = "timestamp")
                data = data.append(newdat, ignore_index = True)

    # Get mean price (average of open and close)
    data["mean"] = data[["open", "close"]].mean(axis = 1)   

    # Convert timestamp to ISO format    
    data["ISO"] = data["timestamp"].map(tsToISO)
    
    # Convert ISO format to datetime
    data["datetime"] = data["ISO"].map(dp.isoparse)
    
    # Reset index to start with smallest timestamp
    data.reset_index(inplace = True, drop = True)
    
    # Return data frame
    return data





##### Get top 24-hour movers or change over timeframe -----------------------------------------------------

# Function to get current prices and return over timeframe
def getPriceSummary(tFrame, currencyList):
    
    # Activate public client and get currency info
    p_client = cbpro.PublicClient()
    
    # Compile current prices and price versus opening price
    d1 = {}
    low, high, opens, closes, returns = [], [], [], [], []
    for i in range(0, len(currencyList)):
        d1["key%s" %i] = getPriceSeries(tFrame, currencyList[i])
        low.append(min(d1["key%s" %i]["low"]))
        high.append(max(d1["key%s" %i]["high"]))
        opens.append(d1["key%s" %i]["open"].iloc[0])
        closes.append(d1["key%s" %i]["close"].iloc[-1])
        returns.append((closes[i] - opens[i])/opens[i]*100)
    
    # Put data into dataframe    
    df = pandas.DataFrame([[tFrame]*len(currencyList), currencyList, low, high, opens, closes, returns],
                          ["Timeframe", "Currency", "Low", "High", "Open", "Close", "Return"]).transpose()
    
    # Return dataframe
    return df

# Function that returns top movers over 24h
def getCurrentMovers():

    # Activate public client and get currency info
    p_client = cbpro.PublicClient()
    currencyInfo = p_client.get_currencies()
    
    # Initialise lists
    currencyList1 = []
    currencyList2 = []
    openV, closeV, delta = [], [], []
    
    # Calculate 24h percent change for each currency
    for i in range(0, len(currencyInfo)):
        currencyList1.append(currencyInfo[i]["id"])
        currencyList2.append(currencyInfo[i]["id"])
        try:
            if currencyList1[i] in ["XLM", "ADA", "DOT", "UNI", "LTC", "ETH", "BTC"]:
                vals = mData[1].loc[mData[1]["Currency"] == currencyList1[i]]
                delta.append(float(vals["Return"]))
                openV.append(float(vals["Open"]))
                closeV.append(float(vals["Close"]))
            else:
                vals = p_client.get_product_24hr_stats(currencyList1[i] + "-USD")
                delta.append((float(vals["last"]) - float(vals["open"]))/float(vals["open"])*100)
                openV.append(float(vals["open"]))
                closeV.append(float(vals["last"]))
        except ZeroDivisionError:
            del currencyList2[-1]
            pass
        except KeyError:
            del currencyList2[-1]
            pass
        
    # Create data frame of all currencies
    df = DataFrame([currencyList2, openV, closeV, delta],
                   ["Currency", "Open", "Close", "Change"]).transpose()
    
    # Get top and bottom performers
    dfTop = df.sort_values("Change", ascending = False).iloc[0:10]
    dfBottom = df.sort_values("Change").iloc[0:10]
    
    # Return new data frame
    return dfTop.append(dfBottom)





##### Generate user wallet summary ------------------------------------------------------------------------

# Access client using secure keys
# Substitute API key and secret key with the user's actual key codes
client = Client("api_key", "api_secret")

# Function to list current holdings for each cryptocurrency
def getCurrentHoldings():
    
    # Initialise lists
    ids = []
    currency = []
    amount = []
    crypto = []
    
    # Populate lists with held currencies
    for wallet in initAccount.data:
        idn = wallet["id"]
        crncy = str(wallet["name"]).replace(" Wallet", "")
        value = float(str(wallet["native_balance"]).replace("USD ", ""))
        if value > 0:
            ids.append(idn)
            currency.append(crncy)
            crypto.append(float(str(wallet["balance"]).replace(crncy + " ", "")))
            amount.append(value)
    pcts = [x/sum(amount)*100 for x in amount]
    dfCurrency = DataFrame([ids, currency, crypto, amount, pcts],
                           ["ID", "Currency", "Crypto", "Amount", "Percent"]).transpose() 
    
    # Return dataframe of held currencies, sorted by value
    return dfCurrency.sort_values("Amount", ascending = False).reset_index(drop = True)

# Function to list current holdings for only a single cryptocurrency (or trading pair)
def getSpecificCurrency(currency1, currency2 = None):
    
    # Initialise lists
    cAmnt = []
    
    # Get crypto and native balance for each specified currency
    cHold1 = client.get_account(initIDs.loc[initIDs["Currency"] == currency1]["ID"].values[0])
    cAmnt.append(cHold1["balance"]["amount"])
    cAmnt.append(cHold1["native_balance"]["amount"])
    if currency2 not in [None, ""]:
        cHold2 = client.get_account(initIDs.loc[initIDs["Currency"] == currency2]["ID"].values[0])
        cAmnt.append(cHold2["balance"]["amount"])
        cAmnt.append(cHold2["native_balance"]["amount"])
        
    # Return list of crypto and native balances
    return cAmnt

# Function to list user's transaction history    
def getTransactionHistory():

    # Initialise lists
    currency = []
    amountC = []
    amountN = []
    tType = []
    tTime = []
    tStat = []
    
    # Get transactions for each wallet
    for i in list(initIDs["ID"].values):
        events = client.get_transactions(i)
        for j in events.data:
            currency.append(j["amount"]["currency"])
            amountC.append(j["amount"]["amount"])
            amountN.append(j["native_amount"]["amount"])
            tType.append(j["type"])
            tTime.append(j["created_at"])
            tStat.append(j["status"])
            
    # Convert amount and native amount to floats
    amountC = [float(i) for i in amountC]
    amountN = [float(i) for i in amountN]
    
    # Put all transaction info into a single data frame
    dfTransactions = DataFrame([currency, amountC, amountN, tType, tTime, tStat],
                               ["Currency", "Amount", "USD", "Type", "Time", "Status"]).transpose()
    
    # Return data frame of transactions
    return dfTransactions 





##### Buy/sell/convert cryptocurrency ---------------------------------------------------------------------

# Function to get list of currencies available for trading
def getTradeList():
    
    # Get trading pairs from Coinbase website
    cbText = json.loads(requests.get("https://api.pro.coinbase.com/products").text)
    
    # Initialise list
    cbList = []
    
    # Get only unique USD-XXX trading pairs
    for i in range(0, len(cbText)):
        cbList.append(cbText[i]["base_currency"])
    cbList = list(set(cbList))
    cbList.sort()
    
    # Return list of currencies available for trading
    return(cbList)

# Function to get all wallet IDs available for trading
def getIDs():
    
    # Initialise list
    ids = []
    currency = []
    
    # Get all wallet IDs
    for wallet in initAccount.data:
        ids.append(wallet["id"])
        currency.append(wallet["currency"])
        
    # Put wallet ID and currency into a data frame
    dfIDs = DataFrame([ids, currency], ["ID", "Currency"]).transpose()
    
    # Return data frame of IDs  
    return(dfIDs)

# Function to get all payment IDs available for trading
def getPmt():
    
    # Initialise lists
    accts = []
    aType = []
    
    # Get payment method ID and types
    payments = client.get_payment_methods()
    for method in payments.data:
        aType.append(method["type"])
        accts.append(method["id"])
        
    # Put payment ID and type into a data frame
    dfPmt = DataFrame([accts, aType], ["ID", "Type"]).transpose()
    
    # Return data frame of payment methods  
    return(dfPmt)

# Function to get buy/sell prices for a given crypto
def getQuote(tType1, tType2, amount, currency1, currency2 = None, push = False): 
    
    # Get wallet IDs for each currency
    id1 = initIDs.loc[initIDs["Currency"] == currency1]["ID"].values[0]
    if currency2 not in [None, ""]:
        id2 = initIDs.loc[initIDs["Currency"] == currency2]["ID"].values[0]
        
    # Get payment method IDs
    bank = initPmt.loc[initPmt["Type"] == "ach_bank_account"]["ID"].values[0]
    fiat = initPmt.loc[initPmt["Type"] == "fiat_account"]["ID"].values[0]
    
    # Get quotes and store data if push is false
    if push == False:
    
        # Get price quote for buy
        if tType1 == "buy":
           if tType2 == "crypto":
               conf = client.buy(id1, amount = amount, quote = True,
                                 currency = currency1, payment_method = bank)
           elif tType2 == "dollar":
               conf = client.buy(id1, total = amount, quote = True,
                                 currency = "USD", payment_method = bank)    
    
        # Get price quote for sell
        if tType1 == "sell":
            if tType2 == "crypto":
                conf = client.sell(id1, amount = amount, quote = True,
                                   currency = currency1, payment_method = fiat)
            elif tType2 == "dollar":
                conf = client.sell(id1, total = amount, quote = True,
                                   currency = "USD", payment_method = fiat)
            
        # Get price quote for conversion (sell then buy)
        if tType1 == "convert":
            if tType2 == "crypto":
                conf1 = client.sell(id1, amount = amount, quote = True,
                                     currency = currency1, payment_method = fiat)
            elif tType2 == "dollar":
                conf1 = client.sell(id1, total = amount, quote = True,
                                    currency = "USD", payment_method = fiat)
            conf2 = client.buy(id2, total = float(conf1["total"]["amount"]),
                               quote = True, currency = "USD", payment_method = bank)
    
        # Compile quote data
        if tType1 != "convert":
            qData = [float(conf["subtotal"]["amount"]), float(conf["fee"]["amount"]),
                     float(conf["total"]["amount"]), float(conf["unit_price"]["amount"])]
        else:
            qData = [float(conf1["subtotal"]["amount"]), float(conf1["fee"]["amount"]),
                     float(conf1["total"]["amount"]), float(conf1["unit_price"]["amount"]),
                     float(conf2["subtotal"]["amount"]), float(conf2["fee"]["amount"]),
                     float(conf2["total"]["amount"]), float(conf2["unit_price"]["amount"])]
    
        # Return quote data
        return qData
    
    # Perform trade if push is true
    elif push == True:
        
        # Execute buy order
        if tType1 == "buy":
           if tType2 == "crypto":
               client.buy(id1, amount = amount, currency = currency1, payment_method = bank)
           elif tType2 == "dollar":
               client.buy(id1, total = amount, currency = "USD", payment_method = bank)    
    
        # Execute sell order
        if tType1 == "sell":
            if tType2 == "crypto":
                client.sell(id1, amount = amount, currency = currency1, payment_method = fiat)
            elif tType2 == "dollar":
                client.sell(id1, total = amount, currency = "USD", payment_method = fiat)
            
        # Execute currency conversion
        if tType1 == "convert":
            if tType2 == "crypto":
                 client.sell(id1, amount = amount, currency = currency1, payment_method = fiat)
            elif tType2 == "dollar":
                client.sell(id1, total = amount, currency = "USD", payment_method = fiat)
            client.buy(id2, total = float(conf1["total"]["amount"]),
                       currency = "USD", payment_method = bank)

