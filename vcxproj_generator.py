#-------------------------------------------------------------------------------
# Name     :   vcxproj_generator
#
# Author   :   Iliass Mahjoub
#
# Created  :   28/06/2022
# Copyright:   (c) Iliass Mahjoub
#
# Licence  :   Distributed under the Boost Software License,
#              Version 1.0. (See accompanying file LICENSE_1_0.txt
#              or copy at http://www.boost.org/LICENSE_1_0.txt)
#-------------------------------------------------------------------------------

# import python packages
import uuid

import os, sys
import subprocess
import re
import threading
import tkinter
import tkinter as tk

from dataclasses import dataclass
from idlelib.tooltip import Hovertip

from PIL import ImageTk
from select import select
from tkinter import ttk
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import *
from fnmatch import fnmatch
#-------------------------------------------------------------------------------
# Global variables
#-------------------------------------------------------------------------------
HEADER_EXT = ['.h', '.inl', '.hpp']
SOURCE_EXT = ['.c', '.cc', '.cpp']
NONE_EXT   = ['.gmk', '.ld']
VS_VERSION = '2015' # 2013 or 2015

PROJECT_NAME    = '' # by default will use current directory name

#-----------------------------------------------------------------------------------
# Global functions
#-----------------------------------------------------------------------------------
def Toolset():
    versions = {
        '2013': '12',
        '2015': '14',
    }
    #defaults to vs2013
    return versions.get(VS_VERSION, '12')

def UUID(name):
    return str(uuid.uuid3(uuid.NAMESPACE_OID, name)).upper()

def IsDebug(configuration):
    return 'debug' in configuration.lower()

def FilterFromPath(path):
    (head, tail) = os.path.split(path)
    head = head.replace('/', '\\').replace('..\\', '').replace('.\\', '')
    if head == '.':
        return ''
    return head

#-----------------------------------------------------------------------------------
# --- Vcxproj class
#-----------------------------------------------------------------------------------
class Vcxproj:
    Header = '<?xml version="1.0" encoding="utf-8"?>'
    Project0 = '<Project DefaultTargets="Build" ToolsVersion="{}.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">'.format(Toolset())
    Project1 = '</Project>'
    ProjectConfigurations0 = '  <ItemGroup Label="ProjectConfigurations">'
    ProjectConfigurations1 = '  </ItemGroup>'
    # configuration, platform
    ConfigurationT = '\n'.join([
            '    <ProjectConfiguration Include="{0}|{1}">',
            '      <Configuration>{0}</Configuration>',
            '      <Platform>{1}</Platform>',
            '    </ProjectConfiguration>'])
    # project name, project uuid
    GlobalsT = '\n'.join([
            '  <PropertyGroup Label="Globals">',
            '    <ProjectGuid>{{{1}}}</ProjectGuid>',
            '    <RootNamespace>{0}</RootNamespace>',
            '  </PropertyGroup>'])
    # configuration, platform, debug
    PropertyT = '\n'.join([
            '  <PropertyGroup Condition="\'$(Configuration)|$(Platform)\'==\'{0}|{1}\'" Label="Configuration">',
            '    <ConfigurationType>Application</ConfigurationType>',
            '    <UseDebugLibraries>{2}</UseDebugLibraries>',
            '    <PlatformToolset>v{}0</PlatformToolset>'.format(Toolset()),
            '    <CharacterSet>MultiByte</CharacterSet>',
            '  </PropertyGroup>'])
    # configuration, platform
    ItemDefenitionDebugT = '\n'.join([
        '  <ItemDefinitionGroup Condition="\'$(Configuration)|$(Platform)\'==\'{0}|{1}\'">',
        '    <ClCompile>',
        '      <WarningLevel>Level3</WarningLevel>',
        '      <Optimization>Disabled</Optimization>',
        '      <SDLCheck>true</SDLCheck>',
        '      <PreprocessorDefinitions>%(PreprocessorDefinitions)</PreprocessorDefinitions>',
        '    </ClCompile>',
        '    <Link>',
        '      <GenerateDebugInformation>true</GenerateDebugInformation>',
        '    </Link>',
        '  </ItemDefinitionGroup>'])
    # configuration, platform
    ItemDefenitionReleaseT = '\n'.join([
        '  <ItemDefinitionGroup Condition="\'$(Configuration)|$(Platform)\'==\'{0}|{1}\'">',
        '    <ClCompile>',
        '      <WarningLevel>Level3</WarningLevel>',
        '      <Optimization>MaxSpeed</Optimization>',
        '      <FunctionLevelLinking>true</FunctionLevelLinking>',
        '      <IntrinsicFunctions>true</IntrinsicFunctions>',
        '      <SDLCheck>true</SDLCheck>',
        '      <PreprocessorDefinitions>%(PreprocessorDefinitions)</PreprocessorDefinitions>',
        '    </ClCompile>',
        '    <Link>',
        '      <GenerateDebugInformation>true</GenerateDebugInformation>',
        '      <EnableCOMDATFolding>true</EnableCOMDATFolding>',
        '      <OptimizeReferences>true</OptimizeReferences>',
        '    </Link>',
        '  </ItemDefinitionGroup>'])
    ItemGroup0 = '  <ItemGroup>'
    ItemGroup1 = '  </ItemGroup>'
    # path
    IncludesT = '    <ClInclude Include="{0}" />'
    # path
    SourcesT = '    <ClCompile Include="{0}" />'
    # path
    NonesT   = '    <None Include="{0}" />'


    ImportTargets = '  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.targets" />'
    ImportProps = '  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.props" />'
    ImportDefaultProps = '  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.Default.props" />'

    @staticmethod
    def Configuration(configuration, platform):
        return Vcxproj.ConfigurationT.format(configuration, platform)
    @staticmethod
    def Globals(name):
        uid = UUID(name)
        return Vcxproj.GlobalsT.format(name, uid)
    @staticmethod
    def Property(configuration, platform):
        debug = 'false'
        if IsDebug(configuration) : debug = 'true'
        return Vcxproj.PropertyT.format(configuration, platform, debug)
    @staticmethod
    def ItemDefenition(configuration, platform):
        defenition = Vcxproj.ItemDefenitionReleaseT
        if IsDebug(configuration): defenition = Vcxproj.ItemDefenitionDebugT
        return defenition.format(configuration, platform)
    @staticmethod
    def Includes(name):
        return Vcxproj.IncludesT.format(name)
    @staticmethod
    def Sources(name):
        return Vcxproj.SourcesT.format(name)
    @staticmethod
    def Nones(name):
        return Vcxproj.NonesT.format(name)

