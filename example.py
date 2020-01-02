import asyncio
import danmaku

def cb(m):
    if m['msg_type'] == 'danmaku':
        print(f'[{m["name"]}]{m["content"]}')


async def main():
    dmc = danmaku.DanmakuClient('https://douyu.com/9999', cb)
    await dmc.start()

asyncio.run(main())
