#-------------------------------------------------------------------------------
# Name     :   vcxproj_generator_gui
#
# Author   :   Iliass Mahjoub
#
# Created  :   29/06/2022
# Copyright:   (c) Iliass Mahjoub
#
# Licence  :   Distributed under the Boost Software License,
#              Version 1.0. (See accompanying file LICENSE_1_0.txt
#              or copy at http://www.boost.org/LICENSE_1_0.txt)
#-------------------------------------------------------------------------------

# import project files
from vcxproj_generator import *

# --- Create the parent window (root)
root = tkinter.Tk()
root.geometry("1000x600")
root.configure(bg="#5c8aFF") # Light DEE4E7

# --- Window title
root.title("Vcxproj-Generator version 1.0.1")

# --- Deactivate the resize button (GUI window size)
root.resizable(0,0)

# --- GUI logo
# TBD add a logo
#LogoDir = current_dir + "\\xyz\\xyz.png"
#Logo    = ImageTk.PhotoImage(file=LogoDir)

#IconDir = current_dir + "\\xyz\\xyz.ico"
#root.iconbitmap(IconDir)


# --- Create a tab control
TabControl = ttk.Notebook(root)
TabControl.pack(expand=1, fill="both")

# --- Create Tabs and disable it since we only have one ATM
MainTab = ttk.Frame(TabControl)
TabControl.add(MainTab, text="")

# ---- Global variable for User setup
WorkingDir    = StringVar()
CurDirCount   = len(os.listdir(os.getcwd())) # check if curdir is empty
WorkingDir.set(os.getcwd())

# +++++++++++
PATHS_TO_SEARCH = ['.']
PROJECT_NAME    = '' # by default will use current directory name
PLATFORMS       = ['Win32', 'x64']
CONFIGURATIONS  = ['Debug', 'Release']


#-------------------------------------------------------------------------------
# Global variables
#-------------------------------------------------------------------------------
RelaseVar       = IntVar(value=0)
DebugVar        = IntVar(value=0)
X64Var          = IntVar(value=0)
Win32Var        = IntVar(value=0)
WorkDirIsOk     = IntVar(value=CurDirCount)
AllVarList      = (RelaseVar, DebugVar, X64Var, Win32Var, WorkDirIsOk)



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
GUI(TabControl, WorkingDir, AllVarList)

#-----------------------------------------------------------------------------------
# --- Mainloop: loop forever until the user exits the window
#               or waits for any events from the user
#-----------------------------------------------------------------------------------
root.mainloop()
