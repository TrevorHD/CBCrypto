import coinbase
import cbpro
from coinbase.wallet.client import Client
from coinbase.wallet.model import APIObject
from matplotlib import pyplot
import dateutil.parser as dp
from datetime import datetime
from numpy import argmax
from numpy import argmin
import json

from pandas import *
chunksize = 10000
dat = read_csv("D:\Documents\coinbaseUSD.csv", iterator = True, chunksize = chunksize)
df = concat(dat, ignore_index=True)

df[df.columns[[1]]].max()

# Initialise data
public_client = cbpro.PublicClient()
data = public_client.get_product_historic_rates('BTC-USD', granularity = 60,
                                                start = "2019-01-01T13:55:00", end = "2019-01-01T18:55:00")
dataframe = DataFrame(data, columns = ['date', 'open', 'high', 'low', 'close', "test"])
dataframe = dataframe.sort_values(by = "date")

# Starting timestamp for 01 Jan 2019 00:00
datetime.utcfromtimestamp(1546350900).isoformat()

# Get data in 5-hour blocks
for i in range(1, 4140):
    ts = 1546350900 + i*5*3600
    isodate0 = datetime.utcfromtimestamp(ts - 5*3600).isoformat()
    isodate1 = datetime.utcfromtimestamp(ts).isoformat()
    newdat = public_client.get_product_historic_rates('BTC-USD', granularity = 60,
                                                start = isodate0, end = isodate1)
    newdat = DataFrame(newdat, columns = ['date', 'open', 'high', 'low', 'close', "test"])
    newdat = newdat.sort_values(by = "date")
    dataframe = dataframe.append(newdat, ignore_index = True)

dataframe['mean'] = dataframe[['open', 'close']].mean(axis = 1)

vals = dataframe['mean']

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
    
pyplot.scatter(nums["tdelta"], nums["pct"], alpha = 0.3)

# Set maximum
# Refresh maximum if new max is greater than old max
# Trigger sell when value drops more than __% of most recent max
# refresh minimum if new min is less than old min
# Buy again once cooldown period has expired

# Substitute API key and secret key with the actual codes
client = Client("api_key", "secret_key")

dat = client._make_api_object(client._get('v2', 'prices', 'BTC-USD', 'historic'), APIObject)

account = client.get_accounts()

total = 0
message = []
accounts = client.get_accounts()
for wallet in accounts.data:
    message.append(str(wallet['name']) + ' ' + str(wallet['native_balance']) )
    value = str(wallet['native_balance']).replace('USD', '')
    total += float(value)
message.append('Total Balance: ' + 'USD ' + str(total))
print '\n'.join(message)

# Sell whenever drop is grater than 5% compared to most recent maximum when CURRENCY IS HELD

price = float(client.get_spot_price(currency_pair = "BTC-USD")["amount"])
if price > price_max:
    price_max = price
    
if (price - price_max)/price_max < -0.05:
    sell = client.sell('2bbf394c-193b-5b2a-9155-3b4732659ede',
                   amount="10",
                   currency="BTC",
                   payment_method="83562370-3e5c-51db-87da-752af5ab9559")
    
    