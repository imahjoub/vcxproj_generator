'''
Copyright Iliass Mahjoub 2022.
Distributed under MIT License
Version 1.0. (See accompanying file LICENSE
or copy at https://opensource.org/licenses/MIT)
'''

#-----------------------------------------------------------------------------------
# Global variables
#-----------------------------------------------------------------------------------
HEADER_EXT = ['.h', '.inl', '.hpp']
SOURCE_EXT = ['.c', '.cc', '.cpp']
VS_VERSION = '2015' # 2013 or 2015
UserDir    = ""
WorkDirIsOk = False

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
            '      <Configuration>Debug</Configuration>',
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
    Folders = set()
    Includes = set()
    Sources = set()
    Platforms = set()
    Configurations = set()
    Name = ''

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

    def AddSource(self, path):
        self.Sources.add(path)

    def AddHeader(self, path):
        self.Includes.add(path)

    def AddFile(self, path):
        (root, ext) = os.path.splitext(path)
        if ext in HEADER_EXT:
            self.AddHeader(path)
        elif ext in SOURCE_EXT:
            self.AddSource(path)
        else:
            return
        self.AddFolder(path)

    def Walk(self, path):
        if os.path.isfile(path):
            self.AddFile(path)
        else:
            for subPath in os.listdir(path):
                self.Walk(os.path.join(path, subPath))

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
        f = open(self.Name + '.vcxproj', 'w')
        f.write(self.CreateProject())
        f.close()

        f = open(self.Name + '.vcxproj.filters', 'w')
        f.write(self.CreateFilters())
        f.close()

#-----------------------------------------------------------------------------------
# --- GUI class
#-----------------------------------------------------------------------------------
class GUI:
  def __init__(self, TabControl, WorkingDir):
    self.PrintMsvcConfigFrame(TabControl, WorkingDir)
    self.PrintCmdLineFrame(TabControl)

  def GetAndCheckUserDir(WorkingDir):
    # the default path, is set to exe/script curdir
    FolderSelected = filedialog.askdirectory()
    WorkingDir.set(FolderSelected)
    UserDir = WorkingDir.get()

    WorkDirIsOk = (        os.path.exists(UserDir)
                   and not os.listdir(UserDir)
                   and not FolderSelected)

    if WorkDirIsOk == False:
      # show error message box
      tk.messagebox.showerror(title="Error", message=" Vcxproj-Generator: selected path is either empty or invalid!")

  def PrintMsvcConfigFrame(self, TabControl, WorkingDir):
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
      command = lambda: GUI.GetAndCheckUserDir(WorkingDir), width=20)
    WdBrowsingBtN.place(x=790, y=20, height=35)


    # Create a combobox for MSVC version
    pf_title_lab = Label(MsvcConfigFrame ,text="Visual Studio Version")
    pf_title_lab.place(x=20, y=90)
    pf_title_lab.configure(font="times 10 bold")

    text_font = ('times', '9')
    combobox = ttk.Combobox(MsvcConfigFrame, state="readonly", font=text_font)
    combobox['values'] =('vs2017', 'vs2019', 'vs2022')
    combobox.place(x=20, y=120, height=35, width=250)


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



