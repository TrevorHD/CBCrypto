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
        tGran = 60
    elif tFrame == "1d":
        tStart = tEnd - 86400
        tGran = 300
    elif tFrame == "1wk":
        tStart = tEnd - 86400*7 
        tGran = 3600
    elif tFrame == "1m":
        tStart = tEnd - 86400*30
        tGran = 21600
    elif tFrame == "3m":
        tStart = tEnd - 86400*30*3
        tGran = 21600
    elif tFrame == "6m":
        tStart = tEnd - 86400*30*6
        tGran = 21600
    elif tFrame == "1yr":
        tStart = tEnd - 86400*365
        tGran = 21600
    elif tFrame == "max":
        tStart = 1375660800
        tGran = 86400

    # Activate public client
    pClient = cbpro.PublicClient()
    
    # Set number of blocks since there is a 300-point limit per block
    nBlocks = ((tEnd - tStart)/tGran + 2)/300
    
    # Set currency conversion string
    cText = currency + "-USD"
    
    # Define internal function to convert timestamp to ISO format
    def tsToISO(ts):
        tz = datetime.datetime.now().astimezone().tzinfo
        return datetime.datetime.fromtimestamp(ts, tz).isoformat()
    
    # Pull data from CoinbasePro API
    if nBlocks <= 1:    
        isodate0 = tsToISO(tStart)
        isodate1 = tsToISO(tEnd)
        data = pClient.get_product_historic_rates(cText, granularity = tGran,
                                                  start = isodate0, end = isodate1)
        data = DataFrame(data, columns = ["timestamp", "open", "high", "low", "close", "volume"])
        data = data.sort_values(by = "timestamp")
    else:
        for i in range(1, math.ceil(nBlocks) + 1):
            if i == 1:
                isodate0 = tsToISO(tStart)
                isodate1 = tsToISO(tStart + tGran*300)
                data = pClient.get_product_historic_rates(cText, granularity = tGran,
                                                          start = isodate0, end = isodate1)
                data = DataFrame(data, columns = ["timestamp", "open", "high", "low", "close", "volume"])
                data = data.sort_values(by = "timestamp")
            else:
                if i > 1 and i < nBlocks:
                    isodate0 = tsToISO(tStart + (i - 1)*tGran*300)
                    isodate1 = tsToISO(tStart + i*tGran*300)
                elif i > nBlocks:
                    isodate0 = tsToISO(tStart + (i - 1)*tGran*300)
                    isodate1 = tsToISO(tEnd)
                newdata = pClient.get_product_historic_rates(cText, granularity = tGran,
                                                             start = isodate0, end = isodate1)
                newdata = DataFrame(newdata, columns = ["timestamp", "open", "high", "low", "close", "volume"])
                newdata = newdata.sort_values(by = "timestamp")
                data = data.append(newdata, ignore_index = True)

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
    pClient = cbpro.PublicClient()
    
    # Compile current prices and price versus opening price
    d1 = {}
    cLow, cHigh, cOpen, cClose, cChange = [], [], [], [], []
    for i in range(0, len(currencyList)):
        d1["key%s" %i] = getPriceSeries(tFrame, currencyList[i])
        cLow.append(min(d1["key%s" %i]["low"]))
        cHigh.append(max(d1["key%s" %i]["high"]))
        cOpen.append(d1["key%s" %i]["open"].iloc[0])
        cClose.append(d1["key%s" %i]["close"].iloc[-1])
        cChange.append((cClose[i] - cOpen[i])/cOpen[i]*100)
    
    # Put data into dataframe    
    data = pandas.DataFrame([[tFrame]*len(currencyList), currencyList, cLow, cHigh, cOpen, cClose, cChange],
                            ["Timeframe", "Currency", "Low", "High", "Open", "Close", "Return"]).transpose()
    
    # Return dataframe
    return data

