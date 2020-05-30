#! /usr/bin/env python3

import sys
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import math
from matplotlib.lines import Line2D
import os
import subprocess

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

def drawPlot(npyfile,logfile,name):

    list_x = []
    list_y = []
    list_x_total = []
    list_y_total = []
    traning_waypoints = np.load(npyfile)
  
    
    fig = plt.figure(figsize=(20, 20))
    fig.canvas.mpl_connect('key_press_event', on_key)
    fig.suptitle(name+" "+npyfile[0:-4], fontsize=16)


    ax = fig.add_subplot(221)
    ax.title.set_text('First Round')
    ax2 = fig.add_subplot(222)
    ax2.title.set_text('Second Round')
    ax3 = fig.add_subplot(223)
    ax3.title.set_text('Third Round')
    ax4 = fig.add_subplot(224)
    ax4.title.set_text('Total Round')

    with open(logfile, 'r', encoding='UTF-8') as file:
        for line in file:
            line = line.split(" ")
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
                roundCount=roundCount[-1:]
                if(roundCount=="0"):
                    ax.plot(traning_waypoints[:, 2],traning_waypoints[:, 3], linewidth=0.5, color='b')
                    ax.plot(traning_waypoints[:, 4],traning_waypoints[:, 5],linewidth=0.5, color='b')
                    x, y, speed = float(line[2]), float(line[3]), float(line[6])
                    scale = transform[track]['scale']
                    x, y = x * scale, y * scale
                    x, y = rotate(x, y, 0, 0, transform[track]['theta'])
                    x, y = shift(x, y, transform[track]['offset_x'], transform[track]['offset_y'])
                    list_x.append(x)
                    list_y.append(y)
                    if len(list_x) >=2:
                        
                        ax.plot(list_x, list_y,color='r', **transform[track]['plot_args'] )
                        list_x = [list_x[-1]]
                        list_y = [list_y[-1]]
                
                elif(roundCount=="1"):
                    ax2.plot(traning_waypoints[:, 2],traning_waypoints[:, 3], linewidth=0.5, color='b')
                    ax2.plot(traning_waypoints[:, 4],traning_waypoints[:, 5], linewidth=0.5, color='b')
                    x, y, speed = float(line[2]), float(line[3]), float(line[6])
                    scale = transform[track]['scale']
                    x, y = x * scale, y * scale
                    x, y = rotate(x, y, 0, 0, transform[track]['theta'])
                    x, y = shift(x, y, transform[track]['offset_x'], transform[track]['offset_y'])
                    list_x.append(x)
                    list_y.append(y)
                    if len(list_x) >=2:
                        
                        ax2.plot(list_x, list_y, color='r', **transform[track]['plot_args'] )
                        list_x = [list_x[-1]]
                        list_y = [list_y[-1]]
                elif(roundCount=="2"):
                    ax3.plot(traning_waypoints[:, 2],traning_waypoints[:, 3], linewidth=0.5, color='b')
                    ax3.plot(traning_waypoints[:, 4],traning_waypoints[:, 5], linewidth=0.5, color='b')
                    x, y, speed = float(line[2]), float(line[3]), float(line[6])
                    scale = transform[track]['scale']
                    x, y = x * scale, y * scale
                    x, y = rotate(x, y, 0, 0, transform[track]['theta'])
                    x, y = shift(x, y, transform[track]['offset_x'], transform[track]['offset_y'])
                    list_x.append(x)
                    list_y.append(y)
                    if len(list_x) >=2:
                        
                        ax3.plot(list_x, list_y, color='r', **transform[track]['plot_args'] )
                        list_x = [list_x[-1]]
                        list_y = [list_y[-1]]
                ax4.plot(traning_waypoints[:, 2],traning_waypoints[:, 3], linewidth=0.5, color='b')
                ax4.plot(traning_waypoints[:, 4],traning_waypoints[:, 5], linewidth=0.5, color='b')
                x, y, speed = float(line[2]), float(line[3]), float(line[6])
                scale = transform[track]['scale']
                x, y = x * scale, y * scale
                x, y = rotate(x, y, 0, 0, transform[track]['theta'])
                x, y = shift(x, y, transform[track]['offset_x'], transform[track]['offset_y'])
                list_x_total.append(x)
                list_y_total.append(y)
                if len(list_x_total) >=2:
                    
                    ax4.plot(list_x_total, list_y_total, color='r', **transform[track]['plot_args'] )
                    list_x_total = [list_x_total[-1]]
                    list_y_total = [list_y_total[-1]]
          
    plt.show()



def main():
#  loadOnlineFiles()
    npyfile=sys.argv[1]
    produce =sys.argv[2]
    n =sys.argv[3]

    if produce == "True":
        if int(n)>0:
            loadOnlineFiles(n)
    
    path="./deepracer_log"
    count=0
    for layer1 in os.listdir(path):
        if count>=int(n):
            break
        file_path = os.path.join(path,layer1) 
        count+=1
        for layer2 in os.listdir(file_path):
            file_path2 = os.path.join(file_path,layer2)
            for layer3 in os.listdir(file_path2):
                if os.path.splitext(layer3)[1]=='.txt': 
                    file_path3 = os.path.join(file_path2,layer3)
                    drawPlot(npyfile,file_path3,layer1)


if __name__ == "__main__":
    main()


