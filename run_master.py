from master import *
from multiprocessing import Process
import queue
import time

def run_master():
    start_url = "http://jandan.net/ooxx"
    v_manager = Process_value_manager()

    master_spider = SpiderManager()
    task_queue = queue.Queue()
    result_queue = queue.Queue()
    conn_queue = queue.Queue()
    store_queue = queue.Queue()
    manager = master_spider.get_manager(task_queue,result_queue,conn_queue,store_queue)
    manager.start()
    task_queue = manager.get_task_queue()
    result_queue = manager.get_result_queue()
    conn_queue = manager.get_conn_queue()
    store_queue = manager.get_store_queue()
    url_manager_process = Process(target=master_spider.url_manager_processing,args=(task_queue,conn_queue,start_url))
    result_process = Process(target=master_spider.result_processing,args=(conn_queue,result_queue,store_queue))
    store_process = Process(target=master_spider.store_processing,args=(store_queue,))
    url_manager_process.start()
    result_process.start()
    store_process.start()
    while True:
        if v_manager.count.value()%100 == 0 and v_manager.count.value()!=0:
            print("\nnow you have %d photo"%v_manager.count.value())
            y_n = input("\nis you continue?(y/n)")
            if y_n !="y":
                y_n = "n"
            v_manager.y_n.set_value(y_n)
            if y_n == "n":
                task_queue.put("end")
                break

    url_manager_process.join()
    result_process.join()
    store_process.join()
    v_manager.close()

if __name__ == "__main__":
    run_master()

