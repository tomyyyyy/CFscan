import asyncio
import aiohttp
from lxml import etree
import requests


# async def fetch(session, url):
#     async with session.get(url) as response:
#         return await response.text()

# async def main():
#     for i in range(10):
#         async with aiohttp.ClientSession() as session:
#             html = etree.HTML(await fetch(session, 'http://baidu.com'))
#             print(html)

# async def test(url):
#     async with aiohttp.ClientSession() as client:
#         async with aiohttp.request('GET',url) as resp:

#             print(etree.HTML(await resp.text()))
#             # print(await )



# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())

session = requests.Session()
req = session.get('https://www.cvedetails.com')



