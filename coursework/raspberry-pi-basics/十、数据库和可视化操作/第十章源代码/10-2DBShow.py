import time
import sys
import sqlite3
import genHtml2

interval = 5

def getCPUTemp():
    with open("/sys/class/thermal/thermal_zone0/temp") as file:
        res = file.readline()
    return round(int(res)/1000,2)

while True:
    time_date = time.strftime("%Y/%m/%d",time.localtime())
    time_time = time.strftime("%H:%M:%S",time.localtime())
    print(time_date,time_time)
    tempCPU = getCPUTemp()
    print("Temperature of CPU: %.2f"%round(tempCPU,3))
    cn = sqlite3.connect('RPiStatus.db')
    cu = cn.cursor()

    item = [None]
    item.append(time_date)
    item.append(time_time)
    item.append(tempCPU)

    cu.execute("INSERT INTO pistatus values(?,?,?,?)", tuple(item))
    cn.commit()

    genHtml2.gen()

    time.sleep(interval)
