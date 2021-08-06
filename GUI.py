##### GUI To-do list --------------------------------------------------------------------------------------

# Fix progress bar
# Move refresh button and text to top-right
    # Allow refresh button to refresh everything at once
# Create login screen using API key and secret
# Fully implement trade functionality
# Add content to portfolio page
# Redo radiobutton and figure numbering to make code more clear





##### Load packages ---------------------------------------------------------------------------------------

# Import packages for GUI
from tkinter import *
from tkinter import ttk
from tkinter.font import Font
from PIL import Image
from PIL import ImageTk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg





##### Set formatting functions ----------------------------------------------------------------------------

# Function to format transaction types and status
def ftStr(x):
    xOutput = x.replace("_", " ").capitalize()
    return xOutput

# Function to format currency numbers and percents
def ftNum(x, xType, dec = 2):
    
    # Set decimal place formatter
    dFormatter = "{:." + str(dec) + "f}"
    
    # Format currency amounts
    if xType == "amount":
        xOutput = dFormatter.format(x)
    
    # Format percents
    elif xType == "percent":
        if x >= 0.01:
            xOutput = dFormatter.format(x) + "%"
        else:
            xOutput = "<0.01%"
    
    # Format percent changes
    elif xType == "percentC":
        if x >= 0.01:
            xOutput = "+" + dFormatter.format(x) + "%"
        elif -0.01 < x < 0.01:
            xOutput = "<0.01%"
        elif x <= -0.01:
            xOutput = "-" + dFormatter.format(abs(x)) + "%"
    
    # Format currency values        
    elif xType == "value":
        if x >= 0.01:
            xOutput = "$" + dFormatter.format(x)
        else:
            xOutput = "<$0.01"
    
    # Format currency value changes
    elif xType == "valueC":
        if x >= 0.01:
            xOutput = "+$" + dFormatter.format(x)
        elif -0.01 < x < 0.01:
            xOutput = "<$0.01"
        elif x <= -0.01:
            xOutput = "-$" + dFormatter.format(abs(x))
            
    # Return formatted number as string
    return xOutput

        



##### Plot price data over a given amount of time ---------------------------------------------------------