#-----------------------------------------------------------------------------------
# --- Filters class
#-----------------------------------------------------------------------------------
class Filters:
    Header = '<?xml version="1.0" encoding="utf-8"?>'
    Project0 = '<Project ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">'
    Project1 = '</Project>'
    ItemGroup0 = '  <ItemGroup>'
    ItemGroup1 = '  </ItemGroup>'
    # path, folder
    SourcesT = '\n'.join([
        '    <ClCompile Include="{0}">',
        '      <Filter>{1}</Filter>',
        '    </ClCompile>'])
    # path, folder
    NonesT = '\n'.join([
        '    <None Include="{0}">',
        '      <Filter>{1}</Filter>',
        '    </None>'])
    # path, folder
    IncludesT = '\n'.join([
        '    <ClInclude Include="{0}">',
        '      <Filter>{1}</Filter>',
        '    </ClInclude>'])
    # folder, uuid
    FoldersT = '\n'.join([
        '    <Filter Include="{0}">',
        '      <UniqueIdentifier>{{{1}}}</UniqueIdentifier>',
        '    </Filter>'])

    @staticmethod
    def Nones(path):
        folder = FilterFromPath(path)
        return Filters.NonesT.format(path, folder)
    @staticmethod
    def Sources(path):
        folder = FilterFromPath(path)
        return Filters.SourcesT.format(path, folder)
    @staticmethod
    def Includes(path):
        folder = FilterFromPath(path)
        return Filters.IncludesT.format(path, folder)
    @staticmethod
    def Folders(folder):
        uid = UUID(folder)
        return Filters.FoldersT.format(folder, uid)

