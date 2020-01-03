import re, asyncio, aiohttp

from .config import VERSION
from .bilibili import Bilibili
from .douyu import Douyu
from .huya import Huya


__version__ = VERSION
__all__     = ['DanmakuClient']

class DanmakuClient:
    def __init__(self, url, cb):
        self.__url          = ''
        self.__site         = None
        self.__hs           = None
        self.__ws           = None
        self.__remnant      = b''
        self.__stop         = False
        self.__callback     = cb
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
            exit
        self.__hs = aiohttp.ClientSession()

    async def init_ws(self):
        # print(self.__site.heartbeat)
        ws_url, reg_datas = await self.__site.get_ws_info(self.__url)
        # print(ws_url)
        # print(reg_datas)
        self.__ws = await self.__hs.ws_connect(ws_url)
        for reg_data in reg_datas:
            await self.__ws.send_bytes(reg_data)

    async def heartbeats(self):
        while self.__stop != True:
            # print('heartbeat')
            await asyncio.sleep(30)
            await self.__ws.send_bytes(self.__site.heartbeat)

    async def fetch_danmaku(self):
        async for msg in self.__ws:
            ms, self.__remnant = self.__site.decode_msg(self.__remnant + msg.data)
            for m in ms:
                self.__callback(m)


    async def start(self):
        await self.init_ws()
        await asyncio.gather(
            self.heartbeats(),
            self.fetch_danmaku(),
        )
