# ------------------------------------------------------------
# pyos6.py  -  The Python Operating System
#
# Added support for task waiting
# ------------------------------------------------------------

# ------------------------------------------------------------
#                       === Tasks ===
# ------------------------------------------------------------
from coroutine_os_01 import Task

# ------------------------------------------------------------
#                      === Scheduler ===
# ------------------------------------------------------------
from queue import Queue

class Scheduler(object):
    def __init__(self):
        self.ready   = Queue()   
        self.taskmap = {}        

        # Tasks waiting for other tasks to exit
        self.exit_waiting = {}

    def new(self,target, name):
        newtask = Task(target,name)
        self.taskmap[newtask.tid] = newtask
        self.schedule(newtask)
        return newtask.tid

    def exit(self,task):
        print(f"Task {task.tid} terminated ")
        del self.taskmap[task.tid]
        # Notify other tasks waiting for exit
        for task in self.exit_waiting.pop(task.tid,[]):
            self.schedule(task)

    def waitforexit(self,task,waittid):
        if waittid in self.taskmap:
            self.exit_waiting.setdefault(waittid,[]).append(task)
            return True
        else:
            return False

    def schedule(self,task):
        self.ready.put(task)

    def mainloop(self):
         while self.taskmap:
            print('Queue State : ')
            for i in list(self.ready.queue):
                print(f'\t Task Details : ', (i.name, i.tid, id(i)))
            print()
            task = self.ready.get()
            try:
                result = task.run()
                if isinstance(result,SystemCall):
                    result.task  = task
                    result.sched = self
                    result.handle()
                    continue
            except StopIteration:
                self.exit(task)
                continue
            self.schedule(task)

# ------------------------------------------------------------
#                   === System Calls ===
# ------------------------------------------------------------

class SystemCall(object):
    def handle(self):
        pass

# Return a task's ID number
class GetTid(SystemCall):
    def handle(self):
        self.task.sendval = self.task.tid
        self.sched.schedule(self.task)

# Create a new task
class NewTask(SystemCall):
    """
    When we create a new task inside another Task by yielding a NewTask Handler. 
    execution goes back to the scheduler. NewTask handler will now schedule the supplied 
    task to the task-queue along with the current task itself.

    We each task will be alternativly run in the main loop. 
    """
    def __init__(self,target, name):
        self.target = target
        self.name = name
    def handle(self):
        # OS schedules the new task
        tid = self.sched.new(self.target, self.name)
        self.task.sendval = tid
        # But also schedule the current task
        self.sched.schedule(self.task)

# Kill a task
class KillTask(SystemCall):
    def __init__(self,tid):
        self.tid = tid
    def handle(self):
        task = self.sched.taskmap.get(self.tid,None)
        if task:
            task.target.close() 
            self.task.sendval = True
        else:
            self.task.sendval = False
        self.sched.schedule(self.task)

# Wait for a task to exit
class WaitTask(SystemCall):
    """
    Impelentation details :
    - scheduler has as waiting area : exit_waiting dict
    - Say we created a task inside another task. Now want to wait until this new task wraps up
    - What we do is, after we hit WaitTask sys call (i.e yield ) in main, we put the `main` in the waiting area and add 
      new task in the queue.
    - Since only new task remains in queue, it gets executed and schedule in the scheduler loop. After it hit gets exhausted 
      and hit's StopIteration, we tell scheduler to bring back the main-task in the queue. Take a look at `exit` method  ! 
    """
    def __init__(self,tid):
        self.tid = tid
    def handle(self):
        result = self.sched.waitforexit(self.task,self.tid)
        self.task.sendval = result
        # If waiting for a non-existent task,
        # return immediately without waiting
        if not result:
            self.sched.schedule(self.task)

# ------------------------------------------------------------
#                      === Example ===
# ------------------------------------------------------------
if __name__ == '__main__':
    
    def foo():
        for i in range(5):
            print("I'm foo")
            yield

    def main():
        child = yield NewTask(foo(), "foo")
        print("Waiting for child")
        # NOTE : We are calling WaitTask  from main. Above when we called NewTask from main, exectuing newtask.handle
        # added new Task `foo` as well as current task `main` in the task-Queue. With wait, we simly don't add current task
        # until the task under wait is finished.
        yield WaitTask(child)
        print("Child done")

    sched = Scheduler()
    sched.new(main(), "main")
    sched.mainloop()