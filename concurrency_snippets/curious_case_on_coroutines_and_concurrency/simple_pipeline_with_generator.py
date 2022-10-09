'''
Emulating the unix pipeline : `tail -f log_file.txt | grep python`
Collect the latest logs being written in a `log_file.txt` and show commands having `python` keyword only 

Assuming another program (curently `writer_test.py`) is separately writing in the `log_file.txt` file.
'''

import time

def follow(log_file):

    log_file.seek(0, 2) ## More to the end of file. i.e position after the last character in the file
    while True:
        # this will read the last line. if there's a line, it moves the index to the end of line it reads. i.e the end of file again.
        line = log_file.readline()
        # if another program hasn't written anything yet, it will be empty string. So we wait for a while. 
        if not line:
            time.sleep(5)
            continue
        # finally return the line if present
        yield line

def grep(lines, pattern ):
    for line in lines:
        if pattern in line:
            yield line

log_file = open('log_file.txt')

## Creating a stack of generators. 
log_lines = follow(log_file)
python_lines = grep( log_lines , pattern='python')

for line in python_lines:
    print(line)
