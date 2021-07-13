##### Load packages ---------------------------------------------------------------------------------------

# Import Coinbase-related packages
import cbpro
import coinbase
from coinbase.wallet.client import Client
from coinbase.wallet.model import APIObject

# Import other packages
import matplotlib.dates
from matplotlib.ticker import StrMethodFormatter
from matplotlib import pyplot
import dateutil.parser as dp
from numpy import linspace
from numpy import argmax
from numpy import argmin
from pandas import *
import datetime
import seaborn
import math
import time





##### Get price data --------------------------------------------------------------------------------------

# Create function to pull price data for a given timeframe
# Possible timeframes: 1hr, 1d (default), 1 wk, 1m, 3m, 6m, 1yr, max
# Note: Coinbase historical data may be incomplete
def getPriceData(tFrame, currency):

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

# Function that returns top movers over 24h
def currentMovers():

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
        vals = p_client.get_product_24hr_stats(currencyList1[i] + "-USD")
        try:
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
    return(dfTop.append(dfBottom))

# Function to get current prices and return over timeframe
def priceCheck(tFrame, currencyList):
    
    # Compile current prices and price versus opening price
    d1, d2 = {}, {}
    prices, high, low, returns = [], [], [], []
    for i in range(0, len(currencyList)):
        d1["key%s" %i] = getPriceData(tFrame, currencyList[i])
        d2["key%s" %i] = d1["key%s" %i]["mean"]/(d1["key%s" %i]["mean"][0])
        prices.append(d1["key%s" %i]["mean"].iloc[-1])
        high.append(max(d1["key%s" %i]["high"]))
        low.append(min(d1["key%s" %i]["low"]))
        returns.append(d2["key%s" %i].iloc[-1])
    
    # Put data into dataframe    
    df = pandas.DataFrame([[tFrame]*5, currencyList, high, low, prices, returns],
                          ["Timeframe", "Currency", "High", "Low", "Price", "Return"]).transpose()
    
    # Return dataframe
    return df





##### Generate user wallet summary ------------------------------------------------------------------------

# Access client using secure keys
# Substitute API key and secret key with the user's actual key codes
client = Client("api_key", "api_secret")

# List current holdings for each cryptocurrency
def currentHoldings():
    
    # Get account
    account = client.get_accounts()
    
    # Initialise lists
    currency = []
    amount = []
    
    # Populate lists with held currencies
    for wallet in account.data:
        value = float(str(wallet["native_balance"]).replace("USD ", ""))
        if value > 0:
            amount.append(value)
            currency.append(str(wallet["name"]).replace(" Wallet", ""))
    pcts = [x/sum(amount) for x in amount]
    dfCurrency = DataFrame([currency, amount, pcts], ["Currency", "Amount", "Percent"]).transpose() 
    
    # Return dataframe of held currencies, sorted by value
    return(dfCurrency.sort_values("Amount", ascending = False))

# List user's transaction history    
def transactionHistory():

    # Initialise lists
    ids = []
    currency = []
    amountC = []
    amountN = []
    tType = []
    tTime = []

    # Get account
    account = client.get_accounts()
    
    # Get all wallet IDs
    for wallet in account.data:
        ids.append(wallet["id"])
    
    # Get transactions for each wallet
    for i in ids:
        events = client.get_transactions(i)
        for j in events.data:
            currency.append(j["amount"]["currency"])
            amountC.append(j["amount"]["amount"])
            amountN.append(j["native_amount"]["amount"])
            tType.append(j["type"])
            tTime.append(j["created_at"])
    
    # Put all transaction info into a single data frame
    dfTranscations = DataFrame([currency, amountC, amountN, tType, tTime],
                               ["Currency", "Amount", "USD", "Type", "Time"]).transpose()
        
   