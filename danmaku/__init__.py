import re, asyncio, aiohttp

from .bilibili import Bilibili
from .douyu import Douyu
from .huya import Huya

__all__     = ['DanmakuClient']

class DanmakuClient:
    def __init__(self, url, q):
        self.__url          = ''
        self.__site         = None
        self.__hs           = None
        self.__ws           = None
        self.__stop         = False
        self.__dm_queue     = q
        self.__link_status  = True
        if 'http://' == url[:7] or 'https://' == url[:8]:
            self.__url = url
        else:
            self.__url = 'http://' + url
        for u, s in {'douyu.com'         : Douyu,
                     'live.bilibili.com' : Bilibili,
                     'huya.com'          : Huya,
                     'huomao.com'        : None, }.items() :
            if re.match(r'^(?:http[s]?://)?.*?%s/(.+?)$' % u, url):
                self.__site = s
                break
        if self.__site == None:
            print('Invalid link!')
            exit
        self.__hs = aiohttp.ClientSession()

    async def init_ws(self):
        ws_url, reg_datas = await self.__site.get_ws_info(self.__url)
        self.__ws = await self.__hs.ws_connect(ws_url)
        for reg_data in reg_datas:
            await self.__ws.send_bytes(reg_data)

    async def heartbeats(self):
        while self.__stop != True:
            # print('heartbeat')
            await asyncio.sleep(20)
            try:
                await self.__ws.send_bytes(self.__site.heartbeat)
            except:
                pass


    async def fetch_danmaku(self):
        while self.__stop != True:
            async for msg in self.__ws:
                self.__link_status = True
                ms = self.__site.decode_msg(msg.data)
                for m in ms:
                    await self.__dm_queue.put(m)
            if self.__stop != True:
                await asyncio.sleep(1)
                await self.init_ws()
                await asyncio.sleep(1)

    async def start(self):
        await self.init_ws()
        await asyncio.gather(
            self.heartbeats(),
            self.fetch_danmaku(),
        )

    async def stop(self):
        self.__stop = True
        await self.__hs.close()
