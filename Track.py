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

#預設下載最新的,顯示一筆
parser = argparse.ArgumentParser()
parser.add_argument("-d","--download",type=bool, default=False, help="download track log")
parser.add_argument("-v","--viewNumber", type=int, default=1, help="how many program show image")
opt = parser.parse_args()
print(opt)


transform=dict()
transform['Spain_track'] = dict(scale=1, offset_x=0, offset_y=0, plot_args=dict(linewidth=1, alpha=0.9), theta=0)

track='Spain_track'

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


def on_key(event):
    if event.key == 'q':
        exit()

def get_waypoints(track_name):
    p = Path(
        '/home/chuyj/CGI_DeepRacer/env/simulation_ws/src/deepracer_simulation_environment/routes/')
    return np.load((p / track_name).with_suffix('.npy'))

class ColorMaper:
    colors=['#9b59b6', '#3498db', '#1abc9c', '#f1c40f', '#e74c3c']
    condition=[(0, 4), (4, 6), (6, 8), (8, 10), (10, 12)]

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
    CENTERLINE_COLOR = "#f1c40f"

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

   
    fig, axs = plt.subplots(2, 2,figsize=(20, 20))

    with open(logfile, 'r', encoding='UTF-8') as file:
        for line in file:
            line = line.split(" ")
            if  len(line)>4 and line[4].startswith("/WORLD_NAME:"):
                npyFile = line[5][:-1]+".npy"

                for i in range(4):
                    plot_track(axs[i // 2, i % 2], npyFile)
                    axs[i // 2, i % 2].title.set_text(encode[0]+'Round')
                
            
                fig.canvas.mpl_connect('key_press_event', on_key)
                fig.suptitle(name+"     "+line[5][:-1] , fontsize=16)

                
            line=line[2]
            if  not line.startswith("SIM_TRACE_LOG"):
                if len(list_x) > 1:
                    plot_args = transform[track]['plot_args']
                    plt.plot(list_x, list_y, **plot_args)
                list_x = []
                list_y = []
            else:
                line = line.split(',')
                roundCount =  str(line[0])
                roundCount=int(roundCount[-1:])
                x, y, speed = float(line[2]), float(line[3]), float(line[6])
                scale = transform[track]['scale']
                x, y = x * scale, y * scale
                x, y = rotate(x, y, 0, 0, transform[track]['theta'])
                x, y = shift(x, y, transform[track]['offset_x'], transform[track]['offset_y'])
                list_x.append(x)
                list_y.append(y)
                if len(list_x) >=2:
                    
                    axs[roundCount//2,roundCount%2].plot(list_x, list_y,color='r', **transform[track]['plot_args'] )
                    list_x = [list_x[-1]]
                    list_y = [list_y[-1]]

                

                x, y, speed = float(line[2]), float(line[3]), float(line[6])
                scale = transform[track]['scale']
                x, y = x * scale, y * scale
                x, y = rotate(x, y, 0, 0, transform[track]['theta'])
                x, y = shift(x, y, transform[track]['offset_x'], transform[track]['offset_y'])
                list_x_total.append(x)
                list_y_total.append(y)
                if len(list_x_total) >=2:
                    
                    axs[1,1].plot(list_x_total, list_y_total, color='r', **transform[track]['plot_args'] )
                    list_x_total = [list_x_total[-1]]
                    list_y_total = [list_y_total[-1]]
          
    plt.show()



def main():

    
    if opt.download:
        if opt.viewNumber>0:
            loadOnlineFiles(opt.viewNumber)
    
    path="./deepracer_log"
    count=0
    for layer1 in os.listdir(path):
        if count>=int(opt.viewNumber):
            break
        file_path = os.path.join(path,layer1) 
        count+=1
        for layer2 in os.listdir(file_path):
            file_path2 = os.path.join(file_path,layer2)
            for layer3 in os.listdir(file_path2):
                if os.path.splitext(layer3)[1]=='.txt': 
                    file_path3 = os.path.join(file_path2,layer3)
                    drawPlot(file_path3,layer1)

    
if __name__ == "__main__":
    main()


