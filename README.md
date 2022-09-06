vcxproj_generator
=====================
<p align="center">
    <a href="https://github.com/imahjoub/vcxproj-generator-gui/blob/main/LICENSE">
        <img src="https://img.shields.io/badge/license-BSL%201.0-blue.svg" alt="MIT License"></a>
    <a href="https://github.com/imahjoub/vcxproj-generator-gui" alt="Activity">
        <img src="https://img.shields.io/github/commit-activity/y/imahjoub/vcxproj-generator-gui" /></a>
</p>

A Tool that iteratively searches for files (`*.h`, `*.cpp`, `*.c`, etc.) in a given path and its subfolders to generate the `*.vcxproj` and `*.vcxproj.filters` files.

## How to use
1. Download GUI
2. set up your visual studio properities
3. run the vcxproj file

## Supported file extensions

```
HEADER_EXT = ['.h',  '.in', '.hpp']
SOURCE_EXT = ['.c',  '.cc', '.cpp']
NONE_EXT   = ['.md', '.ld', '.gmk']
```

###### If you need more extensions, you can add them yourself in `vcxproj_generator.py.`

## SDK problem 8.1
TBD describe visual studio error and how to update the sdk
also close visual studio and delete the sln file if the vcxproj is generated with other additional config


