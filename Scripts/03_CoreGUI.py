##### Set formatting functions ----------------------------------------------------------------------------

# Function to format transaction types and status
def ftStr(x):
    xOut = x.replace("_", " ").capitalize()
    return xOut

# Function to format currency numbers and percents
def ftNum(x, xType, dec = 2):
    
    # Set decimal place tFormat
    dFormatter = "{:." + str(dec) + "f}"
    
    # Format currency amounts
    if xType == "amount":
        xOut = dFormatter.format(x)
    
    # Format percents
    elif xType == "percent":
        if x >= 0.01:
            xOut = dFormatter.format(x) + "%"
        else:
            xOut = "<0.01%"
    
    # Format percent changes
    elif xType == "percentC":
        if x >= 0.01:
            xOut = "+" + dFormatter.format(x) + "%"
        elif -0.01 < x < 0.01:
            xOut = "<0.01%"
        elif x <= -0.01:
            xOut = "-" + dFormatter.format(abs(x)) + "%"
    
    # Format currency values        
    elif xType == "value":
        if x >= 0.01:
            xOut = "$" + dFormatter.format(x)
        else:
            xOut = "<$0.01"
    
    # Format currency value changes
    elif xType == "valueC":
        if x >= 0.01:
            xOut = "+$" + dFormatter.format(x)
        elif -0.01 < x < 0.01:
            xOut = "<$0.01"
        elif x <= -0.01:
            xOut = "-$" + dFormatter.format(abs(x))
            
    # Return formatted number as string
    return xOut

        



##### Plot price data over a given amount of time ---------------------------------------------------------

