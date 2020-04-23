from slave import HTMLDownloader,Parse,NodeSpider
from master import SpiderManager
from multiprocessing.managers import BaseManager
import queue

def test_downloader():
    downloader = HTMLDownloader()
    content = downloader.download("http://jandan.net/ooxx")
    parse = Parse()
    urls,data = parse.parse(content)
    print(urls,data)

task_queue = queue.Queue()
result_queue = queue.Queue()

def return_task_queue():
    global task_queue
    return task_queue

def return_result_queue():
    global result_queue
    return result_queue

def test_nodespider():
    BaseManager.register('get_task_queue', callable=return_task_queue)
    BaseManager.register('get_result_queue', callable=return_result_queue)
    manager = BaseManager(address=('127.0.0.1', 5001), authkey=b'abc')
    manager.start()
    task_queue = manager.get_task_queue()
    result_queue = manager.get_result_queue()
    task_queue.put("end")
    node = NodeSpider()
    node.crawl()
    data = result_queue.get()
    print(data)



if __name__ == "__main__":
    test_nodespider()
