#爬取cnnvd中cve信息
import gc
import sys
import requests
import xlsxwriter
from lxml import etree
from tqdm import tqdm
import threading

class spider(object):
    def __init__(self):
        self.headers={"user-agent":"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0"}

    def cnnvd_vuln_page(self, total_page):

        #创建表格并写入表头
        workbook = xlsxwriter.Workbook(F'cnnvd.xlsx')
        worksheet = workbook.add_worksheet()
        con = ["cnnvd编号","cnnvd漏洞类型"]
        worksheet.write_row("A1",con)
        row = 1
        
        #总共有15596页漏洞详情
        cnnvd_info = []
        if total_page > 15596:
            total_page = 15596
        for page in tqdm(range(1, total_page)):
            url = F"http://cnnvd.org.cn/web/vulnerability/queryLds.tag?pageno={page}&repairLd="
            res = requests.get(url,headers=self.headers)
            html = etree.HTML(res.content)
            #每一页有10条漏洞信息 
            for i in range(10):
                cnnvd_id = html.xpath(F'//*[@id="vulner_{i}"]/p/a/text()')[0].strip()
                cnnvd_type = html.xpath(F'//*[@id="vulner_{i}"]/a/text()')[0].strip()
                cnnvd_info.append([cnnvd_id, cnnvd_type])

            #将cve信息写入表格,然后删除内存数据
            for info in cnnvd_info:
                worksheet.write_row(row, 0, info)
                row += 1
                del info
                gc.collect()

        workbook.close()

if __name__ == "__main__":
    spider = spider()
    spider.cnnvd_vuln_page(10)