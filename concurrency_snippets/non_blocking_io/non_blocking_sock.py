"""
Using select sys-call to understand working of non-blocking I/O in socket programming

References : 
- https://docs.python.org/3/howto/sockets.html
- https://youtu.be/2Oq4FQSr21I || https://github.com/voidrealms/python3/blob/main/python3-59/python3-59.py
"""

# ====== Blocking Socket Example ====== #
import logging
import socket
import select
from typing import final

logging.basicConfig(format='%(levelname)s - %(asctime)s: %(message)s',datefmt='%H:%M:%S', level=logging.DEBUG)

# Blocking Socket Example
def create_blocking(host, ip):
    logging.info('Blocking - Creating Socket')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    logging.info('Blocking - Connecting')
    s.connect((host, ip))

    logging.info('Blocking - sending')
    request = f"GET / HTTP/1.1\r\nHost: {host}\r\n\r\n"
    s.send(request.encode())


    logging.info('Waiting for response')
    data = ""
    while True:
        chunk = s.recv(1024).decode(encoding='ISO-8859-1') # Get first 1024 bytes from the network buffer
        logging.info(f'Received a chunk of len {len(chunk)}')
        if not chunk:
            logging.info('Exiting the recv')
            break
        with open('file.txt', 'a') as f:
            f.write(data)
        data += chunk

    logging.info(f'Got Data of length {len(data)}')

"""
## ====== socket.recv() ====== ##
This system call transfers execution to kernel. In a way, our application-program is asking for service from kernel at some point while getting executed in the CPU.
kernel now checks if the Network Interface Card's network buffer has received some data from the internet. BECAUSE WE RUN socket.recv after making the HTTP request to 
server (socket.send).  
the kernel WAITS for the network buffer (Queue) to be populated. Now this waiting can either happen by kernel pinging the NIC time to time and 
checking if data has arrived (polling). 
Or, NIC interrupts the kernel once the info is available.  
During this wait, CPU is idle. 

## ====== Making sockets Non-Blocking with `select` system call ====== ## 

First and foremost, we must use the command : socket.setBlocking(False)
Now, when we use normally blocking commands like socket.recv, waiting doesn't happen. if data is not available, kernel doesn't wait for NIC to populate. 
It simply returns empty string.
Thus, we need to be wary and add additional checks in the code to deal with this.

NOTE : Even when we use socket.recv(1024) in blocking mode, it's not guarenteed that kernel waits until 1024 byte of data is populated in NIC. 

Finally, We give select function a list of file-descriptions (say 1000 open sockets in a server )
Control goes to kernel now. And OS will check if those files (disk file, socket e.t.c) are available to read from or write to.
During this time period for checking, execution is blocked. Thus, we must provide timeout parameter with select.
"""

def create_non_blocking(host, ip):
    logging.info('Non-Blocking - Creating Socket')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    logging.info('Non-Blocking - Connecting')
    # Returns 0 if connection is established other error id integer.
    # Note : if we use connect only, it's safe to use an explicit try-catch. 
    ret = s.connect_ex((host, ip))  
    if ret != 0:
        logging.info('Non-Blocking : Failed to connect')
        import sys; sys.exit()
    
    logging.info('Non-Blocking : Connection Established')
    # Something Magical and Terrific. Now send, recv, connect, accept commands don't block. they 
    # for example : recv(1024) doesn't wait for network buffer to be filled upto 1024 bytes. it just get's whatever it finds.  
    s.setblocking(0)

    inputs = [s]
    outputs = [s]

    final_data = ''
    while inputs:
        readable, writable, execptional = select.select(inputs, outputs, inputs, 1)

        # Need to send data || write some info to network buffer || i.e. make a request
        # Only after sending something, can we get something back to read.
        for s in writable:
            logging.info('Non-Blocking : Send Start')
            request = f"GET / HTTP/1.1\r\nHost: {host}\r\n\r\n"
            data = s.send(request.encode())
            logging.info(f'Non-Blocking : Send End || sent {data}')
            outputs.remove(s)

        
        # IF we skip the above writing, The while loop will run infinitely 
        # since socket will always be querying the network buffer. But nothing is there to read from.
        for s in readable:
            logging.info('Non-Blocking : Read Start')
            data = s.recv(1024).decode(encoding='ISO-8859-1')
            logging.info(f'Non-Blocking : Read End :: GOT : {len(data)}')
            if not data:
                logging.info(f'Non-Blocking : Closing Sockets ..')
                s.close()
                inputs.remove(s)
                break
            final_data += data
    
        print('Input length is : ',len(inputs))
        for s in execptional:
            logging.info('Non-Blocking : Exception Start')
            inputs.remove(s)
            outputs.remove(s)
            logging.info('Non-Blocking : Exception End')
            break

    import pdb; pdb.set_trace()
    print('outside while')
    

def main():
    # create_blocking('www.google.com', 80) # HTTP services is provided in this port
    create_non_blocking('neverssl.com', 80) # HTTP services is provided in this port

if __name__ == '__main__':
    main()
