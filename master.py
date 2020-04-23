import queue
from multiprocessing.managers import BaseManager
import hashlib, pickle
from multiprocessing import Process
import time


class UrlManager:

    def __init__(self):
        self.hash_obj = hashlib.md5()
        BaseManager.register("get_new_urls")
        BaseManager.register("get_old_urls")
        self.manager = BaseManager(address=("127.0.0.1",5002),authkey=b"def")
        self.manager.connect()
        self.new_urls = self.manager.get_new_urls()
        self.old_urls = self.manager.get_old_urls()

    def has_new_url(self):
        if self.new_urls.len()>0:
            return True
        else:
            return False

    def add_new_url(self, new_url):
        if not new_url:
            return False
        else:
            self.hash_obj.update(new_url.encode('utf8'))
            new_url_md5 = self.hash_obj.hexdigest()
            if self.old_urls.has_one(new_url_md5):
                return False
            self.new_urls.insert(0, new_url)
            return True

    def pop_new_url(self):
        if self.new_urls.len()==0:
            return
        else:
            url = self.new_urls.pop()
            self.hash_obj.update(url.encode('utf8'))
            url_md5 = self.hash_obj.hexdigest()
            self.old_urls.append(url_md5)
            return url

    def new_urls_size(self):
        return self.new_urls.len()

    def old_urls_size(self):
        return self.old_urls.len()

    def add_new_urls(self, new_url_list):
        for url in new_url_list:
            self.add_new_url(url)

        return True

    def __del__(self):
        print('Bey Bey')


class SpiderManager:

    def __init__(self):
        self.url_manager = UrlManager()
        self.data_storer = DataStorer()
        BaseManager.register("get_count")
        BaseManager.register("get_y_n")
        self.manager = BaseManager(address=("127.0.0.1",5002),authkey=b"def")
        self.manager.connect()
        self.count = self.manager.get_count()
        self.y_n = self.manager.get_y_n()

    def get_manager(self, task_queue, result_queue, conn_queue, store_queue):

        def _return_task_queue():
            return task_queue

        def _return_result_queue():
            return result_queue

        def _return_conn_queue():
            return conn_queue

        def _return_store_queue():
            return store_queue

        BaseManager.register('get_task_queue', callable=_return_task_queue)
        BaseManager.register('get_result_queue', callable=_return_result_queue)
        BaseManager.register('get_conn_queue', callable=_return_conn_queue)
        BaseManager.register('get_store_queue', callable=_return_store_queue)
        manager = BaseManager(address=('127.0.0.1', 5001), authkey=b'abc')
        return manager

    def url_manager_processing(self, task_queue, conn_queue, start_url):
        self.url_manager.add_new_url(start_url)
        while True:
            if self.count.value()>=1000:
                print("you most have 1000 photo")
                task_queue.put("end")
                return  
            if self.count.value()%100==0 and self.count.value()!=0:
                time.sleep(5)
            if self.url_manager.has_new_url():
                new_url = self.url_manager.pop_new_url()
                if new_url == 'end':
                    task_queue.put('end')
                    return
                task_queue.put(new_url)

            if not conn_queue.empty():
                urls = conn_queue.get()
                if urls == "end":
                    return 
                self.url_manager.add_new_urls(urls)

    def result_processing(self, conn_queue, result_queue, store_queue):
        while True:
            if not result_queue.empty():
                content = result_queue.get()
                if content['new_urls'] == 'end':
                    store_queue.put("end")
                    conn_queue.put("end")
                    return
                new_urls = content['new_urls']
                conn_queue.put(new_urls)
                data = content['data']
                store_queue.put(data)

    def store_processing(self, store_queue):
        while True:
            if not store_queue.empty():
                data = store_queue.get()
                if data == 'end':
                    del self.data_storer
                    return
                self.data_storer.store_file(data)


