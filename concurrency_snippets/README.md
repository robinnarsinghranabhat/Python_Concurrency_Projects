## Collection of minimal examples to understand concurrency concepts in python


### This repo heavily uses code from following sources :
- (Real Python : Intro to python threading)[https://realpython.com/intro-to-python-threading/]
- (Pycon Talk : Thinking Concurrency in Python by Raymond Hettinger)[https://www.youtube.com/watch?v=Bv25Dwe84g0]


## Unveiling Multi-Threading, Multiprocessing and Aysnc in Python.

### Theading and when to use it
Think of Threads as a subsection of code within an program that can be executed independently. Let's look at example below.
```
"""
Simple, sequential program to download webpage one by one.
"""
import requests
websites = ['www.google.com', 'www.yahoo.com', 'www.bing.com']
def downloader(url):
    """ Simple function to fetch the url """
    return requests.get(url)

output_pages = []
for i in websites: 
    out = downloader(i)
    output_pages.append(out)
```


```
"""
Same Program using Threading
"""
import requests
from threading import Thread

websites = ['www.google.com', 'www.yahoo.com', 'www.bing.com']
def downloader(url):
    """ Simple function to fetch the url """
    webpage_output = request.get(url)
    return webpage_output

threads = []

for i in websites: 
    x = threading.Thread(target=downloader, args=(i,))
    threads.append(x)
    x.start()

# Just like we close open files, `join` closes all these additional open threads. 
for t in threads:
    t.join()

```

So what's happening here. Basically, in Sequentiual program to download webpages, request of second webpage begins only after request of first one finishes.

During the time we are waiting for response to come back, program just waits. CPU remains idle. Isn't there some way to request other pages during that gap, rather than just wait.

That's what we solve with threads. When execution reaches `x.start()` in `Main thread` i.e our main program, a new Thread will be created and the set of instruction defined under `downloader` will start executing in a separate thread. At this point we have two threads going on : 
1. `Main Thread`
2. `Google Thread` : Thread that runs `downloader` for first website : `google.com`.

Now we have two sets of sub-program running. Execution just context switches between `Main thread` and this `Google Thread`. They just run turn by turn in the same CPU. How frequently context switcing happens depends on OS. But it happens quite rapidly. Note that, It's not like, `Google Thread` runs in differnt CPU core.

Request for the webpage is an example of I/O bound operation. We are just waiting for an external agent to give us back the webpage. We are not doing any computation in CPU side.

Since this can take a while, CPU basically remains idle doing nothing. Something like `time.sleep(2)` in middle of your code. During that significantly long time period from CPU's perspective doing billion of operations per second, program execution context switches back to main thread, the loop continues to start executing another thread to download webpage for `yahoo.com`. 

It's like opening `google` and `yahoo` in separate tabs in browser. In such requests, one does not have to wait for another. Finally, `Bing Thread` will be added in similar way and we have three requests made at this point without having to wait for each other.


### When Threading is Bad
This way, for I/O bound application where we have to wait for something, threading works great. 
What if our task was not to download but some some task using CPU.

Well in such cases, Threading slows down program. Because, all those threads to calculate would be using the SAME CPU CORE. 

Imagine 3 folks, each wanting to print 10 pages using a single printer. In sequential program, Each person would use the printer, do their work one by one. IF they did something like; first person using printer for a while to print 3 pages, then gives turn to the second person for a while and prints 4 pages and then third person prints 2 pages. And again continue doing this until each of them have printed 10 pages, total time will be greater due to that overhead of switching.


In a python program (CPython to be specific), the interpreter can only run ONE THREAD AT A TIME. This is called the GLOBAL INTERPRETER LOCK. And the context-switching between threads just becomes an extra overhead. Remember that, in prev example, during a context switch, a request is made externally, and during that wait for page, we made other  requests. To actually utilize multiple CPU cores and execute cpu bound calculation in parallel, we can actually utilize the `multiprocessing`. 

```
"""
Program comparing time taken to do some CPU bound tasks by sequential, multi-threaded and multiprocessing.
"""

import time 
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

nums = [8,7,8,5,8,8,5,4,8,7,7,8,8,7,8,8,8]

def some_computation(n):
    counter = 0
    for _ in range(n*1_000_000):
        counter += 1
    return counter

def sequential():
    """Running calculations sequentially"""
    for n in nums:
        some_computation(n)

def threaded():
    """Running calculations in different threads"""
    with ThreadPoolExecutor() as executor:
        executor.map(some_computation, nums)

def pooled():
    """
    Running calculations in multiple processes. 
    NOTE : For a Single Core computer, this will just execute slower than sequential one because of extra overhead with allocation. 
    """
    with ProcessPoolExecutor() as executor:
        executor.map(some_computation, nums)

if __name__ == '__main__':
    for func in sequential, threaded, pooled:
        start = time.perf_counter()
        func()
        end = time.perf_counter()
        print(func.__name__, f'{end-start:.4f}')

# If you run this, you will find sequential one runs faster than multithreaded one. If your CPU is multi-core, which I am expecting is likely, pooled one runs the fastest.  
```

### More about threads
In threading, context-switch can happen at any time. It's managed by OS. When multiple threads are using a shared resource, undesired behavior may show up.

```
import threading
class FakeDatabase:
    def __init__():
        self.value = 0
    def update(self):
        """Update the value by 1"""
        local_copy = self.value
        local_copy += 1
        time.sleep(0.1)
        self.value = local_copy

fake_database = FakeDatabase()
with ThreadPoolExecutor() as executor:
    for index in range(2):
        executor.submit(fake_database.update, index)
print("The final value is : ", fake_database.value)
```
To prove our point, we place `time.sleep` and ensure that a context switch always happens above `self.value = local_copy`. 

Now running this program, first thread will have set value of `local_copy` to 1 before the `time.sleep` and switching happens back to main thread. In main thread, loop continues, and we call `update` again through another thread.
Notice that even till now, `self.value` is still 0. This second thread will context-swtich before `time.sleep` to first thread. The first thread will set `self.value` to `local_copy` which is one. Again, second thread does the same thing and sets `self.value` to value of `local_copy`,  which is one as well.

This is a simple example to show that when multiple threads are accessing a shared resouce i.e `self.value`, we may have underised behaviour where one thread is overwriting result of another. To synchronize between threads, we again have to use something called Lock. There are also things like Queue. 
```
class FakeDatabase:
    def __init__(self):
        self.value = 0
        self._lock = threading.Lock()
    def locked_update(self):
        with _lock:
            local_copy = self.value
            local_copy += 1
            time.sleep(0.1)
            self.value = local_copy
```


```
### So, where does Async fall ? 
Basically Async solves the same problem that threading did. When we have I/O bound opearation. But key difference is, 
Consider this example below to 