# Function to plot price data over time
def plotSeries(dType = "overview", currencies = None, *args):
    
    # Update progress bar
    pbUpdate()
    
    # Create list of tracked currencies
    if dType == "overview":
        currencyList = ["DOGE", "ADA", "DOT", "LINK", "UNI", "LTC", "ETH", "BTC"]
    elif dType == "portfolio":
        currencyList = currencies
    else:
        if w3_tState1.get() == 3:
            currencyList = [w3_cState1.get(), w3_cState2.get()]
        else:
            currencyList = [w3_cState1.get()]
    
    # Choose timeframe depending on button selection
    if dType == "overview":
        h = w3_bState1.get() - 1
        tFrame = ["1hr", "1d", "1wk", "1m", "3m", "6m", "1yr"][h]
    elif dType == "portfolio":
        h = w3_bState2.get() - 1
        tFrame = ["1hr", "1d", "1wk", "1m", "3m", "6m", "1yr"][h]
    else:
        h = 0
        tFrame = ["1hr", "1d", "1wk", "1m", "3m", "6m", "1yr"][w3_bState3.get() - 1]
    
    # Compile dicts of prices and price versus opening price
    # If price data does not exist, record problematic currencies
    errList = []
    if dType == "overview":
        L1, L2, D1 = sData1, sData2, mData
    elif dType == "portfolio":
        L1, L2 = hData1, hData2
    else:
        d1, d2 = {}, {}
        for i in range(0, len(currencyList)):
            try:
                d1["key%s" %i] = getPriceSeries(tFrame, currencyList[i])
                d2["key%s" %i] = d1["key%s" %i]["mean"]/(d1["key%s" %i]["mean"][0])
            except KeyError:
                errList.append(currencyList[i])
                del d1["key%s" %i]
                pass
        L1, L2 = [d1], [d2]  
    
    # Get min and max price versus opening price
    # Force axis values when no data is plotted
    pMin, pMax = [], []
    for i in range(0, len(currencyList)):
        try:
            pMin.append(min(L2[h]["key%s" %i]))
            pMax.append(max(L2[h]["key%s" %i]))
        except KeyError:
            pass
        except ValueError:
            pass
    if pMin == pMax == []:
        pMin, pMax = [0.98], [1.03]
    
    # Get earliest and latest available datetimes
    dMin, dMax = [], []
    for i in range(0, len(currencyList)):
        try:
            dMin.append(min(L1[h]["key%s" %i]["datetime"]))
            dMax.append(max(L1[h]["key%s" %i]["datetime"]))
        except KeyError:
            pass
        except ValueError:
            pass
                
    # Get difference between min and max price versus opening price, for scaling purposes
    mmDiff = math.ceil((max(pMax) - min(pMin))*100/5)*5/100
    
    # Set scaling based on difference between max and min price versus opening price
    if mmDiff > 0.5:
        lPrice = math.floor(min(pMin)*100/5)*5/100
    else:
        lPrice = math.floor(min(pMin)*100)/100
    
    # Generate colour palette
    if dType == "overview":
        colourList = ["#ed9909", "#e2ed09", "#73ed09", "#09e5ed", "#096ced", "#b809ed", "#f947ff", "#ed098a"]
    elif dType == "portfolio":
        colourList = seaborn.color_palette("tab10", len(currencies))
    elif dType == "trade":
        colourList = ["#b809ed", "#09e5ed"]
    
    # Get current time zone
    tz = datetime.datetime.now().astimezone().tzinfo
    
    # Set axis time format depending on timeframe
    # Force axis values and timescale when no data is plotted
    if tFrame == "1hr":
        tDelta = timedelta(hours = 1)
        tFormat = matplotlib.dates.DateFormatter("%H:%M", tz)
        intvMj = matplotlib.dates.MinuteLocator(interval = 10)
        intvMi = matplotlib.dates.MinuteLocator(interval = 1)
    elif tFrame == "1d":
        tDelta = timedelta(hours = 24)
        tFormat = matplotlib.dates.DateFormatter("%H:%M", tz)
        intvMj = matplotlib.dates.HourLocator(interval = 4)
        intvMi = matplotlib.dates.HourLocator(interval = 1)
    elif tFrame == "1wk":
        tDelta = timedelta(days = 7)
        tFormat = matplotlib.dates.DateFormatter("%m/%d", tz)
        intvMj = matplotlib.dates.DayLocator(interval = 1)
        intvMi = matplotlib.dates.HourLocator(interval = 4)
    elif tFrame == "1m":
        tDelta = timedelta(days = 30)
        tFormat = matplotlib.dates.DateFormatter("%m/%d", tz)
        intvMj = matplotlib.dates.DayLocator(interval = 7)
        intvMi = matplotlib.dates.DayLocator(interval = 1)
    elif tFrame == "3m":
        tDelta = timedelta(days = 90)
        tFormat = matplotlib.dates.DateFormatter("%m/%d", tz)
        intvMj = matplotlib.dates.DayLocator(interval = 14)
        intvMi = matplotlib.dates.DayLocator(interval = 1)
    elif tFrame == "6m":
        tDelta = timedelta(days = 180)
        tFormat = matplotlib.dates.DateFormatter("%m/%d", tz)
        intvMj = matplotlib.dates.MonthLocator(interval = 1)
        intvMi = matplotlib.dates.DayLocator(interval = 7)
    elif tFrame == "1yr":
        tDelta = timedelta(days = 365)
        tFormat = matplotlib.dates.DateFormatter("%m/%Y", tz)
        intvMj = matplotlib.dates.MonthLocator(interval = 2)
        intvMi = matplotlib.dates.DayLocator(interval = 7)
    elif tFrame == "max":
        tFormat = matplotlib.dates.DateFormatter("%m/%Y", tz)
        intvMj = matplotlib.dates.YearLocator()
        intvMi = matplotlib.dates.MonthLocator(interval = 1)
    if dMax == dMin == []:
        dMax = [datetime.datetime.now(tz)]
        dMin = [datetime.datetime.now(tz) - tDelta]
    
    # Initialise plot
    if dType == "overview":
        fig1 = pyplot.figure(1, facecolor = "#33393b")
    elif dType == "portfolio":
        fig1 = pyplot.figure(4, facecolor = "#33393b")
    elif dType == "trade":
        fig1 = pyplot.figure(8, facecolor = "#33393b")
    pyplot.clf()
    whitespace = fig1.add_axes([0, 0, 1, 1])
    whitespace.axis("off")
    ax1 = fig1.add_axes([0.10, 0.06, 0.85, 0.90])
    
    # Plot value relative to opening value for each currency
    # Do not plot if no data exists
    for i in range(0, len(currencyList)):
        try:
            ax1.plot(L1[h]["key%s" %i]["datetime"], L2[h]["key%s" %i], linestyle = "-",
                     linewidth = 1.2, label = currencyList[i], color = colourList[i])
        except KeyError:
            pass
    if len(errList) > 0 and dType == "trade":
        errText = "*" + " and ".join(errList) + " missing price data"
        ax1.text(0.01, 0.96, errText, color = "white", fontsize = 12, transform = ax1.transAxes)
        
    # Format plot axes
    ax1.xaxis.set_major_formatter(tFormat)
    ax1.xaxis.set_major_locator(intvMj)
    ax1.xaxis.set_minor_locator(intvMi)
    ax1.yaxis.set_major_formatter(StrMethodFormatter("{x:,.2f}"))
    if mmDiff > 0.5:
        ax1.yaxis.set_ticks(linspace(lPrice, lPrice + mmDiff, 6))
        ax1.set_ylim([lPrice - mmDiff*0.1, (lPrice + mmDiff + mmDiff*0.1)])
    else:
        ax1.yaxis.set_ticks(linspace(lPrice, lPrice + mmDiff, 6))
        ax1.set_ylim([lPrice - mmDiff*0.1, (lPrice + mmDiff + mmDiff*0.1)])
    ax1.set_xlim(min(dMin), max(dMax))
    ax1.tick_params(length = 5, width = 1.5, axis = "both", which = "major", labelsize = 15)
    ax1.axhline(y = 1, color = "white", linestyle = "--", linewidth = 0.8)
    ax1.set_facecolor("#33393b")
    for i in ax1.spines:
        ax1.spines[i].set_color("white")
    for i in ("x", "y"):
        ax1.tick_params(axis = i, color = "white")
    for i in ax1.get_yticklabels():
        i.set_color("white")
    for i in ax1.get_xticklabels():
        i.set_color("white")
    
    # Create TkInter canvas with Matplotlib figure
    pyplot.gcf().canvas.draw()
    
    # Plot price data
    if dType == "overview":
    
        # Get price data for currencies in previous plot; format and convert to lists
        currencyList = list(D1[h]["Currency"])
        cLow = [ftNum(x, "value", 2) for x in list(D1[h]["Low"])]
        cHigh = [ftNum(x, "value", 2) for x in list(D1[h]["High"])]
        cOpen = [ftNum(x, "value", 2) for x in list(D1[h]["Open"])]
        cClose = [ftNum(x, "value", 2) for x in list(D1[h]["Close"])]
        cChange = [x for x in list(D1[h]["Return"])]
        
        # Get current price as fraction of maximum for each currency
        cRange = []
        for i in range(0, 8):
            cRange.append(list(L1[h]["key%s" %i]["mean"])[-1]/list(D1[h]["High"])[i])
        
        # Format text colour and sign depending on value
        colourList = ["red" if x < 0 else "green" for x in cChange]
        cChange = [ftNum(x, "percentC", 2) for x in cChange]
        
        # Get hyphenated timeframe text
        fText = "-".join([x for x in re.split("([a-z]{0,2})", tFrame) if x != ""]) + " Range"

        # Plot price data as text
        fig2 = pyplot.figure(2)
        pyplot.clf()
        pyplot.scatter([0.04]*8, [0.913/8*x + 0.03 for x in list(range(0, 8))], s = 80, marker = "s",
                       color = ["#ed9909", "#e2ed09", "#73ed09", "#09e5ed", "#096ced", "#b809ed", "#f947ff", "#ed098a"])
        pyplot.scatter([0.79 + 0.17*x for x in cRange], [0.913/8*x + 0.06 for x in range(0, 8)],
                       s = 40, marker = "s", color = "white")
        pyplot.axis("off")
        pyplot.tight_layout()
        ax2 = pyplot.gca()
        ax2.set_xlim(0, 1)
        ax2.set_ylim(0, 1)
        for i in range(0, 8):
            ax2.axhline(xmin = 0.79, xmax = 0.962, y = 0.913/8*i + 0.06, color = "white", linewidth = 0.8)
            for j in range(0, 4):
                ax2.text([0.354, 0.532, 0.709, 0.963][j], 0.95, ["Open", "Close", "Change", fText][j],
                         horizontalalignment = "right", color = "white", fontsize = 20)
            ax2.text(0.082, 0.913/8*i, currencyList[i], color = colourList[i],
                     fontsize = 20, horizontalalignment = "left")
            ax2.text(0.354, 0.913/8*i, cOpen[i], color = colourList[i],
                     fontsize = 20, horizontalalignment = "right")
            ax2.text(0.532, 0.913/8*i, cClose[i], color = colourList[i],
                     fontsize = 20, horizontalalignment = "right")
            ax2.text(0.709, 0.913/8*i, cChange[i], color = colourList[i],
                     fontsize = 20, horizontalalignment = "right")
            ax2.text(0.790, 0.913/8*i + 0.005, cLow[i], color = "white",
                     fontsize = 8, horizontalalignment = "left")
            ax2.text(0.963, 0.913/8*i + 0.005, cHigh[i], color = "white",
                     fontsize = 8, horizontalalignment = "right")
        
        # Create TkInter canvas with Matplotlib figure
        pyplot.gcf().canvas.draw()





