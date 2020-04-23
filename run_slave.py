from slave import *
import time
from multiprocessing import Process

def check():
    manager = BaseManager(address=("127.0.0.1",5001),authkey=b"abc")
    manager.connect()
    task_queue = manager.get_task_queue()
    count = 30
    while True:
        time.sleep(30)
        while count>0:
            time.sleep(0.1)
            if not task_queue.empty():
                count=30
                break
            else:
                count-=1
                if count==0:
                    task_queue.put(end)
                    return


def run_slave():

    node_spider = NodeSpider()
    crawl_process = Process(target=node_spider.crawl,args=())
    #check_process = Process(target=check,args=())
    #check_process.start()
    crawl_process.start()
    crawl_process.join()


if __name__ == "__main__":
    run_slave()
    

