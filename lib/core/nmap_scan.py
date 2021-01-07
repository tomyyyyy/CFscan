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

        
    def scan(self,ip_queue,scan_queue):
        self.lock.acquire()
        ip = ip_queue.get()
        self.lock.release()
        l = []
        arg = "-Pn -n --min-hostgroup 1024 --min-parallelism 1024 -F -T4  -sS -v -O"
        output = nmap.PortScanner().scan(hosts=ip, arguments=arg)

        try:
            for result in output["scan"].values():
                if result["status"]["state"] == "up":
                    host = result["addresses"]["ipv4"]
                    port = self.get_open_port(result["tcp"])
                    vendor = result["osmatch"][0]["osclass"][0]["vendor"]
                    os = result["osmatch"][0]["osclass"][0]["osfamily"]
                    version = result["osmatch"][0]["osclass"][0]["osgen"]
                    data = [host,port,vendor,os,version]
                    self.lock.acquire()
                    scan_queue.put(data)
                    scan_queue.task_done()
                    self.lock.release()
        except:
            pass



    def scan_thread(self):
        with open(self.file,"r") as f:
            ip_list = f.readlines()

        ip_queue = Queue(maxsize=self.thread_num*3)
        scan_queue = Queue(maxsize=self.thread_num*3)

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
        
        ip_queue.join()
        scan_queue.join()


        self.conn.commit()
        self.conn.close()

    def scan_ip(self,host_list,ip_queue):
        for ip in host_list:
            ip_queue.put(ip)
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


    def get_open_port(self,tcp_info):
        port = []
        for i in tcp_info:
            if tcp_info[i]["state"] == "open":
                port.append(i)
        return port


if __name__ == "__main__":
    nm = nmap_scan("ip.txt")
    nm.scan_thread()



