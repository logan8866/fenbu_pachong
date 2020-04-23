from multiprocessing.managers import BaseManager
import hashlib, pickle
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
        self.new_f = open(self.new_urls_path,"wb")
        self.old_f = open(self.old_urls_path,"wb")
        self.count_f = open(self.count_path,"wb")

    def __del__(self):
        print(self.new_urls.get_it())
        pickle.dump(self.new_urls.get_it(),self.new_f)
        pickle.dump(self.old_urls.get_it(),self.old_f)
        pickle.dump(self.count.value(),self.count_f)
        self.new_f.close()
        self.old_f.close()
        self.count_f.close()
        print("---------------------------------------")

    def get_manager(self):
        BaseManager.register("get_new_urls",callable=self.has_new_urls)
        BaseManager.register("get_old_urls",callable=self.has_old_urls)
        BaseManager.register("get_count",callable=self.has_count)
        manager = BaseManager(address=("127.0.0.1",5002),authkey=b"def")
        return manager

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

import time

if __name__ == "__main__":
    p = Process_value_manager()
    p.new_urls.append("hello")
    print(p.new_urls.get_it())
    time.sleep(10)
    p.close()

