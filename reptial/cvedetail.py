#爬取cev_details中cve信息
import gc
import sys
import requests
from lxml import etree
from tqdm import tqdm
import threading
import time
from queue import Queue
import sqlite3
import asyncio
import aiohttp


class spider(object):
    def __init__(self):
        self.headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"}
        self.thread_num = 30
        self.trytimes = 3
        self.lock = threading.Lock()
        self.conn = sqlite3.connect('cvedetail.db',check_same_thread=False)
        self.conn.execute('PRAGMA synchronous = OFF')


    #cev_setails中按照时间找寻cve的信息
    def vulnerabilities_by_date(self):
        #创建表格
        cur = self.conn.cursor()
        #cve_id, cve_type, cve_score, cve_authority, cve_vendor, cve_produce, cve_produce_version
        sql = F"CREATE TABLE IF NOT EXISTS cve(cve_id TEXT PRIMARY KEY, type TEXT,score TEXT, authority TEXT, vendor TEXT, produce TEXT, produce_version TEXT)"
        cur.execute(sql)


        #设置两个队列
        cve_info_queue = Queue(maxsize=self.thread_num*3)

        #生成cve详情url
        producer_thread = threading.Thread(target=self.producer, args=(cve_info_queue, ))
        producer_thread.setDaemon(True)
        producer_thread.start()

        #将cve信息存储到表格之中
        excel_thread = threading.Thread(target=self.write_sql, args=(cve_info_queue, cur,))
        excel_thread.setDaemon(True)
        excel_thread.start()

        #控制线程进度，确定能够生产完毕
        producer_thread.join()
        cve_info_queue.join()


        self.conn.commit()
        self.conn.close()
        


    #将cve信息写入表格,然后删除内存数据
    def write_sql(self, cve_info_queue, cur,):
        while True:
            cve_info = cve_info_queue.get()
            # print(cve_info)
            cve_info = [str(i) for i in cve_info]
            cur.execute(F"INSERT INTO cve values(?,?,?,?,?,?,?)", (tuple(cve_info)))
            
            cve_info_queue.task_done()
            del cve_info
            gc.collect()

    #重试函数,防止连接异常
    def tyr_request(self, url, headers,timeout):
        for i in range(self.trytimes):
            try:
                res = requests.get(url, headers=headers,timeout=timeout)
                if res.status_code == 200:
                    return etree.HTML(res.content)
            except:
                continue
        return None
 
      
    #提取cve信息
    def cve_data(self, url, cve_info_queue):

        async def fetch(session, url):
            async with session.get(url) as response:
                return etree.HTML(await response.text())

        async def main():
            async with aiohttp.ClientSession() as session:
                html = await fetch(session, url)
                    #cve编号 
                cve_id = html.xpath('//*[@id="cvedetails"]/h1/a/text()')[0]
                #供应商 //*[@id="vulnprodstable"]/tbody/tr[2]/td[3]/a
                try:
                    cve_vendor = html.xpath('//*[@id="vulnprodstable"]/tr[2]/td[3]/a/text()')[0]
                except:
                    cve_vendor = " "
                #产品  //*[@id="vulnprodstable"]/tbody/tr[2]/td[4]/a
                try:
                    cve_produce = html.xpath('//*[@id="vulnprodstable"]/tr[2]/td[4]/a/text()')[0]
                except:
                    cve_produce = " "
                #版本 //*[@id="vulnprodstable"]/tbody/tr[2]/td[5]
                try:
                    cve_produce_version = html.xpath('//*[@id="vulnprodstable"]/tr[2]/td[5]')[0].text.strip()
                except:
                    cve_produce_version = " "
                
                #cve漏洞类型 
                try:
                    cve_type = html.xpath('//*[@id="cvssscorestable"]/tr[8]/td/span')[0].text
                except:
                    cve_type = " "
                #cve威胁等级
                cve_score = html.xpath('//*[@id="cvssscorestable"]/tr[1]/td/div')[0].text
                #cve获得的权限
                cve_authority = html.xpath('//*[@id="cvssscorestable"]/tr[7]/td/span')[0].text
                cve_info = [cve_id, cve_type, cve_score, cve_authority, cve_vendor, cve_produce, cve_produce_version]

                cve_info_queue.put(cve_info,timeout=5)
                    
        loop =  asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())


    #产生cve详情url
    def producer(self, cve_info_queue):  # 生产者
        for year in range(1999,2020):
            url = F"https://www.cvedetails.com/vulnerability-list/year-{year}/vulnerabilities.html"
            res = requests.get(url,headers=self.headers)
            html = etree.HTML(res.content)

            #获得漏洞页面的链接漏洞总数: 
            total_vuln = html.xpath('//*[@id="pagingb"]/b/text()')[0]
            link = html.xpath('//*[@id="pagingb"]/a/@href')
            page_link = ["https://www.cvedetails.com" + i for i in link]
            with tqdm(total=int(total_vuln)) as bar:
                for url in page_link:
                    html = self.tyr_request(url,headers=self.headers,timeout=2)
                    for i in range(1, 51):
                        try:
                            url = html.xpath('//*[@id="vulnslisttable"]/tr['+ str(2*i) + ']/td[2]/a/@href')[0]
                            cve_url = "https://www.cvedetails.com" + url
                        except:
                            break
                        self.cve_data(cve_url,cve_info_queue)
                        bar.update()

            print(F"{year}年{total_vuln}个cve信息全部写入成功")


if __name__ == "__main__":
    spider = spider()
    spider.vulnerabilities_by_date()


    
