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

# 功能分级菜单
@mBind.Group_text("#宠物")
async def pet(data:sdk.msgtypes.GroupMessage)->bool:
    msg = sdk.msgtypes.MsgChain()
    msg.addTextMsg("-=OneFurryBot=-")
    msg.addTextMsg("[宠物系统]")
    msg.addTextMsg("")
    msg.addTextMsg("#领养宠物 [名字] 领养一个宠物")
    msg.addTextMsg("#喂养宠物 投喂宠物")
    msg.addTextMsg("#宠物更名 [名字] #宠物改名 [名字] 为宠物改名")
    msg.addTextMsg("")
    msg.addTextMsg("-=By LittleJiu=-")
    await sendGroupMsg(msg,data.fromGroup)
    return sdk.ALLOW_NEXT

# 领养宠物
@mBind.Group_text("#领养宠物","#领养宠物 {name}")
@mBind.Friend_text("#领养宠物","#领养宠物 {name}")
async def getNewPet(data,name:str):
    groupFrom = False
    msg = sdk.msgtypes.MsgChain()
    if(type(data) == sdk.msgtypes.GroupMessage):
        msg.addAt(data.fromQQ)
        groupFrom = True
    
    _mePet = ex.getPetInfo(data.fromQQ)
    if(_mePet != None):
        msg.addTextMsg("你已经有宠物啦，再领养一个养的过来嘛(?)")
        if(groupFrom):
            await sendGroupMsg(msg,data.fromGroup,data.msgChain.getSource().msgId)
        else:
            await sendFriendMsg(msg,data.fromQQ,data.msgChain.getSource().msgId)
        return sdk.ALLOW_NEXT
    _pet = ex.createPet(data.fromQQ,name)
    msg.addTextMsg("-=OneFurryBot=-")
    msg.addTextMsg(f"你成功领养了[{_pet.name}]")
    msg.addTextMsg(f"[{_pet.name}]的物种为：{_pet.family}")
    msg.addTextMsg(f"[{_pet.name}]预计每日最少需要花费{_pet.minNeed}积分投喂")
    msg.addTextMsg(f"请好好爱护Ta哦~")

    if(groupFrom):
        await sendGroupMsg(msg,data.fromGroup)
    else:
        await sendFriendMsg(msg,data.fromQQ)
    return sdk.ALLOW_NEXT

