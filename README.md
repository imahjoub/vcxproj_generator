vcxproj_generator
=====================

<p align="center">
    <a href="https://sonarcloud.io/summary/new_code?id=imahjoub_vcxproj_generator">
        <img src="https://sonarcloud.io/api/project_badges/measure?project=imahjoub_vcxproj_generator&metric=alert_status" alt="Quality Gate Status"></a>
    <a href="https://app.codacy.com/gh/imahjoub/vcxproj_generator/dashboard">
        <img src="https://app.codacy.com/project/badge/Grade/d3d5ebd231b34765bc7b663151a93574" alt="Codacy Badge" /></a>
    <a href="https://github.com/imahjoub/vcxproj_generator/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc">
        <img src="https://custom-icon-badges.herokuapp.com/github/issues-raw/imahjoub/vcxproj_generator?logo=github" alt="Issues" /></a>
    <a href="https://github.com/imahjoub/vcxproj_generator" alt="GitHub code size in bytes">
        <img src="https://img.shields.io/github/languages/code-size/imahjoub/vcxproj_generator" /></a>
    <a href="https://github.com/imahjoub/vcxproj_generator/blob/main/LICENSE_1_0.txt">
        <img src="https://img.shields.io/badge/license-BSL%201.0-blue.svg" alt="Boost Software License 1.0"></a>
    <a href="https://github.com/imahjoub/vcxproj_generator" alt="Activity">
        <img src="https://img.shields.io/github/commit-activity/y/imahjoub/vcxproj_generator" /></a>
</p>

A Tool that iteratively searches for files (`*.h`, `*.cpp`, `*.c`, etc.) in a given path and its subfolders to generate the `*.vcxproj` and `*.vcxproj.filters` files.

## How to use

1. Run the exe file `vcxproj_generator.exe` <sub>***(Temporary workaround, Do copy the `vcxproj_generator.ico` to the same location of the exe)***</sub>
2. Select your project folder
3. Set your visual studio configuration
4. run the program


![image](https://user-images.githubusercontent.com/48915588/189079254-e0e2caa6-58f7-4eae-a588-7f102c11f991.png)


After you run the program, the vcxproj files will be generated and all found files in the specified folder will be listed in the output window

## Supported file extensions

```
HEADER_EXT = ['.h',  '.in', '.hpp']
SOURCE_EXT = ['.c',  '.cc', '.cpp']
NONE_EXT   = ['.md', '.ld', '.gmk']
```

###### If you need more extensions, you can add them yourself in the script `vcxproj_generator.py.`

## Notes:

- If you want to regenerate new vcxproj files, you should first close the Visual Studio IDE.
- The generated project may fail to build due to SDK versions (default 8.1), so I always recommand you to check the SDK version first


