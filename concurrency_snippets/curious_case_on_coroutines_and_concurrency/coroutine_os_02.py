"""
Continuing from `coroutine_os_01.py`, we add concept of coroutine/Application-program requesting services from the 
Scheduler/OS. Take a look at `NewTask` System call. 
"""

from coroutine_os_01 import Task
from queue import Queue

class SystemCall(object):
    def handle(self):
        pass

class GetTid(SystemCall):
    def handle(self):
        self.task.sendval = self.task.tid
        self.sched.schedule(self.task)



class Scheduler:
    def __init__(self):
        self.ready_queue = Queue()
        self.taskmap = {}

    def new(self, target, name):
        newtask = Task(target, name)
        self.taskmap[newtask.tid] = newtask
        self.schedule(newtask)
        return newtask.tid

    def schedule(self, task):
        self.ready_queue.put(task)
    
    def exit(self, task):
        del self.taskmap[task.tid]

    def mainloop(self):
        while self.taskmap:
            # print('Queue State : ')
            # for i in list(self.ready_queue.queue):
            #     print(f'\t Task Details : ', (i.name, i.tid, id(i)))
            # print()
            task = self.ready_queue.get()
            try:
                # print("Executing Task : ", (task.name, task.tid, id(task)))
                # import pdb; pdb.set_trace()
                result = task.run()

                # If result is a system call that the task is requesting, it's job of scheduler
                # to handle that call.
                if isinstance(result, SystemCall):
                    result.task = task
                    result.sched = self
                    result.handle()
                    continue
            except StopIteration:
                self.exit(task)
                continue
            self.schedule(task)


import time
def foo():
    """
    A Task Requesting a Service from OS (i.e our Scheduler) to get it's ID.
    """
    print('Requesting Service for Task Id from OS/Scheduler .. ')
    my_tid = yield GetTid() # Note : During this system call, os also switches to another task.  
    for i in range(10):
        print(f'I am foo. My Id is : {my_tid}')
        yield

def bar():
    my_tid = yield GetTid()
    for i in range(5):
        print(f'I am bar with id {my_tid}')
        yield


## A simple task scheduling between two coroutines. 
## Imagine how could you be achieving this with functions ...
if __name__ == '__main__':
    scheduler = Scheduler()
    b = bar()
    f = foo()
    scheduler.new(f,'foo')
    scheduler.new(b, 'bar')
    scheduler.mainloop()










