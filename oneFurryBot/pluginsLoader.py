import importlib as ilb
import os
from types import ModuleType
import traceback
import ex
import json
import asyncio
from client import *
import opType

import re
import asyncio
import msgtypes

class LoaderMsgBind:
    _f_handler = []
    _g_handler = []
    def Friend_text(self,func,*pat:str):
        for p in pat:
            if('{' in p):
                # 提取其中的参数
                i = re.findall(r'\{([^\s]*)\}', p)
                # 重新构建表达式
                for rei in i:
                    p = p.replace(' {'+rei+'}', '( (?=[^\s])[^\s]*){1}')
                p = "MSGBIND_^" + p + "$"
                self._f_handler.append((p,i,func))
            else:
                p = "MSGBIND_^" + p + "$"
                self._f_handler.append((p,None,func))
            
    async def friend_call(self,_data:msgtypes.FriendMessage):
        pat = await _data.msgChain.getTextMsg()
        for p,i,func in self._f_handler:
            p = p[8:]
            if(i is not None):
                # 有参数列表
                grep = re.match(p,pat)
                if(grep is not None):
                    grepList = grep.groups()
                    # 构造预参数字典
                    prekwargs = {}
                    for args in grepList:
                        prekwargs[i[grepList.index(args)]] = args[1:]
                    kwargs = {}
                    for args in func.__code__.co_varnames[2:func.__code__.co_argcount]:
                        if(args not in prekwargs.keys()):
                            kwargs[args] = None
                        else:
                            kwargs[args] = prekwargs[args]
                        await asyncio.sleep(0)
                    if(await func(_data,**kwargs) == False):
                        return
                else:
                    continue
            else:
                if(re.match(p,pat) != None):
                    kwargs = {}
                    for args in func.__code__.co_varnames[2:func.__code__.co_argcount]:
                        kwargs[args] = None
                    if(await func(_data,**kwargs) == False):
                        return
                    
            await asyncio.sleep(0)

    def Group_text(self,func,*pat:str):
        for p in pat:
            if('{' in p):
                # 提取其中的参数
                i = re.findall(r'\{([^\s]*)\}', p)
                # 重新构建表达式
                for rei in i:
                    p = p.replace(' {'+rei+'}', '( (?=[^\s])[^\s]*){1}')
                p = "MSGBIND_^" + p + "$"
                self._g_handler.append((p,i,func))
            else:
                p = "MSGBIND_^" + p + "$"
                self._g_handler.append((p,None,func))

    async def group_call(self,_data:msgtypes.GroupMessage):
        pat = await _data.msgChain.getTextMsg()
        for p,i,func in self._g_handler:
            p = p[8:]
            if(i is not None):
                # 有参数列表
                grep = re.match(p,pat)
                if(grep is not None):
                    grepList = grep.groups()
                    prekwargs = {}
                    for args in grepList:
                        prekwargs[i[grepList.index(args)]] = args[1:]
                    kwargs = {}
                    for args in func.__code__.co_varnames[2:func.__code__.co_argcount]:
                        if(args not in prekwargs.keys()):
                            kwargs[args] = None
                        else:
                            kwargs[args] = prekwargs[args]
                        await asyncio.sleep(0)
                    if(await func(_data,**kwargs) == False):
                        return
                else:
                    continue
            else:
                if(re.match(p,pat) != None):
                    kwargs = {}
                    for args in func.__code__.co_varnames[2:func.__code__.co_argcount]:
                        kwargs[args] = None
                    if(await func(_data,**kwargs) == False):
                        return
                    
            await asyncio.sleep(0)

class pluginsData:
    pluginsName:str
    pluginsID:int
    pluginsPath:str
    plugins:ModuleType
    def __init__(self,_data:dict = None):
        if(_data is not None and _data != {}):
            self.pluginsName = _data["pluginsName"]
            self.pluginsID = _data["pluginsID"]
            self.pluginsPath = _data["pluginsPath"]
            self.plugins = _data["plugins"]

