#! /usr/bin/env python3

import sys
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import math
from matplotlib.lines import Line2D
import os
import subprocess
import argparse
from datetime import datetime

#預設下載最新的,顯示一筆
parser = argparse.ArgumentParser()
parser.add_argument("-u","--update",type=bool, default=False, help="download track log")
parser.add_argument("-v","--viewNumber", type=int, default=1, help="how many program show image")
opt = parser.parse_args()
print(opt)


transform = dict(scale=1, offset_x=0, offset_y=0, plot_args=dict(linewidth=1, alpha=0.9), theta=0)


def rotate(x, y, xo, yo, theta):  # rotate x,y around xo,yo by theta (rad)
    theta = theta * math.pi / 180
    xr = math.cos(theta)*(x-xo)-math.sin(theta)*(y-yo) + xo
    yr = math.sin(theta)*(x-xo)+math.cos(theta)*(y-yo) + yo
    return [xr, yr]


def shift(x, y, dx, dy):
    return x+dx, y+dy

def plot_photo_track(img_path):
    img = plt.imread(img_path)
    ax = plt.gca()
    ax.imshow(img)

class ColorMaper:
    colors=['#9b59b6', '#93FF93', '#f1c40f', '#FF0000', '#e74c3c']
    condition=[(0, 1), (1, 2), (2, 3), (3, 4)]

    @staticmethod
    def speed2color(speed):
        for i, cond in enumerate(ColorMaper.condition):
            if speed > cond[0] and speed <= cond[1]:
                return ColorMaper.colors[i] 


    @staticmethod
    def custom_lines():
        customized = []
        for c in ColorMaper.colors:
            customized.append(Line2D([0], [0], color=c, lw=4))
        return customized

    @staticmethod
    def legend_label():
        labels = []
        for cond in ColorMaper.condition:
            labels.append(f'{cond[0]} < speed <= {cond[1]}')
        return labels

def loadOnlineFiles(n):
    subprocess.call(['./log.sh',str(n)])


def plot_track(ax, track):
    FIELD_COLOR = "#ecf0f1"
    ROAD_COLOR = "#2c3e50"
    CENTERLINE_COLOR = "#FFFFFF"

    waypoints = np.load(track)

    ax.axis("equal")
    ax.set_facecolor(FIELD_COLOR)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    for side in ["top", "bottom", "left", "right"]:
        ax.spines[side].set_visible(False)

    center_points, inner_points, outer_points = np.hsplit(waypoints, 3)

    ax.fill(outer_points[:, 0], outer_points[:, 1], color=ROAD_COLOR)
    ax.fill(inner_points[:, 0], inner_points[:, 1], color=FIELD_COLOR)
    ax.plot(center_points[:, 0], center_points[:, 1], color=CENTERLINE_COLOR, linestyle="--")


def drawPlot(logfile,name):

    list_x = []
    list_y = []
    list_x_total = []
    list_y_total = []
    encode  = ['First Round','Second Round','Third Round','Total Round']

    last = ""
    now  = ""
    lastTime = 0
    nowTime  = 0
    sumTime = datetime.strptime("0:0:0.0", "%H:%M:%S.%f")-datetime.strptime("0:0:0.0", "%H:%M:%S.%f")

    fig, axs = plt.subplots(2, 2,figsize=(20, 20))
    
    time = []
    first =True
    title =""
    with open(logfile, 'r', encoding='UTF-8') as file:
        for line in file:
            line = line.split(" ")

            #creat and setting figure
            if  len(line)>4 and line[4].startswith("/WORLD_NAME:"):
                npyFile = line[5][:-1]+".npy"

                for i in range(4):
                    plot_track(axs[i // 2, i % 2], npyFile)
                    axs[i // 2, i % 2].title.set_text(encode[i]+'Round')
                
                title =name+"     "+line[5][:-1]
                

            nowTime = datetime.strptime(line[1][0:8], "%H:%M:%S") 
            line=line[2]
            if  not line.startswith("SIM_TRACE_LOG"):
                if len(list_x) > 1:
                    plot_args = transform['plot_args']
                    plt.plot(list_x, list_y, **plot_args)
                list_x = []
                list_y = []
            else:
                line = line.split(',')
                roundCount =  str(line[0])
                roundCount=int(roundCount[-1:])
                x, y, speed ,now = float(line[2]), float(line[3]), float(line[6]), line[-1][:-1]

                '''
                if(first):
                    time.append(line[-2])
                    first =False
                if(now == "lap_complete"):
                    time.append(line[-2])
                '''
                
                if last =="" or last == "off_track"  or last == "lap_complete" or last == "reversed":
                    last  = now
                    lastTime =nowTime
                else:
                    sumTime+=(nowTime-lastTime)
                    lastTime = nowTime
                    last =now
                
                scale = transform['scale']
                x, y = x * scale, y * scale
                x, y = rotate(x, y, 0, 0, transform['theta'])
                x, y = shift(x, y, transform['offset_x'], transform['offset_y'])
                list_x.append(x)
                list_y.append(y)
                list_x_total.append(x)
                list_y_total.append(y)
                if len(list_x) >=2:
                    
                    axs[roundCount//2,roundCount%2].plot(list_x, list_y,color=ColorMaper.speed2color(speed), **transform['plot_args'] )
                    list_x = [list_x[-1]]
                    list_y = [list_y[-1]]

                    axs[1,1].plot(list_x_total, list_y_total,  color=ColorMaper.speed2color(speed), **transform['plot_args'] )
                    list_x_total = [list_x_total[-1]]
                    list_y_total = [list_y_total[-1]]
    
    fig.legend(ColorMaper.custom_lines(), ColorMaper.legend_label(), loc='lower right', fontsize=15)
    fig.suptitle(title+" time:  "+ str(sumTime), fontsize=16)
    plt.show()
    



def main():

    path="./deepracer_log"

    if opt.update:
        if opt.viewNumber>0:
            loadOnlineFiles(opt.viewNumber)
    
    try:
        if len(os.listdir(path)) < opt.viewNumber:
            loadOnlineFiles(opt.viewNumber)
    except:
        loadOnlineFiles(opt.viewNumber)

   
    list_name = []
    #sort data
    for layer1 in os.listdir(path):
        file_path = os.path.join(path,layer1) 
        for layer2 in os.listdir(file_path):
            file_path2 = os.path.join(file_path,layer2)
            list_name.append(file_path2)
    
    list_name.sort(reverse=True,key=lambda date: datetime.strptime(date[33:52], "%Y-%m-%dT%H-%M-%S"))
    
    #draw image
    for i in range(len(list_name)):
        if i>=int(opt.viewNumber):
            break      
        for layer3 in os.listdir(list_name[i]):
            if os.path.splitext(layer3)[1]=='.txt': 
                file_path3 = os.path.join(list_name[i],layer3)
                drawPlot(file_path3,file_path3[16:32])

if __name__ == "__main__":
    main()


