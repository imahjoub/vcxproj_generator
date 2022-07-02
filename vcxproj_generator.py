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


import os, uuid

import tkinter as tk
import os, sys
import subprocess
import re
import threading

from select import select
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *
from idlelib.tooltip import Hovertip
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
  def __init__(self, TabName, WorkingDir):
    self.print_msvc_config_frame(TabName, WorkingDir)
    self.print_cmd_line_frame(TabName)


  def print_msvc_config_frame(self, TabName, WorkingDir):
    # Create frame for MSVC Setup widgets
    release_path_frame = tk.LabelFrame(TabName, text=' MSVC Setup ',relief=GROOVE, bd='3')
    release_path_frame.configure(font="times 11 bold")
    release_path_frame.place(x=20, y=20, height=220, width=950)

    print(WorkingDir)
    # Create the browse folder bar
    search_ini_bar = Entry(release_path_frame, textvariable=WorkingDir)
    search_ini_bar.place(x=20, y=20, height=35, width=750)
    search_ini_bar.configure(font="Arial 11")

    # Create the browse folder button
    find_ini_button = ttk.Button(release_path_frame, text="Select folder",
       command = lambda: 0, width=20)
    find_ini_button.place(x=790, y=20, height=35)

  def print_cmd_line_frame(self, TabName):
    # Create a frame for cmd line
    # Create cmd line output window
    cmd_line_window = tk.LabelFrame(TabName, text=" Command Line ", relief=GROOVE, bd='3')
    cmd_line_window.configure(font="times 11 bold")
    cmd_line_window.place(x=20, y=250, height=340, width=950)

    # Create a scrollbar text frame for the programm output
    scrollbar_v = tk.Scrollbar(cmd_line_window, orient= VERTICAL)
    scrollbar_v.pack(side= RIGHT,fill="y")

    scrollbar_h = tk.Scrollbar(cmd_line_window, orient= HORIZONTAL)
    scrollbar_h.pack(side= BOTTOM, fill= "x")
