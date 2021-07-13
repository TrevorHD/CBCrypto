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
    




##### Plot user portfolio composition ---------------------------------------------------------------------

# Generate donut plot of held currencies
def currentPlot():
    
    # Get current holdings for each cryptocurrency
    values = currentHoldings()
    total = sum(values["Percent"])
    
    # Combine currencies with small holdings into "other" category
    minor = values[values["Percent"] < 0.02]
    minorTotal = DataFrame(["OTHER", sum(minor["Amount"]), sum(minor["Amount"])/sum(values["Amount"])],
                           ["Currency", "Amount", "Percent"]).transpose()
    values = values[values["Percent"] >= 0.02].append(minorTotal)
    
    # Generate donut plot
    pyplot.pie(values["Amount"], labels = values["Currency"])
    pyplot.gcf().gca().add_artist(pyplot.Circle((0,0), 0.7, color = "white"))




##### Examine rolling trends ------------------------------------------------------------------------------

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





##### Trading code [NYI] ----------------------------------------------------------------------------------

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

