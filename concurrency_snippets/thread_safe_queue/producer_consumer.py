"""
Gist : 
There are two threads/processes. 
One thread is producing item. say sending get request and 
retrieving fresh logs from a network.
Another thread is receiving those logs and writing to a database.
"""
import random 
import logging 
import threading
import concurrent.futures


SENTINEL = object()

def producer(pipeline):
    """Pretend we're getting a message from the network."""
    logging.info('Starting Producer Thread')
    for _ in range(5):
        logging.info(f'At index : {_}')

        message = random.randint(1, 101)
        logging.info("Producer got message: %s", message)
        pipeline.set_message(message, "Producer")

    # Send a sentinel message to tell consumer we're done
    pipeline.set_message(SENTINEL, "Producer")


def consumer(pipeline):
    """Pretend we're saving a number in the database."""
    message = 0
    while message is not SENTINEL:
        message = pipeline.get_message("Consumer")
        if message is not SENTINEL:
            logging.info("Consumer storing message: %s", message)


"""
# --------- SOLUTION USING LOCK ---------- #
Both threads use a common object "pipeline". Producer writes it's logs/message 
to a variable `message` of this object. Consumer retrieves int's log's message 
from that same variable.  

Since we update state of pipeline object, we need to implement Locks inside Pipeline's methods
to avoid race condition. 

We ensure, when producer has updated the pipeline with new message, it cannot update the 
value again until consumer has read that message.
Similarly, until producer has updated the pipeline's message attribute, consumer thread isn't 
allowed to read from message attribute.  
"""

class Pipeline:
    """
    Class to allow a single element pipeline between producer and consumer.
    """
    def __init__(self):
        self.message = 0
        self.producer_lock = threading.Lock()
        self.consumer_lock = threading.Lock()
        self.consumer_lock.acquire()

    def get_message(self, name):
        logging.debug("%s:about to acquire getlock", name)
        self.consumer_lock.acquire()
        logging.debug("%s:have getlock", name)
        message = self.message
        logging.debug("%s:about to release setlock", name)
        self.producer_lock.release()
        logging.debug("%s:setlock released", name)
        return message

    def set_message(self, message, name):
        logging.debug("%s:about to acquire setlock", name)
        self.producer_lock.acquire()
        logging.debug("%s:have setlock", name)
        self.message = message
        logging.debug("%s:about to release getlock", name)
        self.consumer_lock.release()
        logging.debug("%s:getlock released", name)


# if __name__ == "__main__":
#     format = "%(asctime)s: %(message)s"
#     logging.basicConfig(format=format, level=logging.INFO,
#                         datefmt="%H:%M:%S")
#     # logging.getLogger().setLevel(logging.DEBUG)

#     pipeline = Pipeline()
#     with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
#         executor.submit(producer, pipeline)
#         executor.submit(consumer, pipeline)



"""
# --------- SOLUTION USING Thread-safe Queue  ---------- #
Both threads use a common object "pipeline". Producer writes it's logs/message 
to a variable `message` of this object. Consumer retrieves int's log's message 
from that same variable.  

Since we update state of pipeline object, we need to implement Locks inside Pipeline's methods
to avoid race condition. 

We ensure, when producer has updated the pipeline with new message, it cannot update the 
value again until consumer has read that message.
Similarly, until producer has updated the pipeline's message attribute, consumer thread isn't 
allowed to read from message attribute.  
"""
from queue import Queue, Full, Empty
import time

class Queue(Queue):
    """
    We overrides put and get method from available Queue for understanding purpose.
    """
    def put(self, item, block=True, timeout=None):
        # When one thread is putting something in queue, other threads cannot touch it.
        with self.not_full:
            print(f'Inside Put by thread {threading.current_thread()}')
            if self.maxsize > 0:
                if not block:
                    if self._qsize() >= self.maxsize:
                        raise Full
                elif timeout is None:
                    while self._qsize() >= self.maxsize:
                        """
                        ###################################################################################
                        # ================ One possible Scenario to explain what's happening ============ #
                        ###################################################################################
                        
                        While putting an item, if it's detected that queue is full,
                        the given thread say T1 releases the lock but blocks it's further execution.

                        Possibly, another producer say T2 could pick up. And get stuck here again.

                        A consumer thread (say TC) will eventually execute "self.get" and "self.non_full.notify" 
                        is executed afterwards.
                        Now, say exwecution transfers to producer T3. put method from this thread won't 
                        fall inside the blocking because Queue is not full.
                        Thus, it will again make queue full

                        Say now execution goes back to T1. Now, T1 is unblocked for a while. Because 
                        self.not_full.notify that ran inside  consumer's get method some steps back unblocks self.not_full.wait. 
                        T1 also re-acquires the lock. But condition fails in the while loop and T1 again 
                        release the lock but get's blocked. like at start 
                        """
                         
                        print(f'Thread blocked : {threading.current_thread()}')
                        print(f'Not full object is : {id(self.not_full)}')
                        self.not_full.wait()
                        print(f'Step after Thread blocked : {threading.current_thread()}')

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
            print(f'Outside Put by thread {threading.current_thread()}')

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

class Pipeline:
    """
    Class to allow a single element pipeline between producer and consumer.
    """
    def __init__(self, size):
        self.message_queue = Queue(size)

    def get_message(self, name):
        message = self.message_queue.get()
        return message

    def set_message(self, message, name):
        self.message_queue.put(message)


if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")
    # logging.getLogger().setLevel(logging.DEBUG)

    pipeline = Pipeline(size=3)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.submit(producer, pipeline)
        executor.submit(producer, pipeline)
        executor.submit(producer, pipeline)
        executor.submit(consumer, pipeline)
        executor.submit(consumer, pipeline)