# Function to plot price data over time
def plotSeries(dType = "overview", currencies = None, *args):
    
    # Start progress bar
    #p1.update_idletasks()
    
    # Create list of tracked currencies
    if dType == "overview":
        currencyList = ["XLM", "ADA", "DOT", "UNI", "LTC", "ETH", "BTC"]
    elif dType == "portfolio":
        currencyList = currencies
    else:
        if tState1.get() == 3:
            currencyList = [cState1.get(), cState2.get()]
        else:
            currencyList = [cState1.get()]
    
    # Choose timeframe depending on button selection
    if dType == "overview":
        h = bState1.get() - 1
        tFrame = ["1hr", "1d", "1wk", "1m", "3m", "6m", "1yr"][h]
    elif dType == "portfolio":
        h = bState3.get() - 1
        tFrame = ["1hr", "1d", "1wk", "1m", "3m", "6m", "1yr"][h]
    else:
        h = 0
        tFrame = ["1hr", "1d", "1wk", "1m", "3m", "6m", "1yr"][bState2.get() - 1]
    
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
    pmin, pmax = [], []
    for i in range(0, len(currencyList)):
        try:
            pmin.append(min(L2[h]["key%s" %i]))
            pmax.append(max(L2[h]["key%s" %i]))
        except KeyError:
            pass
        except ValueError:
            pass
    if pmin == pmax == []:
        pmin, pmax = [0.98], [1.03]
    
    # Get earliest and latest available datetimes
    dmin, dmax = [], []
    for i in range(0, len(currencyList)):
        try:
            dmin.append(min(L1[h]["key%s" %i]["datetime"]))
            dmax.append(max(L1[h]["key%s" %i]["datetime"]))
        except KeyError:
            pass
        except ValueError:
            pass
                
    # Get difference between min and max price versus opening price, for scaling purposes
    mmDiff = math.ceil((max(pmax) - min(pmin))*100/5)*5/100
    
    # Set scaling based on difference between max and min price versus opening price
    if mmDiff > 0.5:
        lPrice = math.floor(min(pmin)*100/5)*5/100
    else:
        lPrice = math.floor(min(pmin)*100)/100
    
    # Generate colour palette
    if dType == "overview":
        colours = ["#ed9909", "#e2ed09", "#73ed09", "#09e5ed", "#096ced", "#b809ed", "#ed098a"]
    elif dType == "portfolio":
        colours = seaborn.color_palette("tab10", len(currencies))
    else:
        colours = ["#b809ed", "#09e5ed"]
    
    # Get current time zone
    tz = datetime.datetime.now().astimezone().tzinfo
    
    # Set axis time format depending on timeframe
    # Force axis values and timescale when no data is plotted
    if tFrame == "1hr":
        tDelta = timedelta(hours = 1)
        formatter = matplotlib.dates.DateFormatter("%H:%M", tz)
        intvMj = matplotlib.dates.MinuteLocator(interval = 10)
        intvMi = matplotlib.dates.MinuteLocator(interval = 1)
    elif tFrame == "1d":
        tDelta = timedelta(hours = 24)
        formatter = matplotlib.dates.DateFormatter("%H:%M", tz)
        intvMj = matplotlib.dates.HourLocator(interval = 4)
        intvMi = matplotlib.dates.HourLocator(interval = 1)
    elif tFrame == "1wk":
        tDelta = timedelta(days = 7)
        formatter = matplotlib.dates.DateFormatter("%m/%d", tz)
        intvMj = matplotlib.dates.DayLocator(interval = 1)
        intvMi = matplotlib.dates.HourLocator(interval = 4)
    elif tFrame == "1m":
        tDelta = timedelta(days = 30)
        formatter = matplotlib.dates.DateFormatter("%m/%d", tz)
        intvMj = matplotlib.dates.DayLocator(interval = 7)
        intvMi = matplotlib.dates.DayLocator(interval = 1)
    elif tFrame == "3m":
        tDelta = timedelta(days = 90)
        formatter = matplotlib.dates.DateFormatter("%m/%d", tz)
        intvMj = matplotlib.dates.DayLocator(interval = 14)
        intvMi = matplotlib.dates.DayLocator(interval = 1)
    elif tFrame == "6m":
        tDelta = timedelta(days = 180)
        formatter = matplotlib.dates.DateFormatter("%m/%d", tz)
        intvMj = matplotlib.dates.MonthLocator(interval = 1)
        intvMi = matplotlib.dates.DayLocator(interval = 7)
    elif tFrame == "1yr":
        tDelta = timedelta(days = 365)
        formatter = matplotlib.dates.DateFormatter("%m/%Y", tz)
        intvMj = matplotlib.dates.MonthLocator(interval = 2)
        intvMi = matplotlib.dates.DayLocator(interval = 7)
    elif tFrame == "max":
        formatter = matplotlib.dates.DateFormatter("%m/%Y", tz)
        intvMj = matplotlib.dates.YearLocator()
        intvMi = matplotlib.dates.MonthLocator(interval = 1)
    if dmax == dmin == []:
        dmax = [datetime.datetime.now(tz)]
        dmin = [datetime.datetime.now(tz) - tDelta]
    
    # Initialise plot
    if dType == "overview":
        fig = pyplot.figure(1, facecolor = "#33393b")
    elif dType == "trade":
        fig = pyplot.figure(11, facecolor = "#33393b")
    elif dType == "portfolio":
        fig = pyplot.figure(13, facecolor = "#33393b")
    pyplot.clf()
    whitespace = fig.add_axes([0, 0, 1, 1])
    whitespace.axis("off")
    ax = fig.add_axes([0.10, 0.06, 0.85, 0.90])
    
    # Plot value relative to opening value for each currency
    # Do not plot if no data exists
    for i in range(0, len(currencyList)):
        try:
            ax.plot(L1[h]["key%s" %i]["datetime"], L2[h]["key%s" %i], linestyle = "-",
                    linewidth = 1.2, label = currencyList[i], color = colours[i])
        except KeyError:
            pass
    if len(errList) > 0 and dType == "trade":
        errText = "*" + " and ".join(errList) + " missing price data"
        ax.text(0.01, 0.96, errText, color = "white", fontsize = 12, transform = ax.transAxes)
        
    # Format plot axes
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
    ax.axhline(y = 1, color = "white", linestyle = "--", linewidth = 0.8)
    ax.set_facecolor("#33393b")
    for i in ax.spines:
        ax.spines[i].set_color("white")
    for i in ("x", "y"):
        ax.tick_params(axis = i, color = "white")
    for i in ax.get_yticklabels():
        i.set_color("white")
    for i in ax.get_xticklabels():
        i.set_color("white")
    
    # Create TkInter canvas with Matplotlib figure
    pyplot.gcf().canvas.draw()
    
    # Plot price data
    if dType == "overview":
    
        # Get price data for currencies in previous plot; format and convert to lists
        #pData = getPriceSummary(tFrame, currencyList)
        names = list(D1[h]["Currency"])
        highs = [ftNum(x, "value", 2) for x in list(D1[h]["High"])]
        lows = [ftNum(x, "value", 2) for x in list(D1[h]["Low"])]
        returns = [(x - 1)*100 for x in list(D1[h]["Return"])]
    
        # Format text colour and sign depending on value
        colours = ["red" if x < 0 else "green" for x in returns]
        returns = [ftNum(x, "percentC", 2) for x in returns]

        # Plot price data as text
        fig2 = pyplot.figure(2)
        pyplot.clf()
        pyplot.scatter([0.03]*7, [x/8 + 0.029 for x in list(range(0, 7))], s = 80, marker = "s",
                       color = ["#ed9909", "#e2ed09", "#73ed09", "#09e5ed", "#096ced", "#b809ed", "#ed098a"])
        pyplot.axis("off")
        pyplot.tight_layout()
        ax2 = pyplot.gca()
        ax2.set_xlim(0, 1)
        ax2.set_ylim(0, 1)
        for i in range(0, 7):
            for j in range(0, 4):
                ax2.text([0.084, 0.437, 0.687, 0.968][j], 7/8, ["Currency", "Max", "Min", "Return"][j],
                         horizontalalignment = ["left", "right", "right", "right"][j],
                         color = "white", fontsize = 20)
            ax2.text(0.084, 1/8*i, names[i], color = colours[i],
                     fontsize = 20, horizontalalignment = "left")
            ax2.text(0.437, 1/8*i, highs[i], color = colours[i],
                     fontsize = 20, horizontalalignment = "right")
            ax2.text(0.687, 1/8*i, lows[i], color = colours[i],
                     fontsize = 20, horizontalalignment = "right")
            ax2.text(0.968, 1/8*i, returns[i], color = colours[i],
                     fontsize = 20, horizontalalignment = "right")
        
        # Create TkInter canvas with Matplotlib figure
        pyplot.gcf().canvas.draw()





