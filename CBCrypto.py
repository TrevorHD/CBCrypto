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
import decimal
import seaborn
import math
import time
import json





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





##### Plot price data -------------------------------------------------------------------------------------

# Function to plot value against opening value for given timeframe
def buildPlot(tFrame, currencyList):
    
    # Compile dicts of prices and price versus opening price
    d1, d2 = {}, {}
    for i in range(0, len(currencyList)):
        d1["key%s" %i] = getPriceData(tFrame, currencyList[i])
        d2["key%s" %i] = d1["key%s" %i]["mean"]/(d1["key%s" %i]["mean"][0])
     
    # Get min and max price versus opening price
    pmin, pmax = [], []
    for i in range(0, len(currencyList)):
        pmin.append(min(d2["key%s" %i]))
        pmax.append(max(d2["key%s" %i]))
    
    # Get earliest and latest available datetimes
    dmin, dmax = [], []
    for i in range(0, len(currencyList)):
        dmin.append(min(d1["key%s" %i]["datetime"]))
        dmax.append(max(d1["key%s" %i]["datetime"]))
                
    # Get difference between min and max price versus opening price, for scaling purposes
    mmDiff = math.ceil((max(pmax) - min(pmin))*100/5)*5/100
    
    # Set scaling based on difference between max and min price versus opening price
    if mmDiff > 0.5:
        lPrice = math.floor(min(pmin)*100/5)*5/100
    else:
        lPrice = math.floor(min(pmin)*100)/100
    
    # Generate colour palette
    # Will later use pre-defined colours for each currency
    colours = seaborn.color_palette("tab10", len(currencyList))
    
    # Get current time zone
    tz = datetime.datetime.now().astimezone().tzinfo
    
    # Set axis time format depending on timeframe
    if tFrame == "1hr":
        formatter = matplotlib.dates.DateFormatter("%H:%M", tz)
        intvMj = matplotlib.dates.MinuteLocator(interval = 10)
        intvMi = matplotlib.dates.MinuteLocator(interval = 1)
    elif tFrame == "1d":
        formatter = matplotlib.dates.DateFormatter("%H:%M", tz)
        intvMj = matplotlib.dates.HourLocator(interval = 4)
        intvMi = matplotlib.dates.HourLocator(interval = 1)
    elif tFrame == "1wk":
        formatter = matplotlib.dates.DateFormatter("%m/%d", tz)
        intvMj = matplotlib.dates.DayLocator(interval = 1)
        intvMi = matplotlib.dates.HourLocator(interval = 4)
    elif tFrame == "1m":
        formatter = matplotlib.dates.DateFormatter("%m/%d", tz)
        intvMj = matplotlib.dates.DayLocator(interval = 7)
        intvMi = matplotlib.dates.DayLocator(interval = 1)
    elif tFrame == "3m":
        formatter = matplotlib.dates.DateFormatter("%m/%d", tz)
        intvMj = matplotlib.dates.DayLocator(interval = 14)
        intvMi = matplotlib.dates.DayLocator(interval = 1)
    elif tFrame == "6m":
        formatter = matplotlib.dates.DateFormatter("%m/%d", tz)
        intvMj = matplotlib.dates.MonthLocator(interval = 1)
        intvMi = matplotlib.dates.DayLocator(interval = 7)
    elif tFrame == "1yr":
        formatter = matplotlib.dates.DateFormatter("%m/%Y", tz)
        intvMj = matplotlib.dates.MonthLocator(interval = 2)
        intvMi = matplotlib.dates.DayLocator(interval = 7)
    elif tFrame == "max":
        formatter = matplotlib.dates.DateFormatter("%m/%Y", tz)
        intvMj = matplotlib.dates.YearLocator()
        intvMi = matplotlib.dates.MonthLocator(interval = 1)
    
    # Plot value relative to opening value
    fig = pyplot.figure(figsize = (9, 6))
    whitespace = fig.add_axes([0, 0, 1, 1])
    whitespace.axis("off")
    ax = fig.add_axes([0.10, 0.06, 0.85, 0.90])
    for i in range(0, len(currencyList)):
        ax.plot(d1["key%s" %i]["datetime"], d2["key%s" %i], linestyle = "-",
                    linewidth = 1.2, label = currencyList[i], color = colours[i])
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_major_locator(intvMj)
    ax.xaxis.set_minor_locator(intvMi)
    ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.2f}"))
    if mmDiff > 0.5:
        ax.yaxis.set_ticks(linspace(lPrice, lPrice + mmDiff, 6))
        ax.set_ylim([lPrice - mmDiff*0.1, (lPrice + mmDiff + mmDiff*0.1)])
    else:
        ax.yaxis.set_ticks(linspace(lPrice, lPrice + mmDiff, 6))
        ax.set_ylim([lPrice - mmDiff*0.1, (lPrice + mmDiff + mmDiff*0.1)])
    ax.set_xlim(min(dmin), max(dmax))
    ax.tick_params(length = 5, width = 1.5, axis = "both", which = "major", labelsize = 15)
    ax.axhline(y = 1, color = "black", linestyle = "--", linewidth = 0.8)

# Test the above function
buildPlot("1hr", ["BTC", "ETH", "ADA", "UNI", "LTC"])
buildPlot("1d", ["BTC", "ETH", "ADA", "UNI", "LTC"])
buildPlot("1wk", ["BTC", "ETH", "ADA", "UNI", "LTC"])
buildPlot("1m", ["BTC", "ETH", "ADA", "UNI", "LTC"])
buildPlot("3m", ["BTC", "ETH", "ADA", "UNI", "LTC"])
buildPlot("6m", ["BTC", "ETH", "ADA", "UNI", "LTC"])
buildPlot("1yr", ["BTC", "ETH", "ADA", "UNI", "LTC"])
buildPlot("max", ["BTC", "ETH", "ADA", "UNI", "LTC"])





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
                   amount = "10",
                   currency = "BTC",
                   payment_method = "83562370-3e5c-51db-87da-752af5ab9559")
    
    