class DataStorer():

    def __init__(self):
        self.datas = list()
        self.store_path = "./store.html"
        self.start_store()
        BaseManager.register("get_count")
        self.manager = BaseManager(address=("127.0.0.1",5002),authkey=b"def")
        self.manager.connect()
        self.count = self.manager.get_count()

    def __del__(self):
        self.end_store()

    def start_store(self):
        f = open(self.store_path,"w")
        f.write("<html>")
        f.write("<body>")
        f.close()

    def data_store(self,data):
        self.datas.append(data)
        if len(self.datas) == 10:
            f = open(self.store_path,"a")
            for data in self.datas:
                f.write(str(data))
            self.datas = []
            f.close()
        else:
            return
    
    def store_file(self,data):
        for text in data:
            if data == None:
                continue
            f = open("./img/"+self.count.str()+".jpg","wb")
            f.write(text)
            f.close()
            self.count.add(1)
            #

    def end_store(self):
        f = open(self.store_path,"a")
        f.write("</body>")
        f.write("</html>")
        f.close()


class Count():
    def __init__(self):
        self.count = 0

    def str(self):
        return str(self.count)

    def add(self,num):
        self.count+=num

    def value(self):
        return self.count

    def set_value(self,value):
        self.count = value

class Urls():
    def __init__(self):
        self.urls = list()

    def append(self,value):
        self.urls.append(value)

    def pop(self):
        return self.urls.pop()

    def has_one(self,value):
        return (value in self.urls)

    def len(self):
        return len(self.urls)

    def insert(self,idx,value):
        self.urls.insert(idx,value)

    def get_it(self):
        return self.urls

    def set_it(self,value):
        self.urls = value

    def set_value(self,value):
        self.urls = value

class Y_N():
    def __init__(self):
        self.y_n = "s"

    def value(self):
        return self.y_n

    def set_value(self,value):
        self.y_n = value


class Process_value_manager():

    def __init__(self):
        self.new_urls_path = "./new_urls.pkl"
        self.old_urls_path = "./old_urls.pkl"
        self.count_path = "./count.pkl"
        self.new_urls = self.load_new_urls()
        self.old_urls = self.load_old_urls()
        self.count = self.load_count()
        self.manager = self.get_manager()
        self.manager.start()
        self.new_urls = self.manager.get_new_urls()
        self.old_urls = self.manager.get_old_urls()
        self.count = self.manager.get_count()
        self.y_n = self.manager.get_y_n()

    def close(self):
        self.new_f = open(self.new_urls_path,"wb")
        self.old_f = open(self.old_urls_path,"wb")
        self.count_f = open(self.count_path,"wb")
        pickle.dump(self.new_urls.get_it(),self.new_f)
        pickle.dump(self.old_urls.get_it(),self.old_f)
        pickle.dump(self.count.value(),self.count_f)
        self.new_f.close()
        self.old_f.close()
        self.count_f.close()
        print("---------------------------------------")

    def get_manager(self):
        BaseManager.register("get_y_n",callable=self.has_y_n)
        BaseManager.register("get_new_urls",callable=self.has_new_urls)
        BaseManager.register("get_old_urls",callable=self.has_old_urls)
        BaseManager.register("get_count",callable=self.has_count)
        manager = BaseManager(address=("127.0.0.1",5002),authkey=b"def")
        return manager
    
    def has_y_n(self):
        y_n = Y_N()
        return y_n

    def has_new_urls(self):
        n = self.new_urls
        return n

    def has_old_urls(self):
        return self.old_urls

    def has_count(self):
        return self.count

    def load_new_urls(self):
        try:
            with open(self.new_urls_path,"rb") as f:
                value = pickle.load(f)
            new_urls = Urls()
            new_urls.set_value(value)
            return new_urls
        except Exception as e:
            print(e)
            return Urls()

    def load_old_urls(self):
        try:
            with open(self.old_urls_path,"rb") as f:
                value = pickle.load(f)
            old_urls = Urls()
            old_urls.set_value(value)
            return old_urls
        except Exception as e:
            print(e)
            return Urls()

    def load_count(self):
        try:
            with open(self.count_path,"rb") as f:
                value = pickle.load(f)
            count = Count()
            count.set_value(value)
            return count
        except Exception as e:
            print(e)
            return Count()

    












