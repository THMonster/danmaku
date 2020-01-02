import socket, time, re, json, threading, select, websocket, ssl
from struct import pack, unpack

import requests

from .Abstract import AbstractDanMuClient

class _socket(websocket.WebSocket):
    def push(self, data, t=b'\x01'):
        # data = t + pack('>I', len(data))[1:] + data
        self.send(data)
    def pull(self):
        try: # for socket.settimeout
            return self.recv()
        except Exception as e:
            return ''

class HuoMaoDanMuClient(AbstractDanMuClient):
    def _get_live_status(self):

        # c = requests.get(self.url).content
        # r = re.search('getFlash\("(.*?)","(.*?)"\);', c)
        # data = {
        #     'cid': r.group(1),
        #     'cdns': '1',
        #     'streamtype': 'live',
        #     'VideoIDS': r.group(2), }
        # j = requests.post('http://www.huomao.com/swf/live_data', data=data).json()
        # # return j['roomStatus'] == '1'
        return True
    def _prepare_env(self):
        c = requests.get(self.url).content
        r = re.search(b'var channel_id = (\d+);', c)
        # r = re.search('/(\d+)$', self.url)
        roomId = r.group(1)
        roomId = roomId.decode('ASCII')
        url = 'http://m.huomao.com/ajax/goimConf'
        params = {
            'type': 'h5',
            # 'callback': 'jQuery171032695039477104815_1477741089191',
            '_': int(time.time() * 100), }
        headers = { 'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 6.3; Win64; x64)'\
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36', }
        c = requests.get(url, params=params, headers=headers).content
        # print(c)
        # r = re.search('jQuery[^(]*?\((.*?)\)$', c)
        socket_url = json.loads(c)['host_wss']
        r = re.search('wss://(.+?):(\d+)/', socket_url)
        danmuPort = {
            'host': r.group(1),
            'port': r.group(2),
        }

        # # s = _socket()
        # # s.connect((j['host'], int(j['port'])))
        # # data = {
        # #     'user': None,
        # #     'sys': {
        # #         'version': '0.1.6b',
        # #         'pomelo_version': '0.7.x',
        # #         'type': 'pomelo-flash-tcp', }, }
        # # data = json.dumps(data, separators=(',', ':'))
        # # s.push(data)
        # # s.pull()
        # # s.sendall(b'\x02\x00\x00\x00')
        # data = {
        #     'channelId': roomId,
        #     'log': True,
        #     'userId': '', }
        # data = '\x00\x01\x20gate.gateHandler.lookupConnector'\
        #     + json.dumps(data, separators=(',', ':'))
        # s.push(data, b'\x04')
        # r = s.pull()[6:]
        # danmuPort = json.loads(r)
        # print(danmuPort)
        # print(roomId)

        return (danmuPort['host'], int(danmuPort['port'])),\
                {'roomId': roomId, 'ws': socket_url}
    def _init_socket(self, danmu, roomInfo):
        self.danmuSocket = _socket(sslopt={"cert_reqs": ssl.CERT_NONE})
        self.danmuSocket.connect(roomInfo['ws'])
        # self.danmuSocket.settimeout(3)

        # data = {
        #     'user': None,
        #     'sys': {
        #         'version': '0.1.6b',
        #         'pomelo_version': '0.7.x',
        #         'type': 'pomelo-flash-tcp', }, }

        dmbody = {
            "Uid": 0,
            "Rid": int(roomInfo['roomId']), }

        # print(roomInfo['ws'])
        dmbody = json.dumps(dmbody, separators=(',', ':'))
        # dmbody = bytes(dmbody, 'ASCII')
        dmbody = dmbody.encode('ascii')
        data = pack('!IHHII', 16 + len(dmbody), 16, 1, 7, 1)
        data = data + dmbody
        # print(hexdump.dump(data, sep=':'))
        # print(''.join("%d " % ord(c) for c in data.decode('ascii')))
        self.danmuSocket.push(data)
        # self.danmuSocket.pull()
        # print(self.danmuSocket.pull())

        self.danmuSocket.send(b'\x00\x00\x00\x10\x00\x10\x00\x01\x00\x00\x00\x02\x00\x00\x00\x01')
        # print(self.danmuSocket.pull())
        # self.danmuSocket.sendall(b'\x02\x00\x00\x00')
        # self.danmuSocket.pull()
        # data = {
        #     'channelId': roomInfo['roomId'],
        #     'token': roomInfo['token'],
        #     'userId': roomInfo['userId'], }
        # data = json.dumps(data, separators=(',', ':'))
        # data = '\x00\x02\x20' + 'connector.connectorHandler.login' + data
        # self.danmuSocket.push(data, b'\x04')

    def _create_thread_fn(self, roomInfo):
        def keep_alive(self):
            time.sleep(30)
            # print('send heartbeat')
            # self.danmuSocket.sendall(b'\x03\x00\x00\x00')
            self.danmuSocket.send(b'\x00\x00\x00\x10\x00\x10\x00\x01\x00\x00\x00\x02\x00\x00\x00\x01')
            # print(self.danmuSocket.pull())
        def get_danmu(self):
            content = self.danmuSocket.pull()
            dm_list = []
            ops = []
            p = 0
            while True:
                if p + 1 >= len(content):
                    break
                packetLen, headerLen, ver, op, seq = unpack('!IHHII', content[p:p+16])
                ops.append(op)
                p = p + headerLen
                dm_list.append(content[p:p+packetLen-16])
                p = p + packetLen - 16
            # print("{} {} {} {} {}".format(packetLen, headerLen, ver, op, seq))
            # print(content.decode('utf8', 'ignore'))
            # print(content)
            # print(dm_list)

            for i, d in enumerate(dm_list):
                try:
                    if ops[i] == 5:
                        j = json.loads(d)
                        if 'code' in j.keys() and 'speak' in j.keys() and j['code'] == '100001':# and 'speak' in j.keys() and j['code'] == 100001:
                            # print(j['speak']['barrage'])
                            msg = {'NickName': j['speak']['user']['name'], 'Content': j['speak']['barrage']['msg'], 'MsgType': 'danmu'}
                            # print('new danmaku launched')
                        else:
                            msg = {'NickName': '', 'Content': '', 'MsgType': 'other'}
                    else:
                        msg = {'NickName': '', 'Content': '', 'MsgType': 'other'}
                except Exception as e:
                    # print(e)
                    pass
                else:
                    self.danmuWaitTime = time.time() + self.maxNoDanMuWait
                    self.msgPipe.append(msg)

            # for msg in re.findall(b'\x04\x00.*?({"[^\x04]*})', content):
            #     try:
            #         msg = json.loads(msg.decode('utf8', 'ignore'))
            #         if 'msg_content' not in msg or 'msg_type' not in msg: continue
            #         msg['NickName'] = msg['msg_content']['username']
            #         msg['Content']  = msg['msg_content'].get('content') or \
            #             msg['msg_content'].get('amount')
            #         msg['MsgType']  = {'msg': 'danmu', 'beans': 'gift',
            #             'welcome': 'enter'}.get(msg.get('msg_type'), 'other')
            #     except Exception as e:
            #         pass
            #     else:
            #         self.danmuWaitTime = time.time() + self.maxNoDanMuWait
            #         self.msgPipe.append(msg)

        return get_danmu, keep_alive # danmu, heart
