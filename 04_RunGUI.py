##### Run login screen ------------------------------------------------------------------------------------

# Create TkInter window
w1 = Tk()

# Set application ID so icon shows up on Windows taskbar
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u'process.cbcrypto')

# Set window theme
w1.tk.call("lappend", "auto_path", "TclTheme")
w1.tk.call("package", "require", "awdark") 
ttk.Style().theme_use("awdark") 

# Set window title, dimensions, and colour
w1.title("CBCrypto: Cryptocurrency Dashboard")
w1.geometry("1920x1080")
w1.configure(bg = "#33393b")
w1.state("zoomed")

# Set window icon
icon = ImageTk.PhotoImage(Image.open("Logo.png"))
w1.wm_iconphoto(False, icon)

# Add app logo as image on canvas
icon2 = ImageTk.PhotoImage(Image.open("Logo.png").resize((500, 500), Image.ANTIALIAS))
w1_cvs = Canvas(w1, width = 460, height = 460, bg = "#33393b", highlightthickness = 1)
w1_cvs.place(x = 500, y = 75)
w1_cvs.create_image((230, 230), anchor = CENTER, image = icon2)

# Add app name as label below logo
w1_l1 = Label(w1, text = "CBCrypto: Cryptocurrency Dashboard", justify = CENTER,
              bg = "#33393b", bd = 0, font = ("Arial", 17), fg = "white")
w1_l1.place(x = 537, y = 550)

# Initialise text entry variables
# Add entry boxes for API Key and Secret
w1_eState1, w1_eState2 = StringVar(), StringVar()
w1_e1 = ttk.Entry(w1, textvariable = w1_eState1, width = 50, foreground = "grey")
w1_e1.place(x = 575, y = 628)
w1_e1.insert(0, "API Key")
w1_e2 = ttk.Entry(w1, textvariable = w1_eState2, width = 50, foreground = "grey")
w1_e2.place(x = 575, y = 660)
w1_e2.insert(0, "API Secret")

# Add entry bindings to mask/unmask text
w1_e1.bind("<FocusIn>", lambda e:[loginFocus(eBox = 1)])
w1_e1.bind("<FocusOut>", lambda e:[loginUnfocus(eBox = 1)])
w1_e2.bind("<FocusIn>", lambda e:[loginFocus(eBox = 2)])
w1_e2.bind("<FocusOut>", lambda e:[loginUnfocus(eBox = 2)])

# Add key bindings to enable/disable login
w1_e1.bind("<Key>", lambda e:[loginDisable()])
w1_e2.bind("<Key>", lambda e:[loginDisable()])

# Add button to connect to Coinbase API
w1_b1 = ttk.Button(w1, text = "Continue", command = userAuth, width = 9)
w1_b1.place(x = 650, y = 700)
w1_b1.state(["disabled"])

# Add button to reset entry box text
w1_b2 = ttk.Button(w1, text = "Reset", command = lambda:[loginReset(), loginDisable()], width = 9)
w1_b2.place(x = 740, y = 700)

# Add blank label; will display message when authentication fails
w1_l2 = Label(w1, text = "", justify = CENTER, bg = "#33393b", bd = 0,
              font = ("Arial", 14), fg = "red")
w1_l2.place(x = 642, y = 750)

# Run TkInter window over loop
w1.mainloop()

# Prevent rest of program from running if user quits before authentication
if "client" not in globals():
    sys.exit()





##### Run splash screen and main window -------------------------------------------------------------------

# Create main TkInter window
w3 = Tk()

# Set application ID so icon shows up on Windows taskbar
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u'process.cbcrypto')

# Set main window theme
w3.tk.call("lappend", "auto_path", "TclTheme")
w3.tk.call("package", "require", "awdark") 
ttk.Style().theme_use("awdark")
ttk.Style().configure("My.TSpinbox", arrowsize = 11)
ttk.Style().configure("small.TButton", font = (None, 5))
 
# Set main window title, dimensions, and colour
w3.title("CBCrypto: Cryptocurrency Dashboard")
w3.geometry("1920x1080")
w3.configure(bg = "#33393b")

# Set main window icon
icon = ImageTk.PhotoImage(Image.open("Logo.png"))
w3.wm_iconphoto(False, icon)

# Minimise main window and run splash screen while app is loading
# Add logo, text, and progress bar to splash screen
w3.withdraw()
w2 = Toplevel()
w2.state("zoomed")
w2.title("CBCrypto: Cryptocurrency Dashboard")
w2.geometry("1920x1080")
w2.configure(bg = "#33393b")
w2.wm_iconphoto(False, icon)
icon2 = ImageTk.PhotoImage(Image.open("Logo.png").resize((500, 500), Image.ANTIALIAS))
w2_cvs = Canvas(w2, width = 460, height = 460, bg = "#33393b", highlightthickness = 1)
w2_cvs.place(x = 500, y = 75)
w2_cvs.create_image((230, 230), anchor = CENTER, image = icon2)
w2_p1 = ttk.Progressbar(w2, orient = HORIZONTAL, length = 300, mode = "determinate")
w2_p1.place(x = 580, y = 700)
w2_pState = IntVar()
w2_pState.set(0)
w2_l1 = Label(w2, text = "CBCrypto: Cryptocurrency Dashboard", justify = "center",
              bg = "#33393b", bd = 0, font = ("Arial", 17), fg = "white")
