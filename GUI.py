##### GUI To-do list --------------------------------------------------------------------------------------

# Put transaction times in local time zone
# Place progress bar and loading messages up near tabs
# Create login screen using API key and secret
# Create trading interface





##### Load packages ---------------------------------------------------------------------------------------

# Import packages for GUI
from tkinter import *
from tkinter import ttk
from tkinter.font import Font
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg





##### Set formatting functions ----------------------------------------------------------------------------

# Function to format transaction types and status
def formatType(transaction):
    transaction = transaction.replace("_", " ").capitalize()
    return transaction

# Function to format currency numbers and percents
def formatCurrency(x, xType, dec = 2):
    
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

        



##### Plot price data -------------------------------------------------------------------------------------

# Build time series plots specifically for use in GUI
def buildPlot():
    
    # Start progress bar
    p1.start()
    
    # Create list of tracked currencies
    currencyList = ["XLM", "ADA", "DOT", "UNI", "LTC", "ETH", "BTC"]
    
    # Choose timeframe depending on button selection
    if bState.get() == 1:
        tFrame = "1hr"
    elif bState.get() == 2:
        tFrame = "1d"
    elif bState.get() == 3:
        tFrame = "1wk"
    elif bState.get() == 4:
        tFrame = "1m"
    elif bState.get() == 5:
        tFrame = "3m"
    elif bState.get() == 6:
        tFrame = "6m"
    elif bState.get() == 7:
        tFrame = "1yr"
    
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
    colours = ["#ed9909", "#e2ed09", "#73ed09", "#09e5ed", "#096ced", "#b809ed", "#ed098a"]
    
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
    fig = pyplot.figure(1, facecolor = "#33393b")
    pyplot.clf()
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
    
    # Get price data for 5 popular currencies; convert to lists
    pData = priceCheck(tFrame, currencyList)
    names = list(pData["Currency"])
    highs = [formatCurrency(x, "value", 2) for x in list(pData["High"])]
    lows = [formatCurrency(x, "value", 2) for x in list(pData["Low"])]
    returns = [(x - 1)*100 for x in list(pData["Return"])]
    
    # Format text colour and return sign depending on value
    colours = ["red" if x < 0 else "green" for x in returns]
    returns = [formatCurrency(x, "percentC", 2) for x in returns]

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
    
    # Stop progress bar
    p1.stop()
    
# Get data on top movers and plot as text    
def moverPlots():
    
    # Start progress bar
    p1.start()
    
    # Retrieve info on top and bottom movers
    pData = currentMovers()
    
    # Plot top and bottom sets as text
    for i in range(0, 2):
        
        # Determine whether set is top or bottom
        if i == 0:
            s1, s2 = 0, 10
            prefix = "Top"
        else:
            s1, s2 = 10, 21
            prefix = "Bottom"
        
        # Convert movement data to lists
        currencyList = list(pData["Currency"])[s1:s2]
        changes = list(pData["Change"])[s1:s2]
        openV = [formatCurrency(x, "value", 3) for x in list(pData["Open"])][s1:s2]
        closeV = [formatCurrency(x, "value", 3) for x in list(pData["Close"])][s1:s2]
        
        # Reverse data so that most extreme movement is listed first
        currencyList.reverse();
        changes.reverse();
        openV.reverse()
        closeV.reverse()
    
        # Format text colour and return sign depending on value
        colours = ["red" if x < 0 else "green" for x in changes]
        changes = [formatCurrency(x, "percentC", 2) for x in changes]
    
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
    
    # Stop progress bar
    p1.stop()
   
# Generate donut plot of held currencies    
def currentPlot():
    
    # Get current holdings for each cryptocurrency
    values = currentHoldings()
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
    
    # Create Tkinter canvas with Matplotlib figure
    pyplot.gcf().canvas.draw()
    
    # Format current holdings
    currencyList = list(values["Currency"])
    amounts = [formatCurrency(x, "value", 2) for x in list(values["Amount"])]
    pcts = [formatCurrency(x, "percent", 2) for x in list(values["Percent"])]
    
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
        temp = open("textfile.txt", "r+")
        pList = temp.read().splitlines()
        temp.close()
        return pList
    def datWrite():
        cList = getBalTime()
        temp = open("textfile.txt", "w")
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
    change1 = formatCurrency(change1, "valueC", 2)
    change2 = formatCurrency(change2, "percentC", 2)
    
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
    
    # Create Tkinter canvas with Matplotlib figure
    pyplot.gcf().canvas.draw()

