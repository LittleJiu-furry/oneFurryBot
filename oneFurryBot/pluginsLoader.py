import importlib as ilb
import os
from types import ModuleType
import traceback
import json
import asyncio
from client import *
import opType
import ex
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
        self.loadDeal.Group_text(self._close,"#loader_close")
        self.loadDeal.Friend_text(self._close,"#loader_close")
        self.loadDeal.Group_text(self._reload,"#reload {plugins}")
        self.loadDeal.Friend_text(self._reload,"#reload {plugins}")

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
                        self._registeredPlugins[plugin]["dec"] = _plugins[plugin]["dec"]
                    except:
                        self.log.log(2,f"Failed to load Plugins: {plugin}")
        except FileNotFoundError:
            self.log.log(4,f'An error config file has been gaven!')
            self.log.log(3,f"Loader catched traceback:\n{traceback.format_exc()}")

    def setBot(self,bot):
        self.bot = bot

    # loader注册消息监听器，进行预处理后向功能插件下发
    @event.bind(opType.GroupMsg)
    async def _groupMsg(self,_data:dict):
        msg = GroupMessage(_data)
        smsg = MsgChain()
        if(ex.isBlocked(msg.fromQQ) == False):
            # loader先处理
            try:
                self.log.log(1,f'[{time.strftime("%H:%M:%S",time.localtime(msg.msgChain.getSource().msgTime))}][{msg.fromGroup_name}][{msg.fromQQ_name}]->{await msg.msgChain.getFullContent()}')
                await self.loadDeal.group_call(msg)
            except:
                self.log.log(2,"loader cannot deal msg")
                self.log.log(3,f"Loader catched error:\n{traceback.format_exc()}")
                smsg.addTextMsg(f"接收到消息内容为: {await msg.msgChain.getFullContent()}\nloader catched error:\n{traceback.format_exc()}")
                await self.sendGroupMsg(smsg,msg.fromGroup)
            # 在这里进行通知下发
            for plugin in self._registeredPlugins:
                try:
                    pluginsIndex = self._registeredPlugins[plugin]["pluginsID"]
                    await self._loaderHandlers[f"MODULE_{pluginsIndex}"].group_call(msg,plugin)
                except:
                    self.log.log(2,f"Loader cannot send msg to {plugin}")
                    self.log.log(3,f"Loader catched error:\n{traceback.format_exc()}")
                    smsg.addTextMsg(f"接收到消息内容为: {await msg.msgChain.getFullContent()}\nloader catched error:\n{traceback.format_exc()}")
                    await self.sendGroupMsg(smsg,msg.fromGroup)
                await asyncio.sleep(0)

    @event.bind(opType.FriendMsg)
    async def _friendMsg(self,_data:dict):
        msg = FriendMessage(_data)
        smsg = MsgChain()
        if(ex.isBlocked(msg.fromQQ) == False):
            # loader先处理
            try:
                self.log.log(1,f'[{time.strftime("%H:%M:%S",time.localtime(msg.msgChain.getSource().msgTime))}][{msg.nickName}]->{await msg.msgChain.getFullContent()}')
                await self.loadDeal.friend_call(msg)
            except:
                self.log.log(2,"loader cannot deal msg")
                self.log.log(3,f"Loader catched error\n{traceback.format_exc()}")
                smsg.addTextMsg(f"接收到消息内容为: {await msg.msgChain.getFullContent()}\nloader catched error:\n{traceback.format_exc()}")
                await self.sendFriendMsg(smsg,msg.fromQQ)
            # 在这里进行通知下发
            for plugin in self._registeredPlugins:
                try:
                    pluginsIndex = self._registeredPlugins[plugin]["pluginsID"]
                    await self._loaderHandlers[f"MODULE_{pluginsIndex}"].friend_call(msg,plugin)
                except:
                    self.log.log(2,f"Loader cannot send msg to {plugin}")
                    self.log.log(3,f"Loader catched error:\n{traceback.format_exc()}")
                    smsg.addTextMsg(f"接收到消息内容为: {await msg.msgChain.getFullContent()}\nloader catched error:\n{traceback.format_exc()}")
                    await self.sendFriendMsg(smsg,msg.fromQQ)
                await asyncio.sleep(0)

    def setFriendMsg(self,func):
        self.friendMsg = func
    
    def setGroupMsg(self,func):
        self.groupMsg = func

    # 获得loader已加载的插件
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
                msg.addTextMsg(f"ID_{self._registeredPlugins[plugin]['pluginsID']}:{plugin}@{self._registeredPlugins[plugin]['version']} {self._registeredPlugins[plugin]['dec']}")

        msg.addTextMsg("")
        msg.addTextMsg("-=By LittleJiu=-")
        if(groupFrom):
            await self.sendGroupMsg(msg,data.fromGroup)
        else:
            await self.sendFriendMsg(msg,data.fromQQ)

    # 尝试关闭机器人
    async def _close(self,data):
        if(self.botConfig.owner == data.fromQQ):
            # 来源于主人
            msg = MsgChain()
            msg.addTextMsg("Loader 正在尝试关闭")
            if(type(data) == GroupMessage):
                await self.sendGroupMsg(msg,data.fromGroup)
            elif(type(data) == FriendMessage):
                await self.sendFriendMsg(msg,data.fromQQ)
            
            self.bot.close()

    # 重载指定插件
    async def _reload(self,data,plugins):
        if(data.fromQQ == self.botConfig.owner):
            # 判断是否来源于主人
            msg = MsgChain()
            groupFrom = False
            if(type(data) == GroupMessage):
                groupFrom = True
                msg.addAt(data.fromQQ)
            if(plugins is not None):
                # 测试，仅尝试卸载
                if(plugins in self._registeredPlugins.keys()):
                    _plugin = {
                        "pluginsName":plugins,
                        "pluginsID":self._registeredPlugins[plugins]['pluginsID'],
                        "pluginsPath":f"./plugins/{plugins}.py",
                        "plugins":self._registeredPlugins[plugins]['plugins'],
                        "version":self._registeredPlugins[plugins]['version'],
                        "dec":self._registeredPlugins[plugins]['dec']
                    }
                    try:
                        self._loaderHandlers.pop(f"MODULE_{_plugin['pluginsID']}")
                        self._registeredPlugins.pop(plugins)
                        self.log.log(1,f"Loader try to uninstalled plugin {plugins} succeed")
                        # 尝试重新载入
                        _plugin["plugins"] = ilb.reload(_plugin["plugins"])
                        _pluginHandler = _plugin["plugins"].init(self.sendFriendMsg,self.sendGroupMsg)
                        self._loaderHandlers[f"MODULE_{_plugin['pluginsID']}"] = _pluginHandler
                        self._registeredPlugins[plugins] = _plugin
                        self.log.log(1,f"Loader try to reload plugin {plugins} succeed")
                        msg.addTextMsg(f"插件 {plugins} 尝试重载成功")
                    except:
                        self.log.log(2,f"Loader cannot try reload plugin {plugins}")
                        self.log.log(3,f"Loader catched error:\n{traceback.format_exc()}")
                        self.log.log(2,f"Loader cannot reinstall plugin {plugins} but this plugin has been uninstalled")
                else:
                    # 指定插件尚未加载，则尝试加载
                    try:
                        if(os.path.exists(f"./plugins/{plugins}.py")):
                            self.load(f"./plugins/{plugins}.py")
                            msg.addTextMsg(f"指定插件尚未被加载，已尝试加载")
                            self.log.log(1,f"Loader not found plugin {plugins} from loaded plugins but installed this plugin succeed")
                        else:
                            # 指定插件文件不存在，无法加载
                            msg.addTextMsg(f"指定插件尚未被加载，且无法尝试加载，请检查插件文件是否存在")
                            self.log.log(2,f"Loader cannot found plugin {plugins} from plugins menu, please ensure plugin file can be found in plugins menu './plugins'")
                    except:
                        self.log.log(2,f"Loader cannot reload plugin {plugins} because something wrong from load function")
                        self.log.log(3,f"Loader catched error:\n{traceback.format_exc()}")

            else:
                msg.addTextMsg("请给定需要重载的插件名")

            if(groupFrom):
                await self.sendGroupMsg(msg,data.fromGroup,data.msgChain.getSource().msgId)
            else:
                await self.sendFriendMsg(msg,data.fromQQ,data.msgChain.getSource().msgId)

    async def sendGroupMsg(self,msg:MsgChain,group:int,msgId:int = None):
        m = (await msg.getTextMsg()).replace("\n","\\n")
        self.log.log(1,f'[{time.strftime("%H:%M:%S",time.localtime(time.time()))}][send]->[{group}] {m}')
        await self.groupMsg(msg,group,msgId)
        
    async def sendFriendMsg(self,msg:MsgChain,qq:int,msgId:int = None):
        m = (await msg.getTextMsg()).replace("\n","\\n")
        self.log.log(1,f'[{time.strftime("%H:%M:%S",time.localtime(time.time()))}][send]->[{qq}] {m}')
        await self.friendMsg(msg,qq,msgId)
