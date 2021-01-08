import requests

def get_proxy():
    return requests.get("http://118.24.52.95:5010/get").json()

def delete_proxy(proxy):
    requests.get("http://118.24.52.95/delete/?proxy={}".format(proxy))

# your spider code

def getHtml():
    # ....
    retry_count = 5
    proxy = get_proxy().get("proxy")
    print(proxy)
    while retry_count > 0:
        try:
            print("http://{}".format(proxy))
            html = requests.get('http://www.example.com', proxies={"http": "http://{}".format(proxy)})
            # 使用代理访问
            return html
        except Exception:
            retry_count -= 1
    # 删除代理池中代理
    delete_proxy(proxy)
    return None

getHtml()