##### Plot information on top and bottom movers -----------------------------------------------------------
    
# Function to plot top and bottom movers  
def plotMovers():
    
    # Retrieve info on top and bottom movers
    pData = getCurrentMovers()
    
    # Plot top and bottom sets as text
    for i in range(0, 2):
        
        # Determine whether set is top or bottom
        if i == 0:
            s1, s2 = 0, 10
            prefix = "Top"
        else:
            s1, s2 = 10, 21
            prefix = "Bottom"
        
        # Convert movement data to lists, then format
        currencyList = list(pData["Currency"])[s1:s2]
        changes = list(pData["Change"])[s1:s2]
        openV = [ftNum(x, "value", 3) for x in list(pData["Open"])][s1:s2]
        closeV = [ftNum(x, "value", 3) for x in list(pData["Close"])][s1:s2]
        
        # Reverse data so that most extreme movement is listed first
        currencyList.reverse();
        changes.reverse();
        openV.reverse()
        closeV.reverse()
    
        # Format text colour and sign depending on value
        colours = ["red" if x < 0 else "green" for x in changes]
        changes = [ftNum(x, "percentC", 2) for x in changes]
    
        # Plot movement data as text
        if i == 0:
            fig3 = pyplot.figure(3)
        else:
            fig4 = pyplot.figure(4)
        pyplot.clf()
        pyplot.axis("off")
        pyplot.tight_layout()
        ax = pyplot.gca()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        for j in range(0, 10):
            for k in range(0, 4):
                ax.text([0.084, 0.437, 0.687, 0.968][k], 10/14, ["Currency", "Open", "Close", "Return"][k],
                        horizontalalignment = ["left", "right", "right", "right"][k],
                        color = "white", fontsize = 20)
            ax.text(0.084, 1/14*j, currencyList[j], color = colours[j],
                    fontsize = 20, horizontalalignment = "left")
            ax.text(0.437, 1/14*j, openV[j], color = colours[j],
                    fontsize = 20, horizontalalignment = "right")
            ax.text(0.687, 1/14*j, closeV[j], color = colours[j],
                    fontsize = 20, horizontalalignment = "right")
            ax.text(0.968, 1/14*j, changes[j], color = colours[j],
                    fontsize = 20, horizontalalignment = "right")
        ax.text(0.084, 12/14, prefix + " 24-Hour Movers", color = "white", fontsize = 35,
                horizontalalignment = "left")
        
        # Create Tkinter canvas with Matplotlib figure
        pyplot.gcf().canvas.draw()





##### Plot information on user's current holdings ---------------------------------------------------------

