import gc
import nmap
import threading
from queue import Queue
import sqlite3

class nmap_scan(object):
    def __init__(self,file):
        self.file = file
        self.thread_num = 10
        self.lock = threading.Lock()
        self.conn = sqlite3.connect('scan.db',check_same_thread=False)
        self.cur = self.conn.cursor()
        self.sql ="CREATE TABLE IF NOT EXISTS scan(host TEXT PRIMARY KEY, port TEXT,vendor TEXT, os TEXT, version TEXT)"
        self.cur.execute(self.sql)
        self.nm =nmap.PortScanner()

        
    def scan(self,ip_queue,scan_queue):
        ip = ip_queue.get()
        l = []
        arg = "-Pn -n --min-hostgroup 1024 --min-parallelism 1024 -F -T4  -sS -v -O"
        output = self.nm.scan(hosts=ip, arguments=arg)

        try:
            for result in output["scan"].values():
                if result["status"]["state"] == "up":
                    host = result["addresses"]["ipv4"]
                    port = []
                    for i in result["tcp"]:
                        if result["tcp"][i]["state"] == "open":
                            port.append(i)
                    vendor = result["osmatch"][0]["osclass"][0]["vendor"]
                    os = result["osmatch"][0]["osclass"][0]["osfamily"]
                    version = result["osmatch"][0]["osclass"][0]["osgen"]
                    data = [host,port,vendor,os,version]

                    scan_queue.put(data)
                    scan_queue.task_done()

        except:
            print("主机down")



    def scan_thread(self):
        with open(self.file,"r") as f:
            ip_list = f.readlines()

        ip_queue = Queue(maxsize=self.thread_num*5)
        scan_queue = Queue(maxsize=self.thread_num*5)

        ip_thread = threading.Thread(target=self.scan_ip, args=(ip_list,ip_queue,))
        ip_thread.setDaemon(True)
        ip_thread.start()


        for i in range(self.thread_num):
            scan_thread = threading.Thread(target=self.scan, args=(ip_queue,scan_queue,))
            scan_thread.setDaemon(True)
            scan_thread.start()

        sql_thread = threading.Thread(target=self.write_sql, args=(scan_queue,))
        sql_thread.setDaemon(True)
        sql_thread.start()

        ip_thread.join()
        print("ip_thread.join()")
        ip_queue.join()
        print("ip_queue.join()")
        scan_queue.join()
        print("scan_queue.join()")


        self.conn.commit()
        self.conn.close()

    def scan_ip(self,host_list,ip_queue):
        for ip in host_list:
            ip_queue.put(ip,block=True)
            ip_queue.task_done()


    def write_sql(self,scan_queue):
        while True:
            try:
                data = scan_queue.get()
                data = [str(i) for i in data]
                print(data)
                self.cur.execute(F"INSERT INTO scan values(?,?,?,?,?)", (tuple(data)))
            except:
                continue


if __name__ == "__main__":
    nm = nmap_scan("ip.txt")
    nm.scan_thread()



