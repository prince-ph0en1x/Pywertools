import time
import numpy as np
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed

def addone(t, wtime):
    time.sleep(wtime)
    return t, t+1

def trypp(tasks = 100, pplim = 20, wtime = 0.1):
    
    cpus = mp.cpu_count() 
    workers = max(pplim,cpus)
    
    # Parallel version
    results = np.empty(tasks)
    start = time.time()
    with ProcessPoolExecutor(max_workers = workers) as executor:
        ptasks = []
        for t in range(tasks):
            ptask = executor.submit(addone,t, wtime)
            ptasks.append(ptask)
        for ptask_done in as_completed(ptasks):
            ip, op = ptask_done.result()
            results[ip] = op
    ptime = time.time() - start
    # print(results)
    print(ptime)
    
    # Serial version
    results = np.empty(tasks)
    start = time.time()
    with ProcessPoolExecutor(max_workers = workers) as executor:
        ptasks = []
        for t in range(tasks):
            ip, op = addone(t, wtime)
            results[ip] = op
    stime = time.time() - start
    # print(results)
    print(stime)

if __name__ == '__main__':
    trypp()