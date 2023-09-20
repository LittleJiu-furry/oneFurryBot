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
    msg.addTextMsg("#我的信息 #me 获得你的一些信息")
    msg.addTextMsg("#补签 [日期] 进行补签，每次补签扣除30分")
    msg.addTextMsg("#宠物 宠物相关菜单")
    msg.addTextMsg("")
    msg.addTextMsg("-=By LittleJiu=-")
    await sendGroupMsg(msg,data.fromGroup)
    return sdk.ALLOW_NEXT


import time
import platform
import io
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

import json
import base64
# 获取信息
@mBind.Group_text("#我的信息","#me")
@mBind.Friend_text("#我的信息","#me")
async def getMe(data)->bool:
    msg = sdk.msgtypes.MsgChain()
    try:
        with open(ex.getPath("./config/sign.json"),mode="r",encoding="utf-8") as f:
            userData = json.load(f)
        try:
            userData = userData[f"U{data.fromQQ}"]
            if(type(data) == sdk.msgtypes.GroupMessage):
                # 来自群里
                msg.addAt(data.fromQQ)
            msg.addTextMsg(f'总积分: {userData["signValue"]}')
            msg.addTextMsg(f'最后一次签到在 {userData["lastSignGroup_name"]}({userData["lastSignGroup"]})')
            msg.addTextMsg(f'签到时间: {time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(userData["lastSignTimestamp"]))}')

            import calendar as cal
            from PIL import Image, ImageDraw, ImageFont

            now = time.localtime(time.time())
            cal.setfirstweekday(6)
            monthStr = cal.month(now.tm_year,now.tm_mon)
            signedDay = userData["signDate"]["thisMonth"]
            # 对文字进行处理
            monthStrList = monthStr.split("\n")
            imageList = []
            firstLine = True
            font = ImageFont.truetype(ex.getPath("./imgFont.ttf"),25)
            for raw in monthStrList[1:]:
                _indexList = []
                for index in range(0,len(raw),3):
                    word = raw[index:index+2]
                    baseSize = (40,40)
                    if(firstLine):
                        backColor = (255,255,255)
                    else:
                        if(word != "  " and int(word) in signedDay):
                            backColor = (0,255,0)
                        else:
                            backColor = (255,255,255)
                    word = word.replace(" ","") # 删除其中的空格
                    _img = Image.new("RGB", baseSize, backColor)
                    _dr = ImageDraw.Draw(_img)
                    x1,y1,x2,y2 = _dr.textbbox((0,0),word,font=font)
                    _dr.text(((baseSize[0]-x2)/2,(baseSize[1]-y2)/2),word,font=font, fill=(0, 0, 0))
                    _indexList.append(_img)
                firstLine = False
                if(len(_indexList) != 0):
                    imageList.append(_indexList)
                await asyncio.sleep(0)
            # 构造标题
            title = monthStrList[0]
            _title = Image.new("RGB", (280,40), (255, 255, 255))
            _dr = ImageDraw.Draw(_title)
            x1,y1,x2,y2 = _dr.textbbox((0,0),title,font=font)
            _dr.text(((280-x2)/2,(40-y2)/2),title,font=font, fill=(0, 0, 0))
            image = Image.new("RGB", (280,(len(imageList) + 1)* 40), (255, 255, 255))
            dr = ImageDraw.Draw(image)
            image.paste(_title, (0,0))
            for rawImageListIndex in range(len(imageList)):
                for imgIndex in range(len(imageList[rawImageListIndex])):
                    img = imageList[rawImageListIndex][imgIndex]
                    image.paste(img, (40 * imgIndex,40 * (rawImageListIndex + 1)))
                    await asyncio.sleep(0)
                await asyncio.sleep(0)
            ioBytes = io.BytesIO()
            image.save(ioBytes,format="png")
            imgBase64 = base64.b64encode(ioBytes.getvalue()).decode()
            msg.addTextMsg("签到日历")
            msg.addImg_Base64(imgBase64)

        except KeyError:
            if(type(data) == sdk.msgtypes.GroupMessage):
                # 来自群里
                msg.addAt(data.fromQQ)
                msg.addTextMsg("你的数据有误，暂时无法读取，如果多次遇到此问题，请提交反馈")
    except FileNotFoundError:
        if(type(data) == sdk.msgtypes.GroupMessage):
            # 来自群里
            msg.addAt(data.fromQQ)
    if(type(data) == sdk.msgtypes.GroupMessage):
        # 来自群里
        await sendGroupMsg(msg,data.fromGroup)
    elif(type(data) == sdk.msgtypes.FriendMessage):
        # 来自好友
        await sendFriendMsg(msg,data.fromQQ)
    return sdk.ALLOW_NEXT