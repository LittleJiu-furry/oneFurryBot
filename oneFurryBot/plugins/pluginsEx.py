'''
    本模块为所有插件提供工具函数
'''
from decimal import Decimal
def getRound(num):
    return float(Decimal(num).quantize(Decimal("0.1"), rounding="ROUND_HALF_UP"))