##### Plot information on top and bottom movers -----------------------------------------------------------
    
# Function to plot top and bottom movers  
def plotMovers():
    
    # Update progress bar
    pbUpdate()
        
    # Convert movement data to lists, then format
    currencyList = list(pData["Currency"])
    cChange = list(pData["Change"])
    cOpen = [ftNum(x, "value", 3) for x in list(pData["Open"])]
    cClose = [ftNum(x, "value", 3) for x in list(pData["Close"])]
    
    # Reverse data so that most extreme movement is listed first
    currencyList.reverse();
    cChange.reverse();
    cOpen.reverse()
    cClose.reverse()
    
    # Format text colour and sign depending on value
    colourList = ["red" if x < 0 else "green" for x in cChange]
    cChange = [ftNum(x, "percentC", 2) for x in cChange]
    
    # Determine y-coordinates for plotting
    yTop = [0.32/10*x + 0.54 for x in range(0, 10)]
    yBottom = [0.32/10*x + 0.02 for x in range(0, 10)]
    
    # Plot movement data as text
    fig = pyplot.figure(3)
    pyplot.clf()
    pyplot.axis("off")
    pyplot.tight_layout()
    ax = pyplot.gca()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    for i in range(0, 2):
        ax.text(0.029, [0.940, 0.420][i], ["Top", "Bottom"][i] + " 24-Hour Movers",
                color = "white", fontsize = 35, horizontalalignment = "left")
        for j in range(0, 3):
            ax.text([0.433, 0.711, 0.968][j], [0.874, 0.354][i], ["Open", "Close", "Change"][j],
                    horizontalalignment = "right", color = "white", fontsize = 20)
    for i in range(0, 20):
        ax.text(0.029, (yBottom + yTop)[i], currencyList[i], color = colourList[i],
                fontsize = 18, horizontalalignment = "left")
        ax.text(0.433, (yBottom + yTop)[i], cOpen[i], color = colourList[i],
                fontsize = 18, horizontalalignment = "right")
        ax.text(0.711, (yBottom + yTop)[i], cClose[i], color = colourList[i],
                fontsize = 18, horizontalalignment = "right")
        ax.text(0.968, (yBottom + yTop)[i], cChange[i], color = colourList[i],
                fontsize = 18, horizontalalignment = "right")
        
    # Create Tkinter canvas with Matplotlib figure
    pyplot.gcf().canvas.draw()





##### Plot information on user's current holdings ---------------------------------------------------------

