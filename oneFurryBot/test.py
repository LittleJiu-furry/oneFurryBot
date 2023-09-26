import datetime
import time

t = time.time()
t1 = datetime.datetime.fromtimestamp(t)
t2 = datetime.datetime.fromtimestamp(t + 15)
print(t1 - t2)