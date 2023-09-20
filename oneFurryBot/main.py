import pluginsLoader
import logger
from client import *
import ex

botConfig = ex.getRobotConf()
botAccount = dict
log = logger.Log()
loader = pluginsLoader.pluginsLoader(log,botConfig)
with open(ex.getPath("./config/bot.json"),mode="r",encoding="utf-8") as f:
    botAccount = json.load(f)
bot = Bot(
    vk=botAccount["vk"],
    botQQ=botAccount["account"],
    baseURL=botAccount["baseURL"],
    eventBind=loader.event,
    log=log
)

loader.setFriendMsg(bot.sendFriendMsg)
loader.setGroupMsg(bot.sendGroupMsg)
bot.setFatherObject(loader)

loader.loadByConfig("./config/plugins.json")

bot.connect()

print()