# Function to plot user's current holdings   
def plotHoldings():
    
    # Update progress bar
    pbUpdate()
    
    # Get current holdings for each cryptocurrency
    hVals = getCurrentHoldings()
    hLength = len(hVals)
    
    # Set labels as blank for curriencies with small holdings
    hLabs = ["" if hVals["Percent"][x] < 3 else hVals["Currency"][x] for x in range(0, hLength)]
    
    # Set colour palette
    colourList = seaborn.color_palette("tab10", len(hLabs))
    
    # Generate donut plot
    fig1 = pyplot.figure(5, facecolor = "#33393b")
    pyplot.clf()
    pyplot.pie(hVals["Amount"], labels = hLabs, colors = colourList,
               textprops = {"color" : "w"}, radius = 1.2, startangle = 60)
    pyplot.gcf().gca().add_artist(pyplot.Circle((0, 0), 0.7, color = "#33393b"))
    pyplot.gcf().text(0.5, 0.5, "$" + "{:.2f}".format(sum(hVals["Amount"])), color = "white",
                      fontsize = 24, horizontalalignment = "center")
    pyplot.subplots_adjust(left = 0.1, right = 0.9, top = 0.9, bottom = 0.1)
    
    # Create TkInter canvas with Matplotlib figure
    pyplot.gcf().canvas.draw()
    
    # Get currency list
    currencyList = list(hVals["Currency"])
    
    # Calculate cost basis and total return for each currency
    cBasis, cReturn = [], []
    for i in range(0, len(currencyList)):
        ftHist = tHist.loc[(tHist["Currency"] == currencyList[i]) & (tHist["Type"].isin(["buy", "trade"])) & (tHist["Amount"] > 0)]
        cBasis.append(sum(ftHist["USD"])/sum(ftHist["Amount"]))
        cReturn.append((list(hVals["Amount"])[i]/(cBasis[i]*list(hVals["Crypto"])[i]) - 1)*100)
    
    # Get current prices and 24-hour returns for each currency
    cPrice, cReturn1D = [], []
    for i in range(0, len(currencyList)):
        cPrice.append(float(oData.loc[oData["Currency"] == currencyList[i]]["Close"]))
        cReturn1D.append(float(oData.loc[oData["Currency"] == currencyList[i]]["Change"]))
        
    # Format holdings data
    cCrypto = [ftNum(x, "amount", 5) for x in list(hVals["Crypto"])]
    cDollar = [ftNum(x, "value", 2) for x in list(hVals["Amount"])]
    cPercent = [ftNum(x, "percent", 2) for x in list(hVals["Percent"])]
    cBasis = [ftNum(x, "value", 2) + "/unit" for x in cBasis]
    cPrice = [ftNum(x, "value", 2) + "/unit" for x in cPrice]
    cReturn = [ftNum(x, "percentC", 2) for x in cReturn]
    cReturn1D = [ftNum(x, "percentC", 2) for x in cReturn1D]
    
    # Reverse holdings data for plotting compatibility
    currencyList.reverse()
    colourList.reverse()
    cCrypto.reverse()
    cDollar.reverse()
    cPercent.reverse()
    cBasis.reverse()
    cPrice.reverse()
    cReturn.reverse()
    cReturn1D.reverse()
    
    # Plot current holdings as text
    fig2 = pyplot.figure(7)
    pyplot.clf()
    pyplot.scatter([0.025]*hLength, [x/(hLength + 1) + 0.029 for x in list(range(0, hLength))],
                   color = colourList, s = 80, marker = "s")
    pyplot.axis("off")
    pyplot.tight_layout()
    ax2 = pyplot.gca()
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    for i in range(0, hLength):
        for j in range(0, 8):
            ax2.text([0.050, 0.217, 0.327, 0.437, 0.593, 0.747, 0.880, 0.999][j], 0.95, 
                     ["", "Amount", "Value", "Percent", "Current Price", "Cost Basis", "24-hr Return", "Total Return"][j],
                     color = "white", fontsize = 20,
                     horizontalalignment = ["left", "right", "right", "right", "right", "right", "right", "right"][j])
        ax2.text(0.050, 0.9/hLength*i, currencyList[i], color = "white",
                 fontsize = 20, horizontalalignment = "left")
        ax2.text(0.217, 0.9/hLength*i, cCrypto[i], color = "white",
                 fontsize = 20, horizontalalignment = "right")
        ax2.text(0.327, 0.9/hLength*i, cDollar[i], color = "white",
                 fontsize = 20, horizontalalignment = "right")
        ax2.text(0.437, 0.9/hLength*i, cPercent[i], color = "white",
                 fontsize = 20, horizontalalignment = "right")
        ax2.text(0.593, 0.9/hLength*i, cPrice[i], color = "white",
                 fontsize = 20, horizontalalignment = "right")
        ax2.text(0.747, 0.9/hLength*i, cBasis[i], color = "white",
                 fontsize = 20, horizontalalignment = "right")
        ax2.text(0.880, 0.9/hLength*i, cReturn1D[i], color = "white",
                 fontsize = 20, horizontalalignment = "right")
        ax2.text(0.999, 0.9/hLength*i, cReturn[i], color = "white",
                 fontsize = 20, horizontalalignment = "right")
        
    # Create TkInter canvas with Matplotlib figure
    pyplot.gcf().canvas.draw()
    
    # Define internal functions to read and write user data from file
    def getBalTime():
        return ["{:.2f}".format(sum(hVals["Amount"])),
                datetime.datetime.now().strftime("%m/%d/%Y %H:%M")]
    def datRead():
        temp = open("UserData.txt", "r+")
        dPrevious = temp.read().splitlines()
        temp.close()
        return dPrevious
    def datWrite():
        dCurrent = getBalTime()
        temp = open("UserData.txt", "w")
        temp.writelines([dCurrent[0] + "\n", dCurrent[1] + "\n"])
        temp.close()
    
    # Get portfolio balance and time from last refresh
    # If first time running, create file and perform this operation
    try:
        dPrevious = datRead()
    except FileNotFoundError:
        datWrite()
        dPrevious = datRead()
    dCurrent = getBalTime()
    datWrite()
    bPrevious, tPrevious = float(dPrevious[0]), dPrevious[1]
    bCurrent, tCurrent = float(dCurrent[0]), dCurrent[1]
    
    # Get change and percent change in portfolio value since last update
    bChange1 = bCurrent - bPrevious
    bChange2 = bChange1/bPrevious*100
    
    # Format change and percent change for text
    bChange1 = ftNum(bChange1, "valueC", 2)
    bChange2 = ftNum(bChange2, "percentC", 2)
    
    # Plot portfolio balance
    fig3 = pyplot.figure(6)
    pyplot.clf()
    pyplot.axis("off")
    pyplot.tight_layout()
    ax3 = pyplot.gca()
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)
    ax3.text(0.99, 0.47, bChange1 + " (" + bChange2 + ") change in portfolio value since last update",
             color = "white", fontsize = 14, horizontalalignment = "right")
    
    # Create TkInter canvas with Matplotlib figure
    pyplot.gcf().canvas.draw()





