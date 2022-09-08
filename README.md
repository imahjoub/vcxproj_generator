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

1. Run the exe file `vcxproj_generator.exe`.
2. Select your project folder.
3. Set your visual studio configuration
4. run the program


![image](https://user-images.githubusercontent.com/48915588/189079254-e0e2caa6-58f7-4eae-a588-7f102c11f991.png)


After you run the program, the Visual Studio files will be generated and the program will list you all found files in the specified folder in the output window

## Supported file extensions

```
HEADER_EXT = ['.h',  '.in', '.hpp']
SOURCE_EXT = ['.c',  '.cc', '.cpp']
NONE_EXT   = ['.md', '.ld', '.gmk']
```

###### If you need more extensions, you can add them yourself in the script `vcxproj_generator.py.`

## Notes:

- If you want to regenerate new Visual Studio files, you should first close the Visual Studio IDE.
- The generated project may fail to build due to SDK versions (default 8.1), so I always recommand you to check the SDK version first


