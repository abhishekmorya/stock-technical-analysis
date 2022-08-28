import time

def timeit(func):
    """Pass the function then with function execution it will
    print the execution in addition.
    """
    def logtime(*args):
        start = time.time()
        func(*args)
        print(f'execution time {time.time()-start:0.4f} sec')
    return logtime