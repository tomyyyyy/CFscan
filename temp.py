import asyncio
import aiohttp



def main():
    async def fetch(session, url):
        async with session.get(url) as response:
            return await response.text()

    async def main():
        for i in range(10):
            async with aiohttp.ClientSession() as session:
                html = await fetch(session, 'http://baidu.com')
                print(i,">>>>>>>>",html)

    # tasks = [asyncio.ensure_future(fetch()) for _ in range(5)]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

main()