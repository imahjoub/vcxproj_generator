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

from dataclasses     import dataclass
from idlelib.tooltip import Hovertip

from PIL         import ImageTk
from select      import select
from tkinter     import ttk
from tkinter     import *
from tkinter     import filedialog
from tkinter.ttk import *
from fnmatch     import fnmatch

#-------------------------------------------------------------------------------
# Global variables
#-------------------------------------------------------------------------------
HEADER_EXT = ['.h',  '.in', '.hpp']
SOURCE_EXT = ['.c',  '.cc', '.cpp']
NONE_EXT   = ['.md', '.ld', '.gmk', 'yml']

#-------------------------------------------------------------------------------
# Global functions
#-------------------------------------------------------------------------------
def GetToolsetVersion():
  VsVersion = '15.0' # TBD check which vs version is selected
  return VsVersion

def GenerateUniqueID(Name):
  return str(uuid.uuid3(uuid.NAMESPACE_OID, Name)).upper()

def UseDebugLib(configuration):
  return 'debug' in configuration.lower()

def GetParentPath(Path):
  (FilePath, Filename) = os.path.split(Path)
  FilePath = FilePath.replace('/', '\\').replace('..\\', '').replace('.\\', '')

  if FilePath == '.':
    return ''
  else:
    return FilePath

#-------------------------------------------------------------------------------
# --- Vcxproj class
#-------------------------------------------------------------------------------
class Vcxproj:
  Header = '<?xml version="1.0" encoding="utf-8"?>'
  Project0 = '<Project DefaultTargets="Build" ToolsVersion="{}.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">'.format(GetToolsetVersion())
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
          '    <PlatformToolset>{3}</PlatformToolset>',
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
  # Header files path
  IncludesT = '    <ClInclude Include="{0}" />'
  # Source files path
  SourcesT = '    <ClCompile Include="{0}" />'
  # None files path
  NonesT   = '    <None Include="{0}" />'

  ImportTargets = '  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.targets" />'
  ImportProps   = '  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.props" />'
  ImportDefaultProps = '  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.Default.props" />'

  @staticmethod
  def Configuration(configuration, platform):
    return Vcxproj.ConfigurationT.format(configuration, platform)

  @staticmethod
  def Globals(ProjectName):
    UniqueID = GenerateUniqueID(ProjectName)
    return Vcxproj.GlobalsT.format(ProjectName, UniqueID)

  @staticmethod
  def Property(configuration, platform, ToolVer):
    debug = 'false'
    if UseDebugLib(configuration) : debug = 'true'
    return Vcxproj.PropertyT.format(configuration, platform, debug, ToolVer)

  @staticmethod
  def ItemDefenition(configuration, platform):
    defenition = Vcxproj.ItemDefenitionReleaseT
    if UseDebugLib(configuration): defenition = Vcxproj.ItemDefenitionDebugT
    return defenition.format(configuration, platform)

  @staticmethod
  def Includes(Filename):
    return Vcxproj.IncludesT.format(Filename)

  @staticmethod
  def Sources(Filename):
    return Vcxproj.SourcesT.format(Filename)

  @staticmethod
  def Nones(Filename):
    return Vcxproj.NonesT.format(Filename)

#-------------------------------------------------------------------------------
# --- Filters class
#-------------------------------------------------------------------------------
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
  def Nones(Path):
    Filter = GetParentPath(Path)
    return Filters.NonesT.format(Path, Filter)

  @staticmethod
  def Sources(Path):
    Filter = GetParentPath(Path)
    return Filters.SourcesT.format(Path, Filter)

  @staticmethod
  def Includes(Path):
    Filter = GetParentPath(Path)
    return Filters.IncludesT.format(Path, Filter)

  @staticmethod
  def Folders(FolderPath):
    UniqueID = GenerateUniqueID(FolderPath)
    return Filters.FoldersT.format(FolderPath, UniqueID)

