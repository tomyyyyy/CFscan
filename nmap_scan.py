import gc
import geoip2.database
import nmap

class nmap_scan(object):
    def __init__(self):
        pass
        
    def scan(self,host):
        l = []
        arg = "-PE -n --min-hostgroup 1024 --min-parallelism 1024 -F -T4 -Pn -sS -v -O"
        output = nmap.PortScanner().scan(hosts=host, arguments=arg)

        for result in output["scan"].values():
            if result["status"]["state"] == "up":
                host_list = result["addresses"]["ipv4"]
                vendor = result["vendor"]
                reason = result["status"]["reason"]
                port = result["portused"]
                os = result["osmatch"]
                data = {"host":host_list,"vendor":vendor,"reason":reason,"port":port,"os":os}

            l.append(data)
            del result
            gc.collect()
        return l


    def geo(self, allDate):
        l = []
        list = []

        # 将所查询的IP地址读取出来赋值给data
        for i in range(len(allDate)):
            ip = allDate[i]['host']
            list.append(self.get_address(ip))
        return list

    def get_address(self,ip):
        reader = geoip2.database.Reader('./resourses/GeoLite2-City.mmdb')
        response = reader.city(ip)

        country = response.country.names["zh-CN"]
        site = response.subdivisions.most_specific.names.get("zh-CN")
        city = response.city.names.get("zh-CN")
        Location_Latitude = response.location.latitude
        Location_Longitude = response.location.longitude
        address = '{}{}{} 经纬度:{} {}'.format(country, site, str(city),str(Location_Latitude),str(Location_Longitude))
        return address


if __name__ == "__main__":
    nm = nmap_scan()
    l = nm.scan("47.95.4.158")
    print(l)
    address = nm.geo(l)
    print(address)

