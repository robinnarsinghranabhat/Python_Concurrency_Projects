import time
from concurrent.futures import ThreadPoolExecutor 
pool = ThreadPoolExecutor (8)

def func(x,y) : 
    time.sleep(1) 
    return x + y


def do_func(x, y) : 
    result = yield pool.submit (func, x, y) 
    print("Got : ", result) 

class Task : 
    def __init__(self, gen) : 
        self._gen = gen 
    def step (self, value=None) : 
        #Run to the next yield 
        try :
            print('Inside Step')
            fut = self._gen.send(value) 
            # Future returned 
            fut.add_done_callback(self._wakeup) 
            print('exiting Step')
        except StopIteration as exc :
            print('StopIteration ... End of Generator execution') 
            pass
    
    def _wakeup(self, fut):
        # Handler of results
        print('Inside wakeup')
        result = fut.result()
        self.step(result)
        print('Exiting wakeup')

# Normal usecase
Task(do_func(1,2)).step()

# Another usecase
 
def example(n):
    while n>0:
        result = yield pool.submit (func, n, n) 
        print("Got : ", result) 
        n -= 1

# This emulates a background task where we iteratively submit new tasks one after another.
# So, normal usecase would be
Task(example(10)).step()

# New Usecase
def after(delay, gen):
    yield pool.submit(time.sleep, delay)
    result = None
    try:
        while True:
            f = gen.send(result)
            result = yield f
    except StopIteration:
        pass            
    # yield from gen

# Even Better implementation
def after(delay, gen):
    yield pool.submit(time.sleep, delay)
    yield from gen

# This won't work though. Lot going on with `yield from` that just iteration over generators.
# def after(delay, gen):
#     yield pool.submit(time.sleep, delay)
#     for fut in gen:
#         yield fut

Task(after(4,do_func(1,2))).step()