# Function to plot user's current holdings   
def plotHoldings():
    
    # Get current holdings for each cryptocurrency
    values = getCurrentHoldings()
    total = sum(values["Percent"])
    
    # Combine currencies with small holdings into "other" category
    minor = values[values["Percent"] < 3]
    minorTotal = DataFrame(["OTHER", sum(minor["Amount"]), sum(minor["Amount"])/sum(values["Amount"])],
                           ["Currency", "Amount", "Percent"]).transpose()
    valuesC = values[values["Percent"] >= 3].append(minorTotal)
    
    # Set colour palette
    colours = seaborn.color_palette("tab10", len(valuesC))
    
    # Generate donut plot
    fig = pyplot.figure(7, facecolor = "#33393b")
    pyplot.clf()
    pyplot.pie(valuesC["Amount"], labels = valuesC["Currency"], colors = colours,
               textprops = {"color" : "w"}, radius = 1.2, startangle = 60)
    pyplot.gcf().gca().add_artist(pyplot.Circle((0, 0), 0.7, color = "#33393b"))
    pyplot.gcf().text(0.5, 0.5, "$" + "{:.2f}".format(sum(values["Amount"])), color = "white",
                      fontsize = 24, horizontalalignment = "center")
    pyplot.subplots_adjust(left = 0.1, right = 0.9, top = 0.9, bottom = 0.1)
    
    # Create TkInter canvas with Matplotlib figure
    pyplot.gcf().canvas.draw()
    
    # Format current holdings
    currencyList = list(values["Currency"])
    amounts = [ftNum(x, "value", 2) for x in list(values["Amount"])]
    pcts = [ftNum(x, "percent", 2) for x in list(values["Percent"])]
    
    # Reverse holdings data for plotting compatibility
    currencyList.reverse();
    amounts.reverse();
    pcts.reverse()
    colours.reverse()
    
    # Plot current holdings as text
    fig2 = pyplot.figure(8)
    pyplot.clf()
    pyplot.scatter([0.03]*len(values), [x/(len(values) + 1) + 0.029 for x in list(range(0, len(values)))],
                   color = [colours[0]]*(len(values) - len(valuesC)) + colours,
                   s = 80, marker = "s")
    pyplot.axis("off")
    pyplot.tight_layout()
    ax2 = pyplot.gca()
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    for i in range(0, len(values)):
        for j in range(0, 3):
            ax2.text([0.084, 0.487, 0.687][j], len(values)/(len(values) + 1), 
                     ["Currency", "Value (USD)", "Percent"][j], color = "white", fontsize = 20,
                     horizontalalignment = ["left", "right", "right", "right"][j])
        ax2.text(0.084, 1/(len(values) + 1)*i, currencyList[i], color = "white",
                 fontsize = 20, horizontalalignment = "left")
        ax2.text(0.487, 1/(len(values) + 1)*i, amounts[i], color = "white",
                 fontsize = 20, horizontalalignment = "right")
        ax2.text(0.687, 1/(len(values) + 1)*i, pcts[i], color = "white",
                 fontsize = 20, horizontalalignment = "right")
        
    # Create TkInter canvas with Matplotlib figure
    pyplot.gcf().canvas.draw()
    
    # Define internal functions to read and write user data from file
    def getBalTime():
        return ["{:.2f}".format(sum(values["Amount"])),
                datetime.datetime.now().strftime("%m/%d/%Y %H:%M")]
    def datRead():
        temp = open("UserData.txt", "r+")
        pList = temp.read().splitlines()
        temp.close()
        return pList
    def datWrite():
        cList = getBalTime()
        temp = open("UserData.txt", "w")
        temp.writelines([cList[0] + "\n", cList[1] + "\n"])
        temp.close()
    
    # Get portfolio balance and time from last refresh
    # If first time running, create file and perform this operation
    try:
        pList = datRead()
    except FileNotFoundError:
        datWrite()
        pList = datRead()
    cList = getBalTime()
    datWrite()
    pBal, pTime = float(pList[0]), pList[1]
    cBal, cTime = float(cList[0]), cList[1]
    
    # Get change and percent change in portfolio value since last update
    change1 = cBal - pBal
    change2 = change1/pBal*100
    
    # Format change and percent change for text
    change1 = ftNum(change1, "valueC", 2)
    change2 = ftNum(change2, "percentC", 2)
    
    # Plot portfolio balance
    fig2 = pyplot.figure(9)
    pyplot.clf()
    pyplot.axis("off")
    pyplot.tight_layout()
    ax2 = pyplot.gca()
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.text(0.08, 0.5, change1 + " (" + change2 + ") since last update on " + pList[1],
             color = "white", fontsize = 22)
    
    # Create TkInter canvas with Matplotlib figure
    pyplot.gcf().canvas.draw()





##### Plot information on user's transaction history ---------------------------------------------------------

# Function to plot user's transaction history
def plotTransactions(tHist, ref = False):
    
    # Get transaction history again if refeshing
    if ref == True:
        tHist = getTransactionHistory()
    
    # Get page number
    page = thMaxPage - sState.get() + 1
    
    # Number transactions by chronological order
    # Subset depending on page number
    tNum = list(range(1, len(tHist) + 1))
    tNum.reverse()
    tNum = tNum[((page - 1)*25):(page*25)]
    
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
    tHist = tHist.iloc[((page - 1)*25):(page*25)]
    
    # Limit data to 25 entries per page
    pageLength = len(tHist)

    # Create lists of transaction stats
    currency = list(tHist["Currency"])
    amounts = [ftNum(x, "amount", 4) for x in list(tHist["Amount"])]
    usd = [ftNum(x, "valueC", 2) for x in list(tHist["USD"])]
    tType = list(tHist["Type"])
    tTime = list(tHist["Time"])
    tStat = list(tHist["Status"])
    
    # Plot transaction stats as text
    fig10 = pyplot.figure(10)
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
        ax.text(0.620, 24/26 - j/26, currency[j], color = "white",
                fontsize = 12, horizontalalignment = "left")
        ax.text(0.820, 24/26 - j/26, amounts[j], color = "white",
                fontsize = 12, horizontalalignment = "right")
        ax.text(0.983, 24/26 - j/26, usd[j], color = "white",
                fontsize = 12, horizontalalignment = "right")
        
    # Create TkInter canvas with Matplotlib figure
    pyplot.gcf().canvas.draw()





