import yaml
from yaml.loader import SafeLoader
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
import os
import pandas as pd


Data_File = r"C:/Users/17577/Thesis_Work/RELAP_FILES/Automation_Tools/Experimental_Data/PG_28/PG28_Data_Quality.csv"
Base_Directory = r'C:/Users/17577/Thesis_Work/RELAP_FILES/Automation_Tools/Thermocouple_Locations'
CURRENT_DIRECTORY = os.getcwd()
Plot_Path = os.path.join(CURRENT_DIRECTORY,"STAR_CCM_Files/PostProcessing_Folder/Plots/LP")

with open(os.path.join(CURRENT_DIRECTORY,'STAR_CCM_Files/PostProcessing_Folder/Plots/TC_Locations.txt')) as f:
    lines = f.read().splitlines()

with open(os.path.join(CURRENT_DIRECTORY,'STAR_CCM_Files/PostProcessing_Folder/Plots/TC_info.yml')) as f:
    data = yaml.load(f, Loader=SafeLoader)

with open(os.path.join(CURRENT_DIRECTORY,'STAR_CCM_Files/PostProcessing_Folder/Coarse_Mesh_Reports.txt')) as f:
    coarse_lines = f.read().splitlines()

with open(os.path.join(CURRENT_DIRECTORY,'STAR_CCM_Files/PostProcessing_Folder/Medium_Mesh_Reports.txt')) as f:
    medium_lines = f.read().splitlines()

with open(os.path.join(CURRENT_DIRECTORY,'STAR_CCM_Files/PostProcessing_Folder/Fine_Mesh_Reports.txt')) as f:
    fine_lines = f.read().splitlines()

xcoord = []
ycoord = []
zcoord = []

newlist = []
for line in lines:
    line = line.split("]")[0]
    line = line.split("[")[1]
    xcoord.append(float(line.split(", ")[0])+1.13)
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
    try:
        if x >= 0 and y >= 0:
            return float(math.atan(y/x))
        elif x <= 0 and y >= 0:
            return float(math.atan(y/x)) + np.pi/2.0
        elif x <= 0 and y <= 0:
            return float(math.atan(y/x)) + np.pi
        elif x >= 0 and y <= 0:
            return float(math.atan(y/x)) + 3.0*np.pi/2.0
    except ZeroDivisionError:
        if y>0:
            return np.pi/2.0
        elif y<0:
            return 3.0*np.pi/2.0
        else:
            return 0.0

def MakeContourPlot(theta, r, colors, name):
    fig = plt.figure(figsize=(10,4),tight_layout=False)
    ax = fig.add_subplot(111, projection='polar')
    ax.add_artist(Wedge((0.5,0.5), 0.53, 150,210, width=0.2, transform=ax.transAxes, color='blue',alpha=0.5, zorder=0))  # I had problems that the color wedges always appeared ON TOP of the data points. The 'zorder' attribute makes sure they are always UNDER the data points.
    ax.add_artist(Wedge((0.5,0.5), 0.53, 30,90, width=0.2, transform=ax.transAxes, color='green',alpha=0.5, zorder=0))
    ax.add_artist(Wedge((0.5,0.5), 0.53, 330,30, width=0.2, transform=ax.transAxes, color='brown',alpha=0.5, zorder=0))
    ax.set_yticklabels([])
    sectors = ["Primary\nSector", "Secondary\nSector", "Tertiary\nSector"]
    lines, labels = plt.thetagrids([180,60,0],(sectors), fontsize=8, fontweight='bold')
    ax.set_title('LP (Experimental) %s @ 5000 seconds'%(name),fontsize=15,fontweight='bold')
    c = ax.scatter(theta, r, c=colors, edgecolors='black', s=100,cmap='Reds',alpha=1.0, vmin=np.min(colors), vmax=np.max(colors))

    cbar1 = plt.colorbar(c, shrink=0.25, orientation='horizontal', use_gridspec=False, anchor=(0.5, -0.625), ticks=[np.min(colors), (np.max(colors)+(np.min(colors)))/2, np.max(colors)])
    cbar1.ax.tick_params(labelsize=10)
    plt.tight_layout()
    ax.set_rgrids(np.arange(0,0.8,0.1),fontsize=10,fontweight='bold')
    plt.savefig(os.path.join(Plot_Path,"LP_Temps_Experimental_%s"%name+'.png'),dpi=300,format='png',transparent=True)
    plt.close()
    pass

iteration = 0
for Height in data.keys():
    Radii = []
    Theta = []
    temps = []
    for TC in data[Height]:
        data[Height][TC]['Location']['x'] = xcoord[iteration]
        data[Height][TC]['Location']['y'] = ycoord[iteration]
        data[Height][TC]['Location']['z'] = zcoord[iteration]
        data[Height][TC]['Location']['Radius'] = float(GetNormalizedRadius(xcoord[iteration], zcoord[iteration]))
        data[Height][TC]['Location']['Theta'] = float(GetTheta(xcoord[iteration], zcoord[iteration]))
        data[Height][TC]['Results']['Coarse'] = SearchforTemp(coarse_lines, TC)
        data[Height][TC]['Results']['Medium'] = SearchforTemp(medium_lines, TC)
        data[Height][TC]['Results']['Fine'] = SearchforTemp(fine_lines, TC)
        temps.append((data[Height][TC]['Results']['Coarse'] + data[Height][TC]['Results']['Medium'] + data[Height][TC]['Results']['Fine'])/3)
        Radii.append(data[Height][TC]['Location']['Radius'])
        Theta.append(data[Height][TC]['Location']['Theta'])
        iteration += 1
    #MakeContourPlot(np.array(Theta), np.array(Radii), np.array(temps), Height)

with open(os.path.join(CURRENT_DIRECTORY, 'STAR_CCM_Files/PostProcessing_Folder/Plots/TC_info.yml'), 'w') as f:
    new_data = yaml.dump(data, f, sort_keys=False, default_flow_style=False)

def ImportStuff(filename):
    import_df = pd.read_csv(filename)
    return import_df

def DataUnitConversions(Measured):
    for (colname,colval) in Measured.iteritems():
        if "DP" in colname:
            Measured[colname] = colval.values * 1000.0
        elif "PT" in colname:
            Measured[colname] = colval.values * 1000.0
        elif "TF" or "TS" in colname:
            Measured[colname] = colval.values + 273.15
    return Measured

def BuildExperimentalPlots():
    experimental_Data = DataUnitConversions(ImportStuff(Data_File))
    for Height in data.keys():
        Radii = []
        Theta = []
        temps = []
        for TC in data[Height].keys():          
            try:
                TC_new = TC.split("_")[0] + '-' + TC.split("_")[1]
                some_column = experimental_Data['%s'%(TC_new)]
                temps.append(some_column.iloc[10001])
                Radii.append(data[Height][TC]['Location']['Radius'])
                Theta.append(data[Height][TC]['Location']['Theta'])
            except:
                print("Could not find %s"%(TC))
        MakeContourPlot(Theta, Radii, pd.Series(temps), Height)

BuildExperimentalPlots()