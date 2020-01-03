# danmaku
一个基于aiohttp的直播网站弹幕库(WIP)

目前支持斗鱼、虎牙、B站

感谢[danmu](https://github.com/littlecodersh/danmu)

## 用法

```
import asyncio
import danmaku

def cb(m):
    if m['msg_type'] == 'danmaku':
        print(f'[{m["name"]}]{m["content"]}')


async def main():
    dmc = danmaku.DanmakuClient('https://douyu.com/9999', cb)
    await dmc.start()

asyncio.run(main())
```