##### Plot information on trade orders --------------------------------------------------------------------

# Function to plot trade orders
def plotTrade(push = False):
    
    # Convert state indicators to acceptable arguments for getQuote
    currency1 = cState1.get()
    currency2 = cState2.get()
    if eState1.get() == "":
        cT1, cT2 = currency2, currency1
        amount = eState2.get()
    elif eState2.get() == "":
        cT1, cT2 = currency1, currency2
        amount = eState1.get()
    if tState1.get() == 1:
        tType1 = "buy"
    elif tState1.get() == 2:
        tType1 = "sell"
    elif tState1.get() == 3:
        tType1 = "convert"
    if tState2.get() == 1:
        tType2 = "dollar"
    elif tState2.get() == 2:
        tType2 = "crypto"
    if amount == "":
        blank = True
    else:
        blank = False
    
    # If push is set to false, only get a quote and plot info
    if push == False:
    
        # Get trade order information
        if blank == False:
            tInfo = getQuote(tType1, tType2, float(amount), cT1, cT2)
        
        # Get currency owned information
        cInfo = getSpecificCurrency(currency1, currency2)
    
        # Get currency owned text
        oT1 = currency1 + " owned: " + ftNum(float(cInfo[0]), "amount", 4) + " ($" + cInfo[1] + ")"
        if tType1 == "convert":
            oT2 = currency2 + " owned: " + ftNum(float(cInfo[2]), "amount", 4) + " ($" + cInfo[3] + ")"
        else:
            oT2 = ""
    
        # Get trade text
        if blank == False:
            tT1 = "$" + ftNum(tInfo[0], "amount")
            if tType1 != "convert":
                tT2 = ("-" if tType1 == "sell" else "") + "$" + ftNum(tInfo[1], "amount")
                tT3 = "$" + ftNum(tInfo[2], "amount")
            else:
                tT2 = "-$" + ftNum(tInfo[1] + tInfo[5], "amount")
                tT3 = "$" + ftNum(tInfo[4], "amount")
        else:
            tT1, tT2, tT3 = "$---", "$---", "$---"
    
        # List disclaimer text
        dT1 = "Rates may differ at the time of transaction completion due to changes in market conditions."
        dT2 = "A detailed schedule of transaction fees can be found on Coinbase (www.coinbase.com)."
    
        # Plot trade order information as text
        fig12 = pyplot.figure(12)
        pyplot.clf()
        pyplot.axis("off")
        pyplot.tight_layout()
        ax = pyplot.gca()
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.text(0.430, 0.87, oT1, color = "white", fontsize = 14, horizontalalignment = "left")
        ax.text(0.430, 0.78, oT2, color = "white", fontsize = 14, horizontalalignment = "left")
        ax.text(0.430, 0.87, currency1 + " ", color = "#b809ed", fontsize = 14, horizontalalignment = "left")
        ax.text(0.430, 0.78, currency2 + " ", color = "#09e5ed", fontsize = 14, horizontalalignment = "left")
        ax.text(0.430, 0.53, "Subtotal:", color = "white", fontsize = 20, horizontalalignment = "left")
        ax.text(0.430, 0.37, "Fees:", color = "white", fontsize = 20, horizontalalignment = "left")
        ax.text(0.430, 0.21, "Total:", color = "white", fontsize = 20, horizontalalignment = "left")
        ax.text(0.000, 0.05, dT1, color = "white", fontsize = 10, horizontalalignment = "left")
        ax.text(0.000, 0.00, dT2, color = "white", fontsize = 10, horizontalalignment = "left")
        ax.text(0.986, 0.53, tT1, color = "white", fontsize = 20, horizontalalignment = "right")
        ax.text(0.986, 0.37, tT2, color = "white", fontsize = 20, horizontalalignment = "right")
        ax.text(0.986, 0.21, tT3, color = "white", fontsize = 20, horizontalalignment = "right")
    
        # Create TkInter canvas with Matplotlib figure
        pyplot.gcf().canvas.draw()
    
    # If push is set to true, execute trade without plotting
    elif push == True:
        tInfo = getQuote(tType1, tType2, float(amount), cT1, cT2, push = True)

# Function to plot trade confirmation text
def plotTradeConfirmation():
    
    # Convert state indicators to text
    currency1 = cState1.get()
    currency2 = cState2.get()
    if eState1.get() == "":
        c1, c2 = currency2, currency1
        amount = eState2.get()
    elif eState2.get() == "":
        c1, c2 = currency1, currency2
        amount = eState1.get()
    if tState1.get() == 1:
        tType1 = "Buy"
        cT1, cT2 = "USD ($)", c1
    elif tState1.get() == 2:
        tType1 = "Sell"
        cT1, cT2 = c1, "USD ($)"
    elif tState1.get() == 3:
        tType1 = "Convert"
        cT1, cT2 = c1, c2
        if tState2.get() == 1:
            amount = "$" + amount
    
    # Plot trade order information as text
    fig13 = pyplot.figure(13)
    pyplot.clf()
    pyplot.axis("off")
    pyplot.tight_layout()
    ax = pyplot.gca()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    for i in range(0, 4):
        ax.text(0.38, 0.85 - i*0.2, ["Type: " +  tType1, "Amount: " + amount,
                                    "From: " + cT1, "To: " + cT2][i],
                horizontalalignment = "left", color = "white", fontsize = 13)
    ax.text(0.045, 0.85, "Confirm?", horizontalalignment = "left", color = "white", fontsize = 13)

    # Create TkInter canvas with Matplotlib figure
    pyplot.gcf().canvas.draw()