##### Plot information on user's transaction history ---------------------------------------------------------

# Function to plot user's transaction history
def plotTransactions(tHist, ref = False):
    
    # Update progress bar
    pbUpdate()
    
    # Get transaction history again if refeshing
    if ref == True:
        tHist = getTransactionHistory()
    
    # Get page number
    pNum = thMaxPage - w3_sState.get() + 1
    
    # Number transactions by chronological order
    # Subset depending on page number
    tNum = list(range(1, len(tHist) + 1))
    tNum.reverse()
    tNum = tNum[((pNum - 1)*25):(pNum*25)]
    
    # Change time string to datetime, convert from UTC to local, then format appropriately
    tHist["Time"] = [dp.parse(x) for x in list(tHist["Time"])]
    tHist["time"] = [x.replace(tzinfo = datetime.datetime.now().astimezone().tzinfo) for x in list(tHist["Time"])]
    tHist["Time"] = [x.strftime("%m/%d/%Y %H:%M:%S") for x in list(tHist["Time"])]
    
    # Format transaction types and status
    tHist["Type"] = [ftStr(x) for x in list(tHist["Type"])]
    tHist["Status"] = [ftStr(x) for x in list(tHist["Status"])]
    
    # Sort transactions by date and time
    # Subset depending on page number
    tHist = tHist.sort_values(by = "Time", ascending = False)
    tHist = tHist.iloc[((pNum - 1)*25):(pNum*25)]
    
    # Limit data to 25 entries per page
    pageLength = len(tHist)

    # Create lists of transaction stats
    currencyList = list(tHist["Currency"])
    tCrypto = [ftNum(x, "amount", 4) for x in list(tHist["Amount"])]
    tDollar = [ftNum(x, "valueC", 2) for x in list(tHist["USD"])]
    tType = list(tHist["Type"])
    tTime = list(tHist["Time"])
    tStat = list(tHist["Status"])
    
    # Plot transaction stats as text
    fig = pyplot.figure(10)
    pyplot.clf()
    pyplot.axis("off")
    pyplot.tight_layout()
    ax = pyplot.gca()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    for j in range(0, pageLength):
        for k in range(0, 6):
            ax.text([0.075, 0.285, 0.422, 0.620, 0.820, 0.983][k], 25/26, 
                    ["Time Initiated", "Status", "Transaction Type", "Currency", "Amount", "USD Amount"][k],
                    horizontalalignment = ["left", "left", "left", "left", "right", "right"][k],
                    color = "white", fontsize = 13)
        ax.text(0.017, 24/26 - j/26, tNum[j], color = "white",
                fontsize = 12, horizontalalignment = "left")
        ax.text(0.075, 24/26 - j/26, tTime[j], color = "white",
                fontsize = 12, horizontalalignment = "left")
        ax.text(0.285, 24/26 - j/26, tStat[j], color = "white",
                fontsize = 12, horizontalalignment = "left")
        ax.text(0.422, 24/26 - j/26, tType[j], color = "white",
                fontsize = 12, horizontalalignment = "left")
        ax.text(0.620, 24/26 - j/26, currencyList[j], color = "white",
                fontsize = 12, horizontalalignment = "left")
        ax.text(0.820, 24/26 - j/26, tCrypto[j], color = "white",
                fontsize = 12, horizontalalignment = "right")
        ax.text(0.983, 24/26 - j/26, tDollar[j], color = "white",
                fontsize = 12, horizontalalignment = "right")
        
    # Create TkInter canvas with Matplotlib figure
    pyplot.gcf().canvas.draw()





##### Plot information on trade orders --------------------------------------------------------------------