#-------------------------------------------------------------------------------
# --- Generator class
#-------------------------------------------------------------------------------
class Generator:
  Folders        = set()
  Includes       = set()
  Sources        = set()
  Nones          = set()
  Platforms      = set()
  Configurations = set()
  ToolVersion    = set()
  Name           = ''

  def __init__(self, ProjectName, AllVarList, VSVersion):
    self.Name = ProjectName
    self.GetProjectConfig(AllVarList)
    self.ToolVersion = self.GetToolSetVer(VSVersion)

  def GetProjectConfig(self, AllVarList):
    self.Configurations.clear()
    self.Platforms.clear()

    if (AllVarList[0].get() != 0 and AllVarList[1].get() == 0):
      self.Configurations = ['Release']
    if (AllVarList[0].get() == 0 and AllVarList[1].get() != 0):
      self.Configurations = ['Debug']
    if (AllVarList[0].get() != 0 and AllVarList[1].get() != 0):
      self.Configurations = ['Release', 'Debug']
    if (AllVarList[2].get() != 0 and AllVarList[3].get() == 0):
      self.Platforms = ['Win32']
    if (AllVarList[2].get() == 0 and AllVarList[3].get() != 0):
      self.Platforms = ['x64']
    if (AllVarList[2].get() != 0 and AllVarList[3].get() != 0):
      self.Platforms = ['x64', 'Win32']

  def GetToolSetVer(self, ToolVer):
    if ToolVer == 0:
      LocalToolVer = 'v141'
    if ToolVer == 1:
      LocalToolVer = 'v142'
    if ToolVer == 2:
      LocalToolVer = 'v143'
    return LocalToolVer

  def AddFolder(self, path):
    LocalFilter = GetParentPath(path)
    if LocalFilter == '':
      return
    if LocalFilter not in self.Folders:
      self.Folders.add(LocalFilter)
      MyFilters = ''
      for Iter in os.path.split(LocalFilter):
        MyFilters = os.path.join(MyFilters, Iter)
        if MyFilters != '':
          self.Folders.add(MyFilters)

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
    for Iter_1 in self.Configurations:
      for Iter_2 in self.Platforms:
        project.append(Vcxproj.Configuration(Iter_1, Iter_2))
    project.append(Vcxproj.ProjectConfigurations1)

    project.append(Vcxproj.Globals(self.Name))

    project.append(Vcxproj.ImportDefaultProps)

    for Iter_1 in self.Configurations:
      for Iter_2 in self.Platforms:
        project.append(Vcxproj.Property(Iter_1, Iter_2, self.ToolVersion))

    project.append(Vcxproj.ImportProps)

    for Iter_1 in self.Configurations:
      for Iter_2 in self.Platforms:
        project.append(Vcxproj.ItemDefenition(Iter_1, Iter_2))

    project.append(Vcxproj.ItemGroup0)
    for MyFile in self.Includes:
      project.append(Vcxproj.Includes(MyFile))
    project.append(Vcxproj.ItemGroup1)

    project.append(Vcxproj.ItemGroup0)
    for MyFile in self.Sources:
      project.append(Vcxproj.Sources(MyFile))
    project.append(Vcxproj.ItemGroup1)

    project.append(Vcxproj.ItemGroup0)
    for MyFile in self.Nones:
      project.append(Vcxproj.Nones(MyFile))
    project.append(Vcxproj.ItemGroup1)
    project.append(Vcxproj.ImportTargets)

    project.append(Vcxproj.Project1)
    return '\n'.join(project)

  def CreateFilters(self):
    project = []
    project.append(Filters.Header)
    project.append(Filters.Project0)

    project.append(Filters.ItemGroup0)
    for MyFolder in self.Folders:
      project.append(Filters.Folders(MyFolder))
    project.append(Filters.ItemGroup1)

    project.append(Filters.ItemGroup0)
    for MyFile in self.Nones:
      project.append(Filters.Nones(MyFile))
    project.append(Filters.ItemGroup1)

    project.append(Filters.ItemGroup0)
    for MyFile in self.Includes:
      project.append(Filters.Includes(MyFile))
    project.append(Filters.ItemGroup1)

    project.append(Filters.ItemGroup0)
    for MyFile in self.Sources:
      project.append(Filters.Sources(MyFile))
    project.append(Filters.ItemGroup1)

    project.append(Filters.Project1)
    return '\n'.join(project)

  def Generate(self):
    # Check if old MSVC files exists and delete them
    if os.path.exists(self.Name + '.vcxproj'):
      os.remove(self.Name + '.vcxproj')
    if os.path.exists(self.Name + '.vcxproj.filters'):
      os.remove(self.Name + '.vcxproj.filters')

    # Create new MSVC files
    f = open(self.Name + '.vcxproj', 'w')
    f.write(self.CreateProject())
    f.close()

    f = open(self.Name + '.vcxproj.filters', 'w')
    f.write(self.CreateFilters())
    f.close()


  def GetHeaderFiles(self):
    return self.Includes
  def GetSourceFiles(self):
    return self.Sources
  def GetNoneFiles(self):
    return self.Nones

     # print("--- Source Files ---")
     # for idx in self.Sources:
     #   print(idx)

     # print("--- None Files ---")
     # for idx in self.Nones:
     #   print(idx)

     # print("--- Header Files ---")
     # for idx in self.Includes:
     #   print(idx)


