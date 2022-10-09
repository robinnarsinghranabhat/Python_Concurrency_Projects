"""
Goal : 
- Make a multitasking os using coroutines.
- By multitasking, we don't mean parallel processing. We will do something that a single core CPU does.
  Rapidly context switch between different tasks/coroutines and execution each of them for a while.
  WE WILL DO THIS IN PURE PYTHON WITHOUT USING THREADS ! 
 
## Coroutine itself is a task ##  
 - A task that runs until it hits yield. Then it transfers execution to another task.
"""

class Task:
    """
    Create a Task class as a  Wrapper to run a coroutine.
    i.e rather than using coroutine object directly, use it through the `Task` interface
    """
    taskid = 0
    def __init__(self, target):
        Task.taskid += 1
        self.tid = Task.taskid
        self.target = target # coroutine to be executed
        self.sendval = None
    # Run the task until it hits the next yield statement.
    def run(self):
        return self.target.send(self.sendval)

## Scheduler
from queue import Queue
from sched import scheduler

class Scheduler:
    """
    Scheduler emulates an OS. 
    OS 101 :
    - OS continously switches between differnt application programs. NOTE that all our CPU does is execute
      instruction given to it. That means, when OS places our application-program in CPU, it itself doesnt run.
      Infact, only when Application-program requests services from Operating systems (system calls like read), 
      execution transfers back to operationg system. 

    Now our Scheduler will do something similar. Rapidly context switch between tasks. And our Tasks are coroutines 
    with yield statements. One key difference is here, we need to place `yield` in our application-program (i.e tasks) 
    itself to pause/resume between tasks.  


    """
    def __init__(self):
        self.ready_queue = Queue()
        self.taskmap = {}

    def new(self, target):
        newtask = Task(target)
        self.taskmap[newtask.tid] = newtask
        self.schedule(newtask)
        return newtask.tid

    def schedule(self, task):
        self.ready_queue.put(task)
    
    def exit(self, task):
        del self.taskmap[task.tid]

    def mainloop(self):
        while self.taskmap:
            task = self.ready_queue.get()
            try:
                result = task.run()
            except StopIteration:
                self.exit(task)
                continue
            self.schedule(task)


import time
def foo():
    for i in range(10):
        time.sleep(0.01)
        print('I am foo')
        yield

def bar():
    for i in range(5):
        time.sleep(0.1)
        print('I am bar')
        yield


## A simple task scheduling between two coroutines. 
## Imagine how could you be achieving this with functions ...
if __name__ == '__main__':
    scheduler = Scheduler()
    b = bar()
    f = foo()
    scheduler.new(f)
    scheduler.new(b)
    scheduler.mainloop()
    
