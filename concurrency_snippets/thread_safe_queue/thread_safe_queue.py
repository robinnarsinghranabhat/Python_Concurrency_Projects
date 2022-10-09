import queue
from queue import Full
import threading
import time
import requests


"""
-- Queue Implementation --
put :
    As long as queue is full, wait for get to execute.
    After we get one element, unblock the wait. 

get :
    As long as queue is empty, wait for put to execute
    Afte we put one element, unblock the wait for get. 

-- Extra Terminology --

threading.Condtion : Works just like a lock. But we can also call `wait` inside the lock. 
Calling this will "open the lock" allowing the same piece of program to be executed in other threads.
But for the thread itself `wait` as called, execution is blocked. 
Only after calling `notify` from another thread (which me must ensure we should ! ), exection is unblocked and lock is resumed.
"""

class Queue(queue.Queue):
    def put(self, item, block=True, timeout=None):
        # When one thread is putting something in queue, other threads cannot touch it.
        with self.not_full:
            if self.maxsize > 0:
                if not block:
                    if self._qsize() >= self.maxsize:
                        raise Full
                elif timeout is None:
                    while self._qsize() >= self.maxsize:
                        # While putting an item, if it's detected that queue is full,
                        # the thread is blocked. Which happens
                        # when consumer uses the get method. 
                        # we get out of this blocking only 
                        self.not_full.wait()
                elif timeout < 0:
                    raise ValueError("'timeout' must be a non-negative number")
                else:
                    endtime = time() + timeout
                    while self._qsize() >= self.maxsize:
                        remaining = endtime - time()
                        if remaining <= 0.0:
                            raise Full
                        self.not_full.wait(remaining)
            self._put(item)
            self.unfinished_tasks += 1
            self.not_empty.notify()

    def get(self, block=True, timeout=None):
        with self.not_empty:
            if not block:
                if not self._qsize():
                    raise Empty
            elif timeout is None:
                while not self._qsize():
                    self.not_empty.wait()
            elif timeout < 0:
                raise ValueError("'timeout' must be a non-negative number")
            else:
                endtime = time() + timeout
                while not self._qsize():
                    remaining = endtime - time()
                    if remaining <= 0.0:
                        raise Empty
                    self.not_empty.wait(remaining)
            item = self._get()
            # Whenever we do self.get, we notify that quene is now not full. 
            self.not_full.notify()
            return item

def save_image(id, url):
    with open(f'pic{id}.jpg','wb') as image:
        response = requests.get(url, stream=True)
        for block in response.iter_content(1024):
            if not block:
                break
            image.write(block)

def download(queue):
    print('QUEUE ID IS : ', id(queue))
    print('Befoer get')
    iden = queue.get()
    print('After get')
    result = requests.get(f"https://jsonplaceholder.typicode.com/photos/{iden}")
    url = result.json()["thumbnailUrl"]
    # save_image(id, url)
    print(f"Save image {iden}")
    queue.task_done() # this is new 
    
NUM_THREADS = 10
q = queue.Queue()

for i in range(NUM_THREADS):
    worker = threading.Thread(target=download,args=(q,))
    worker.start()

# for i in range(NUM_THREADS):
#     id = random.randint(1,100)
#     q.put(id)

q.join() # this is new



 
