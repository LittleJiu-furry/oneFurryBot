'''
    本模块提供一些已经封装好的方法函数，便于读取用户数据
'''
import os
import json

# =========数据结构定义=========

# 用户数据结构
class userSignDataClass:
    lastSignGroup = 0
    lastSignGroup_name = ""
    lastSignTimestamp = 0
    signValue = 0
    thisMonth = []
    def __init__(self,_data:dict = None) -> None:
        if(_data is not None and _data != {}):
            self.lastSignGroup =_data["lastSignGroup"]
            self.lastSignGroup_name = _data["lastSignGroup_name"]
            self.lastSignTimestamp = _data["lastSignTimestamp"]
            self.signValue = _data["signValue"]
            self.thisMonth = _data["signDate"]["thisMonth"]

class signBotConfig:
    signValueRange = [10,100]
    signTimeRange = [0,0]
    signName = "积分"
    signText = [
        "签到成功",
        "本次签到获得 {{ newValue }} 点{{ signName }}",
        "当前有 {{ totalValue }} 点{{ signName }}"
    ]
    signText_faile = [
        "你今天已经在 {{ GroupName }}({{ GroupId }}) 签到过了，请不要重复签到~"
    ]
    reSignCutValue = 30

class uiConfig:
    port:9000     

# 机器人配置
class botConfig:
    signConfig = signBotConfig()
    owner = 0
    uiConfig = uiConfig()
    def __init__(self,_data:dict == None) -> None:
        if(_data is not None and _data != {}):
            self.signConfig.signValueRange = _data["signBot"]["signValueRange"]
            self.signConfig.signTimeRange = _data["signBot"]["signTimeRange"]
            self.signConfig.signName = _data["signBot"]["signName"]
            self.signConfig.signText = _data["signBot"]["signText"]
            self.signConfig.signText_faile = _data["signBot"]["signText_faile"]
            self.signConfig.reSignCutValue = _data["signBot"]["reSignCutValue"]
            self.owner = _data["owner"]
            self.uiConfig.port = _data["ui"]["port"]

# 宠物信息
class PetInfo:
    name:str # 名称
    createTime:int # 创建时间
    level:int # 等级
    exp:int # 经验
    family:str # 物种
    minNeed:int # 最小需要消耗值
    lastEatTime:int # 最后投喂时间
    funLevel:int # 好感等级
    funValue:int # 好感值
    dead:bool # 是否已死亡
    deadValue:int # 死亡值
    def __init__(self,_data:dict == None) -> None:
        if(_data is not None and _data != {}):
            self.name = _data["name"]
            self.createTime = _data["createTime"]
            self.level = _data["level"]
            self.exp = _data["exp"]
            self.family = _data["family"]
            self.minNeed = _data["minNeed"]
            self.lastEatTime = _data["lastEatTime"]
            self.dead = _data["dead"]
            self.deadValue = _data["deadValue"]
            self.funLevel = _data["funLevel"]
            self.funValue = _data["funValue"]

# 物种信息
class petFamilyInfo:
    family_name:str
    actions:list
    says:list
    def __init__(self,_data:dict == None,familyName:str == None) -> None:
        if(_data is not None and _data != {}):
            self.family_name = familyName
            self.actions = _data["actions"]
            self.says = _data["says"]





# ===========方法函数===========

# 用于处理文件路径
def getPath(*path):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), *path))

# 获得用户数据
def getUserSignData(user_id:str) -> userSignDataClass:
    try:
        with open(getPath("./config/sign.json"),mode="r",encoding="utf-8") as f:
            try:
                user_data = json.load(f)[f"U{user_id}"]
            except KeyError:
                return userSignDataClass()
    except FileNotFoundError:
        return userSignDataClass()
    
    return userSignDataClass(user_data)

# 覆写用户数据
def writeUserData(userDict:userSignDataClass,user_id:str):
    # 构造写入的数据
    new_data = {
        f"U{user_id}":{
            "lastSignGroup":userDict.lastSignGroup,
            "lastSignGroup_name":userDict.lastSignGroup_name,
            "lastSignTimestamp":userDict.lastSignTimestamp,
            "signValue":userDict.signValue,
            "signDate":{
                "thisMonth":userDict.thisMonth
            }
        }
    }
    try:
        with open(getPath("./config/sign.json"),mode="r+",encoding="utf-8") as f:
            _old = json.load(f) # 读取并暂存旧数据
            _new = _old.copy()
            _new.update(new_data)
            f.seek(0,0)
            f.truncate(0)
            f.write(json.dumps(_new,ensure_ascii=False,indent=4))
    except FileNotFoundError:
        # 没有找到配置文件
        with open(getPath("./config/sign.json"),mode="a+",encoding="utf-8") as f:
            # 不需要读取旧数据
            f.write(json.dumps(new_data,ensure_ascii=False,indent=4))