#-----------------------------------------------------------------------------------
# --- Generator class
#-----------------------------------------------------------------------------------
class Generator:
    Folders        = set()
    Includes       = set()
    Sources        = set()
    Nones          = set()
    Platforms      = set()
    Configurations = set()
    Name           = ''

    def __init__(self, name, platforms, configurations):
        self.Name = name
        for platform in platforms:
            self.Platforms.add(platform)
        for configuration in configurations:
            self.Configurations.add(configuration)

    def AddFolder(self, path):
        filt = FilterFromPath(path)
        if filt == '':
            return
        if filt not in self.Folders:
            self.Folders.add(filt)
            filters = ''
            for f in os.path.split(filt):
                filters = os.path.join(filters, f)
                if filters != '':
                    self.Folders.add(filters)

    def AddSource(self, Filename):
        LocalDir = "".join(( ".\\", Filename))
        self.Sources.add(str(LocalDir))

    def AddNone(self, Filename):
        LocalDir = "".join(( ".\\", Filename))
        self.Nones.add(str(LocalDir))

    def AddHeader(self, Filename):
        LocalDir = "".join(( ".\\", Filename))
        self.Includes.add(str(LocalDir))

    def RemoveRelativPath(self, Dir, RootDir):
        RootDir = "".join((RootDir, "\\"))
        LocalDir = Dir.replace(RootDir, "")
        return LocalDir

    def AddFile(self, Dir, RootDir):
        LocalDir = self.RemoveRelativPath(Dir, RootDir)
        (root, ext) = os.path.splitext(Dir)
        if ext in HEADER_EXT:
            self.AddHeader(str(LocalDir))
        elif ext in SOURCE_EXT:
            self.AddSource(str(LocalDir))
        elif ext in NONE_EXT:
            self.AddNone(str(LocalDir))
        else:
            return
        self.AddFolder(str(LocalDir))

    def Walk(self,Dir, RootDir):
        if os.path.isfile(Dir):
            self.AddFile(Dir, RootDir)
        else:
            for subPath in os.listdir(Dir):
                self.Walk(os.path.join(Dir, subPath), RootDir)

    def CreateProject(self):
        project = []
        project.append(Vcxproj.Header)
        project.append(Vcxproj.Project0)

        project.append(Vcxproj.ProjectConfigurations0)
        for c in self.Configurations:
            for p in self.Platforms:
                project.append(Vcxproj.Configuration(c, p))
        project.append(Vcxproj.ProjectConfigurations1)

        project.append(Vcxproj.Globals(self.Name))

        project.append(Vcxproj.ImportDefaultProps)

        for c in self.Configurations:
            for p in self.Platforms:
                project.append(Vcxproj.Property(c, p))

        project.append(Vcxproj.ImportProps)

        for c in self.Configurations:
            for p in self.Platforms:
                project.append(Vcxproj.ItemDefenition(c, p))

        project.append(Vcxproj.ItemGroup0)
        for f in self.Includes:
            project.append(Vcxproj.Includes(f))
        project.append(Vcxproj.ItemGroup1)

        project.append(Vcxproj.ItemGroup0)
        for f in self.Sources:
            project.append(Vcxproj.Sources(f))
        project.append(Vcxproj.ItemGroup1)
        project.append(Vcxproj.ImportTargets)

        project.append(Vcxproj.ItemGroup0)
        for f in self.Nones:
            project.append(Vcxproj.Nones(f))
        project.append(Vcxproj.ItemGroup1)
        project.append(Vcxproj.ImportTargets)

        project.append(Vcxproj.Project1)
        return '\n'.join(project)

    def CreateFilters(self):
        project = []
        project.append(Filters.Header)
        project.append(Filters.Project0)

        project.append(Filters.ItemGroup0)
        for f in self.Folders:
            project.append(Filters.Folders(f))
        project.append(Filters.ItemGroup1)

        project.append(Filters.ItemGroup0)
        for f in self.Nones:
            project.append(Filters.Nones(f))
        project.append(Filters.ItemGroup1)

        project.append(Filters.ItemGroup0)
        for f in self.Includes:
            project.append(Filters.Includes(f))
        project.append(Filters.ItemGroup1)

        project.append(Filters.ItemGroup0)
        for f in self.Sources:
            project.append(Filters.Sources(f))
        project.append(Filters.ItemGroup1)

        project.append(Filters.Project1)
        return '\n'.join(project)

    def Generate(self):
        # Check if file exists and delete them
        if os.path.exists(self.Name + '.vcxproj'):
           os.remove(self.Name + '.vcxproj')
        if os.path.exists(self.Name + '.vcxproj'):
           os.remove(self.Name + '.vcxproj.filters')

        f = open(self.Name + '.vcxproj', 'w')
        f.write(self.CreateProject())
        f.close()

        f = open(self.Name + '.vcxproj.filters', 'w')
        f.write(self.CreateFilters())
        f.close()

       # print("--- Source Files ---")
       # for idx in self.Sources:
       #   print(idx)

       # print("--- None Files ---")
       # for idx in self.Nones:
       #   print(idx)

       # print("--- Header Files ---")
       # for idx in self.Includes:
       #   print(idx)


