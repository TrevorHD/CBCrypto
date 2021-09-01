# Overview

A cryptocurrency desktop application built using Python, Tk/Tcl, and the API from Coinbase (a popular cryptocurrency trading platform). Includes visualisation and statistics on market trends, user portfolio summary and transaction history, and trading support for buying/selling/converting various cryptocurrencies such as Bitcoin, Litecoin, Etherium, etc.

<br/>

# Files

## Scripts

**00_RunAll** *(.py)* - Script that runs CBCrypto in its entirety.

**01_Imports** *(.py)* - Script responsible for managing imports of packages/modules necessary to run the program.

**02_CoreAPI** *(.py)* - Script defining all functions that are used in pulling information from the Coinbase API.

**03_CoreGUI** *(.py)* - Script defining all functions used in setting up and running the GUI

**04_RunGui** *(.py)* - Script that runs the GUI.

## Other

**S1_OldCode** *(.py)* - Code from older versions of the program that, while currently unused, is kept here just in case it is needed again.

**UserData** *(.txt)* - File responsible for storing user data between application launches.

**TclTheme** *(folder)* - Folder containing files responsible for managing the Tcl theme used by the application; these files are created by Brad Lanam and can be found [here](https://sourceforge.net/projects/tcl-awthemes/).