w2_l1.place(x = 537, y = 550)
w2_l2 = Label(w2, text = "Loading... (0%)", justify = "center",
              bg = "#33393b", bd = 0, font = ("Arial", 10), fg = "white")
w2_l2.place(x = 682, y = 726)
w2.update()

# Set application screen tabs
w3_tC = ttk.Notebook(w3)
w3_t1 = ttk.Frame(w3_tC)
w3_t2 = ttk.Frame(w3_tC)
w3_t3 = ttk.Frame(w3_tC)
w3_tC.add(w3_t1, text = "Overview")
w3_tC.add(w3_t2, text = "My Portfolio")
w3_tC.add(w3_t3, text = "Trade")
w3_tC.pack(expand = 1, fill = "both")

# Set up main window graphics, each plotted on their own canvas
w3_figX = [pyplot.figure(figsize = [(12.00, 6.00), (11.89, 3.65), (6.97, 9.51), (12.00, 6.00),
                                    (6.97, 5.43), (10.00, 0.30), (19.14, 3.65), (7.50, 6.00),
                                    (6.80, 3.60), (10.80, 9.50), (5.00, 0.25)][x],
                         edgecolor = ["white" if w in [3, 5, 10] else "#33393b" for w in range(1, 12)][x],
                         facecolor = "#33393b", linewidth = 2) for x in range(0, 11)]
w3_figL = [w3_t1]*3 + [w3_t2]*4 + [w3_t3]*3 + [w3]
w3_cvsX = [FigureCanvasTkAgg(w3_figX[x], master = w3_figL[x]) for x in range(0, len(w3_figX))]

# Place all graphics
for i in range(0, len(w3_figX)):
    w3_cvsX[i].get_tk_widget().place(x = [19, 26, 890, 19, 890, 749, 26, 51, 90, 614, 980][i], 
                                     y = [50, 500, 67, 50, 67, 44, 500, 50, 500, 67, 7][i])
    
# Set up pop-up window trade confirmation graphic
w4_fig = pyplot.figure(figsize = (4.9, 2), facecolor = "#33393b")

# Graphic orders from above:
# 1: time series chart [w3_t1]
# 2: currency overview [w3_t1]
# 3: top/bottom movers [w3_t1]
# 4: time series chart [w3_t2]
# 5: holdings chart [w3_t2]
# 6: portfolio change text [w3_t2]
# 7: portfolio overview [w3_t2]
# 8: time series chart [w3_t3]
# 9: trade text [w3_t3]
# 10: transaction history [w3_t3]
# 11: refresh text [w3]
# 12: trade confirmation [w4]

# Set state variables for buttons, text, and menus
w3_bState1, w3_bState2, w3_bState3 = IntVar(), IntVar(), IntVar()
w3_tState1, w3_tState2, w3_tState3 = IntVar(), IntVar(), IntVar()
w3_tState1.set(1)
w3_eState1, w3_eState2 = StringVar(), StringVar()
w3_cState1, w3_cState2 = StringVar(), StringVar()
w3_cState1.set("BTC")
w3_sState = IntVar()
w3_rState = IntVar()
w3_rState.set(0)
w3_fState = IntVar()
w3_fState.set(0)

# Add master refresh button in top-right corner
# Run once on startup and again any time button is pressed
w3_b1 = ttk.Button(w3, text = "Refresh", style = "small.TButton",
                   command = lambda:[fullRefresh(rType = "manual")])
#w3_b1.place(x = 1390, y = 1, width = 30, height = 20)
w3_b1.place(x = 1420, y = 6)
fullRefresh()

# Add trade button to buy/sell/convert currency
w3_b2 = ttk.Button(w3_t3, text = "Confirm", command = tradeWindow, width = 9)
w3_b2.place(x = 101, y = 675)

# Add button to reset trade settings
w3_b3 = ttk.Button(w3_t3, text = "Reset", width = 9,
                command = lambda:[resetTrades(), clearBox(), placeMenu(), changeList(), 
                                  disableTrades(), plotTrade(), plotSeries(dType = "trade")])
w3_b3.place(x = 180, y = 675)

# Add radiobuttons for time series plotting control (Overview)
w3_r1 = [ttk.Radiobutton(w3_t1, command = lambda:[plotSeries()],
                         text = ["1h", "1d", "1wk", "1m", "3m", "6m", "1yr"][x], 
                         variable = w3_bState1, value = x + 1) for x in range(0, 7)]
