'''
Copyright Iliass Mahjoub 2022.
Distributed under MIT License
Version 1.0. (See accompanying file LICENSE
or copy at https://opensource.org/licenses/MIT)
'''

# import modules from project
from vcxproj_generator import *

# import modules/packages
import os, uuid
import tkinter
import tkinter as tk
import os, sys
import subprocess
import re
import threading

from select import select
from tkinter import ttk
from tkinter.ttk import *
from idlelib.tooltip import Hovertip
from PIL import ImageTk
from dataclasses import dataclass



# ---- Global variable for User setup
PATHS_TO_SEARCH = ['.']
PROJECT_NAME    = '' # by default will use current directory name
PLATFORMS       = ['Win32', 'x64']
CONFIGURATIONS  = ['Debug', 'Release']


# --- Create the parent window (root)
root = tkinter.Tk()
root.geometry("1000x600")
root.configure(bg="#5c8a8a") # Light DEE4E7

# --- Deactivate the resize button (GUI window size)
root.resizable(0,0)

# --- Create Tkinter Notebook for controlling sxpf-tools tabs
control_tab = ttk.Notebook(root)
control_tab.pack(expand=1, fill="both")

# ---- Global variable for User setup
WorkingDir      = StringVar()
WorkingDir.set(os.getcwd())


#-----------------------------------------------------------------------------------
# --- main function
# this must be run fron GUI class
#-----------------------------------------------------------------------------------
#def main(paths, name, platforms, configurations):
#    if name == '':
#        name = os.path.split(os.getcwd())[-1]
#    generator = vcxproj_generator.Generator(name, platforms, configurations)
#    for path in paths:
#        generator.Walk(path)
#    generator.Generate()

#main(PATHS_TO_SEARCH, PROJECT_NAME, PLATFORMS, CONFIGURATIONS)

#-----------------------------------------------------------------------------------
# --- frame 1: MSVC Setup
#-----------------------------------------------------------------------------------
GUI(control_tab, WorkingDir)

#-----------------------------------------------------------------------------------
# --- Mainloop: loop forever until the user exits the window
#               or waits for any events from the user
#-----------------------------------------------------------------------------------
root.mainloop()

