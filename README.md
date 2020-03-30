# danmaku
一个基于aiohttp的直播网站弹幕库(WIP)

目前支持斗鱼、虎牙、B站

感谢[danmu](https://github.com/littlecodersh/danmu)

## 用法

```
import asyncio
import danmaku

async def printer(q):
    while True:
        m = await q.get()
        if m['msg_type'] == 'danmaku':
            print(f'[{m["name"]}]{m["content"]}')


async def main():
    q = asyncio.Queue()
    dmc = danmaku.DanmakuClient('https://douyu.com/9999', q)
    asyncio.create_task(printer(q))
    await dmc.start()

asyncio.run(main())
```
