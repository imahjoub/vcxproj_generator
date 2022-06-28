'''
Copyright Iliass Mahjoub 2022.
Distributed under MIT License
Version 1.0. (See accompanying file LICENSE
or copy at https://opensource.org/licenses/MIT)
'''

# Script settings

PATHS_TO_SEARCH = ['.']
PROJECT_NAME    = '' # by default will use current directory name
PLATFORMS       = ['Win32', 'x64']
CONFIGURATIONS  = ['Debug', 'Release']

# Script starts here
import os, uuid
import vcxproj_generator

def main(paths, name, platforms, configurations):
    if name == '':
        name = os.path.split(os.getcwd())[-1]
    generator = vcxproj_generator.Generator(name, platforms, configurations)
    for path in paths:
        generator.Walk(path)
    generator.Generate()

main(PATHS_TO_SEARCH, PROJECT_NAME, PLATFORMS, CONFIGURATIONS)
