'''
    本文件当作所有插件的sdk，为所有功能插件提供功能方法
'''

import re
import asyncio
import msgtypes

class MsgBind:
    _fri_handler = []
    _gro_handler = []
    def Friend_text(self,*pat:str):
        def deco(func):
            for p in pat:
                if('{' in p):
                    # 提取其中的参数
                    i = re.findall(r'\{([^\s]*)\}', p)
                    # 重新构建表达式
                    for rei in i:
                        p = p.replace(' {'+rei+'}', '( (?=[^\s])[^\s]*){1}')
                    p = "MSGBIND_^" + p + "$"
                    self._fri_handler.append((p,i,func))
                else:
                    p = "MSGBIND_^" + p + "$"
                    self._fri_handler.append((p,None,func))
            return func
        return deco

    async def friend_call(self,_data:msgtypes.FriendMessage):
        pat = await _data.msgChain.getTextMsg()
        for p,i,func in self._fri_handler:
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
                    for args in func.__code__.co_varnames[1:func.__code__.co_argcount]:
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
                    for args in func.__code__.co_varnames[1:func.__code__.co_argcount]:
                        kwargs[args] = None
                    if(await func(_data,**kwargs) == False):
                        return
            await asyncio.sleep(0)

    def Group_text(self,*pat:str):
        def deco(func):
            for p in pat:
                if('{' in p):
                    # 提取其中的参数
                    i = re.findall(r'\{([^\s]*)\}', p)
                    # 重新构建表达式
                    for rei in i:
                        p = p.replace(' {'+rei+'}', '( (?=[^\s])[^\s]*){1}')
                    p = "MSGBIND_^" + p + "$"
                    self._gro_handler.append((p,i,func))
                else:
                    p = "MSGBIND_^" + p + "$"
                    self._gro_handler.append((p,None,func))
            return func
        return deco

    async def group_call(self,_data:msgtypes.GroupMessage):
        pat = await _data.msgChain.getTextMsg()
        for p,i,func in self._gro_handler:
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
                    for args in func.__code__.co_varnames[1:func.__code__.co_argcount]:
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
                    for args in func.__code__.co_varnames[1:func.__code__.co_argcount]:
                        kwargs[args] = None
                    if(await func(_data,**kwargs) == False):
                        return
            await asyncio.sleep(0)