##### Plot information on last refresh time ---------------------------------------------------------------
    
# Function to display time at which a widget was last refreshed
def plotRefresh(instance):
    
    # Get current time
    cTime = datetime.datetime.now().strftime("%H:%M")
    if instance == 5:
        fig5 = pyplot.figure(5)
    else:
        fig6 = pyplot.figure(6)
        
    # Plot text
    pyplot.clf()
    pyplot.axis("off")
    pyplot.tight_layout()
    ax = pyplot.gca()
    ax.set_xlim(0, 0.1)
    ax.set_ylim(0, 0.1)
    ax.text(0.1, 0.05, "Last updated at " + cTime, color = "white", style = "italic",
            fontsize = 10, horizontalalignment = "right")
    
    # Create TkInter canvas with Matplotlib figure
    pyplot.gcf().canvas.draw()





##### Run GUI ---------------------------------------------------------------------------------------------

# Initialise account data
initAccount = client.get_accounts(limit = 100)
initIDs = getIDs()
initPmt = getPmt()

# Initialise time series data for featured currencies
sData1, sData2, mData, cData, hData1, hData2 = [], [], [], [], [], []
cData = list(getCurrentHoldings()["Currency"])
for h in range(0, 7):
    d1, d2, d3, d4 = {}, {}, {}, {}
    for i in range(0, 7):
        d1["key%s" %i] = getPriceSeries(["1hr", "1d", "1wk", "1m", "3m", "6m", "1yr"][h],
                                        ["XLM", "ADA", "DOT", "UNI", "LTC", "ETH", "BTC"][i])
        d2["key%s" %i] = d1["key%s" %i]["mean"]/(d1["key%s" %i]["mean"][0])
        d3["key%s" %i] = getPriceSeries(["1hr", "1d", "1wk", "1m", "3m", "6m", "1yr"][h], cData[i])
        d4["key%s" %i] = d3["key%s" %i]["mean"]/(d3["key%s" %i]["mean"][0])
    sData1.append(d1)
    sData2.append(d2)
    hData1.append(d3)
    hData2.append(d4)
    mData.append(getPriceSummary(["1hr", "1d", "1wk", "1m", "3m", "6m", "1yr"][h],
                                 ["XLM", "ADA", "DOT", "UNI", "LTC", "ETH", "BTC"]))

# Get list of currencies available for trading
cbList = getTradeList()

# Create main TkInter window
window = Tk()

# Set window theme
window.tk.call("lappend", "auto_path", "C:/Users/Trevor Drees/Downloads/awthemes-10.4.0")
window.tk.call("package", "require", "awdark") 
ttk.Style().theme_use("awdark") 
ttk.Style().configure("My.TSpinbox", arrowsize = 11)
 
# Set window title
window.title("CBCrypto: Cryptocurrency Dashboard")
  
# Set window dimensions and colour
window.geometry("1920x1080")
window.configure(bg = "#33393b")

# Set window tabs
tC = ttk.Notebook(window)
t1 = ttk.Frame(tC)
t2 = ttk.Frame(tC)
t3 = ttk.Frame(tC)
tC.add(t1, text = "Overview")
tC.add(t2, text = "My Portfolio")
tC.add(t3, text = "Trade")
tC.pack(expand = 1, fill = "both")

# Initialise transaction history and set maximum number of pages
tHist = getTransactionHistory()
thMaxPage = 999 if math.ceil(len(tHist)/25) > 999 else math.ceil(len(tHist)/25)

# Set up plots, each as its own canvas
figX = [pyplot.figure(figsize = [(9, 6), (9, 3.5), (9, 4.9), (9, 4.9), (5, 0.3), (5, 0.3), (5.8, 5.8),
                                 (9, 3.5), (12, 0.6), (10.8, 9.5), (7.5, 6), (6.8, 3.6), (9, 6)][x],
                      edgecolor = ["white" if w in [7, 10] else "#33393b" for w in range(1, 13)][x],
                      facecolor = "#33393b",
                      linewidth = 2) for x in range(0, 12)]
canvasX = [FigureCanvasTkAgg(figX[x], master = ([t1]*6 + [t2]*3 + [t3]*3 + [t2])[x]) for x in range(0, len(figX))]

