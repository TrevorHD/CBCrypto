##### Load packages ---------------------------------------------------------------------------------------

# Import packages for GUI
from tkinter import *
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg





##### Plot price data -------------------------------------------------------------------------------------

# Build time series plots specifically for use in GUI
def buildPlot():
    
    # Create list of tracked currencies
    currencyList = ["BTC", "ETH", "ADA", "UNI", "LTC"]
    
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
    fig = Figure(figsize = (9, 6), facecolor = "#33393b")
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
    
    # Create Tkinter canvas with Matplotlib figure
    pyplot.gcf().canvas.draw()
    canvas1 = FigureCanvasTkAgg(fig, master = window)
    
    # Place canvas in Tkinter window
    canvas1.get_tk_widget().place(x = 50, y = 50)
    
    # Get price data for 5 popular currencies
    pData = priceCheck(tFrame, ["BTC", "ETH", "ADA", "UNI", "LTC"])
    names = list(pData["Currency"])
    highs = list(pData["High"])
    lows = list(pData["Low"])
    returns = list(pData["Return"])
    colours = ["red" if x < 1 else "green" for x in returns]

    # Plot price data as text
    fig2 = Figure(figsize = (9, 3), dpi = 800, facecolor = "#33393b")
    fig2.add_axes([0, 0, 1, 1]).axis("off")
    ax2 = fig.add_axes([0, 0, 1, 1])
    for i in range(0, 5):
        ax2.text(0.0, 0.25*(i - 1), names[i], color = colours[i],
                 fontsize = 12, horizontalalignment = "left")
        ax2.text(0.2, 0.25*(i - 1), round(highs[i], 2), color = colours[i],
                 fontsize = 12, horizontalalignment = "left")
        ax2.text(0.6, 0.25*(i - 1), round(lows[i], 2), color = colours[i],
                 fontsize = 12, horizontalalignment = "left")
        ax2.text(1.0, 0.25*(i - 1), round(returns[i], 2), color = colours[i],
                 fontsize = 12, horizontalalignment = "left")
        
    # Create Tkinter canvas with Matplotlib figure
    pyplot.gcf().canvas.draw()
    canvas2 = FigureCanvasTkAgg(fig2, master = window)  
    
    # Place canvas in Tkinter window
    canvas2.get_tk_widget().place(x = 1500, y = 700)

    



##### Run GUI ---------------------------------------------------------------------------------------------
   
# Create Tkinter window
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

# Set timeframe button state
bState = IntVar()
bState.set(2) 

# Build initial plot
buildPlot()

# Control plot timeframe with radiobuttons
ttk.Radiobutton(window, command = buildPlot, text = "1h", variable = bState, value = 1).place(x = 110, y = 40) 
ttk.Radiobutton(window, command = buildPlot, text = "1d", variable = bState, value = 2).place(x = 170, y = 40)
ttk.Radiobutton(window, command = buildPlot, text = "1wk", variable = bState, value = 3).place(x = 230, y = 40)
ttk.Radiobutton(window, command = buildPlot, text = "1m", variable = bState, value = 4).place(x = 290, y = 40)
ttk.Radiobutton(window, command = buildPlot, text = "3m", variable = bState, value = 5).place(x = 350, y = 40)
ttk.Radiobutton(window, command = buildPlot, text = "6m", variable = bState, value = 6).place(x = 410, y = 40)
ttk.Radiobutton(window, command = buildPlot, text = "1yr", variable = bState, value = 7).place(x = 470, y = 40)
  
# Run Tkinter window over loop
window.mainloop()