# Function to plot trade orders
def plotTrade(push = False):
    
    # Update progress bar
    pbUpdate()
    
    # Convert state indicators to acceptable arguments for getQuote
    currency1 = w3_cState1.get()
    currency2 = w3_cState2.get()
    if w3_eState1.get() == "":
        cText1, cText2 = currency2, currency1
        aText = w3_eState2.get()
        cIndex = 2
    elif w3_eState2.get() == "":
        cText1, cText2 = currency1, currency2
        aText = w3_eState1.get()
        cIndex = 0
    if w3_tState1.get() == 1:
        tType1 = "buy"
    elif w3_tState1.get() == 2:
        tType1 = "sell"
    elif w3_tState1.get() == 3:
        tType1 = "convert"
    if w3_tState2.get() == 1:
        tType2 = "dollar"
    elif w3_tState2.get() == 2:
        tType2 = "crypto"
    if aText == "" or float(aText) == 0:
        blank = True
    else:
        blank = False
    
    # If push is set to false, only get a quote and plot info
    if push == False:
    
        # Get trade order information
        if blank == False:
            tInfo = getQuote(tType1, tType2, float(aText), cText1, cText2)
        
        # Get currency owned information
        cInfo = getSpecificCurrency(currency1, currency2)
        if cText1 in cData:
            cCapDollar = float(cInfo[cIndex + 1])
        else:
            cCapDollar = -1
    
        # Get currency owned text
        oText1 = currency1 + " owned: " + ftNum(float(cInfo[0]), "amount", 4) + " ($" + cInfo[1] + ")"
        if tType1 == "convert":
            oText2 = currency2 + " owned: " + ftNum(float(cInfo[2]), "amount", 4) + " ($" + cInfo[3] + ")"
        else:
            oText2 = ""
    
        # Get trade text for given specifications
        # Reject trade if amount exceeds holdings or $10000
        failureState = 0
        eText = ""
        if blank == False:
            try:
                if tType1 == "buy":
                    if 1 <= tInfo[2] < 10000:
                        tText1 = "$" + ftNum(tInfo[0], "amount")
                        tText2 = "$" + ftNum(tInfo[1], "amount")
                        tText3 = "$" + ftNum(tInfo[2], "amount")
                        w3_tState3.set(0)
                    else:
                        failureState = 1
                elif tType1 == "sell":
                    if tInfo[0] <= cCapDollar:
                        if 1 <= tInfo[0] < 10000:
                            tText1 = "$" + ftNum(tInfo[0], "amount")
                            tText2 = "-$" + ftNum(tInfo[1], "amount")
                            tText3 = "$" + ftNum(tInfo[2], "amount")
                            w3_tState3.set(0)
                        elif tInfo[0] < 1:
                            failureState = 2
                        else:
                            failureState = 1
                    else:
                        if tInfo[0] >= 10000:
                            failureState = 1
                        elif tInfo[0] < 1:
                            failureState = 2
                        else:
                            failureState = 3
                elif tType1 == "convert":
                    if tInfo[0] <= cCapDollar:
                        if 1.99 <= tInfo[0] < 10000:
                            tText1 = "$" + ftNum(tInfo[0], "amount")
                            tText2 = "-$" + ftNum(tInfo[1] + tInfo[5], "amount")
                            tText3 = "$" + ftNum(tInfo[6], "amount")
                            w3_tState3.set(0)
                        elif tInfo[0] < 1.99:
                            failureState = 2
                        else:
                            failureState = 1
                    else:
                        if tInfo[0] >= 10000:
                            failureState = 1
                        elif tInfo[0] < 1:
                            failureState = 2
                        else:
                            failureState = 3  
            except coinbase.wallet.error.InvalidRequestError:
                failureState = 1
        elif blank == True:
            tText1, tText2, tText3 = "$---", "$---", "$---"
            failureState = 4
        if failureState in [1, 2, 3, 4]:
            w3_tState3.set(1)
            tText1, tText2, tText3 = "$---", "$---", "$---"
            if failureState == 1:
                eText = "Transactions of $10000 or more not supported!"
            elif failureState == 2:
                eText = "Transaction amount lower than minimum limit!"
            elif failureState == 3:
                eText = "Transaction amount exceeds current holdings!"
            elif failureState == 4:
                eText = "Transaction amount must be greater than zero!"
        
        # List disclaimer text
        dText1 = "Rates may differ at the time of transaction completion due to changes in market conditions."
        dText2 = "A detailed schedule of transaction fees can be found on Coinbase (www.coinbase.com)."
    
        # Plot trade order information as text
        fig = pyplot.figure(9)
        pyplot.clf()
        pyplot.axis("off")
        pyplot.tight_layout()
        ax = pyplot.gca()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.text(0.430, 0.87, oText1, color = "white", fontsize = 14, horizontalalignment = "left")
        ax.text(0.430, 0.78, oText2, color = "white", fontsize = 14, horizontalalignment = "left")
        ax.text(0.430, 0.87, currency1 + " ", color = "#b809ed", fontsize = 14, horizontalalignment = "left")
        ax.text(0.430, 0.78, currency2 + " ", color = "#09e5ed", fontsize = 14, horizontalalignment = "left")
        ax.text(0.430, 0.53, "Subtotal:", color = "white", fontsize = 20, horizontalalignment = "left")
        ax.text(0.430, 0.37, "Fees:", color = "white", fontsize = 20, horizontalalignment = "left")
        ax.text(0.430, 0.21, "Total:", color = "white", fontsize = 20, horizontalalignment = "left")
        ax.text(0.430, 0.67, eText, color = "red", fontsize = 11, horizontalalignment = "left")
        ax.text(0.000, 0.05, dText1, color = "white", fontsize = 10, horizontalalignment = "left")
        ax.text(0.000, 0.00, dText2, color = "white", fontsize = 10, horizontalalignment = "left")
        ax.text(0.986, 0.53, tText1, color = "white", fontsize = 20, horizontalalignment = "right")
        ax.text(0.986, 0.37, tText2, color = "white", fontsize = 20, horizontalalignment = "right")
        ax.text(0.986, 0.21, tText3, color = "white", fontsize = 20, horizontalalignment = "right")
    
        # Create TkInter canvas with Matplotlib figure
        pyplot.gcf().canvas.draw()
    
    # If push is set to true, execute trade without plotting
    elif push == True:
        tInfo = getQuote(tType1, tType2, float(amount), cText1, cText2, push = True)

# Function to plot trade confirmation text
def plotTradeConfirmation():
    
    # Update progress bar
    pbUpdate()
    
    # Convert state indicators to text
    if w3_eState1.get() == "":
        currency1, currency2 = w3_cState2.get(), w3_cState1.get()
        aText = w3_eState2.get()
    elif w3_eState2.get() == "":
        currency1, currency2 = w3_cState1.get(), w3_cState2.get()
        aText = w3_eState1.get()
    if w3_tState1.get() == 1:
        tType1 = "Buy"
        cText1, cText2 = "USD ($)", currency1
    elif w3_tState1.get() == 2:
        tType1 = "Sell"
        cText1, cText2 = currency1, "USD ($)"
    elif w3_tState1.get() == 3:
        tType1 = "Convert"
        cText1, cText2 = currency1, currency2
        if w3_tState2.get() == 1:
            aText = "$" + aText
    
    # Plot trade order information as text
    fig = pyplot.figure(12)
    pyplot.clf()
    pyplot.axis("off")
    pyplot.tight_layout()
    ax = pyplot.gca()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    for i in range(0, 4):
        ax.text(0.38, 0.85 - i*0.2, ["Type: " +  tType1, "Amount: " + aText,
                                     "From: " + cText1, "To: " + cText2][i],
                horizontalalignment = "left", color = "white", fontsize = 13)
    ax.text(0.045, 0.85, "Confirm?", horizontalalignment = "left", color = "white", fontsize = 13)

    # Create TkInter canvas with Matplotlib figure
    pyplot.gcf().canvas.draw()





