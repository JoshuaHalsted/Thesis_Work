import yaml
from yaml.loader import SafeLoader
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
import os

Plot_Path = r"C:/Users/17577/Thesis_Work/STAR_CCM_Files/PostProcessing_Folder/Plots/LP"

with open('C:\\Users\\17577\\Thesis_Work\\STAR_CCM_Files\\PostProcessing_Folder\\Plots\\TC_Locations.txt') as f:
    lines = f.read().splitlines()

with open('C:\\Users\\17577\\Thesis_Work\\STAR_CCM_Files\\PostProcessing_Folder\\Plots\\TC_info.yml') as f:
    data = yaml.load(f, Loader=SafeLoader)

with open('C:\\Users\\17577\\Thesis_Work\\STAR_CCM_Files\\PostProcessing_Folder\\Coarse_Mesh_Reports.txt') as f:
    coarse_lines = f.read().splitlines()

with open('C:\\Users\\17577\\Thesis_Work\\STAR_CCM_Files\\PostProcessing_Folder\\Medium_Mesh_Reports.txt') as f:
    medium_lines = f.read().splitlines()

with open('C:\\Users\\17577\\Thesis_Work\\STAR_CCM_Files\\PostProcessing_Folder\\Fine_Mesh_Reports.txt') as f:
    fine_lines = f.read().splitlines()

xcoord = []
ycoord = []
zcoord = []

newlist = []
for line in lines:
    line = line.split("]")[0]
    line = line.split("[")[1]
    xcoord.append(float(line.split(", ")[0]))
    ycoord.append(float(line.split(", ")[1]))
    zcoord.append(float(line.split(", ")[2]))

def SearchforTemp(temp_list, TC):
    for line in temp_list:
        if TC in line:
            temp = float(line.split("    ")[1])
            return temp

def GetNormalizedRadius(x, y):
    MaxRadius = 28.694
    LocationRadius = np.sqrt((x**2 + y**2))/MaxRadius
    return LocationRadius

def GetTheta(x, y):
    theta = float(math.atan(y/x))
    return theta

iteration = 0
Radii = []
Theta = []
for TC in data.keys():
    data[TC]['Location']['x'] = xcoord[iteration]
    data[TC]['Location']['y'] = ycoord[iteration]
    data[TC]['Location']['z'] = zcoord[iteration]
    data[TC]['Location']['Radius'] = float(GetNormalizedRadius(xcoord[iteration], ycoord[iteration]))
    data[TC]['Location']['Theta'] = float(GetTheta(xcoord[iteration], ycoord[iteration]))
    data[TC]['Results']['Coarse'] = SearchforTemp(coarse_lines, TC)
    data[TC]['Results']['Medium'] = SearchforTemp(medium_lines, TC)
    data[TC]['Results']['Fine'] = SearchforTemp(fine_lines, TC)
    Radii.append(data[TC]['Location']['Radius'])
    Theta.append(data[TC]['Location']['Theta'])
    iteration += 1

with open('C:\\Users\\17577\\Thesis_Work\\STAR_CCM_Files\\PostProcessing_Folder\\Plots\\TC_info.yml', 'w') as f:
    data = yaml.dump(data, f, sort_keys=False, default_flow_style=False)

def MakeContourPlot(theta, r, colors, name):
    print(name)
    theta = 2*np.pi*theta/360
    fig = plt.figure(figsize=(15,10))
    ax = fig.add_subplot(111, projection='polar')
    ax.add_artist(Wedge((0.5,0.5), 0.53, 150,210, width=0.2, transform=ax.transAxes, color='blue',alpha=0.5, zorder=0))  # I had problems that the color wedges always appeared ON TOP of the data points. The 'zorder' attribute makes sure they are always UNDER the data points.
    ax.add_artist(Wedge((0.5,0.5), 0.53, 30,90, width=0.2, transform=ax.transAxes, color='green',alpha=0.5, zorder=0))
    ax.add_artist(Wedge((0.5,0.5), 0.53, 330,30, width=0.2, transform=ax.transAxes, color='brown',alpha=0.5, zorder=0))
    ax.set_yticklabels([])
    sectors = ["Primary\nSector", "Secondary\nSector", "Tertiary\nSector"]
    lines, labels = plt.thetagrids([180,60,0],(sectors), fontsize=15, fontweight='bold')
    ax.set_title('Core-Block#1 (Experiment) @ {}'.format(round(i))+' seconds',fontsize=30,fontweight='bold')
    c = ax.scatter(theta, r, c=colors, s=500,cmap='Reds',alpha=1.0, vmin=np.min(colors), vmax=np.max(colors))

    cbar1 = plt.colorbar(c, shrink=0.5, orientation='horizontal', use_gridspec=False, anchor=(0.5, 0.5), ticks=[np.min(colors), (np.max(colors)+np.min(colors))/2, np.max(colors)])
    cbar1.ax.tick_params(labelsize=25)
    plt.tight_layout()
    ax.set_rgrids(np.arange(0,0.8,0.1),fontsize=20,fontweight='bold')
    plt.savefig(os.path.join(Plot_Path,"LP_Temps_STAR"+'.png'),dpi=300,format='png',transparent=True)
    plt.close()
    pass

MakeContourPlot(Theta, Radii, colors, name)