import time
import ex
import os


class Log:
    _log_level = ["info","warning","error","fatal"]
    def __init__(self,logLevel:int = 4):
        self.logLevel = logLevel
        if(os.path.exists(ex.getPath("./log")) == False):
            os.makedirs(ex.getPath("./log"))
        self.log(None,"==============")
        self.log(1,f"Program Start")
    
    def log(self,level:int,content:str,autoEnter:bool = True,echo:bool = True):
        with open(ex.getPath(f'./log/log-{time.strftime("%Y-%m-%d",time.localtime(time.time()))}.log'),mode="a+",encoding="utf-8") as f:
            if(level is not None):
                if level <= self.logLevel:
                    _text = f'[{self._log_level[level - 1]}] {content}' + ("\n" if autoEnter else "")
            else:
                _text = f'{content}' + ("\n" if autoEnter else "")
            f.write(_text)

        if(echo):
            print(_text if '\n' not in _text else _text[:-1])