# Function to list transaction history
def transPlot(tHist = tHist, ref = False):
    
    # Get transaction history again if refeshing
    if ref == True:
        tHist = transactionHistory()
    
    # Get page number
    page = thMaxPage - sState.get() + 1
    
    # Number transactions by chronological order
    # Subset depending on page number
    tNum = list(range(1, len(tHist) + 1))
    tNum.reverse()
    tNum = tNum[((page - 1)*25):(page*25)]
    
    # Change time string to datetime, then format appropriately
    tHist["Time"] = [dp.parse(x) for x in list(tHist["Time"])]
    tHist["Time"] = [x.strftime("%m/%d/%Y %H:%M:%S") for x in list(tHist["Time"])]
    
    # Format transaction types and status
    tHist["Type"] = [formatType(x) for x in list(tHist["Type"])]
    tHist["Status"] = [formatType(x) for x in list(tHist["Status"])]
    
    # Sort transactions by date and time
    # Subset depending on page number
    tHist = tHist.sort_values(by = "Time", ascending = False)
    tHist = tHist.iloc[((page - 1)*25):(page*25)]
    
    # Limit data to 25 entries per page
    pageLength = len(tHist)

    # Create lists of transaction stats
    currency = list(tHist["Currency"])
    amounts = [formatCurrency(x, "amount", 4) for x in list(tHist["Amount"])]
    usd = [formatCurrency(x, "valueC", 2) for x in list(tHist["USD"])]
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
        
    # Create Tkinter canvas with Matplotlib figure
    pyplot.gcf().canvas.draw()
    
# Display time at which a widget was last refreshed
def refreshTime(instance):
    
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

# Create TkInter window
window = Tk()

# Set theme
window.tk.call("lappend", "auto_path", "C:/Users/Trevor Drees/Downloads/awthemes-10.4.0")
window.tk.call("package", "require", "awdark") 
ttk.Style().theme_use("awdark") 
ttk.Style().configure("My.TSpinbox", arrowsize = 11)
 
# Set window title
window.title("CBCrypto: Cryptocurrency Dashboard")
  
# Set window dimensions and colour
window.geometry("1920x1080")
window.configure(bg = "#33393b")

# Set tabs
tC = ttk.Notebook(window)
t1 = ttk.Frame(tC)
t2 = ttk.Frame(tC)
tC.add(t1, text = "Overview")
tC.add(t2, text = "My Portfolio")
tC.pack(expand = 1, fill = "both")

# Initialise transaction history
tHist = transactionHistory()

# Set maximum number of pages on transaction history
thMaxPage = 999 if math.ceil(len(tHist)/25) > 999 else math.ceil(len(tHist)/25)

