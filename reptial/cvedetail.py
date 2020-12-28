#爬取cev_details中cve信息
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


    #cev_setails中按照时间找寻cve的信息
    def vulnerabilities_by_date(self,year):
        url = F"https://www.cvedetails.com/vulnerability-list/year-{year}/vulnerabilities.html"
        res = requests.get(url,headers=self.headers)
        html = etree.HTML(res.content)

        #漏洞总数
        vuln_total = html.xpath('//*[@id="pagingb"]/b/text()')
        #获得漏洞页面的链接
        link = html.xpath('//*[@id="pagingb"]/a/@href')
        page_link = []
        for i in link:
            i = "https://www.cvedetails.com" + i
            page_link.append(i)


        #创建表格并写入表头
        workbook = xlsxwriter.Workbook(F'cve_details_{year}.xlsx')
        worksheet = workbook.add_worksheet()
        con = ["cve编号","漏洞类型","发布日期","更新时间","cve威胁等级","获得的权限","访问方式","供应商","产品","型号"]
        worksheet.write_row("A1",con)
        row = 1

        #获取详细信息
        cve_info = []
        print("正在处理页面信息:")
        for url in tqdm(page_link):
            res = requests.get(url,headers=self.headers)
            html = etree.HTML(res.content)
            cve_info = self.cve_data(html)
            
            #将cve信息写入表格,然后删除内存数据
            for info in cve_info:
                worksheet.write_row(row, 0, info)
                row += 1
                del info
                gc.collect()

        workbook.close()


    #提取cve信息
    def cve_data(self,html):
        result_list = []
        b = 1
        while b <= 50:
            #cve编号
            cve_id = html.xpath('//*[@id="vulnslisttable"]/tr[' + str(2*b) +']/td[2]/a/text()')
            if not cve_id:
                break
            cve_id = cve_id[0]

            #进入cve详情url
            cve_url = "https://www.cvedetails.com" + html.xpath('//*[@id="vulnslisttable"]/tr['+ str(2*b) + ']/td[2]/a/@href')[0]
            cve_html = etree.HTML(requests.get(cve_url,headers=self.headers).content)
            #供应商 
            try:
                cve_vendor = cve_html.xpath('//*[@id="vulnversconuttable"]/tr[2]/td[1]/a/text()')[0]
            except:
                cve_vendor = " "
            #产品
            try:
                cve_produce = cve_html.xpath('//*[@id="vulnversconuttable"]/tr[2]/td[2]/a/text()')[0]
            except:
                cve_produce = " "
            #版本
            try:
                cve_produce_version = cve_html.xpath('//*[@id="vulnversconuttable"]/tr[2]/td[3]')[0].text.strip()
            except:
                cve_produce_version = " "
            
            #cve漏洞类型 
            cve_type = html.xpath('//*[@id="vulnslisttable"]/tr[' + str(2*b) +']/td[5]')[0].text.strip()
            #cve发布日期
            release_time = html.xpath('//*[@id="vulnslisttable"]/tr[' + str(2*b) +']/td[6]')[0].text
            #cve更新时间 
            update_time = html.xpath('//*[@id="vulnslisttable"]/tr[' + str(2*b) +']/td[7]')[0].text
            #cve威胁等级
            cve_score = html.xpath('//*[@id="vulnslisttable"]/tr[' + str(2*b) +']/td[8]/div/text()')[0]
            #cve获得的权限
            cve_authority = html.xpath('//*[@id="vulnslisttable"]/tr[' + str(2*b) +']/td[9]')[0].text
            #cve访问方式
            cve_view = html.xpath('//*[@id="vulnslisttable"]/tr[' + str(2*b) +']/td[10]')[0].text
            cve_info = [cve_id, cve_type, release_time, update_time, cve_score, cve_authority, cve_view, cve_vendor, cve_produce, cve_produce_version]

            b += 1
            print(cve_info)
            result_list.append(cve_info)

        return result_list


if __name__ == "__main__":
    spider = spider()
    spider.vulnerabilities_by_date(1999)

    
