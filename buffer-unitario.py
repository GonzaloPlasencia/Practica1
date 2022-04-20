

from multiprocessing import Process
from multiprocessing import BoundedSemaphore, Semaphore, Lock
from multiprocessing import current_process
from multiprocessing import Value, Array
from time import sleep
from random import random, randint


K=3


def delay(factor = 3):
    sleep(random()/factor)

#Añadimos un nuevo dato al almacen cuando se pueda (igual a cero)
def add_data(storage, pid, data, mutex):
    mutex.acquire()
    try:
        if storage[pid] == 0:
            storage[pid] = randint(0,5)+data.value 
        delay(6)
    finally:
        mutex.release()
        
#Sacamos el mínmo elemento del almacen y su posicion
def get_data(storage, pid, mutex, data):
    mutex.acquire()
    try:
        dato=storage[0]
        k=0
        for j in range(len(storage)):
            if storage[j]!=-1:
                dato=storage[j]
                k=j
                break
        for i in range(len(storage)):
            if storage[i]<dato and storage[i]!=-1:
                dato=storage[i]
                k=i
        data.value=dato
        storage[k]=0
    finally:
        mutex.release()
    return data.value,k

#Iniciamos a los productores
def producer(storage, empty, non_empty, mutex, data):
    for v in range(K):
        print(f"producer {current_process().name} produciendo")
        empty[int(current_process().name.split('_')[1])].acquire()
        try: 
            add_data(storage, int(current_process().name.split('_')[1]),data,mutex)
        finally:          
            non_empty[int(current_process().name.split('_')[1])].release()
        print(f"producer {current_process().name} almacenando {data}")
    empty[int(current_process().name.split('_')[1])].acquire()
    storage[int(current_process().name.split('_')[1])]=-1
    non_empty[int(current_process().name.split('_')[1])].release()
 
#Nos dice si hay algún proceso acabado
def productor(storage):
    res=False
    i=0
    while i<len(storage) and not(res):
        if storage[i]!=-1:
            res=True
        i=i+1
    return res
        
#Iniciamos al consumidor, que tomara el minimo elemento del almacen
def consumer(storage, empty, non_empty, mutex, data):
    for v in range(K):
        non_empty[v].acquire()
    lista_ord=[]
    while productor(storage):
        print("consumer desalmacenando")
        dato,k=get_data(storage,int(current_process().name.split('_')[1]), mutex, data)
        lista_ord=lista_ord+[dato]
        empty[k].release()
        non_empty[k].acquire()
        print(f"consumer consumiendo {dato}")
        delay()
    print(lista_ord)
        
def main():
    storage=Array('i',K)
    data=Value('i',0)
    for i in range(K):
        storage[i]=0
    print("almacén inicial", storage[:])
    non_empty=[Semaphore(0) for _ in range(K)]
    empty = [Lock() for _ in range(K)]
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
        

