# Plot figures
fig1 = pyplot.figure(figsize = (9, 6), facecolor = "#33393b")
canvas1 = FigureCanvasTkAgg(fig1, master = t1)
canvas1.get_tk_widget().place(x = 50, y = 50)
fig2 = pyplot.figure(figsize = (9, 3.5), facecolor = "#33393b")
canvas2 = FigureCanvasTkAgg(fig2, master = t1)
canvas2.get_tk_widget().place(x = 50, y = 500)
fig3 = pyplot.figure(figsize = (9, 4.9), facecolor = "#33393b")
canvas3 = FigureCanvasTkAgg(fig3, master = t1)
canvas3.get_tk_widget().place(x = 775, y = 35)
fig4 = pyplot.figure(figsize = (9, 4.9), facecolor = "#33393b")
canvas4 = FigureCanvasTkAgg(fig4, master = t1)
canvas4.get_tk_widget().place(x = 775, y = 400)
fig5 = pyplot.figure(figsize = (5, 0.3), facecolor = "#33393b")
canvas5 = FigureCanvasTkAgg(fig5, master = t1)
canvas5.get_tk_widget().place(x = 341, y = 750)
fig6 = pyplot.figure(figsize = (5, 0.3), facecolor = "#33393b")
canvas6 = FigureCanvasTkAgg(fig6, master = t1)
canvas6.get_tk_widget().place(x = 1068, y = 750)
fig7 = pyplot.figure(figsize = (5.8, 5.8), facecolor = "#33393b", edgecolor = "white", linewidth = 2)
canvas7 = FigureCanvasTkAgg(fig7, master = t2)
canvas7.get_tk_widget().place(x = 75, y = 65)
fig8 = pyplot.figure(figsize = (9, 3.5), facecolor = "#33393b")
canvas8 = FigureCanvasTkAgg(fig8, master = t2)
canvas8.get_tk_widget().place(x = 50, y = 500)
fig9 = pyplot.figure(figsize = (12, 0.6), facecolor = "#33393b")
canvas9 = FigureCanvasTkAgg(fig9, master = t2)
canvas9.get_tk_widget().place(x = 535, y = 71)
fig10 = pyplot.figure(figsize = (10.8, 8.8), facecolor = "#33393b", edgecolor = "white", linewidth = 2)
canvas10 = FigureCanvasTkAgg(fig10, master = t2)
canvas10.get_tk_widget().place(x = 614, y = 110)

# Set state variable for radiobuttons
bState = IntVar()
sState = IntVar()
sState.set(thMaxPage)

# Control plot timeframe with radiobuttons
rb1 = ttk.Radiobutton(t1, command = lambda:[buildPlot(), refreshTime(5)],
                      text = "1h", variable = bState, value = 1) 
rb2 = ttk.Radiobutton(t1, command = lambda:[buildPlot(), refreshTime(5)],
                      text = "1d", variable = bState, value = 2)
rb3 = ttk.Radiobutton(t1, command = lambda:[buildPlot(), refreshTime(5)],
                      text = "1wk", variable = bState, value = 3)
rb4 = ttk.Radiobutton(t1, command = lambda:[buildPlot(), refreshTime(5)],
                      text = "1m", variable = bState, value = 4)
rb5 = ttk.Radiobutton(t1, command = lambda:[buildPlot(), refreshTime(5)],
                      text = "3m", variable = bState, value = 5)
rb6 = ttk.Radiobutton(t1, command = lambda:[buildPlot(), refreshTime(5)],
                      text = "6m", variable = bState, value = 6)
rb7 = ttk.Radiobutton(t1, command = lambda:[buildPlot(), refreshTime(5)],
                      text = "1yr", variable = bState, value = 7)

# Place radiobuttons side-by-side
rb1.place(x = 113, y = 40)
rb2.place(x = 173, y = 40)
rb3.place(x = 233, y = 40)
rb4.place(x = 293, y = 40)
rb5.place(x = 353, y = 40)
rb6.place(x = 413, y = 40)
rb7.place(x = 473, y = 40)

# Refresh button for top movers
b1 = ttk.Button(t1, text = "Refresh", command = lambda:[moverPlots(), refreshTime(6)])
b1.place(x = 1327, y = 70)

# Refresh button for portfolio current holdings
b2 = ttk.Button(t2, text = "Refresh", command = lambda:[currentPlot(), transPlot(ref = True)])
b2.place(x = 1327, y = 70)

# Spinbox to select transaction history page
s1 = ttk.Spinbox(t2, from_ = 1, to = thMaxPage, textvariable = sState, width = 4,
                 font = Font(size = 10), style = "My.TSpinbox", command = lambda:[transPlot()])
s1.state(["readonly"])
s1.place(x = 1268, y = 71)

# Progress bar
p1 = ttk.Progressbar(t1, orient = HORIZONTAL, length = 100, mode = "indeterminate")
p1.place(x = 566, y = 40)

# Set default button states
rb2.invoke()
b1.invoke()
b2.invoke()

# Run TkInter window over loop
window.mainloop()

