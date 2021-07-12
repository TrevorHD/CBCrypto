##### Load packages ---------------------------------------------------------------------------------------

# Import packages for GUI
from tkinter import *
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg





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
    highs = ["{:.2f}".format(x) for x in list(pData["High"])]
    lows = ["{:.2f}".format(x) for x in list(pData["Low"])]
    returns = [(x - 1)*100 for x in list(pData["Return"])]
    
    # Format text colour and return sign depending on value
    colours = ["red" if x < 0 else "green" for x in returns]
    returns = ["{:.2f}".format(x) + "%" if x < 0 else "+" + "{:.2f}".format(x) + "%" for x in returns]

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
        openV = ["{:.3f}".format(x) for x in list(pData["Open"])][s1:s2]
        closeV = ["{:.3f}".format(x) for x in list(pData["Close"])][s1:s2]
        
        # Reverse data so that most extreme movement is listed first
        currencyList.reverse();
        changes.reverse();
        openV.reverse()
        closeV.reverse()
    
        # Format text colour and return sign depending on value
        colours = ["red" if x < 0 else "green" for x in changes]
        changes = ["{:.2f}".format(x) + "%" if x < 0 else "+" + "{:.2f}".format(x) + "%" for x in changes]
    
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
    minor = values[values["Percent"] < 0.02]
    minorTotal = DataFrame(["OTHER", sum(minor["Amount"]), sum(minor["Amount"])/sum(values["Amount"])],
                           ["Currency", "Amount", "Percent"]).transpose()
    values = values[values["Percent"] >= 0.02].append(minorTotal)
    
    # Generate donut plot
    fig = pyplot.figure(7, facecolor = "#33393b")
    pyplot.clf()
    pyplot.pie(values["Amount"], labels = values["Currency"], textprops = {"color" : "w"})
    pyplot.gcf().gca().add_artist(pyplot.Circle((0,0), 0.7, color = "#33393b"))
    
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
window.tk.call('lappend', 'auto_path', 'C:/Users/Trevor Drees/Downloads/awthemes-10.4.0')
window.tk.call('package', 'require', 'awdark') 
ttk.Style().theme_use("awdark") 
 
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
fig7 = pyplot.figure(figsize = (9, 6), facecolor = "#33393b")
canvas7 = FigureCanvasTkAgg(fig7, master = t2)
canvas7.get_tk_widget().place(x = 50, y = 50)

# Set state variable for radiobuttons
bState = IntVar()

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
b2 = ttk.Button(t2, text = "Refresh", command = currentPlot)
b2.place(x = 1327, y = 70)

# Progress bar
p1 = ttk.Progressbar(t1, orient = HORIZONTAL, length = 100, mode = "indeterminate")
p1.place(x = 566, y = 40)

# Set default button states
rb2.invoke()
b1.invoke()
b2.invoke()

# Run TkInter window over loop
window.mainloop()

