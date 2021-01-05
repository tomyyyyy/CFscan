import gc
import geoip2.database
import nmap

class nmap_scan(object):
    def __init__(self):
        pass
        
    def scan(self,host_list):
        l = []
        arg = "-Pn -n --min-hostgroup 1024 --min-parallelism 1024 -F -T4  -sS -v -O"
        output = nmap.PortScanner().scan(hosts=host_list, arguments=arg)

        for result in output["scan"].values():
            if result["status"]["state"] == "up":
                host = result["addresses"]["ipv4"]
                port = self.get_open_port(result["tcp"])
                vendor = result["osmatch"][0]["osclass"][0]["vendor"]
                os = result["osmatch"][0]["osclass"][0]["osfamily"]
                version = result["osmatch"][0]["osclass"][0]["osgen"]
                data = {"host":host, "port":port, "vendor":vendor, "os":os, "version":version}

            l.append(data)
            del result
            gc.collect()
        return l


    def get_open_port(self,tcp_info):
        port = []
        for i in tcp_info:
            if tcp_info[i]["state"] == "open":
                port.append(i)
        return port

   
if __name__ == "__main__":
    nm = nmap_scan()
    ip = "47.95.4.158"
    l = nm.scan(ip)
    print(l)