##### Plot information on last refresh time ---------------------------------------------------------------
    
# Function to display time at which a widget was last refreshed
def plotRefresh(rActive = False):
    
    # Update progress bar
    pbUpdate()
    
    # Get current time
    tCurrent = datetime.datetime.now().strftime("%m/%d/%Y %H:%M")
    
    # Get text
    if rActive == True:
        rText = "Refreshing... Please Wait."
    else:
        if w3_fState.get() == 1:
            rText = "Previous trade failed; Last updated " + tCurrent
        else:
            rText = "Last updated " + tCurrent
        
    # Plot text
    fig = pyplot.figure(11)
    pyplot.clf()
    pyplot.axis("off")
    pyplot.tight_layout()
    ax = pyplot.gca()
    ax.set_xlim(0, 0.1)
    ax.set_ylim(0, 0.1)
    ax.text(0.1, 0.01, rText, color = "white", style = "italic",
            fontsize = 14, horizontalalignment = "right")
    
    # Create TkInter canvas with Matplotlib figure
    pyplot.gcf().canvas.draw()





##### Define GUI functions --------------------------------------------------------------------------------

# Function to run user authentication
def userAuth():
    APIKey = w1_e1.get()
    APISecret = w1_e2.get()
    try:
        global client
        client = Client(APIKey, APISecret)
        client.get_accounts()
        w1.destroy()
    except coinbase.wallet.error.AuthenticationError:
        w1_l2.configure(text = "Authentication failed!")

# Function to pull all necessary data from the API
def refreshData():
    
    # Declare variables for external use
    global initAccount
    global initIDs
    global initPmt
    global sData1
    global sData2
    global mData
    global cData
    global hData1
    global hData2
    global oData
    global pData
    global cbList
    global tHist
    global thMaxPage
    
    # Initialise account data
    pbUpdate()
    initAccount = client.get_accounts(limit = 100)
    initIDs = getIDs()
    initPmt = getPmt()
    
    # Retrieve time series data for featured and/or held currencies
    sData1, sData2, mData, cData, hData1, hData2 = [], [], [], [], [], []
    cData = list(getCurrentHoldings()["Currency"])
    for h in range(0, 7):
        d1, d2, d3, d4 = {}, {}, {}, {}
        for i in range(0, 8):
            pbUpdate()
            d1["key%s" %i] = getPriceSeries(["1hr", "1d", "1wk", "1m", "3m", "6m", "1yr"][h],
                                            ["DOGE", "ADA", "DOT", "LINK", "UNI", "LTC", "ETH", "BTC"][i])
            d2["key%s" %i] = d1["key%s" %i]["mean"]/(d1["key%s" %i]["mean"][0])
        for i in range(0, len(cData)):
            pbUpdate()
            d3["key%s" %i] = getPriceSeries(["1hr", "1d", "1wk", "1m", "3m", "6m", "1yr"][h], cData[i])
            d4["key%s" %i] = d3["key%s" %i]["mean"]/(d3["key%s" %i]["mean"][0])
        sData1.append(d1)
        sData2.append(d2)
        hData1.append(d3)
        hData2.append(d4)
        mData.append(getPriceSummary(["1hr", "1d", "1wk", "1m", "3m", "6m", "1yr"][h],
                                     ["DOGE", "ADA", "DOT", "LINK", "UNI", "LTC", "ETH", "BTC"]))
    
    # Retrieve info on top and bottom movers
    pbUpdate()
    oData = getCurrentMovers()
    pData = getTopMovers(oData)

    # Retrieve list of currencies available for trading
    pbUpdate()
    cbList = getTradeList()

    # Retrieve transaction history and set maximum number of pages
    pbUpdate()
    tHist = getTransactionHistory()
    thMaxPage = 99 if math.ceil(len(tHist)/25) > 99 else math.ceil(len(tHist)/25)
    w3_sState.set(thMaxPage)
    
    # Filter data to ensure that currencies without price data are not available
    initIDs = initIDs[initIDs.Currency.isin(oData["Currency"].values)]
    cbList = list(set(cbList) & set(oData["Currency"].values))
    cbList.sort()

# Function to mask information when login boxes are activated
def loginFocus(eBox, *args):
    if eBox == 1:
        if w1_eState1.get() == "API Key":
            w1_e1.delete(0, "end")
            w1_e1.insert(0, "")
            w1_e1.configure(show = "*")
            w1_e1.configure(foreground = "white")
    elif eBox == 2:
        if w1_eState2.get() == "API Secret":
            w1_e2.delete(0, "end")
            w1_e2.insert(0, "")
            w1_e2.configure(show = "*")
            w1_e2.configure(foreground = "white")

# Function to unmask default text when login boxes are deactivated            
def loginUnfocus(eBox, *args):
    if eBox == 1:
        if w1_eState1.get() == "":
            w1_e1.configure(show = "", foreground = "grey")
            w1_e1.insert(0, "API Key")
    elif eBox == 2:
        if w1_eState2.get() == "":
            w1_e2.configure(show = "", foreground = "grey")
            w1_e2.insert(0, "API Secret")

