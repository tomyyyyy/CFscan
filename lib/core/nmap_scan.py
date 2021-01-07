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

        
    def scan(self,ip):
        l = []
        arg = "-Pn -n --min-hostgroup 1024 --min-parallelism 1024 -F -T4  -sS -v -O"
        output = nmap.PortScanner().scan(hosts=ip, arguments=arg)

        for result in output["scan"].values():
            if result["status"]["state"] == "up":
                host = result["addresses"]["ipv4"]
                port = self.get_open_port(result["tcp"])
                vendor = result["osmatch"][0]["osclass"][0]["vendor"]
                os = result["osmatch"][0]["osclass"][0]["osfamily"]
                version = result["osmatch"][0]["osclass"][0]["osgen"]
                # data = {"host":host, "port":port, "vendor":vendor, "os":os, "version":version}
                data = [host,port,vendor,os,version]
                return data


    def scan_thread(self):
        with open(self.file,"r") as f:
            ip_list = f.readlines()

        scan_thread_list = []
        for i in range(self.thread_num):
            scan_thread = threading.Thread(target=self.scan_ip, args=(ip_list,))
            scan_thread.setDaemon(True)
            scan_thread.start()
            scan_thread_list.append(scan_thread)

        for i in scan_thread_list:
            i.join()
        self.conn.commit()
        self.conn.close()


    def scan_ip(self,host_list):
        for ip in host_list:
            try:
                data = self.scan(ip)
                if data is None:
                    continue
                print(data)
                self.lock.acquire()
                self.cur.execute(F"INSERT INTO scan values(?,?,?,?,?)", (tuple(data)))
                self.lock.release()
            except:
                print("null")


    def get_open_port(self,tcp_info):
        port = []
        for i in tcp_info:
            if tcp_info[i]["state"] == "open":
                port.append(i)
        return port

   
if __name__ == "__main__":
    nm = nmap_scan("ip.txt")
    nm.scan_thread()



