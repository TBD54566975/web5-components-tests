import os
import re

directory = "./"
dir_list = os.listdir(directory)

test_files = []

for file in dir_list:
    if re.search("[0-9]+", file) != None:
        test_files.append(file)

test_files = filter(lambda file: file != "0-all-tests.py", test_files)

for file in sorted(test_files):
    print("\n\nRunning test file: " + file)
    exec(open(file).read())