# Place all plots
for i in range(0, len(figX)):
    canvasX[i].get_tk_widget().place(x = [50, 50, 775, 775, 341, 1068, 75, 50, 535, 614, 50, 90, 500][i], 
                                     y = [50, 500, 35, 400, 750, 750, 65, 500, 71, 67, 50, 500, 250][i])
    
# Set up trade confirmation plot for pop-up window
figP = pyplot.figure(figsize = (4.9, 2), facecolor = "#33393b")

# Set state variables
bState1 = IntVar()
bState2 = IntVar()
bState3 = IntVar()
sState = IntVar()
sState.set(thMaxPage)
tState1 = IntVar()
tState2 = IntVar()
cState1 = StringVar()
cState1.set("BTC")
cState2 = StringVar()
eState1 = StringVar()
eState2 = StringVar()

# Control currnecy time series plot timeframe with radiobuttons (Overview)
rb1 = [ttk.Radiobutton(t1, command = lambda:[plotSeries(), plotRefresh(5)],
                       text = ["1h", "1d", "1wk", "1m", "3m", "6m", "1yr"][x], 
                       variable = bState1, value = x + 1) for x in range(0, 7)]

# Place plot timeframe radiobuttons side-by-side (Overview)
for i in range(0, len(rb1)):
    rb1[i].place(x = [113, 173, 233, 293, 353, 413, 473][i], y = 40)
    
# Control currnecy time series plot timeframe with radiobuttons (Trade)
rb2 = [ttk.Radiobutton(t3, command = lambda:[plotSeries(dType = "trade")],
                       text = ["1h", "1d", "1wk", "1m", "3m", "6m", "1yr"][x], 
                       variable = bState2, value = x + 1) for x in range(0, 7)]

# Place plot timeframe radiobuttons side-by-side (Trade)
for i in range(0, len(rb2)):
    rb2[i].place(x = [113, 173, 233, 293, 353, 413, 473][i], y = 40)
    
# Control currnecy time series plot timeframe with radiobuttons (Portfolio)
rb5 = [ttk.Radiobutton(t2, command = lambda:[plotSeries(dType = "portfolio", currencies = cData)],
                       text = ["1h", "1d", "1wk", "1m", "3m", "6m", "1yr"][x], 
                       variable = bState3, value = x + 1) for x in range(0, 7)]

# Place plot timeframe radiobuttons side-by-side (Trade)
for i in range(0, len(rb5)):
    rb5[i].place(x = [113, 173, 233, 293, 353, 413, 473][i], y = 40)

# Create dropdown menu to select currency to buy/sell
# Create a second dropdown menu for currency conversion
c1 = ttk.Combobox(t3, textvariable = cState1, width = 8, state = "readonly",
                  values = [x for x in cbList if x != cState2.get()])
c1.place(x = 101, y = 608)
c2 = ttk.Combobox(t3, textvariable = cState2, width = 8, state = "readonly",
                  values = [x for x in cbList if x != cState1.get()])
c2.place(x = 101, y = 628)

# Define function to validate entry in trade entry boxes
def checkKey(keyVal):
    if tState2.get() == 1:
        return re.match("^(\d)*(\.)?([0-9]{0,2})?$", keyVal) is not None
    elif tState2.get() == 2:
        return re.match("^(\d)*(\.)?([0-9])*$", keyVal) is not None
checkKeyWrapper = (window.register(checkKey), "%P")

# Create entry box to specify currency/dollar amounts
# Create a second entry box for currency conversion
e1 = ttk.Entry(t3, textvariable = eState1, width = 9, validate = "key",
               validatecommand = checkKeyWrapper)
e1.place(x = 181, y = 608)
e2 = ttk.Entry(t3, textvariable = eState2, width = 9, validate = "key",
               validatecommand = checkKeyWrapper)
e2.place(x = 181, y = 628)
    
# Define internal function to place or remove second dropdown menu
def placeMenu():
    if tState1.get() == 3:
        c2.configure(state = "readonly")
        e2.configure(state = "normal")
        if cbList.index(cState1.get()) == len(cbList) - 1:
            cState2.set(cbList[cbList.index(cState1.get()) - 1])
        else:
            cState2.set(cbList[cbList.index(cState1.get()) + 1])
    elif tState1.get() != 3:
        try:
            c2.configure(state = "disabled")
            cState2.set("")
            e2.configure(state = "disabled")
            eState2.set("")
        except NameError:
            pass
    
# Ensure that selection from first menu is absent from second
def changeList(*args):
    c1.configure(values = [x for x in cbList if x != cState2.get()])
    c2.configure(values = [x for x in cbList if x != cState1.get()])
c1.bind("<<ComboboxSelected>>", lambda e:[c1.selection_clear(), changeList(), plotTrade(),
                                          plotSeries(dType = "trade")])
c2.bind("<<ComboboxSelected>>", lambda e:[c2.selection_clear(), changeList(), plotTrade(),
                                          plotSeries(dType = "trade")])

# Ensure that entry box is cleared when switching from dollars to crypto or vice-versa
def clearBox(target = None, *args):
    if target == None:
        e1.delete(0, "end")
        e2.delete(0, "end")
    elif target == 1:
        e1.delete(0, "end")
    elif target == 2:
        e2.delete(0, "end")

