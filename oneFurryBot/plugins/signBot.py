from . import sdk
import asyncio
mBind = sdk.MsgBind()

def init(fm,gm):
    global sendFMsg,sendGMsg
    sendFMsg = fm
    sendGMsg = gm
    return mBind.friend_call,mBind.group_call

async def sendGroupMsg(msg:sdk.msgtypes.MsgChain,group:int,MsgId:int = None):
    await sendGMsg(msg,group,MsgId)

async def sendFriendMsg(msg:sdk.msgtypes.MsgChain,friend:int,MsgId:int = None):
    await sendFMsg(msg,friend,MsgId)


@mBind.Group_text("签到")
async def test(data:sdk.msgtypes.GroupMessage):
    msg = sdk.msgtypes.MsgChain()
    msg.addTextMsg(await data.msgChain.getTextMsg())
    await sendGroupMsg(msg,data.fromGroup)