from multiprocessing.managers import BaseManager

BaseManager.register("get_new_urls")
m = BaseManager(address=("127.0.0.1",5002),authkey=b"def")
m.connect()
print(m.get_new_urls().get_it())
