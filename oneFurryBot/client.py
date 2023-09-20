from websocket import WebSocket
import json
import time
import re
import asyncio
from msgtypes import *
import requests
import platform

# 类型绑定器
class TypeBind:
    event_handlers = {}
    def bind(self,type:str):
        def decorator(func):
            if type in self.event_handlers:
                self.event_handlers[type].append(func)
            else:
                self.event_handlers[type] = [func]
            return func
        return decorator
    
    def getHandlers(self):
        return self.event_handlers

# 机器人基础类
class Bot:
    def __init__(self,vk:str,botQQ:int,eventBind:TypeBind,baseURL:str):
        self.baseURL = baseURL
        self.vk = vk
        self.botQQ = botQQ
        self.sessionKey = ""
        self.ws_status = False
        self.event = eventBind
        self.ws = WebSocket()
        if(platform.system() == "Linux"):
            import uvloop
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        
        self.loop = asyncio.new_event_loop()

    def connect(self):
        self.ws.connect(f"{self.baseURL}/all?verifyKey={self.vk}&qq={str(self.botQQ)}")
        self.ws_status = True
        asyncio.get_event_loop().run_until_complete(self._outData())

    def close(self):
        self.ws_status = False
        self.ws.close()

    async def _outData(self):
        while self.ws_status:
            await asyncio.sleep(0)
            data = self.ws.recv()
            recData = json.loads(data)
            if(recData["syncId"] == ""):
                # 是初次连接时返回sessionKey的响应
                self.sessionKey = recData["data"]["session"]
            elif(recData["syncId"] == "-1"):
                await self._deal(recData["data"])
            await asyncio.sleep(0)
    
    async def _deal(self,data:dict):
        handlers = self.event.getHandlers()
        if data["type"] in handlers:
            for _handler in handlers[data["type"]]:
                await _handler(self.obj,data)

    def _putData(self,content:dict,command:str):
        msgData = {}
        msgData["syncId"] = int(time.time() * 1000)
        msgData["command"] = command
        msgData["subCommand"] = None
        msgData["content"] = content
        self.ws.send(json.dumps(msgData))

    async def sendFriendMsg(self,msg:MsgChain,target:int,MsgId:int = None):
        # 构建发送的消息
        _msg = {
            "sessionKey": self.sessionKey,
            "target": target,
            "messageChain":msg.getMsgChain()
        }
        if(MsgId != None):
            _msg["quote"] = MsgId
        self._putData(_msg,"sendFriendMessage")
    
    async def sendGroupMsg(self,msg:MsgChain,group:int,MsgId:int = None):
        # 构建发送的消息
        _msg = {
            "sessionKey": self.sessionKey,
            "target": group,
            "messageChain":msg.getMsgChain()
        }
        if(MsgId != None):
            _msg["quote"] = MsgId
        self._putData(_msg,"sendGroupMessage")

    def setFatherObject(self,fatherObject):
        self.obj = fatherObject