# Function that returns all currency movement over 24 hours
def getCurrentMovers():

    # Activate public client and get currency info
    pClient = cbpro.PublicClient()
    cInfo = pClient.get_currencies()
    
    # Initialise lists
    currencyList1 = []
    currencyList2 = []
    cOpen, cClose, cChange = [], [], []
    
    # Calculate 24h percent change for each currency
    for i in range(0, len(cInfo)):
        currencyList1.append(cInfo[i]["id"])
        currencyList2.append(cInfo[i]["id"])
        try:
            if currencyList1[i] in ["DOGE", "ADA", "DOT", "LINK", "UNI", "LTC", "ETH", "BTC"]:
                cVals = mData[1].loc[mData[1]["Currency"] == currencyList1[i]]
                cChange.append(float(cVals["Return"]))
                cOpen.append(float(cVals["Open"]))
                cClose.append(float(cVals["Close"]))
            else:
                cVals = pClient.get_product_24hr_stats(currencyList1[i] + "-USD")
                cChange.append((float(cVals["last"]) - float(cVals["open"]))/float(cVals["open"])*100)
                cOpen.append(float(cVals["open"]))
                cClose.append(float(cVals["last"]))
        except ZeroDivisionError:
            del currencyList2[-1]
            pass
        except KeyError:
            del currencyList2[-1]
            pass
        
    # Create data frame of all currencies
    data = DataFrame([currencyList2, cOpen, cClose, cChange],
                     ["Currency", "Open", "Close", "Change"]).transpose()
    
    # Return data frame
    return data

# Addition to the previous function, getting only top and bottom movers
def getTopMovers(movers):
    
    # Get top and bottom performers
    dataTop = movers.sort_values("Change", ascending = False).iloc[0:10]
    dataBottom = movers.sort_values("Change").iloc[0:10]
    
    # Return new data frame
    return dataTop.append(dataBottom)





##### Generate user wallet summary ------------------------------------------------------------------------

# Function to list current holdings for each cryptocurrency
def getCurrentHoldings():
    
    # Initialise lists
    currencyList = []
    cIDs = []
    cDollar = []
    cCrypto = []
    
    # Populate lists with held currencies
    for wallet in initAccount.data:
        wIDs = wallet["id"]
        wCurrency = str(wallet["name"]).replace(" Wallet", "")
        wDollar = float(str(wallet["native_balance"]).replace("USD ", ""))
        if wDollar > 0:
            currencyList.append(wCurrency)
            cIDs.append(wIDs)
            cCrypto.append(float(str(wallet["balance"]).replace(wCurrency + " ", "")))
            cDollar.append(wDollar)
    cPercent = [x/sum(cDollar)*100 for x in cDollar]
    data = DataFrame([cIDs, currencyList, cCrypto, cDollar, cPercent],
                     ["ID", "Currency", "Crypto", "Amount", "Percent"]).transpose() 
    
    # Sort holdings by cash value
    data = data.sort_values("Amount", ascending = False).reset_index(drop = True)
    
    # Return dataframe of currency holdings
    return data

# Function to list current holdings for only a single cryptocurrency (or trading pair)
def getSpecificCurrency(currency1, currency2 = None):
    
    # Initialise lists
    cHold = []
    
    # Get crypto and native balance for each specified currency
    cHold1 = client.get_account(initIDs.loc[initIDs["Currency"] == currency1]["ID"].values[0])
    cHold.append(cHold1["balance"]["amount"])
    cHold.append(cHold1["native_balance"]["amount"])
    if currency2 not in [None, ""]:
        cHold2 = client.get_account(initIDs.loc[initIDs["Currency"] == currency2]["ID"].values[0])
        cHold.append(cHold2["balance"]["amount"])
        cHold.append(cHold2["native_balance"]["amount"])
        
    # Return list of crypto and native balances
    return cHold

# Function to list user's transaction history    
def getTransactionHistory():

    # Initialise lists
    currencyList = []
    tCrypto = []
    tDollar = []
    tType = []
    tTime = []
    tStat = []
    
    # Get transactions for each wallet
    for i in list(initIDs["ID"].values):
        events = client.get_transactions(i)
        pbUpdate()
        for j in events.data:
            currencyList.append(j["amount"]["currency"])
            tCrypto.append(j["amount"]["amount"])
            tDollar.append(j["native_amount"]["amount"])
            tType.append(j["type"])
            tTime.append(j["created_at"])
            tStat.append(j["status"])
            
    # Convert amount and native amount to floats
    tCrypto = [float(i) for i in tCrypto]
    tDollar = [float(i) for i in tDollar]
    
    # Put all transaction info into a single data frame
    data = DataFrame([currencyList, tCrypto, tDollar, tType, tTime, tStat],
                     ["Currency", "Amount", "USD", "Type", "Time", "Status"]).transpose()
    
    # Return data frame of transactions
    return data 





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
    cIDs = []
    currencyList = []
    
    # Get all wallet IDs
    for wallet in initAccount.data:
        cIDs.append(wallet["id"])
        currencyList.append(wallet["currency"])
        
    # Put wallet ID and currency into a data frame
    data = DataFrame([cIDs, currencyList], ["ID", "Currency"]).transpose()
    
    # Return data frame of IDs  
    return(data)