#-------------------------------------------------------------------------------
# --- GUI class
#-------------------------------------------------------------------------------
class GUI:
  Configurations = []
  Platforms      = []

  def __init__(self, TabControl, WorkingDir, AllVarList):
    OutputText = self.PrintCmdLineFrame(TabControl)
    self.PrintMsvcConfigFrame(TabControl, WorkingDir, AllVarList, OutputText)

  def GetAndCheckUserDir(self,WorkingDir, AllVarList):
    # help function for "select folder" button
    FolderSelected = filedialog.askdirectory()
    WorkingDir.set(FolderSelected)
    #check if given path exists and not empty
    AllVarList[4].set(    os.path.exists(WorkingDir.get())
                      and len(os.listdir(WorkingDir.get())))

    if AllVarList[4].get() == 0:
      # show error message box
      tk.messagebox.showerror(title="Error",
      message=" Vcxproj-Generator: selected folder is either empty or invalid!")

  def PrintVcxprojGenOutput(self, MyObj, OutputText):
    LocalHeaderFiles = MyObj.GetHeaderFiles()
    LocalSourceFiles = MyObj.GetSourceFiles()
    LocalNoneFiles   = MyObj.GetNoneFiles()

    OutputText.config(state=NORMAL)

    OutputText.insert(END, "\n---- Source Files ---- \n")
    for File in LocalSourceFiles:
      OutputText.insert(END, str(File+"\n"))

    OutputText.insert(END, "\n--- Header Files --- \n")
    for File in LocalHeaderFiles:
      OutputText.insert(END, str(File+"\n"))

    OutputText.insert(END, "\n---- None Files ---- \n")
    for File in LocalNoneFiles:
      OutputText.insert(END, str(File+"\n"))

    OutputText.config(state=DISABLED)


  def main_xx(self, GenerateBtN, WorkingDir, AllVarList, ToolVer, OutputText):
    name = os.path.split(os.getcwd())[-1]
    generator = Generator(name,AllVarList, ToolVer)

    RootDir = WorkingDir.get()
    path_as_list = list(RootDir.split(","))
    for Dir in path_as_list:
        generator.Walk(Dir, RootDir)
    generator.Generate()

    # print the result of vcxproj-generator
    self.PrintVcxprojGenOutput(generator, OutputText)

    # Activate generate button
    GenerateBtN.configure(stat=NORMAL)

  def GenerateVcxprojFile(self, GenerateBtN, CombBox, WorkingDir, AllVarList,
                          OutputText):
    SlnConfigIsOk = (AllVarList[0].get() != 0 or  AllVarList[1].get() != 0)
    PlatformIsOk  = (AllVarList[2].get() != 0 or  AllVarList[3].get() != 0)
    PathIsOk      =  AllVarList[4].get() != 0
    MSVSVerIsOk   =  CombBox.current()   != -1

    if PathIsOk == True:
      if MSVSVerIsOk == True:
        ToolVer = CombBox.current()
        if SlnConfigIsOk == True and PlatformIsOk == True:
          # clear and activate the text frame
          OutputText.config(state=NORMAL)
          OutputText.delete('1.0', END)
          OutputText.insert(END, "vcxproj-genrator is running ...\n")
          OutputText.config(state=DISABLED)
          GenerateBtN.configure(stat=DISABLED)
          self.main_xx(GenerateBtN, WorkingDir, AllVarList, ToolVer, OutputText)

        else:
          tk.messagebox.showerror(title="Error",
          message=" Vcxproj-Generator: Project config are not selected!")
      else:
        tk.messagebox.showerror(title="Error",
        message=" Vcxproj-Generator: MSVS is not selected!")
    else:
      tk.messagebox.showerror(title="Error",
      message=" Vcxproj-Generator: Folder is not selected or empty!")


  def PrintMsvcConfigFrame(self, TabControl, WorkingDir, AllVarList, OutputText):
    # Create frame for MSVC config widgets
    MsvcConfigFrame = tk.LabelFrame(TabControl, text=' Visual Studio Config ',
                      relief=GROOVE, bd='3')
    MsvcConfigFrame.configure(font="times 11 bold")
    MsvcConfigFrame.place(x=20, y=20, height=220, width=950)

    # Create the working dir entry box
    WdEntryBox = Entry(MsvcConfigFrame, textvariable=WorkingDir)
    WdEntryBox.place(x=20, y=20, height=35, width=750)
    WdEntryBox.configure(font="times 11")
    WdEntryBoxTip = Hovertip(WdEntryBox,'Working directory')

    # Create the working dir browsing button
    WdBrowsingBtN = ttk.Button(MsvcConfigFrame, text="Select folder",
                    command = lambda: GUI.GetAndCheckUserDir(WorkingDir,
                    AllVarList), width=20)
    WdBrowsingBtN.place(x=790, y=20, height=35)
    WdBrowsingBtNTip = Hovertip(WdBrowsingBtN,'Select your working directory')

    # Create a combobox for MSVC version
    MsvcVersion = Label(MsvcConfigFrame ,text="Visual Studio Version")
    MsvcVersion.place(x=20, y=90)
    MsvcVersion.configure(font="times 10 bold")

    text_font = ('times', '9')
    CombBox = ttk.Combobox(MsvcConfigFrame, state="readonly", font=text_font)
    CombBox['values'] =('vs2017', 'vs2019', 'vs2022')
    CombBox.place(x=20, y=120, height=35, width=200)
    CombBoxTip = Hovertip(CombBox,'Select your visual studio version')

    # Create "Generate vcxproj files" button
    GenerateBtN = ttk.Button(MsvcConfigFrame, text="Generate Vcxproj Files",
                  command = lambda:
                  self.GenerateVcxprojFile(GenerateBtN, CombBox, WorkingDir,
                  AllVarList, OutputText),width=30)
    GenerateBtN.place(x=700, y=100, height=60)
    GenerateBtNTip = Hovertip(GenerateBtN,'Press to generate vcxproj files')

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
      ProjectConfigLabel = Label(ProjectConfigFrame,
                                 text=ProjectConfigList[Idx])
      ProjectConfigLabel.place(x=40, y=ProjectConfigYCordinate[Idx])
      ProjectConfigLabel.configure(font="times 10")

      ProjectplatformLabel = Label(ProjectConfigFrame,
                                   text=ProjectPlatformList[Idx])
      ProjectplatformLabel.place(x=140, y=ProjectConfigYCordinate[Idx])
      ProjectplatformLabel.configure(font="times 10")


      # Create project config checkbuttons
      ProjectConfigCheckBtn = ttk.Checkbutton(ProjectConfigFrame,
                              variable= AllVarList[Idx],
                              onvalue=1, offvalue=0).place(x=20,
                              y=ProjectConfigYCordinate[Idx])
      #ProjectConfigBtnTip   = Hovertip(ProjectConfigCheckBtn, ProjectConfigYCordinate[Idx])


      ProjectplatformCheckBtn = ttk.Checkbutton(ProjectConfigFrame,
                                variable= AllVarList[Idx + 2],  # TBD change this hard coded iteration
                                onvalue=1, offvalue=0).place(x=120,
                                y=ProjectConfigYCordinate[Idx])
      #ProjectplatformBtnTip = Hovertip(ProjectplatformCheckBtn, ProjectConfigYCordinate[Idx])


  def PrintCmdLineFrame(self, TabControl):
    # Create cmd line output window
    CmdLineWindow = tk.LabelFrame(TabControl, text=" Output ",
                                  relief=GROOVE, bd='3')
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
    OutputText.config(state=DISABLED)


    # Assign the scrollbar with the text widget
    ScrollBar_H['command'] = OutputText.xview
    ScrollBar_V['command'] = OutputText.yview

    return OutputText