import time
import random
# 投喂宠物
@mBind.Group_text("#喂养宠物")
@mBind.Friend_text("#喂养宠物")
async def feedPet(data):
    groupFrom = False
    msg = sdk.msgtypes.MsgChain()
    if(type(data) == sdk.msgtypes.GroupMessage):
        msg.addAt(data.fromQQ)
        groupFrom = True

    _mePet = ex.getPetInfo(data.fromQQ)
    if(_mePet == None):
        msg.addTextMsg("你还没有宠物，先去领养一个吧~")
        if(groupFrom):
            await sendGroupMsg(msg,data.fromGroup,data.msgChain.getSource().msgId)
        else:
            await sendFriendMsg(msg,data.fromQQ,data.msgChain.getSource().msgId)
        return sdk.ALLOW_NEXT
    
    if(_mePet.dead):
        msg.addTextMsg("你的宠物不幸死掉了，请先安置好Ta吧")
        if(groupFrom):
            await sendGroupMsg(msg,data.fromGroup,data.msgChain.getSource().msgId)
        else:
            await sendFriendMsg(msg,data.fromQQ,data.msgChain.getSource().msgId)
        return sdk.ALLOW_NEXT
    
    # 判断今天是否投喂过了
    _lastEat = time.localtime(_mePet.lastEatTime)
    _now = time.localtime(data.msgChain.getSource().msgTime)
    if(_lastEat.tm_yday == _now.tm_yday):
        msg.addTextMsg("今天已经投喂过了，明天再来吧~")
        if(groupFrom):
            await sendGroupMsg(msg,data.fromGroup)
        else:
            await sendFriendMsg(msg,data.fromQQ)
        return sdk.ALLOW_NEXT
    _minNeed = _mePet.minNeed
    _thisNeed = _minNeed + random.choice(range(0,51))
    _nowUserData = ex.getUserSignData(data.fromQQ)
    if(_nowUserData.signValue < 0):
        msg.addTextMsg(f"emmm,看起来你的{botConfig.signConfig.signName}不足了呢，你现在有{_nowUserData.signValue}点{botConfig.signConfig.signName}，想办法搞点吧！")
        if(groupFrom):
            await sendGroupMsg(msg,data.fromGroup)
        else:
            await sendFriendMsg(msg,data.fromQQ)
        return sdk.ALLOW_NEXT
    # 修改宠物属性
    _mePet.deadValue = _mePet.deadValue - 1 if _mePet.deadValue > 0 else 0
    msg.addTextMsg(f"投喂成功，今天投喂消耗{_thisNeed}点{botConfig.signConfig.signName}")
    if(_mePet.lastEatTime != 0):
        if(_now.tm_yday - _lastEat.tm_yday != 1 and _now.tm_year == _lastEat.tm_year):
            msg.addTextMsg(f"宠物已经饿了{_now.tm_yday - _lastEat.tm_yday}天了，难道才想起来投喂么？")
            _c = random.choice(range(30,80))
            _thisNeed += _c
            msg.addTextMsg(f"本次额外消耗了{_c}点{botConfig.signConfig.signName}来投喂宠物")
            _fc = random.choice(range(3,8))
            _mePet.funValue -= _fc
            if(_mePet.funValue < 0):
                _mePet.funValue = _mePet.funLevel * 100 + _mePet.funValue
                _mePet.funLevel -= 1 if _mePet.funLevel > 0 else 0
                _mePet.deadValue += 1 if _mePet.funValue < 0 else 0
            msg.addTextMsg(f"好感度减少了{_fc}点，宠物患病死亡的概率增加了")
        elif(_now.tm_yday != 1 and _now.tm_year != _lastEat.tm_year):
            import calendar as cal
            _yearDays = 366 if cal.isleap(_lastEat.tm_year) else 365
            msg.addTextMsg(f"宠物已经饿了{_now.tm_yday + _yearDays - _lastEat.tm_yday}天了，难道才想起来投喂么？")
            _c = random.choice(range(30,80))
            _thisNeed += _c
            msg.addTextMsg(f"本次额外消耗了{_c}点{botConfig.signConfig.signName}来投喂宠物")
            _fc = random.choice(range(3,8))
            _mePet.funValue -= _fc
            if(_mePet.funValue < 0):
                _mePet.funValue = _mePet.funLevel * 100 + _mePet.funValue
                _mePet.funLevel -= 1 if _mePet.funLevel > 0 else 0
                _mePet.deadValue += 1 if _mePet.funValue < 0 else 0
            msg.addTextMsg(f"好感度减少了{_fc}点，宠物患病死亡的概率增加了")
        elif(random.choice([0,1]) == 1):
            _funValueAdd = random.choice(range(1,6))
            _mePet.funValue += _funValueAdd
            msg.addTextMsg(f"获得了{_funValueAdd}好感度")
            if(_mePet.funValue >= 100 * (_mePet.funLevel + 1)):
                _mePet.funLevel += 1
                _mePet.funValue -= _mePet.funValue * 100
                msg.addTextMsg(f"好感度达到了{_mePet.funValue * 100},你对[{_mePet.name}]的好感度等级提升了！")
    else:
        if(random.choice([0,1]) == 1):
            _funValueAdd = random.choice(range(1,6))
            _mePet.funValue += _funValueAdd
            msg.addTextMsg(f"获得了{_funValueAdd}好感度")
            if(_mePet.funValue >= 100 * (_mePet.funLevel + 1)):
                _mePet.funLevel += 1
                _mePet.funValue -= _mePet.funValue * 100
                msg.addTextMsg(f"好感度达到了{_mePet.funValue * 100},你对[{_mePet.name}]的好感度等级提升了！")
    _nowUserData.signValue -= _thisNeed
    _mePet.lastEatTime = data.msgChain.getSource().msgTime
    ex.writeUserData(_nowUserData,data.fromQQ)
    ex.writePet(data.fromQQ,_mePet)

    if(groupFrom):
        await sendGroupMsg(msg,data.fromGroup)
    else:
        await sendFriendMsg(msg,data.fromQQ)
    return sdk.ALLOW_NEXT

# 宠物更名
@mBind.Group_text("#宠物更名 {name}","#宠物改名 {name}","#宠物更名","#宠物改名")
@mBind.Friend_text("#宠物更名 {name}","#宠物改名 {name}","#宠物更名","#宠物改名")
async def renamePet(data,name):
    _petInfo = ex.getPetInfo(data.fromQQ)
    msg = sdk.msgtypes.MsgChain()
    groupFrom = False
    if(type(data) == sdk.msgtypes.GroupMessage):
        groupFrom = True
        msg.addAt(data.fromQQ)
    if(_petInfo != None):
        if(name != None):
            _petInfo.name = name
            ex.writePet(data.fromQQ,_petInfo)
            _user = ex.getUserSignData(data.fromQQ)
            if(_user.signValue <= 15):
                msg.addTextMsg(f"你现在持有的{botConfig.signConfig.signName}已经不足以更名了哦")
            else:
                _user.signValue -= 15
                msg.addTextMsg(f"你的宠物已经改名为[{name}],本次更名消耗15点{botConfig.signConfig.signName}")
        else:
            msg.addTextMsg("你的宠物名字叫空格嘛(？？？")
    else:
        msg.addTextMsg("你还没有宠物，怎么改名啊(问号脸?")
    
    if(groupFrom):
        await sendGroupMsg(msg,data.fromGroup,data.msgChain.getSource().msgId)
    else:
        await sendFriendMsg(msg,data.fromQQ,data.msgChain.getSource().msgId)
    return sdk.ALLOW_NEXT

