"""
Experimenting with Multiple processes writing on the same file.

Open a terminal and run : 
- `python writer_test.py --name 1`
Open  another terminal and run : 
- `python writer_test.py --name 2`

See the output : test_same_writing.txt
   - You will observe for Ubuntu that
   - Each program is at different postion of file.
   - While program 1 is wiriting at latest index, program 2 is ovrwriting contents above.
   - They write to file independently and don't coordinate to get the latest index.
   - Had we used `append` mode, we are  guarenteeed that each process gets the latest index in the file.
"""


import argparse
from importlib.resources import path
import time
import os
import pathlib


def cycler():
    while True:
        for i in [1, 2, 3, '4 - python']:
            yield i

if __name__ == '__main__':
    # Create the parser
    parser = argparse.ArgumentParser()
    parser.add_argument('--program_name', type=str, required=True)
    parser.add_argument('--file_name', type=str, required=True)
    parser.add_argument('--mode', default='r', type=str, nargs='?')

    args = parser.parse_args()
    program_name =  args.program_name
    file_name = args.file_name
    mode = args.mode

    # Create the file
    if os.path.exists(file_name):
        os.remove(file_name)
    open(file_name, 'w').close()

    cycle_int = cycler()
    
    test_file = open( file_name, mode='w' )
    while True:
        try:
            time.sleep(1)
            val = next(cycle_int)

            index_pos = test_file.tell()
            write_val_1 = f'Writer {program_name} || Id {val} || At file index Position | {index_pos} '
            writer_val_2 = ''.join( i for i in [str(program_name)] * ( 100-len(write_val_1)-1 ) ) + '\n'
            write_val = write_val_1 + writer_val_2

            test_file.write(write_val)
        except KeyboardInterrupt:
            print('Halting the program.')
            test_file.close()
            break
        

