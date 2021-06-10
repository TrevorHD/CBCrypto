##### Load packages ---------------------------------------------------------------------------------------

# Import Coinbase-related packages
import math
import time
import json
import cbpro
import coinbase
from coinbase.wallet.client import Client
from coinbase.wallet.model import APIObject

# Import other packages
from matplotlib import pyplot
import dateutil.parser as dp
from datetime import datetime
from numpy import argmax
from numpy import argmin
from pandas import *





##### Get price data --------------------------------------------------------------------------------------

# Read in data from saved file on BTC prices
# This code is just a test and will likely be deprecated
chunksize = 10000
dat = read_csv("D:\Documents\coinbaseUSD.csv", iterator = True, chunksize = chunksize)
df = concat(dat, ignore_index = True)

# Create function to pull price data for a given timeframe
# Possible timeframes: 1hr, 1d (default), 1 wk, 1m, 6m, 1yr, max
def getPriceData(tFrame, currency):

    # Set end of timeframe
    tEnd = round(time.time())

    # Set beginning of timeframe and data granularity
    # Max is still a work in progress
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
    elif tFrame == "6m":
        tStart = tEnd - 86400*30*6
        gran = 21600
    elif tFrame == "1yr":
        tStart = tEnd - 86400*365
        gran = 21600
    elif tFrame == "max":
        gran = 86400

    # Activate public client
    p_client = cbpro.PublicClient()
    
    # Set number of blocks since there is a 300-point limit per block
    nBlocks = ((tEnd - tStart)/gran + 2)/300
    
    # Set currency conversion string
    ccs = currency + "-USD"
    
    # Define internal function to convert timestamp to ISO format
    def tsToISO(ts):
        return datetime.utcfromtimestamp(ts).isoformat()
    
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
    
    # Return data frame
    return data
    
# Test the above function
data = getPriceData("1yr", "BTC")
data = getPriceData("1wk", "ETH")
data = getPriceData("1d", "ADA")





##### Examine data ----------------------------------------------------------------------------------------

# Find maximum and minimum price in a rolling 30-minute interval
nums = DataFrame(columns = ["max14", "min14", "pct", "tdelta"])
for i in range(15, len(vals) - 15):
    timedelta = argmax(vals[(i - 15):(i + 15)]) - argmin(vals[(i - 15):(i + 15)])
    if timedelta < 0:
        max14 = max(vals[(i - 15):(i + 15)])
        min14 = min(vals[(i - 15):(i + 15)])
        pct = (min14 - max14)/max14*100
        newvals = DataFrame({"max14":[max14], "min14":[min14], "pct":[pct], "tdelta":[timedelta]})
        nums = nums.append(newvals, ignore_index = True)
    else:
        pass

# Plot percent change as a function of time difference between maximum and minimum    
pyplot.scatter(nums["tdelta"], nums["pct"], alpha = 0.3)





##### Wallet operations -----------------------------------------------------------------------------------

# Access client using secure keys
# Substitute API key and secret key with the user's actual key codes
client = Client("api_key", "secret_key")

# Get prices using API
# Note: this can be done like earlier without needing an API key
# Will probably remove this later
dat = client._make_api_object(client._get('v2', 'prices', 'BTC-USD', 'historic'), APIObject)

# List accounts
account = client.get_accounts()

# List current holdings for each cryptocurrency
total = 0
message = []
for wallet in account.data:
    message.append(str(wallet["name"]) + " " + str(wallet["native_balance"]) )
    value = str(wallet["native_balance"]).replace("USD", "")
    total += float(value)
message.append("Total Balance: " + "USD " + str(total))
print "\n".join(message)

# Possible algorithm for auto buys/sells:
# Set maximum
# Refresh maximum if new max is greater than old max
# Trigger sell when value drops more than __% of most recent max
# refresh minimum if new min is less than old min
# Buy again once cooldown period has expired

# The below code is not currently functional and should not be used

# Get current price
price = float(client.get_spot_price(currency_pair = "BTC-USD")["amount"])
if price > price_max:
    price_max = price
    
# Sell if current price drops more than 5% relative to recent maximum
if (price - price_max)/price_max < -0.05:
    sell = client.sell('2bbf394c-193b-5b2a-9155-3b4732659ede',
                   amount="10",
                   currency="BTC",
                   payment_method="83562370-3e5c-51db-87da-752af5ab9559")
    
    