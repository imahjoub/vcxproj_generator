#-------------------------------------------------------------------------------
# Name     :   run_vcxproj_generator
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

#-------------------------------------------------------------------------------
# --- Tkinter initialization
#-------------------------------------------------------------------------------
# --- Create the parent window (root)
root = tkinter.Tk()
root.geometry("1000x600")
root.configure(bg="#5c8aFF") # Light DEE4E7

# --- Window title
root.title("Vcxproj-Generator version 1.0.1")

# --- Disable the resize button (GUI window size)
root.resizable(0,0)

# --- GUI iconbitmap
IconData= base64.b64decode(IconInBase64Format)
TmpFile= "IconInBase64Format.ico"
IconFile= open(TmpFile,"wb")
IconFile.write(IconData)
IconFile.close()
root.wm_iconbitmap(TmpFile)
os.remove(TmpFile)

# --- Create a tab control
TabControl = ttk.Notebook(root)
TabControl.pack(expand=1, fill="both")

# --- Create a main tab
MainTab = ttk.Frame(TabControl)
TabControl.add(MainTab, text="")

# ---- Global variable for default working directory
WorkingDir    = StringVar()
CurDirCount   = len(os.listdir(os.getcwd())) # check if curdir is empty
WorkingDir.set(os.getcwd())

#-------------------------------------------------------------------------------
# --- Global variables
#-------------------------------------------------------------------------------
RelaseVar       = IntVar(value=0)
DebugVar        = IntVar(value=0)
X64Var          = IntVar(value=0)
Win32Var        = IntVar(value=0)
WorkDirIsOk     = IntVar(value=CurDirCount)
AllVarList      = (RelaseVar, DebugVar, Win32Var, X64Var, WorkDirIsOk)

#-------------------------------------------------------------------------------
# --- Run Gui
#-------------------------------------------------------------------------------
GUI(TabControl, WorkingDir, AllVarList)

#-------------------------------------------------------------------------------
# --- Mainloop: loop forever until the user exits the window
#               or waits for any events from the user
#-------------------------------------------------------------------------------
root.mainloop()