# Function to get all payment IDs available for trading
def getPmt():
    
    # Initialise lists
    aIDs = []
    aType = []
    
    # Get payment method ID and types
    payments = client.get_payment_methods()
    for method in payments.data:
        aIDs.append(method["id"])
        aType.append(method["type"])
        
    # Put payment ID and type into a data frame
    data = DataFrame([aIDs, aType], ["ID", "Type"]).transpose()
    
    # Return data frame of payment methods  
    return(data)

# Function to get buy/sell prices for a given crypto, or perform trades            
def getQuote(tType1, tType2, amount, currency1, currency2 = None, push = False):
    
    # Get prices for each currency
    cPrice1 = oData.loc[oData["Currency"] == currency1]["Close"].values[0]
    if currency2 not in [None, ""]:
        cPrice2 = oData.loc[oData["Currency"] == currency2]["Close"].values[0]
    
    # Internal function to calculate fees
    def getFee(amount, cPrice):
        if tType2 == "crypto":
            nAmount = amount*cPrice
        elif tType2 == "dollar":
            nAmount = amount
        if nAmount <= 10.00:
            nFee = 0.99
        elif 10.00 < nAmount <= 25.00:
            nFee = 1.49
        elif 25.00 < nAmount <= 50.00:
            nFee = 1.99
        elif 50.00 < nAmount <= 200.00:
            nFee = 2.99
        elif nAmount > 200.00:
            nFee = nAmount*0.0149
        return(round(nFee, 2))
    
    # Execute buy order
    if tType1 == "buy":
        pFee = getFee(amount, cPrice1)
        if tType2 == "crypto":
            pList = [round(amount*cPrice1, 2), pFee, round(amount*cPrice1 + pFee, 2), cPrice1]
        elif tType2 == "dollar":
            pList = [round(amount, 2), pFee, round(amount + pFee, 2), cPrice1]
    
    # Execute sell order
    elif tType1 == "sell":
        pFee = getFee(amount, cPrice1)
        if tType2 == "crypto":
            pList = [round(amount*cPrice1, 2), pFee, round(amount*cPrice1 - pFee, 2), cPrice1]
        elif tType2 == "dollar":
            pList = [round(amount, 2), pFee, round(amount - pFee, 2), cPrice1]
    
    # Execute currency conversion
    elif tType1 == "convert":
        pFee1 = getFee(amount, cPrice1)
        if tType2 == "crypto":
            pList1 = [round(amount*cPrice1, 2), pFee1, round(amount*cPrice1 - pFee1, 2), cPrice1]
        elif tType2 == "dollar":
            pList1 = [round(amount, 2), pFee1, round(amount - pFee1, 2), cPrice1]
        pFee2 = getFee(pList1[2], cPrice2)
        pList2 = [pList1[2], pFee2, pList1[2] - pFee2, cPrice2]
    
    # Perform trade if push is true
    if push == True:   
        
        # Get wallet IDs for each currency
        id1 = initIDs.loc[initIDs["Currency"] == currency1]["ID"].values[0]
        if currency2 not in [None, ""]:
            id2 = initIDs.loc[initIDs["Currency"] == currency2]["ID"].values[0]
    
        # Get payment method IDs
        pBank = initPmt.loc[initPmt["Type"] == "ach_bank_account"]["ID"].values[0]
        pFiat = initPmt.loc[initPmt["Type"] == "fiat_account"]["ID"].values[0]
    
        # Execute buy order
        #if tType1 == "buy":
        #    client.buy(id1, total = pList1[2], currency = currency1, payment_method = pBank) 
    
        # Execute sell order
        #elif tType1 == "sell":
        #    client.sell(id1, total = pList1[2], currency = currency1, payment_method = pFiat)
            
        ## Execute currency conversion
        #elif tType1 == "convert":
        #    if tType2 == "crypto":
        #         client.sell(id1, amount = amount, currency = currency1, payment_method = pFiat)
        #    elif tType2 == "dollar":
        #        client.sell(id1, total = amount, currency = "USD", payment_method = pFiat)
        #    client.buy(id2, total = float(conf1["total"]["amount"]),
        #               currency = "USD", payment_method = pBank)
    
    # Otherwise return just a quote
    elif push == False:
        if tType1 == "convert":
            return(pList1 + pList2)
        else:
            return(pList)
    
