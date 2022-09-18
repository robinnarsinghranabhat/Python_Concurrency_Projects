"""
Race condition in threads and using Locks / Mutex in multithreading for sane global variable modification. 
"""

import logging
import threading
import time
import concurrent.futures


def fib(n):
    if n <= 1 :
        return n
    else:
        return fib(n-1) + fib(n-2)
        
class FakeDatabase:
    """
    A Fake Database class to experiment with threads
    """
    def __init__(self):
        self.value = 0
        self._lock = threading.Lock()

    def update(self, name):
        """
        Increments the attribute `value` of FakeDatabase object by 1
        """
        logging.info("Thread %s: starting update", name)
        local_copy = self.value
        local_copy += 1
        logging.info("Thread %s: Before sleeping", name)
        
        # Probably context switching goes here 
        # fib(30) # could use time.sleep here as well
        self.value = local_copy
        logging.info("Thread %s: finishing update", name)

    def locked_update(self, name):
        """
        Thread-Safe implementation of `update` functionality.

        Using Locks : 
            With locks, both threads cannot at the same time, modify section inside lock.
            Say Thead 0 is executing a section inside Lock. During that period, say context switcing 
            happens and execution transfers to start Thread 1.
        """
        logging.info("Thread %s: starting update", name)
        logging.debug("Thread %s about to lock", name)
        # Normally Threads can context switch anytime. 
        # time.sleep is the most probable time thread can switch ! 
        # without time.sleep executing locked_update would take say be 0.0001 sec. 
        # which is a very small period for context switching. 
        # when statements are in a lock, we are sure that context switching doesn't happen in this part.

        
        # To solve your race condition above, you need to find a way to allow 
        # only one thread at a time into the read-modify-write section of your code
        with self._lock:
            logging.debug("Thread %s has lock", name)
            local_copy = self.value
            local_copy += 1
            time.sleep(0.1)
            self.value = local_copy
            logging.debug("Thread %s about to release lock", name)
        time.sleep()
        logging.debug("Thread %s after release", name)
        logging.info("Thread %s: finishing update", name)

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.DEBUG,
                        datefmt="%H:%M:%S")

    database = FakeDatabase()
    logging.info("Testing update. Starting value is %d.", database.value)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        for index in range(2):
            executor.submit(database.locked_update, index)
    logging.info("Testing update. Ending value is %d.", database.value)