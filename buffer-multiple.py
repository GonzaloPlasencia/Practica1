# -*- coding: utf-8 -*-
"""
Created on Sun Mar  6 22:53:08 2022

@author: Gonzalo
"""

from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Value, Array
from time import sleep
from random import random, randint

K=3
N=2

def delay(factor = 3):
    sleep(random()/factor)
    
def add_data(storage, pid, data, mutex):
    mutex.acquire()
    try:
        l=pid*N
        for _ in range(N):
            if storage[l]==0:
                storage[l]=randint(0,5)+data.value
            else:
                l+=1
        delay(6)
    finally:
        mutex.release()
        
def get_data(storage, pid, mutex, data):
    mutex.acquire()
    try:
        dato=storage[0]
        k=0
        for j in range(K):
            if storage[j*N]!=-1:
                dato=storage[j*N]
                k=j*N
                break
        for i in range(K):
            if storage[i*N]<dato and storage[i*N]!=-1:
                dato=storage[i*N]
                k=i*N
        data.value=dato
        for i in range(N-1):
            storage[k+i]=storage[k+i+1]
        storage[k+N-1]=0
    finally:
        mutex.release()
    return data.value,k
        
def producer(storage, empty, non_empty, mutex, data):
    for v in range(K):
        print(f"producer {current_process().name} produciendo")
        empty[int(current_process().name.split('_')[1])].acquire()
        try: 
            for _ in range(N):
                add_data(storage, int(current_process().name.split('_')[1]),data,mutex)
        finally:          
            non_empty[int(current_process().name.split('_')[1])].release()
        print(f"producer {current_process().name} almacenando {data}")
    empty[int(current_process().name.split('_')[1])].acquire()
    storage[int(current_process().name.split('_')[1])*N]=-1
    non_empty[int(current_process().name.split('_')[1])].release()
    
def productor(storage):
    res=False
    i=0
    while i<len(storage) and not(res):
        if storage[i]!=-1:
            res=True
        i=i+1
    return res

def consumer(storage, empty, non_empty, mutex, data):
    for v in range(K):
        non_empty[v].acquire()
    lista_ord=[]
    while productor(storage):
        print("consumer desalmacenando")
        dato,k=get_data(storage,int(current_process().name.split('_')[1]), mutex, data)
        print(dato)
        lista_ord=lista_ord+[dato]
        pos=k//K
        empty[pos].release()
        non_empty[pos].acquire()
        print(f"consumer consumiendo {dato}")
        delay()
    print(lista_ord)
    
def main():
    storage=Array('i',K*N)
    data=Value('i',0)
    for i in range(K*N):
        storage[i]=0
    print("almacén inicial", storage[:])
    non_empty=[Semaphore(0) for _ in range(K)]
    empty = [BoundedSemaphore(N) for _ in range(K)]
    mutex = Lock()

    prodlst=[Process(target=producer,name=f'prod_{i}',args=(storage,empty,
                        non_empty,mutex, data)) for i in range(K)]

    conslst=Process(target=consumer,name=f'cons_{i}',args=
                        (storage,empty,non_empty,mutex,data))
 
    for p in prodlst + [conslst]:
        p.start()

    for p in prodlst + [conslst]:
        p.join()


if __name__ == '__main__':
    main()