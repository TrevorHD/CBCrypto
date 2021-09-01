# Overview

A cryptocurrency desktop application built using Python, Tk/Tcl, and the API from Coinbase (a popular cryptocurrency trading platform). Includes visualisation and statistics on market trends, user portfolio summary and transaction history, and trading support for buying/selling/converting various cryptocurrencies such as Bitcoin, Litecoin, Etherium, etc.

<br/>

# Files

## Scripts

**00_RunAll** *(.py)* - Script that runs CBCrypto in its entirety.

**01_Imports** *(.py)* - Script responsible for managing imports of packages/modules necessary to run the program.

**02_CoreAPI** *(.py)* - Script defining all functions that are used in pulling information from the Coinbase API.

**03_CoreGUI** *(.py)* - Script defining all functions used in setting up and running the GUI.

**04_RunGui** *(.py)* - Script that runs the GUI.

**S1_OldCode** *(.py)* - Code from older versions of the program that, while currently unused, is kept here just in case it is needed again.

## Screenshots

**MS1-3** *(.jpeg)* - Screenshots from the application's main pages: cryptocurrency overview, portfolio overview, and trade screen.

**SS1-2** *(.jpeg)* - Screenshots from the login and splash screens.

## Other

**Logo** *(.png)* - Logo for the application that is used on the splash screen, window bar, and taskbar.

**UserData** *(.txt)* - File responsible for storing user data between application launches.

**TclTheme** *(folder)* - Folder containing files responsible for managing the Tcl theme used by the application; these files are created by Brad Lanam and can be found [here](https://sourceforge.net/projects/tcl-awthemes/).

<br/>

# Featured Images

The "Overview" screen displays, for several cryptocurrencies with the highest market cap, a time series of cryptocurrency value relative to its opening price for a variety of time periods; it also displays some of the top and bottom movers over the past 24 hours. 

<kbd>![](https://github.com/TrevorHD/CBCrypto/blob/main/Screenshots/MS1.png)</kbd>

The "My Portfolio" screen displays, for currencies that the user owns, a time series of cryptocurrency value relative to its opening price for a variety of time periods; it also displays the USD value of owned cryptocurrencies, the percentage of the portfolio that each currency constitutes, and information regarding cost basis and return on investment. 

<kbd>![](https://github.com/TrevorHD/CBCrypto/blob/main/Screenshots/MS2.png)</kbd>

The "Trade" screen allows the user to buy, sell, or convert cryptocurrencies, and to specify the desired amount in either dollars or crypto. Transaction totals are displayed, as are the fees that Coinbase collects, and a time series for each currency is also shown. The user's transaction history is displayed as well.

<kbd>![](https://github.com/TrevorHD/CBCrypto/blob/main/Screenshots/MS3.png)</kbd>

Upon launching the application, the user is greeted with a splash screen with the application logo and is required to enter their API key and API secret before continuing. After successful authentication with the Coinbase API, the application takes a minute or two to load and displays loading progress.

<kbd>![](https://github.com/TrevorHD/CBCrypto/blob/main/Screenshots/SS1.png)</kbd>

<kbd>![](https://github.com/TrevorHD/CBCrypto/blob/main/Screenshots/SS2.png)</kbd>
