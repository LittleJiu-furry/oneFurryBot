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
@mBind.Friend_text("#宠物")
async def pet(data)->bool:
    msg = sdk.msgtypes.MsgChain()
    msg.addTextMsg("-=OneFurryBot=-")
    msg.addTextMsg("[宠物系统]")
    msg.addTextMsg("")
    msg.addTextMsg("#领养宠物 <名字> 领养一个宠物")
    msg.addTextMsg("#喂养宠物 投喂宠物")
    msg.addTextMsg("#宠物更名 [名字] #宠物改名 [名字] 为宠物改名")
    msg.addTextMsg("#宠物信息 获得宠物的信息")
    msg.addTextMsg("#放生宠物 放生你的宠物")
    msg.addTextMsg("#宠物探险 <步数> 进行探险")
    msg.addTextMsg("")
    msg.addTextMsg("-=By LittleJiu=-")
    if(type(data) == sdk.msgtypes.GroupMessage):
        await sendGroupMsg(msg,data.fromGroup)
    else:
        await sendFriendMsg(msg,data.fromQQ)
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
        enable = ex.getGroupEnable(data.fromGroup,"pet")
    else:
        enable = True
    if(enable):
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
        enable = ex.getGroupEnable(data.fromGroup,"pet")
    else:
        enable = True
    if(enable):
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
        enable = ex.getGroupEnable(data.fromGroup,"pet")
    else:
        enable = True
    if(enable):
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

# 宠物信息
@mBind.Group_text("#宠物信息")
@mBind.Friend_text("#宠物信息")
async def petInfo(data):
    msg = sdk.msgtypes.MsgChain()
    groupFrom = False
    if(type(data) == sdk.msgtypes.GroupMessage):
        groupFrom = True
        msg.addAt(data.fromQQ)
        enable = ex.getGroupEnable(data.fromGroup,"pet")
    else:
        enable = True
    if(enable):
        _pet = ex.getPetInfo(data.fromQQ)
        if(_pet != None):
            msg.addTextMsg(f"-=OneFurryBot=-")
            msg.addTextMsg(f"[{_pet.name}]的信息如下:")
            msg.addTextMsg(f"当前等级: {_pet.level}")
            msg.addTextMsg(f"当前经验值: {_pet.exp}")
            msg.addTextMsg(f"物种: {_pet.family}")
            msg.addTextMsg(f"好感等级: {_pet.funLevel}")
            msg.addTextMsg(f"当前好感度: {_pet.funValue}")
            msg.addTextMsg(f"每日最少花费: {_pet.minNeed}")
            _last = time.localtime(_pet.lastEatTime)
            _now = time.localtime(time.time())
            _cutDays = ex.getTimeCut(_now,_last)
            if(_cutDays.days == 0):
                msg.addTextMsg(f"今日已投喂，没有挨饿")
            elif(_cutDays.days == 1):
                msg.addTextMsg(f"今天还没有投喂，别忘了哦~")
            elif(_cutDays.days > 1):
                msg.addTextMsg(f"已经{_cutDays.days}天没有投喂了，Ta快饿坏了(颓废)")
            
            msg.addTextMsg("")
            msg.addTextMsg("-=By LittleJiu=-")
        else:
            msg.addTextMsg("你还没有宠物哦，请先领养一个吧~")

        
        if(groupFrom):
            await sendGroupMsg(msg,data.fromGroup)
        else:
            await sendFriendMsg(msg,data.fromQQ)
    
    return sdk.ALLOW_NEXT

# 交互彩蛋
@mBind.Group_text("#喵喵喵")
async def mewoEgg(data:sdk.msgtypes.GroupMessage):
    msg = sdk.msgtypes.MsgChain()
    msg.addAt(data.fromQQ)
    msg.addTextMsg("喵喵喵？")
    await sendGroupMsg(msg,data.fromGroup,data.msgChain.getSource().msgId)
    await asyncio.sleep(1)
    msg.clearMsgChain()
    msg.addTextMsg("被你发现了呢，不过我可不是猫猫哦^o^y")
    await sendGroupMsg(msg,data.fromGroup)

# 放生宠物
@mBind.Group_text("#放生宠物")
@mBind.Friend_text("#放生宠物")
async def freePet(data):
    msg = sdk.msgtypes.MsgChain()
    groupFrom = False
    if(type(data) == sdk.msgtypes.GroupMessage):
        groupFrom = True
        msg.addAt(data.fromQQ)
        enable = ex.getGroupEnable(data.fromGroup,"pet")
    else:
        enable = True
    if(enable):
        if(ex.deletePet(data.fromQQ)):
            msg.addTextMsg("你的宠物被放生了")
        else:
            msg.addTextMsg("你都没有宠物难道要删空气嘛(x_x)")
        
        if(groupFrom):
            await sendGroupMsg(msg,data.fromGroup,data.msgChain.getSource().msgId)
        else:
            await sendFriendMsg(msg,data.fromQQ,data.msgChain.getSource().msgId)
    return sdk.ALLOW_NEXT