# Function to reset login entry boxes
def loginReset():
    w1_e1.configure(show = "", foreground = "grey")
    w1_e1.delete(0, "end")
    w1_e1.insert(0, "API Key")
    w1_e2.configure(show = "", foreground = "grey")
    w1_e2.delete(0, "end")
    w1_e2.insert(0, "API Secret")
    
# Function to disable trade confirmation button when no input is provided
def loginDisable():
    if w1_eState1.get() == "API Key" or w1_eState2.get() == "API Secret":
        w1_b1.state(["disabled"])
        w1.update()
    else:
        w1_b1.state(["!disabled"])
        w1.update()

# Function to update progress bars
def pbUpdate():
    try:
        w2_p1.step(0.432)
        w2_pState.set(w2_p1.cget("value"))
        w2_l2.configure(text = "Loading... (" + str(round(w2_pState.get(), 2)) + "%)")
        w2.update_idletasks()
        w2.update()
    except TclError:
        if w3_rState.get() == 1:
            try:
                w3_p1.step(3)
                w3.update_idletasks()
                w3.update()
            except NameError:
                pass
            except TclError:
                pass
        else:
            pass
        
# Function to enable/disable master refresh while refreshing data
def toggleReset(action):
    if action == "disable":
        w3_rState.set(1)
        w3_b1.state(["disabled"])
        w3.update()
    elif action == "enable":
        w3_rState.set(0)
        w3_b1.state(["!disabled"])
        w3.update()
        
# Function to validate numerics in trade entry boxes
def checkKey(keyVal):
    if w3_tState2.get() == 1:
        return re.match("^(\d)*(\.)?([0-9]{0,2})?$", keyVal) is not None
    elif w3_tState2.get() == 2:
        return re.match("^(\d)*(\.)?([0-9])*$", keyVal) is not None
    
# Function to clear trade entry box when switching between dollars and crypto
def clearBox(target = None, *args):
    if target == None:
        w3_e1.delete(0, "end")
        w3_e2.delete(0, "end")
    elif target == 1:
        w3_e1.delete(0, "end")
    elif target == 2:
        w3_e2.delete(0, "end")

# Function to update trade info after the user stops typing  
afterNum = None      
def entryWait(*args, aN = afterNum):
    if aN is not None:
        w3_e1.after_cancel(aN)
    global afterNum; afterNum = w3_e1.after(300, lambda:[plotTrade(), disableTrades()])
    
# Function to place or remove second dropdown menu for currency conversion
def placeMenu():
    if w3_tState1.get() == 3:
        w3_c2.configure(state = "readonly")
        w3_e2.configure(state = "normal")
        if cbList.index(w3_cState1.get()) == len(cbList) - 1:
            w3_cState2.set(cbList[cbList.index(w3_cState1.get()) - 1])
        else:
            w3_cState2.set(cbList[cbList.index(w3_cState1.get()) + 1])
    elif w3_tState1.get() != 3:
        try:
            w3_c2.configure(state = "disabled")
            w3_cState2.set("")
            w3_e2.configure(state = "disabled")
            w3_eState2.set("")
        except NameError:
            pass

# Function to exclude selection in one dropdown menu from the other
def changeList(*args):
    w3_c1.configure(values = [x for x in cbList if x != w3_cState2.get()])
    w3_c2.configure(values = [x for x in cbList if x != w3_cState1.get()])

# Function to disable trade confirmation button when no input is provided
def disableTrades():
    if w3_eState1.get() == "" and w3_eState2.get() == "":
        w3_tState3.set(1)
    if w3_tState3.get() == 1:
        w3_b2.state(["disabled"])
        w3.update()
    else:
        w3_b2.state(["!disabled"])
        w3.update()

# Function to reset all trade radiobuttons and text fields
def resetTrades():
    w3_tState1.set(1)
    w3_tState2.set(1)

# Function to create pop-up window for trade confirmation
def tradeWindow():
    
    # Create pop-up window; set window details
    w4 = Toplevel()
    w4.title("Trade Confirmation")
    w4.geometry("300x120")
    w4.resizable(width = False, height = False)
    w4.configure(bg = "#33393b")
    w4.wm_iconphoto(False, icon)
    
    # Set up message plot and canvas
    plotTradeConfirmation()
    w4_cvs = FigureCanvasTkAgg(w4_fig, master = w4)
    w4_cvs.get_tk_widget().place(x = 0, y = 0)
    
    # Internal function to complete trande and handle exceptions
    def finishTrade():
        try:
            plotTrade(push = True)
            w3_fState.set(0)
        except:
            w3_fState.set(1)

    # Create buttons to confirm or cancel trade
    w4_b1 = ttk.Button(w4, command = lambda:[w4.destroy(), fullRefresh(rType = "trade")],
                       text = "Yes",  width = 9)
    w4_b1.place(x = 20, y = 45)
    w4_b2 = ttk.Button(w4, text = "No", command = w4.destroy, width = 9)
    w4_b2.place(x = 20, y = 80)

# Function to refresh the entire application
def fullRefresh(rType = "startup"):
    toggleReset("disable")
    plotRefresh(rActive = True)
    if rType in ["manual", "trade"]:
        resetTrades()
        clearBox()
        placeMenu()
        changeList()
        disableTrades()
        plotTrade()
    refreshData()
    plotSeries()
    plotSeries(dType = "portfolio", currencies = cData)
    plotSeries(dType = "trade")
    plotMovers()
    plotHoldings()
    plotTransactions(tHist = tHist)
    plotRefresh()
    toggleReset("enable")

