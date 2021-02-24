import asyncio
import danmaku
import sys


async def printer(q):
    while True:
        m = await q.get()
        print(m)


async def main():
    q = asyncio.Queue()
    dmc = danmaku.DanmakuClient(sys.argv[1], q)
    asyncio.create_task(printer(q))
    await dmc.start()


asyncio.run(main())
