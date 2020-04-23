from multiprocessing.managers import BaseManager
import requests
from bs4 import BeautifulSoup
import hashlib,pickle

class NodeSpider():

    def __init__(self):
        BaseManager.register("get_task_queue")
        BaseManager.register("get_result_queue")
        self.address = ("127.0.0.1",5001)
        self.manager = BaseManager(address=self.address,authkey=b"abc")
        try:
            self.manager.connect()
        except:
            print("no master")
        self.task_queue = self.manager.get_task_queue()
        self.result_queue = self.manager.get_result_queue()
        self.downloader = HTMLDownloader()
        self.parse = Parse()

    def crawl(self):
        while True:
            if not self.task_queue.empty():
                url = self.task_queue.get()
                if url == "end":
                    self.result_queue.put({"new_urls":url,"data":url})
                    return 
                content = self.downloader.download(url)
                urls,datas = self.parse.parse(content)
                data_file = list()
                for data in datas:
                    text = self.downloader.download_file(data)
                    data_file.append(text)
                self.result_queue.put({"new_urls":urls,"data":data_file})

        return


class HTMLDownloader():

    def __init__(self):
        self.agent = {
                "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
                "User-Agent":"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)"
        }
        self.hash_obj = hashlib.md5()
        self.process_path = "./download_process.pkl"
        self.downloaded_url = self.load_download_process()
        self.f = open(self.process_path,"wb")
    
    def save_download_process(self):
        pickle.dump(self.downloaded_url,self.f)
        self.f.close()

    def load_download_process(self):
        try:
            f = open(self.process_path,'rb')
            a = pickle.load(f)
            f.close()
            return a
        except:
            return list()

    def __del__(self):
        self.save_download_process()
        
    def download(self,url):
        response = requests.get(url,headers=self.agent)
        if response.status_code == 200:
            return response.content.decode("utf8")
        else:
            return None
    def download_file(self,url):
        response = requests.get(url,headers=self.agent)
        if response.status_code == 200:
            self.hash_obj.update(url.encode("utf8"))
            hash_value = self.hash_obj.hexdigest()
            self.downloaded_url.append(hash_value)
            return response.content
        else:
            return None

class Parse():

    def __init__(self):
        self.url_header = "http:"

    def parse(self,content):
        self.soup = BeautifulSoup(content,"lxml")
        self.soup.prettify()
        next_urls = self._find_next_urls()
        data = self._find_data()
        return next_urls,data

    def _find_next_urls(self):
        urls = self.soup.select("a[class='previous-comment-page']")
        next_urls = list()
        next_urls.append(self.url_header+urls[0].get("href"))
        return next_urls

    def _find_data(self):
        imgs = self.soup.select("img[referrerpolicy='no-referrer']")
        data = list()
        for img in imgs:
            url = self.url_header+img.get("src")
            data.append(url)
        return data



















