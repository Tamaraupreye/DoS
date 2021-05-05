import psutil
import sys
import csv
import time
from time import sleep, strftime, time
import matplotlib.pyplot as plt
import subprocess

# interactive plotting
plt.ion()
x = []
y = []

# f=open(testfile.txt,"")
with open("heavyattacknoattack.csv", 'w', newline='') as csvfile:
    fieldnames = ['AttackFlag', 'CPUPercent', 'AvailableMemory', 'ActiveMemory', 'CPUTime-User', 'CPUTime-System',
                  'CPUTime-Idle']

    thewriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
    thewriter.writeheader()

    count = 0
    attackenterline = 1800
    attackflag = 0
    while count <= 3600:

        cpu_percent = psutil.cpu_percent()

        cpu_times_user = psutil.cpu_times().user
        cpu_times_system = psutil.cpu_times().system
        cpu_times_idle = psutil.cpu_times().idle
        availablememory = psutil.virtual_memory().available
        activememory = psutil.virtual_memory().active

        # attackflag to distinguish when the attack is triggered
        if count < attackenterline:
            attackflag = 0
        else:
            attackflag = 1

        # calling the python program at a specfic line.
        if count == attackenterline:
            subprocess.call(["python", "/home/pi/Desktop/ReverseTCP/payload.py"])

        thewriter.writerow({'AttackFlag': attackflag, 'CPUPercent': cpu_percent, 'AvailableMemory': availablememory,
                            'ActiveMemory': activememory, 'CPUTime-User': cpu_times_user,
                            'CPUTime-System': cpu_times_system, 'CPUTime-Idle': cpu_times_idle})
        sleep(1)
        count = count + 1
        print(count, '', attackflag)
