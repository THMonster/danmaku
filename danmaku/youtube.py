import json, re, select, random, traceback
import asyncio, aiohttp

# The core codes for YouTube support are basically from taizan-hokuto/pytchat

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
}


class Youtube:
    q = None
    url = ''
    vid = ''
    ctn = ''
    client = None
    stop = False

    @classmethod
    async def run(cls, url, q, client, **kargs):
        from .paramgen import liveparam
        cls.q = q
        cls.url = url
        cls.client = client
        cls.stop = False
        await cls.get_url()
        while cls.stop == False:
            try:
                await cls.get_room_info()
                cls.ctn = liveparam.getparam(cls.vid, 1)
                await cls.get_chat()
            except:
                # traceback.print_exc()
                await asyncio.sleep(1)

    @classmethod
    async def stop(cls):
        cls.stop == True

    @classmethod
    async def get_url(cls):
        a = re.search(r'youtube.com/channel/([^/?]+)', cls.url)
        try:
            cid = a.group(1)
            cls.url = f'https://www.youtube.com/channel/{cid}/videos'
        except:
            a = re.search(r'youtube.com/c/([^/?]+)', cls.url)
            cid = a.group(1)
            cls.url = f'https://www.youtube.com/c/{cid}/videos'

    @classmethod
    async def get_room_info(cls):
        async with cls.client.request('get', cls.url) as resp:
            t = re.search(r'"gridVideoRenderer"((.(?!"gridVideoRenderer"))(?!"style":"UPCOMING"))+"label":"(LIVE|LIVE NOW|PREMIERING NOW)"([\s\S](?!"style":"UPCOMING"))+?("gridVideoRenderer"|</script>)', await resp.text()).group(0)
            # t = re.search(r'("gridVideoRenderer"(.(?!"gridVideoRenderer"))+"label":"(LIVE|LIVE NOW|PREMIERING NOW)".+)', t).group(1) 
            cls.vid = re.search(r'"gridVideoRenderer".+?"videoId":"(.+?)"', t).group(1) 

    @classmethod
    async def get_chat_single(cls):
        import urllib.parse
        msgs = []
        u = f'https://www.youtube.com/live_chat/get_live_chat?continuation={urllib.parse.quote(cls.ctn)}&pbj=1'
        async with cls.client.request('get', u, headers=headers) as resp:
            j = await resp.json()
            j = j['response']['continuationContents']
            # print(j)
            cont = j['liveChatContinuation']['continuations'][0]
            if cont is None:
                raise Exception('No Continuation')
            metadata = (cont.get('invalidationContinuationData')
                        or cont.get('timedContinuationData')
                        or cont.get('reloadContinuationData')
                        or cont.get('liveChatReplayContinuationData')
                        )
            cls.ctn = metadata['continuation']
            # print(j['liveChatContinuation'].get('actions'))
            for action in j['liveChatContinuation'].get('actions', []):
                try:
                    renderer = action['addChatItemAction']['item']['liveChatTextMessageRenderer']
                    msg = {}
                    msg['name'] = renderer['authorName']['simpleText']
                    message = ''
                    runs = renderer["message"].get("runs")
                    for r in runs:
                        if r.get('emoji'):
                            message += r['emoji'].get('shortcuts', [''])[0]
                        else:
                            message += r.get('text', '')
                    msg['content'] = message
                    msg['msg_type']  = 'danmaku'
                    msgs.append(msg)
                except:
                    pass

        return msgs

    @classmethod
    async def get_chat(cls):
        while cls.stop == False:
            ms = await cls.get_chat_single()
            if len(ms) != 0:
                interval = 1 / len(ms)
            else:
                await asyncio.sleep(1)
            for m in ms:
                await cls.q.put(m)
                await asyncio.sleep(interval)
