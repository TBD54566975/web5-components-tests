import os
import re

dir_list = os.listdir("./")

test_files = []

for file in dir_list :
    if re.search('[0-9]+', file) != None :
        test_files.append(file)

test_files = filter(lambda file: file != '0-all-tests.py', test_files)


for ele in sorted(test_files):
    print("\n\nRunning test file: " + ele)
    exec(open(ele).read())