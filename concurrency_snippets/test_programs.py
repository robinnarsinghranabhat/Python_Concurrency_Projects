import time 
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

nums = [8,7,8,5,8,8,5,4,8,7,7,8,8,7,8,8,8]

def some_computation(n):
    counter = 0
    for _ in range(n*1_000_000):
        counter += 1
    return counter

def sequential():
    for n in nums:
        some_computation(n)

def threaded():
    with ThreadPoolExecutor() as executor:
        executor.map(some_computation, nums)

def pooled():
    with ProcessPoolExecutor() as executor:
        executor.map(some_computation, nums)

if __name__ == '__main__':
    for func in sequential, threaded, pooled:
        start = time.perf_counter()
        func()
        end = time.perf_counter()
        print(func.__name__, f'{end-start:.4f}')
