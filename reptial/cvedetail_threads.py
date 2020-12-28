#爬取cev_details中cve信息
import gc
import sys
import requests
import xlsxwriter
from lxml import etree
from tqdm import tqdm
import threading
import time
from queue import Queue
import sqlite3

class spider(object):
    def __init__(self):
        self.headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"}
        self.thread_num = 10
        self.trytimes = 3
        self.lock = threading.Lock()

    #cev_setails中按照时间找寻cve的信息
    def vulnerabilities_by_date(self,year):
        url = F"https://www.cvedetails.com/vulnerability-list/year-{year}/vulnerabilities.html"
        res = requests.get(url,headers=self.headers)
        html = etree.HTML(res.content)

        #获得漏洞页面的链接漏洞总数: 
        total_vuln = html.xpath('//*[@id="pagingb"]/b/text()')
        link = html.xpath('//*[@id="pagingb"]/a/@href')
        page_link = ["https://www.cvedetails.com" + i for i in link]
 

        #创建表格并写入表头
        workbook = xlsxwriter.Workbook(F'cve_details_{year}.xlsx')
        worksheet = workbook.add_worksheet()
        con = ["cve编号","漏洞类型","cve威胁等级","获得的权限","供应商","产品","型号"]
        worksheet.write_row("A1",con)
        row = 1

        #设置两个队列
        url_queue = Queue(maxsize=self.thread_num*3)
        cve_info_queue = Queue()

        #生成cve详情url
        producer_thread = threading.Thread(target=self.producer, args=(url_queue, page_link))
        producer_thread.setDaemon(True)
        producer_thread.start()

        #处理cve详情页面
        for index in range(self.thread_num):
            consumer_thread = threading.Thread(target=self.cve_data, args=(url_queue, cve_info_queue, ))
            consumer_thread.setDaemon(True)
            consumer_thread.start()

        #将cve信息存储到表格之中
        excel_thread = threading.Thread(target=self.write_excel, args=(cve_info_queue, worksheet, row,))
        excel_thread.setDaemon(True)
        excel_thread.start()

        #控制线程进度，确定能够生产完毕
        producer_thread.join()
        url_queue.join()
        print(url_queue.qsize())
        cve_info_queue.join()
        print(cve_info_queue.qsize())
        workbook.close()


    #将cve信息写入表格,然后删除内存数据
    def write_excel(self, cve_info_queue, worksheet, row):
        while True:
                if  not cve_info_queue.empty():
                    cve_info = cve_info_queue.get()
                    worksheet.write_row(row, 0, cve_info)
                    row += 1

                    cve_info_queue.task_done()
                    del cve_info
                    gc.collect()

    #重试函数,防止连接异常
    def tyr_request(self, url, headers):
        for i in range(self.trytimes):
            try:
                res = requests.get(url, headers=headers)
                if res.status_code == 200:
                    return etree.HTML(res.content)
            except:
                continue
        return None
 
      
    #提取cve信息
    def cve_data(self, url_queue, cve_info_queue):
        while True:
            if not url_queue.empty():
                url = url_queue.get()
                html = self.tyr_request(url, headers=self.headers)
                #cve编号 
                try:
                    cve_id = html.xpath('//*[@id="cvedetails"]/h1/a/text()')[0]
                except:
                    print(url + "异常")
                #供应商 
                try:
                    cve_vendor = html.xpath('//*[@id="vulnversconuttable"]/tr[2]/td[1]/a/text()')[0]
                except:
                    cve_vendor = None
                #产品
                try:
                    cve_produce = html.xpath('//*[@id="vulnversconuttable"]/tr[2]/td[2]/a/text()')[0]
                except:
                    cve_produce = None
                #版本
                try:
                    cve_produce_version = html.xpath('//*[@id="vulnversconuttable"]/tr[2]/td[3]')[0].text.strip()
                except:
                    cve_produce_version = None
                
                #cve漏洞类型 
                try:
                    cve_type = html.xpath('//*[@id="cvssscorestable"]/tr[8]/td/span')[0].text
                except:
                    cve_type = None
                #cve威胁等级
                cve_score = html.xpath('//*[@id="cvssscorestable"]/tr[1]/td/div')[0].text
                #cve获得的权限
                cve_authority = html.xpath('//*[@id="cvssscorestable"]/tr[7]/td/span')[0].text
                cve_info = [cve_id, cve_type, cve_score, cve_authority, cve_vendor, cve_produce, cve_produce_version]

                cve_info_queue.put(cve_info)
                url_queue.task_done()

                #控制打印进度，防止不同进程同时打印
                self.lock.acquire()
                print(cve_info)
                self.lock.release()


            
    #产生cve详情url
    def producer(self, url_queue, page_link):  # 生产者
        for url in tqdm(page_link):
            html = self.tyr_request(url,headers=self.headers)
            for i in range(1, 51):
                try:
                    url = html.xpath('//*[@id="vulnslisttable"]/tr['+ str(2*i) + ']/td[2]/a/@href')[0]
                    cve_url = "https://www.cvedetails.com" + url
                except:
                    print("页面生产完毕")
                    break
                while True:
                    if not url_queue.full():
                        url_queue.put(cve_url)
                        break


if __name__ == "__main__":
    spider = spider()
    spider.vulnerabilities_by_date(1999)

    