# Function to create pop-up window for trade confirmation
def tradeWindow():
    
    # Create pop-up window; set window details
    p1 = Toplevel()
    p1.title("Trade Confirmation")
    p1.geometry("300x120")
    p1.resizable(width = False, height = False)
    p1.configure(bg = "#33393b")
    p1.wm_iconphoto(False, icon)
    
    # Set up message plot and canvas
    plotTradeConfirmation()
    canvasP = FigureCanvasTkAgg(figP, master = p1)
    canvasP.get_tk_widget().place(x = 0, y = 0)
    
    # Create buttons to confirm or cancel trade
    b1_p1 = ttk.Button(p1, text = "Yes", command = lambda:[plotTransactions(tHist = tHist, ref = True), p1.destroy()], width = 9)
    b1_p1.place(x = 20, y = 45)
    b2_p1 = ttk.Button(p1, text = "No", command = p1.destroy, width = 9)
    b2_p1.place(x = 20, y = 80)

    # Confirmation button with actual trade functionality
    # Temporarily disabled to avoid accidental purchases while testing
    #b1_p1 = ttk.Button(p1, text = "Yes", command = lambda:[plotTrade(push = True), plotTransactions(tHist = tHist, ref = True), p1.destroy()], width = 9)    

# Function to reset radiobuttons and text fields
def resetTrades():
    tState1.set(1)
    tState2.set(1)
    
# Function to disable trade confirmation button when no input is provided
def disableTrades():
    if eState1.get() == "" and eState2.get() == "":
        b3.state(["disabled"])
        window.update()
    else:
        b3.state(["!disabled"])
        window.update()
    
# Control trade type with radiobuttons
rb3 = [ttk.Radiobutton(t3, command = lambda:[placeMenu(), changeList(), plotTrade(),
                                             plotSeries(dType = "trade")],
                       text = ["Buy", "Sell", "Convert"][x], 
                       variable = tState1, value = x + 1) for x in range(0, 3)]

# Place trade type radiobuttons side-by-side
for i in range(0, len(rb3)):
    rb3[i].place(x = 100, y = [526, 546, 566][i])

# Control trade dollar/crypto with radiobuttons
rb4 = [ttk.Radiobutton(t3, command = lambda:[clearBox(), plotTrade()],
                       text = ["Dollars", "Crypto"][x], 
                       variable = tState2, value = x + 1) for x in range(0, 2)]

# Place trade dollar/crypto radiobuttons side-by-side
for i in range(0, len(rb4)):
    rb4[i].place(x = 186, y = [526, 546][i])

# Add refresh button for top movers
b1 = ttk.Button(t1, text = "Refresh", command = lambda:[plotMovers(), plotRefresh(6)])
b1.place(x = 1327, y = 70)

# Add refresh button for transaction history
b2 = ttk.Button(t3, text = "Refresh", command = lambda:[plotHoldings(), plotTransactions(tHist = tHist, ref = True)])
b2.place(x = 1327, y = 35)

# Add trade button to buy/sell/convert currency
b3 = ttk.Button(t3, text = "Confirm", command = tradeWindow, width = 9)
b3.place(x = 101, y = 675)

# Add button to reset trade settings
b4 = ttk.Button(t3, text = "Reset", width = 9,
                command = lambda:[resetTrades(), clearBox(), placeMenu(), changeList(), 
                                  disableTrades(), plotTrade(), plotSeries(dType = "trade")])
b4.place(x = 180, y = 675)

# Add spinbox to select transaction history page
s1 = ttk.Spinbox(t3, from_ = 1, to = thMaxPage, textvariable = sState, width = 4,
                 font = Font(size = 10), style = "My.TSpinbox", command = lambda:[plotTransactions(tHist = tHist)])
s1.state(["readonly"])
s1.place(x = 1268, y = 36)

# Add progress bar indicating when application is loading
p1 = ttk.Progressbar(window, orient = HORIZONTAL, length = 100, mode = "indeterminate")
p1.place(x = 1360, y = 7)
p1.update_idletasks()

# Set default button states
rb1[1].invoke()
rb2[1].invoke()
rb3[0].invoke()
rb4[0].invoke()
rb5[0].invoke()
b1.invoke()
b2.invoke()
b3.state(["disabled"])

# Set system for updating trade information when entry typing stops
afterNum = None
def entryWait(*args, aN = afterNum):
    if aN is not None:
        e1.after_cancel(aN)
    global afterNum; afterNum = e1.after(2000, plotTrade)
e1.bind("<Key>", lambda e:[entryWait(), clearBox(2), disableTrades()])
e2.bind("<Key>", lambda e:[entryWait(), clearBox(1), disableTrades()])

# Set window icon
icon = ImageTk.PhotoImage(Image.open("Logo.png"))
window.wm_iconphoto(False, icon)

# Run TkInter window over loop
window.mainloop()