for i in range(0, len(w3_r1)):
    w3_r1[i].place(x = [103, 163, 223, 283, 343, 403, 463][i], y = 40)

# Add radiobuttons for time series plotting control (Portfolio)
w3_r2 = [ttk.Radiobutton(w3_t2, command = lambda:[plotSeries(dType = "portfolio", currencies = cData)],
                         text = ["1h", "1d", "1wk", "1m", "3m", "6m", "1yr"][x], 
                         variable = w3_bState2, value = x + 1) for x in range(0, 7)]
for i in range(0, len(w3_r2)):
    w3_r2[i].place(x = [103, 163, 223, 283, 343, 403, 463][i], y = 40)
    
# Add radiobuttons for time series plotting control (Trade)
w3_r3 = [ttk.Radiobutton(w3_t3, command = lambda:[plotSeries(dType = "trade")],
                         text = ["1h", "1d", "1wk", "1m", "3m", "6m", "1yr"][x], 
                         variable = w3_bState3, value = x + 1) for x in range(0, 7)]
for i in range(0, len(w3_r3)):
    w3_r3[i].place(x = [103, 163, 223, 283, 343, 403, 463][i], y = 40)

# Add radiobuttons for controlling trade type
w3_r4 = [ttk.Radiobutton(w3_t3, command = lambda:[placeMenu(), changeList(), plotTrade(),
                                                  plotSeries(dType = "trade")],
                         text = ["Buy", "Sell", "Convert"][x], 
                         variable = w3_tState1, value = x + 1) for x in range(0, 3)]
for i in range(0, len(w3_r4)):
    w3_r4[i].place(x = 100, y = [526, 546, 566][i])
    
# Add radiobuttons for controlling trade dollar/crypto input
w3_r5 = [ttk.Radiobutton(w3_t3, command = lambda:[clearBox(), plotTrade(), disableTrades()],
                         text = ["Dollars", "Crypto"][x], 
                         variable = w3_tState2, value = x + 1) for x in range(0, 2)]
for i in range(0, len(w3_r5)):
    w3_r5[i].place(x = 186, y = [526, 546][i])

# Add a first dropdown menu to select currency to buy/sell
# Add a second dropdown menu for currency conversion
w3_c1 = ttk.Combobox(w3_t3, textvariable = w3_cState1, width = 8, state = "readonly",
                     values = [x for x in cbList if x != w3_cState2.get()])
w3_c2 = ttk.Combobox(w3_t3, textvariable = w3_cState2, width = 8, state = "readonly",
                     values = [x for x in cbList if x != w3_cState1.get()])
w3_c1.place(x = 101, y = 608)
w3_c2.place(x = 101, y = 628)

# Add menu bindings for when a menu item is selected
w3_c1.bind("<<ComboboxSelected>>", lambda e:[w3_c1.selection_clear(), changeList(), plotTrade(),
                                             plotSeries(dType = "trade")])
w3_c2.bind("<<ComboboxSelected>>", lambda e:[w3_c2.selection_clear(), changeList(), plotTrade(),
                                             plotSeries(dType = "trade")])

# Define key wrapper for text validation
checkKeyWrapper = (w3.register(checkKey), "%P")

# Add a first entry box to specify currency/dollar amounts
# Add a second entry box for currency conversion
w3_e1 = ttk.Entry(w3_t3, textvariable = w3_eState1, width = 9, validate = "key",
                  validatecommand = checkKeyWrapper)
w3_e1.place(x = 181, y = 608)
w3_e2 = ttk.Entry(w3_t3, textvariable = w3_eState2, width = 9, validate = "key",
                  validatecommand = checkKeyWrapper)
w3_e2.place(x = 181, y = 628)

# Add entry bindings for updating trade information when typing stops
w3_e1.bind("<Key>", lambda e:[entryWait(), clearBox(2)])
w3_e2.bind("<Key>", lambda e:[entryWait(), clearBox(1)])

# Add spinbox to select transaction history page
w3_s1 = ttk.Spinbox(w3_t3, from_ = 1, to = thMaxPage, textvariable = w3_sState, width = 2,
                    font = Font(size = 10), style = "My.TSpinbox",
                    command = lambda:[plotTransactions(tHist = tHist)])
w3_s1.state(["readonly"])
w3_s1.place(x = 620, y = 74)

# Add progress bar indicating when application is loading
w3_p1 = ttk.Progressbar(w3, orient = HORIZONTAL, length = 100, mode = "indeterminate")
w3_p1.place(x = 1315, y = 7)

# Set default button states
w3_b2.state(["disabled"])
w3_r1[1].invoke()
w3_r2[1].invoke()
w3_r3[1].invoke()
w3_r4[0].invoke()
w3_r5[0].invoke()

# End splash screen once app has loaded
w2.destroy()
w3.deiconify()
w3.state("zoomed")

# Run TkInter window over loop
w3.mainloop()