class pluginsLoader:
    _loaderHandlers = {}
    _registeredPlugins = {}
    _regID = 0
    event = TypeBind()
    friendMsg:None
    groupMsg:None
    def __init__(self,log,botConfig):
        self.needExit = False
        self.log = log
        self.botConfig = botConfig
        self.loadDeal = LoaderMsgBind()
        # loader消息注册
        self.loadDeal.Friend_text(self._gdeal,"#loader")
        self.loadDeal.Group_text(self._gdeal,"#loader")

    def load(self,modulePath:str)->int:
        moduleName,_ = os.path.splitext(os.path.basename(modulePath))
        try:
            _plugin = {
                "pluginsName":moduleName,
                "pluginsID":self._regID,
                "pluginsPath":ex.getPath(modulePath),
                "plugins":ilb.import_module("." + moduleName,"plugins")
            }
            self._registeredPlugins.update({moduleName:_plugin})
            self._regID += 1
            # 初始化模块，执行模块中的init方法，拿到模块内部的函数注册器
            _pluginsHandler = _plugin["plugins"].init(self.sendFriendMsg,self.sendGroupMsg)
            self._loaderHandlers[f"MODULE_{_plugin['pluginsID']}"] = _pluginsHandler
            self.log.log(1,f"Loaded Plugins: {moduleName} at {modulePath}")
            return _plugin["pluginsID"]
        except:
            self.log.log(2,f"Failed to load Plugins: {moduleName}")
            self.log.log(3,f"Loader catched traceback:\n{traceback.format_exc()}")

    def loadByConfig(self,configFilePath:str):
        try:
            with open(ex.getPath(configFilePath),mode="r",encoding="utf-8") as f:
                _plugins = json.load(f)
                pluginsList = _plugins.keys()
                self.log.log(1,f"Got {len(pluginsList)} plugins from plugins config file, try to load them...")
                for plugin in pluginsList:
                    try:
                        self.load(_plugins[plugin]["pluginsPath"])
                        self._registeredPlugins[plugin]["version"] = _plugins[plugin]["version"]
                    except:
                        self.log.log(2,f"Failed to load Plugins: {plugin}")
        except FileNotFoundError:
            self.log.log(4,f'An error config file has been gaven!')
            self.log.log(3,f"Loader catched traceback:\n{traceback.format_exc()}")

    # loader注册消息监听器，进行预处理后向功能插件下发
    @event.bind(opType.GroupMsg)
    async def _groupMsg(self,_data:dict):
        msg = GroupMessage(_data)
        # loader先处理
        try:
            await self.loadDeal.group_call(msg)
            self.log.log(1,f'[{time.strftime("%H:%M:%S",time.localtime(msg.msgChain.getSource().msgTime))}][{msg.fromGroup_name}][{msg.fromQQ_name}]->{await msg.msgChain.getTextMsg()}')
        except:
            self.log.log(2,"loader cannot deal msg")
            self.log.log(3,f"Loader catched traceback:\n{traceback.format_exc()}")
        # 在这里进行通知下发
        for plugin in self._registeredPlugins:
            try:
                pluginsIndex = self._registeredPlugins[plugin]["pluginsID"]
                await self._loaderHandlers[f"MODULE_{pluginsIndex}"].group_call(msg,plugin)
            except:
                self.log.log(2,f"Loader cannot send msg to {plugin}")
                self.log.log(3,f"Loader catched error:\n{traceback.format_exc()}")
            await asyncio.sleep(0)

    @event.bind(opType.FriendMsg)
    async def _friendMsg(self,_data:dict):
        msg = FriendMessage(_data)
        # loader先处理
        try:
            await self.loadDeal.friend_call(msg)
            self.log.log(1,f'[{time.strftime("%H:%M:%S",time.localtime(msg.msgChain.getSource().msgTime))}][{msg.fromQQ_name}]->{await msg.msgChain.getTextMsg()}')
        except:
            self.log.log(2,"loader cannot deal msg")
            self.log.log(3,f"Loader catched error\n{traceback.format_exc()}")
        # 在这里进行通知下发
        for plugin in self._registeredPlugins:
            try:
                pluginsIndex = self._registeredPlugins[plugin]["pluginsID"]
                await self._loaderHandlers[f"MODULE_{pluginsIndex}"].friend_call(msg,plugin)
            except:
                self.log.log(2,f"Loader cannot send msg to {plugin}")
                self.log.log(3,f"Loader catched error:\n{traceback.format_exc()}")
            await asyncio.sleep(0)

    def setFriendMsg(self,func):
        self.friendMsg = func
    
    def setGroupMsg(self,func):
        self.groupMsg = func

    async def _gdeal(self,data):
        msg = MsgChain()
        groupFrom = False
        if(type(data) == GroupMessage):
            msg.addAt(data.fromQQ)
            groupFrom = True
        msg.addTextMsg("-=OneFurryBot=-")
        msg.addTextMsg("已加载如下功能插件")
        if(data.fromQQ == self.botConfig.owner):
            for plugin in self._registeredPlugins:
                msg.addTextMsg(f"ID_{self._registeredPlugins[plugin]['pluginsID']}:{plugin}@{self._registeredPlugins[plugin]['version']}")

        msg.addTextMsg("")
        msg.addTextMsg("-=By LittleJiu=-")
        if(groupFrom):
            await self.sendGroupMsg(msg,data.fromGroup)
        else:
            await self.sendFriendMsg(msg,data.fromQQ)

    async def sendGroupMsg(self,msg:MsgChain,group:int,msgId:int = None):
        self.log.log(1,f'[{time.strftime("%H:%M:%S",time.localtime(time.time()))}][send] {await msg.getTextMsg()}')
        await self.groupMsg(msg,group,msgId)
        
    async def sendFriendMsg(self,msg:MsgChain,qq:int,msgId:int = None):
        self.log.log(1,f'[{time.strftime("%H:%M:%S",time.localtime(time.time()))}][send] {await msg.getTextMsg()}')
        await self.friendMsg(msg,qq,msgId)