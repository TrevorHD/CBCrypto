##### Load packages ---------------------------------------------------------------------------------------

# Import packages for GUI
from tkinter import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
    fig = Figure(figsize = (9, 6))
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
    
    # Create Tkinter canvas with Matplotlib figure
    canvas = FigureCanvasTkAgg(fig, master = window)  
    canvas.draw()
  
    # Place canvas in Tkinter window
    canvas.get_tk_widget().place(x = 75, y = 80)   
  
# Create Tkinter window
window = Tk()
  
# Set window title
window.title("CBCrypto: Cryptocurrency Dashboard")
  
# Set window dimensions
window.geometry("500x500")

# Set timeframe button label
#Label(window, text = "Timeframe", justify = LEFT, padx = 20).pack()

# Set timeframe button state
bState = IntVar()
bState.set(2) 

# Build initial plot
buildPlot()

# Control plot timeframe with radiobuttons
Radiobutton(window, command = buildPlot, text = "1h", padx = 20, variable = bState, value = 1).pack(anchor = W)
Radiobutton(window, command = buildPlot, text = "1d", padx = 20, variable = bState, value = 2).pack(anchor = W)
Radiobutton(window, command = buildPlot, text = "1wk", padx = 20, variable = bState, value = 3).pack(anchor = W)
Radiobutton(window, command = buildPlot, text = "1m", padx = 20, variable = bState, value = 4).pack(anchor = W)
Radiobutton(window, command = buildPlot, text = "3m", padx = 20, variable = bState, value = 5).pack(anchor = W)
Radiobutton(window, command = buildPlot, text = "6m", padx = 20, variable = bState, value = 6).pack(anchor = W)
Radiobutton(window, command = buildPlot, text = "1yr", padx = 20, variable = bState, value = 7).pack(anchor = W)
  
# Run Tkinter window over loop
window.mainloop()