#-----------------------------------------------------------------------------------
# --- GUI class
#-----------------------------------------------------------------------------------
class GUI:
  Configurations = []
  Platforms      = []

  def __init__(self, TabControl, WorkingDir, AllVarList):
    self.PrintMsvcConfigFrame(TabControl, WorkingDir, AllVarList)
    self.PrintCmdLineFrame(TabControl)

  def GetAndCheckUserDir(self,WorkingDir, AllVarList):
    # help function for "select folder" button
    FolderSelected = filedialog.askdirectory()
    WorkingDir.set(FolderSelected)
    #check if given path exists and not empty
    AllVarList[4].set(    os.path.exists(WorkingDir.get())
                      and len(os.listdir(WorkingDir.get())))

    if AllVarList[4].get() == 0:
      # show error message box
      tk.messagebox.showerror(title="Error", message=" Vcxproj-Generator: selected folder is either empty or invalid!")

  def main_xx(self, WorkingDir, Platforms, Configurations):
    name = os.path.split(os.getcwd())[-1]
    generator = Generator(name, Platforms, Configurations)

    #print("******************")
    #for idx in Platforms:
    #  print(idx)
    #for idx in Configurations:
    #  print(idx)
    #print("******************")

    RootDir = WorkingDir.get()
    path_as_list = list(RootDir.split(","))
    for Dir in path_as_list:
        generator.Walk(Dir, RootDir)
    generator.Generate()

  def GetProjectConfig(self, AllVarList):
    print("####################################################################")
    self.Configurations.clear()
    self.Platforms.clear()
    if (AllVarList[0].get() != 0 and AllVarList[1].get() == 0):
        print("***** Release *****")
        self.Configurations = ['Release']

    if (AllVarList[0].get() == 0 and AllVarList[1].get() != 0):
        print("****** Debug ******")
        self.Configurations = ['Debug']

    if (AllVarList[0].get() != 0 and AllVarList[1].get() != 0):
        print("**** Release - Debug ****")
        self.Configurations = ['Release', 'Debug']

    if (AllVarList[2].get() != 0 and AllVarList[3].get() == 0):
        print("****** Win32 ********")
        self.Platforms = ['Win32']
    if (AllVarList[2].get() == 0 and AllVarList[3].get() != 0):
       print("****** x64 ********")
       self.Platforms = ['x64']
    if (AllVarList[2].get() != 0 and AllVarList[3].get() != 0):
        print("***** Win32 - x64 ******")
        self.Platforms = ['x64', 'Win32']

    for idx_1 in self.Configurations:
      print(idx_1)
    for idx_2 in self.Platforms:
      print(idx_2)



    print("####################################################################")

  def GenerateVcxprojFile(self, CombBox, WorkingDir, AllVarList):
    SlnConfigIsOk = (AllVarList[0].get() != 0 or  AllVarList[1].get() != 0)
    PlatformIsOk  = (AllVarList[2].get() != 0 or  AllVarList[3].get() != 0)
    PathIsOk      =  AllVarList[4].get() != 0
    MSVSVerIsOk   =  CombBox.current()   != -1

    if PathIsOk == True:
      if MSVSVerIsOk == True:
        if SlnConfigIsOk == True and PlatformIsOk == True:
          self.GetProjectConfig(AllVarList)
          #for idx in self.Platforms:
          #  print("+++++++")
          #  print(idx)
          #  print("+++++++")
          self.main_xx(WorkingDir, self.Platforms, self.Configurations)
        else:
          tk.messagebox.showerror(title="Error", message=" Vcxproj-Generator: Project config are not selected!")
      else:
        tk.messagebox.showerror(title="Error", message=" Vcxproj-Generator: MSVS is not selected!")
    else:
      tk.messagebox.showerror(title="Error", message=" Vcxproj-Generator: Folder is not selected or empty!")


  def PrintMsvcConfigFrame(self, TabControl, WorkingDir, AllVarList):
    # Create frame for MSVC config widgets
    MsvcConfigFrame = tk.LabelFrame(TabControl, text=' Visual Studio Config ',relief=GROOVE, bd='3')
    MsvcConfigFrame.configure(font="times 11 bold")
    MsvcConfigFrame.place(x=20, y=20, height=220, width=950)

    # Create the working dir entry box
    WdEntryBox = Entry(MsvcConfigFrame, textvariable=WorkingDir)
    WdEntryBox.place(x=20, y=20, height=35, width=750)
    WdEntryBox.configure(font="times 11")

    # Create the working dir browsing button
    WdBrowsingBtN = ttk.Button(MsvcConfigFrame, text="Select folder",
      command = lambda: GUI.GetAndCheckUserDir(WorkingDir, AllVarList), width=20)
    WdBrowsingBtN.place(x=790, y=20, height=35)

    # Create a combobox for MSVC version
    MsvcVersion = Label(MsvcConfigFrame ,text="Visual Studio Version")
    MsvcVersion.place(x=20, y=90)
    MsvcVersion.configure(font="times 10 bold")

    text_font = ('times', '9')
    CombBox = ttk.Combobox(MsvcConfigFrame, state="readonly", font=text_font)
    CombBox['values'] =('vs2017', 'vs2019', 'vs2022')
    CombBox.place(x=20, y=120, height=35, width=200)

    # Create "Generate vcxproj files" button
    GenerateBtN = ttk.Button(MsvcConfigFrame, text="Generate vcxproj files",
      command = lambda:
        self.GenerateVcxprojFile(CombBox, WorkingDir, AllVarList), width=30)
    GenerateBtN.place(x=700, y=100, height=60)

    # Create a frame for Solution configurations and platform
    ProjectConfigFrame = tk.LabelFrame(MsvcConfigFrame,
      text=" Solution configurations and platforms ",
      relief=GROOVE, bd='2')
    ProjectConfigFrame.configure(font="times 11 bold")
    ProjectConfigFrame.place(x=250, y=80, height=100, width=400)

    # print project config
    ProjectConfigList   = [" Release ", " Debug " ]
    ProjectPlatformList = [" Win32 "  , " x64 " ]

    ProjectConfigYCordinate = [10, 40]

    for Idx in range(2):
      # Create project config labels
      ProjectConfigLabel = Label(ProjectConfigFrame ,text=ProjectConfigList[Idx])
      ProjectConfigLabel.place(x=40, y=ProjectConfigYCordinate[Idx])
      ProjectConfigLabel.configure(font="times 10")

      ProjectplatformLabel = Label(ProjectConfigFrame ,text=ProjectPlatformList[Idx])
      ProjectplatformLabel.place(x=140, y=ProjectConfigYCordinate[Idx])
      ProjectplatformLabel.configure(font="times 10")


      # Create project config checkbuttons
      ProjectConfigCheckBtn = ttk.Checkbutton(ProjectConfigFrame,
        variable= AllVarList[Idx],
        onvalue=1, offvalue=0).place(x=20,
        y=ProjectConfigYCordinate[Idx])

      ProjectplatformCheckBtn = ttk.Checkbutton(ProjectConfigFrame,
        variable= AllVarList[Idx + 2],  # TBD change this hard coded iteration
        onvalue=1, offvalue=0).place(x=120,
        y=ProjectConfigYCordinate[Idx])

  def PrintCmdLineFrame(self, TabControl):
    # Create cmd line output window
    CmdLineWindow = tk.LabelFrame(TabControl, text=" Output ", relief=GROOVE, bd='3')
    CmdLineWindow.configure(font="times 11 bold")
    CmdLineWindow.place(x=20, y=250, height=340, width=950)

    # Create a scrollbar text frame for programm results
    ScrollBar_V = tk.Scrollbar(CmdLineWindow, orient= VERTICAL)
    ScrollBar_V.pack(side= RIGHT,fill="y")

    ScrollBar_H = tk.Scrollbar(CmdLineWindow, orient= HORIZONTAL)
    ScrollBar_H.pack(side= BOTTOM, fill= "x")

    OutputText = tk.Text(CmdLineWindow, height= 440, width= 370,
                         yscrollcommand = ScrollBar_V.set,
                         xscrollcommand = ScrollBar_H.set, wrap= NONE)
    OutputText.pack(fill=BOTH, expand=0)

    # Assign the scrollbar with the text widget
    ScrollBar_H['command'] = OutputText.xview
    ScrollBar_V['command'] = OutputText.yview