# 读取群聊某个功能的开关状态
def getGroupEnable(group_id:str,menu_name:str)->bool:
    with open(getPath("./config/Gconf.json"),mode="a+",encoding="utf-8") as f:
        f.seek(0,0)
        try:
            _data = json.load(f)
        except json.JSONDecodeError:
            _data = {}
        if(f'G{group_id}' in _data):
            if(menu_name in _data[f'G{group_id}']):
                return _data[f'G{group_id}'][menu_name]
            else:
                # 不存在这个配置，要把他的状态更新
                f.seek(0,0)
                f.truncate(0)
                _data[f'G{group_id}'][menu_name] = False
                f.write(json.dumps(_data,ensure_ascii=False,indent=4))
                return False
        else:
            # 不存在这个配置，要把他的状态更新
            f.seek(0,0)
            f.truncate(0)
            _data[f'G{group_id}'] = {}
            _data[f'G{group_id}'][menu_name] = False
            f.write(json.dumps(_data,ensure_ascii=False,indent=4))
            return False

# 读取机器人配置
def getRobotConf()->botConfig:
    with open(getPath("./config/conf.json"),mode="a+",encoding="utf-8") as f:
        f.seek(0,0)
        _data = json.load(f)
        return botConfig(_data)

# 读取宠物信息
def getPetInfo(user_id:str)->PetInfo:
    with open(getPath("./config/pet.json"),mode="a+",encoding="utf-8") as f:
        f.seek(0,0)
        try:
            _data = json.load(f)
        except:
            _data = {}
        if(f'U{user_id}' in _data):
            return PetInfo(_data[f"U{user_id}"])
        else:
            return None

# 随机字符
def randomStr()->str:
    from hashlib import md5
    import time
    return md5(str(time.time()).encode()).hexdigest()

# 获得物种的基础信息
def getPetFamilyInfo(family:str)->petFamilyInfo:
    with open(getPath("./config/petsFamily.json"),mode="r",encoding="utf-8") as f:
        _pets = json.load(f)
        return petFamilyInfo(_pets[family],family)

# 选择一个随机物种
def randomPetFamily() -> str:
    with open(getPath("./config/petsFamily.json"),mode="a+",encoding="utf-8") as f:
        f.seek(0,0)
        try:
            _data = json.load(f)
        except json.JSONDecodeError:
            _data = {}
        import random
        allFamilys = list(_data.keys())
        return random.choice(allFamilys)

# 创建一个宠物
def createPet(user_id:str,pet_name:str = None)->PetInfo:
    with open(getPath("./config/pet.json"),mode="a+",encoding="utf-8") as f:
        f.seek(0,0)
        try:
            _data = json.load(f)
        except json.JSONDecodeError:
            _data = {}
        _petFamily = randomPetFamily()
        import random
        _minNeed = random.randint(50,300)
        import time
        _pet = {
            "name": pet_name if pet_name is not None else f"{_petFamily}{randomStr()[:6]}",
            "createTime": int(time.time()),
            "level": 1,
            "exp": 0,
            "family": _petFamily,
            "minNeed": _minNeed,
            "lastEatTime": 0,
            "funLevel": 1,
            "funValue": 0,
            "dead":False,
            "deadValue":0
        }
        _data.update({f'U{user_id}': _pet})
        f.seek(0,0)
        f.truncate(0)
        f.write(json.dumps(_data,ensure_ascii=False))
        return PetInfo(_pet)

# 修改宠物属性
def writePet(user_id:str,petInfo:PetInfo):
    with open(getPath("./config/pet.json"),mode="a+",encoding="utf-8") as f:
        f.seek(0,0)
        try:
            _data = json.load(f)
        except json.JSONDecodeError:
            _data = {}
        _pet = {
            "name": petInfo.name,
            "createTime": petInfo.createTime,
            "level": petInfo.level,
            "exp": petInfo.exp,
            "family": petInfo.family,
            "minNeed": petInfo.minNeed,
            "lastEatTime": petInfo.lastEatTime,
            "funLevel": petInfo.funLevel,
            "funValue": petInfo.funValue,
            "dead":petInfo.dead,
            "deadValue":petInfo.deadValue
        }
        _data.update({f'U{user_id}': _pet})
        f.seek(0,0)
        f.truncate(0)
        f.write(json.dumps(_data,ensure_ascii=False))
        














