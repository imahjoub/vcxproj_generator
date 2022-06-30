'''
Copyright Iliass Mahjoub 2022.
Distributed under MIT License
Version 1.0. (See accompanying file LICENSE
or copy at https://opensource.org/licenses/MIT)
'''

# import modules from project
import vcxproj_generator

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


# Script settings

PATHS_TO_SEARCH = ['.']
PROJECT_NAME    = '' # by default will use current directory name
PLATFORMS       = ['Win32', 'x64']
CONFIGURATIONS  = ['Debug', 'Release']


# --- Create the parent window (root)
root = tkinter.Tk()
root.geometry("1000x600")
root.configure(bg="#5c8a8a")

#-----------------------------------------------------------------------------------
# --- main function
# this must be run fron GUI class
#-----------------------------------------------------------------------------------
def main(paths, name, platforms, configurations):
    if name == '':
        name = os.path.split(os.getcwd())[-1]
    generator = vcxproj_generator.Generator(name, platforms, configurations)
    for path in paths:
        generator.Walk(path)
    generator.Generate()

main(PATHS_TO_SEARCH, PROJECT_NAME, PLATFORMS, CONFIGURATIONS)


#-----------------------------------------------------------------------------------
# --- Mainloop: loop forever until the user exits the window
#               or waits for any events from the user
#-----------------------------------------------------------------------------------
root.mainloop()

