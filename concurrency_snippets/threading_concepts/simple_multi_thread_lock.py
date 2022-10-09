import threading
import time
import inspect

class Thread(threading.Thread):
    def __init__(self, t, *args):
        threading.Thread.__init__(self, target=t, args=args)
        self.start()

count = 0
lock = threading.Lock()

def incre():
    global count
    caller = inspect.getouterframes(inspect.currentframe())[1][3]
    print(f"{caller} :: Starting at count : {count}")
    print(f"{caller} :: Acquiring Lock")
    with lock:
        print(f"{caller} :: Lock Acquired")
        count += 1  
        time.sleep(2)  
        print(f"{caller} :: Lock Released")

def bye():
    while count < 3:
        incre()

def hello_there():
    while count < 3:
        incre()

def main():    
    hello = Thread(hello_there)
    goodbye = Thread(bye)


if __name__ == '__main__':
    main()
