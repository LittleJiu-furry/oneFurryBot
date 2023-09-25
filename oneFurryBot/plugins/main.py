from . import sdk
import asyncio
import ex
import os

class myBind(sdk.MsgBind):
    def __init__(self) -> None:
        super().__init__()
        self.pluginName = os.path.splitext(os.path.basename(__file__))[0]
    
    def Friend_text(self, *pat: str):
        return super().Friend_text(self.pluginName, *pat)
    
    def Group_text(self, *pat: str):
        return super().Group_text(self.pluginName,*pat)

mBind = myBind()
botConfig = ex.getRobotConf()

def init(fm,gm):
    global sendFMsg,sendGMsg
    sendFMsg = fm
    sendGMsg = gm
    return mBind

async def sendGroupMsg(msg:sdk.msgtypes.MsgChain,group:int,MsgId:int = None):
    await sendGMsg(msg,group,MsgId)

async def sendFriendMsg(msg:sdk.msgtypes.MsgChain,friend:int,MsgId:int = None):
    await sendFMsg(msg,friend,MsgId)



# 菜单
@mBind.Group_text("#菜单","#menu")
async def menu(data:sdk.msgtypes.GroupMessage)->bool:
    msg = sdk.msgtypes.MsgChain()
    msg.addTextMsg("-=OneFurryBot=-")
    msg.addTextMsg("#菜单 #menu 打开菜单")
    msg.addTextMsg("#系统信息 #system 查看系统信息")
    msg.addTextMsg("#签到 签到相关菜单")
    msg.addTextMsg("#宠物 宠物相关菜单")
    msg.addTextMsg("#主人 主人指令")
    msg.addTextMsg("#loader 获得加载器的信息")
    msg.addTextMsg("")
    msg.addTextMsg("[使用说明]")
    msg.addTextMsg("[]表示必给参数")
    msg.addTextMsg("<>表示可选参数")
    msg.addTextMsg("")
    msg.addTextMsg("-=By LittleJiu=-")
    await sendGroupMsg(msg,data.fromGroup)
    return sdk.ALLOW_NEXT


import time
import platform
# 系统信息 
@mBind.Group_text("#系统信息","#system")
@mBind.Friend_text("#系统信息","#system")
async def systemInfo(data)->bool:
    msg = sdk.msgtypes.MsgChain()
    msg.addTextMsg("-=OneFurryBot=-")
    msg.addTextMsg("所用框架: Mirai")
    msg.addTextMsg(f'当前平台: {platform.system()}')
    msg.addTextMsg(f'平台版本信息: {platform.version()}')
    msg.addTextMsg(f'当前Python版本: {platform.python_version()}')
    _now = time.localtime(time.time())
    msg.addTextMsg(f'当前系统时间: {time.strftime("%Y-%m-%d %H:%M:%S", _now)}')
    msg.addTextMsg("-=By LittleJiu=-")
    if(type(data) == sdk.msgtypes.GroupMessage):
        # 来自群里
        await sendGroupMsg(msg,data.fromGroup)
    elif(type(data) == sdk.msgtypes.FriendMessage and data.fromQQ == botConfig.owner):
        # 来自好友
        await sendFriendMsg(msg,data.fromQQ)
    return sdk.ALLOW_NEXT

@mBind.Group_text("#主人")
@mBind.Friend_text("#主人")
async def ownerMenu(data):
    msg = sdk.msgtypes.MsgChain()
    msg.addTextMsg("-=OneFurryBot=-")
    msg.addTextMsg("[主人模块]")
    msg.addTextMsg("")
    msg.addTextMsg(f"#补偿 [user] [num] 为用户补偿{botConfig.signConfig.signName}")
    msg.addTextMsg("#loader_close 关闭Loader(关闭机器人)")
    msg.addTextMsg("#reload [plugin] 重载插件")
    msg.addTextMsg("")
    msg.addTextMsg("【本模块下所有指令仅主人生效】")
    msg.addTextMsg("-=By LittleJiu=-")
    if(type(data) == sdk.msgtypes.GroupMessage):
        await sendGroupMsg(msg,data.fromGroup)
    else:
        await sendFriendMsg(msg,data.fromQQ)
    
    return sdk.ALLOW_NEXT


import re
# 主人功能，为所有用户补偿积分
@mBind.Group_text("#补偿 {user} {num}")
@mBind.Friend_text("#补偿 {user} {num}")
async def owner_addSignValue(data,user,num):
    if(data.fromQQ == botConfig.owner):
        if('@' in user):
            if(re.match(r'^\[@\(\d*\)\]$',user) != None):
                user_id = ex.analysisAt(user)
            else:
                return sdk.ALLOW_NEXT
        else:
            user_id = user
        
        _user = ex.getUserSignData(user_id)
        _user.signValue += int(num)
        ex.writeUserData(_user,user_id)
        msg = sdk.msgtypes.MsgChain()
        groupFrom = False
        if(type(data) == sdk.msgtypes.GroupMessage):
            msg.addAt(data.fromQQ)
            groupFrom = True
        
        msg.addTextMsg(f"已为用户({user_id})补偿{botConfig.signConfig.signName}{num}点")
        if(groupFrom):
            await sendGroupMsg(msg,data.fromGroup)
        else:
            await sendFriendMsg(msg,data.fromQQ)
    
    return sdk.ALLOW_NEXT