import random
# 宠物探险
@mBind.Group_text("#宠物探险","#宠物探险 {step}")
@mBind.Friend_text("#宠物探险","#宠物探险 {step}")
async def explorePet(data,step):
    msg = sdk.msgtypes.MsgChain()
    msg.addTextMsg("-=OneFurryBot=-")
    msg.addTextMsg("[宠物模块]")
    groupFrom = False
    if(type(data) == sdk.msgtypes.GroupMessage):
        groupFrom = True
        msg.addAt(data.fromQQ)
    
    _pet = ex.getPetInfo(data.fromQQ)
    _user = ex.getUserSignData(data.fromQQ)
    try:
        if(_pet != None):
            if(_pet.needBreak != True):
                _step = int(step) if step is not None else 1
                msg.addTextMsg(f"已设置当前执行步数为 {_step} 步")
                msg.addTextMsg("(警告：步数过大将可能导致程序崩溃，请谨慎使用)")
                msg.addTextMsg("计算过程中，其他指令不可用")
                msg.addTextMsg("正在进行计算...")
                msg.addTextMsg("-=By LittleJiu=-")
                ex.changeBlocked(data.fromQQ,True)
                if(groupFrom):
                    await sendGroupMsg(msg,data.fromGroup,data.msgChain.getSource().msgId)
                else:
                    await sendFriendMsg(msg,data.fromQQ,data.msgChain.getSource().msgId)
                msg.clearMsgChain()
                msg.addTextMsg("-=OneFurryBot=-")
                msg.addTextMsg("[宠物模块]")
                groupFrom = False
                if(type(data) == sdk.msgtypes.GroupMessage):
                    groupFrom = True
                    msg.addAt(data.fromQQ)

                _runStep = 0
                _addValue = 0
                _addBlockValue = 0
                _addFunValue = 0
                while _runStep < _step:
                    _runStep += 1
                    _chose = random.choice(range(0,6 * 1000 + 1))
                    _chose = _chose % 6
                    if(_chose > 3):
                        # 重新进行选择，如果5次之内这个值小于3，则返回，否则直接输出
                        for i in range(5):
                            _chose = random.choice(range(0,6 * 1000 + 1))
                            _chose = _chose % 6
                            if(_chose <= 3):
                                break
                            await asyncio.sleep(0)
                    if(_chose <= 3): 
                        # 如果选到了小于等于3的值，则生成一个包含7个0,1个1,1个2,1个3的列表并对它打乱
                        _choseList = [0] * 10
                        _list2ChoseList = list(range(0,10))
                        _a = random.choice(_list2ChoseList)
                        _choseList[_a] = 1
                        _list2ChoseList.remove(_a)
                        _a = random.choice(_list2ChoseList)
                        _choseList[_a] = 2
                        _list2ChoseList.remove(_a)
                        _a = random.choice(_list2ChoseList)
                        _choseList[_a] = 3
                        del _list2ChoseList
                        del _a
                        # 再次进行选择
                        _chose = _choseList[random.choice(range(0,10))]
                    elif(_chose == 6):
                        # 抽到死亡事件，再重新抽取5次
                        for i in range(5):
                            _chose = random.choice(range(0,6 * 1000 + 1))
                            _chose = _chose % 6
                            if(_chose != 6):
                                break
                            await asyncio.sleep(0)
                    if(_chose == 0):
                        _content = f"[{_runStep}/{_step}] 什么也没有发生"
                    elif(_chose == 1):
                        _thisValue = random.randint(5,20)
                        _addValue += _thisValue
                        _content = f"[{_runStep}/{_step}] 找到了一些东西[增加{_thisValue}点{botConfig.signConfig.signName}]"
                    elif(_chose == 2):
                        _thisValue = random.randint(15,30)
                        _addValue += _thisValue
                        _thisFun = random.randint(0,2)
                        _addFunValue += _thisFun
                        _content = f"[{_runStep}/{_step}] 发生了战斗，但是对面看起来很弱，你和[{_pet.name}]几下就将其击败了[增加了{_thisValue}点{botConfig.signConfig.signName}][增加了{_thisFun}点好感度]"
                    elif(_chose == 3):
                        _thisValue = random.randint(20,50)
                        _addValue += _thisValue
                        _thisBreak = random.randint(1,3)
                        _addBlockValue += _thisBreak
                        _thisFun = random.randint(1,3)
                        _addFunValue += _thisFun
                        _content = f"[{_runStep}/{_step}] 发生了战斗，虽然身上不小心挂彩，但是你和[{_pet.name}]还是成功将其击败[增加了{_thisValue}点{botConfig.signConfig.signName}][增加了{_thisBreak}点疲劳度][增加了{_thisFun}点好感度]"
                    elif(_chose == 4):
                        # 0：什么也没有
                        # 1：找到了一些东西[增加积分]
                        # 2：发生战斗，但是无受伤战胜[增加积分]
                        # 3：发生战斗，但是受伤战胜[增加积分，增加疲劳度]
                        # 4：发生战斗，战败，但是带走了部分收益并成功逃脱[获得部分收益，增加疲劳度]
                        # 5：发生战斗，战败，但是丢弃了所有收益并成功逃脱[增加疲劳度]
                        # 6：发生战斗，战败，死亡[宠物死亡]
                        _thisBreak = random.randint(3,5)
                        import math
                        _addValue = math.floor(_addValue * 0.8) + 1
                        _content = f"[{_runStep}/{_step}] 发生了战斗，你和[{_pet.name}]略显下风，无法战胜，只好逃离[收益削减20%][增加了{_thisBreak}点疲劳度]"
                        break
                    elif(_chose == 5):
                        _thisBreak = random.randint(7,9)
                        _addBlockValue = _thisBreak
                        _addValue = 0
                        _content = f"[{_runStep}/{_step}] 发生了战斗，对手过于强大，你使用了保命道具带着[{_pet.name}]逃走了[丢失全部收益][增加了{_thisBreak}点疲劳度]"
                        break
                    elif(_chose == 6):
                        _addValue = 0
                        _addBlockValue = 0
                        _addFunValue = 0
                        _pet.dead = True
                        _content = f"[{_runStep}/{_step}] ╥﹏╥... 你的宠物[{_pet.name}]在发生的战斗中为了保护你而死亡[丢失全部收益][宠物死亡]"
                        break
                msg.addTextMsg(f"你和[{_pet.name}]探险完毕")
                _user.signValue += _addValue
                msg.addTextMsg(f"获得了{_addValue}点{botConfig.signConfig.signName}")
                _pet.funValue += _addFunValue
                msg.addTextMsg(f"增加了{_addFunValue}点好感度")
                _addedFunLevel = 0
                while _pet.funValue >= (_pet.funLevel + 1) * 100:
                    _pet.funValue -= ((_pet.funLevel + 1) * 100)
                    _pet.funLevel += 1
                    _addedFunLevel += 1
                
                if(_addedFunLevel > 0):
                    msg.addTextMsg(f"好感度等级提升了{_addedFunLevel}级")
                
                _pet.needBreak = True
                _pet.breakStartTime = int(time.time())
                _pet.breakTime = _addBlockValue * random.choice(range(150,351))
                msg.addTextMsg(f"本次探险需要休息 {_pet.breakTime}s")
                msg.addTextMsg(_content)
                msg.addTextMsg("")
                msg.addTextMsg("-=By LittleJiu=-")
                ex.writeUserData(_user,data.fromQQ)
                ex.writePet(data.fromQQ,_pet)
                if(groupFrom):
                    await sendGroupMsg(msg,data.fromGroup)
                else:
                    await sendFriendMsg(msg,data.fromQQ)             
            else:
                msg.addTextMsg("你的宠物需要休息哦~")
                _now = time.localtime(time.time())
                _end = time.localtime(_pet.breakStartTime + _pet.breakTime)
                _cut = ex.getTimeCut(_end,_now).seconds
                if(_cut > 0):
                    msg.addTextMsg(f"剩余休息时间: {_cut}s")
                else:
                    # 修正一些值后重新调用自身
                    _pet.needBreak = False
                    ex.writePet(data.fromQQ,_pet)
                    await explorePet(data,step)
                if(groupFrom):
                    await sendGroupMsg(msg,data.fromGroup,data.msgChain.getSource().msgId)
                else:
                    await sendFriendMsg(msg,data.fromQQ,data.msgChain.getSource().msgId)
        else:
            msg.addTextMsg("没有宠物怎么探险啊(问号脸")
            if(groupFrom):
                await sendGroupMsg(msg,data.fromGroup,data.msgChain.getSource().msgId)
            else:
                await sendFriendMsg(msg,data.fromQQ,data.msgChain.getSource().msgId)  
    finally:
        ex.changeBlocked(data.fromQQ,False)
    return sdk.ALLOW_NEXT

      

        