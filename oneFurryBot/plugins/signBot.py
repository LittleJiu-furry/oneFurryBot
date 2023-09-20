from . import sdk
import asyncio
import time
import ex
import random
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


# 签到功能
@mBind.Group_text("sign","签到")
async def sign(data:sdk.msgtypes.GroupMessage)->bool:
    msg = sdk.msgtypes.MsgChain()
    msg.addAt(data.fromQQ)
    # 判断是否开启
    enable = ex.getGroupEnable(data.fromGroup,"signBot")
    if(enable):
        userData = ex.getUserSignData(data.fromQQ)
        # 判断今天是否已经签到
        _last = time.localtime(userData.lastSignTimestamp)
        _now = time.localtime(data.msgChain.getSource().msgTime)

        if(_last.tm_yday == _now.tm_yday):
            # 今天已经签到
            for text in botConfig.signConfig.signText_faile:
                text = text.replace("{{ GroupName }}",f"{userData.lastSignGroup_name}")
                text = text.replace("{{ GroupId }}",f"{userData.lastSignGroup}")
                msg.addTextMsg(text)
            await sendGroupMsg(msg,data.fromGroup)
        else:
            # 今天未签到
            # 需要判断是否在签到时间段内，并清理签到日历
            minH,maxH = botConfig.signConfig.signTimeRange
            # 构造时间戳范围
            _min = time.mktime(time.strptime(f'{_now.tm_year}-{_now.tm_mon}-{_now.tm_mday} {minH}:00:00',"%Y-%m-%d %H:%M:%S"))
            _max = time.mktime(time.strptime(f'{_now.tm_year}-{_now.tm_mon}-{_now.tm_mday} {maxH}:59:59',"%Y-%m-%d %H:%M:%S"))
            _nt = time.mktime(_now)
            if(_min <= _nt <= _max):
                # 在签到时间段内
                valueMin,valueMax = botConfig.signConfig.signValueRange
                _value = random.randint(valueMin,valueMax)
                userData.signValue += _value
                userData.lastSignTimestamp = data.msgChain.getSource().msgTime
                userData.lastSignGroup = data.fromGroup
                userData.lastSignGroup_name = data.fromGroup_name
                # 更新签到日历
                if(_now.tm_mon != _last.tm_mon):
                    userData.thisMonth = [_now.tm_mday]
                else:
                    userData.thisMonth.append(_now.tm_mday)
                ex.writeUserData(userData,data.fromQQ)
                for text in botConfig.signConfig.signText:
                    text = text.replace("{{ newValue }}",f"{_value}")
                    text = text.replace("{{ signName }}",f"{botConfig.signConfig.signName}")
                    text = text.replace("{{ totalValue }}",f"{userData.signValue}")
                    msg.addTextMsg(text)
                await sendGroupMsg(msg,data.fromGroup)
            else:
                # 不在签到时段
                msg.addTextMsg("不在签到时段")
                msg.addTextMsg(f"签到时段为{minH}:00:00 ~ {maxH}:59:59")
                await sendGroupMsg(msg,data.fromGroup)
    return sdk.ALLOW_NEXT

# 补签功能
@mBind.Group_text("#补签 {day}","#补签")
@mBind.Friend_text("#补签 {day}","#补签")
async def signDay(data,day):
    msg = sdk.msgtypes.MsgChain()
    if(day == None):
        # 没有指定日期
        if(type(data) == sdk.msgtypes.GroupMessage):
            msg.addAt(data.fromQQ)
            msg.addTextMsg("请指定日期")
            msg.addTextMsg("格式为 #补签 {日期}")
            await sendGroupMsg(msg,data.fromGroup)
        elif(type(data) == sdk.msgtypes.FriendMessage):
            msg.addTextMsg("请指定日期")
            msg.addTextMsg("格式为 #补签 {日期}")
            await sendFriendMsg(msg,data.fromQQ)
        return sdk.ALLOW_NEXT
    else:
        _day = int(day)
        # 获得本月日期的最大值
        import calendar as cal
        _now = time.localtime(time.time())
        _firstWeekDay,_maxDay = cal.monthrange(_now.tm_year,_now.tm_mon)
        if(1 <= _day <= _maxDay and 1 <= _day < _now.tm_mday):
            userData = ex.getUserSignData(data.fromQQ)
            if(_day in userData.thisMonth):
                # 已经签过
                if(type(data) == sdk.msgtypes.GroupMessage):
                    msg.addAt(data.fromQQ)
                msg.addTextMsg("当天已签到，不允许补签")
                if(type(data) == sdk.msgtypes.GroupMessage):
                    await sendGroupMsg(msg,data.fromGroup)
                elif(type(data) == sdk.msgtypes.FriendMessage):
                    await sendFriendMsg(msg,data.fromQQ)
                return sdk.ALLOW_NEXT
            userData.thisMonth.append(_day)
            userData.signValue -= botConfig.signConfig.reSignCutValue
            valueRange = botConfig.signConfig.signValueRange
            _value = random.randint(valueRange[0],valueRange[1])
            userData.signValue += _value
            ex.writeUserData(userData,data.fromQQ)
            if(type(data) == sdk.msgtypes.GroupMessage):
                msg.addAt(data.fromQQ)
                msg.addTextMsg("补签成功")
                msg.addTextMsg(f'补签已经扣除{botConfig.signConfig.reSignCutValue}点{botConfig.signConfig.signName}')
                msg.addTextMsg(f'补签获得了{_value}点{botConfig.signConfig.signName}')
                await sendGroupMsg(msg,data.fromGroup)
            elif(type(data) == sdk.msgtypes.FriendMessage):
                msg.addTextMsg("补签成功")
                msg.addTextMsg(f'补签已经扣除{botConfig.signConfig.reSignCutValue}点{botConfig.signConfig.signName}')
                msg.addTextMsg(f'补签获得了{_value}点{botConfig.signConfig.signName}')
                await sendFriendMsg(msg,data.fromQQ)
        else:
            if(type(data) == sdk.msgtypes.GroupMessage):
                msg.addAt(data.fromQQ)
            
            msg.addTextMsg("补签失败")
            msg.addTextMsg("仅允许在本月份已经过但未签到的日期补签")

            if(type(data) == sdk.msgtypes.GroupMessage):
                await sendGroupMsg(msg,data.fromGroup)
            elif(type(data) == sdk.msgtypes.FriendMessage):
                await sendFriendMsg(msg,data.fromQQ)
    return sdk.ALLOW_NEXT


