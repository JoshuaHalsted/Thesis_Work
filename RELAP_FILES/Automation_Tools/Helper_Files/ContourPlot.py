import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
import numpy as np
import pandas as pd
import os
from path import Path

TCLocationFolder = r"C:/Users/17577/Thesis_Work/RELAP_FILES/Automation_Tools/Thermocouple_Locations/"
Solid_Plot_Path = r"C:/Users/17577/Thesis_Work/RELAP_FILES/Automation_Tools/Experimental_Data/PG_28/Plots/RXC/Solid_Temps"
Fluid_Plot_Path = r"C:/Users/17577/Thesis_Work/RELAP_FILES/Automation_Tools/Experimental_Data/PG_28/Plots/RXC/Fluid_Temps"
Data_File = r"C:/Users/17577/Thesis_Work/RELAP_FILES/Automation_Tools/Experimental_Data/PG_28/PG28_Data_Quality.csv"
Base_Directory = r'C:/Users/17577/Thesis_Work/RELAP_FILES/Automation_Tools/Thermocouple_Locations'

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

def MakeContourPlot(theta, r, colors, Plot_Path, name):
    i = 8000
    Location = name.split("_")[:-2]
    Location_String = ''
    for split in Location:
        Location_String += split + ' '
    theta = 2*np.pi*theta/360
    fig = plt.figure(figsize=(10,4), tight_layout=False)
    ax = fig.add_subplot(111, projection='polar')
    ax.add_artist(Wedge((0.5,0.5), 0.53, 150, 210, width=0.2, transform=ax.transAxes, color='blue',alpha=0.5, zorder=0))  # I had problems that the color wedges always appeared ON TOP of the data points. The 'zorder' attribute makes sure they are always UNDER the data points.
    ax.add_artist(Wedge((0.5,0.5), 0.53, 30, 90, width=0.2, transform=ax.transAxes, color='green',alpha=0.5, zorder=0))
    ax.add_artist(Wedge((0.5,0.5), 0.53, 330, 30, width=0.2, transform=ax.transAxes, color='brown',alpha=0.5, zorder=0))
    ax.set_yticklabels([])
    sectors = ["Primary\nSector", "Secondary\nSector", "Tertiary\nSector"]
    lines, labels = plt.thetagrids([180,60,0],(sectors), fontsize=8, fontweight='bold')
    ax.set_title('%s'%(Location_String) + ' (Experiment) @ {}'.format(round(i))+' seconds',fontsize=15,fontweight='bold')
    print(name)
    print(colors)
    c = ax.scatter(theta, r, c=colors, edgecolors='black', s=100, cmap='Reds', alpha=1.0, vmin=np.min(colors), vmax=np.max(colors))

    cbar1 = plt.colorbar(c, shrink=0.25, orientation='horizontal', use_gridspec=False, anchor=(0.5, -0.625), ticks=[np.min(colors), (np.max(colors)+(np.min(colors)))/2, np.max(colors)])
    cbar1.ax.tick_params(labelsize=10)
    plt.tight_layout()
    ax.set_rgrids(np.arange(0,0.8,0.1),fontsize=10,fontweight='bold')
    TC_type = str(name.split('_')[-1])
    plt.savefig(os.path.join(Plot_Path, name + str(i) + 'Relap_%s'%(TC_type) + '.png'), dpi=300, format='png', transparent=True)
    plt.close()
    pass


def main():
    experimental_Data = DataUnitConversions(ImportStuff(Data_File))
    for folder in os.listdir(Base_Directory):
        for file in os.listdir(os.path.join(Base_Directory, folder)):
            TCInformationDF = ImportStuff(os.path.join(Base_Directory, folder, file))
            Colors = []
            for index, row in TCInformationDF.iterrows():
                instrument = row['Instrument']
                try:
                    TC_Tag = experimental_Data['%s'%(instrument)]
                    Colors.append(TC_Tag.iloc[16001])
                except:
                    print("Could not find %s"%(instrument))
                    TCInformationDF.drop(TCInformationDF[TCInformationDF['Instrument'] == '%s'%(instrument)].index, inplace = True)
                print(instrument)
                print(Colors)
            if len(Colors)>0:
                if folder.split("_")[0] == 'Solid':
                    MakeContourPlot(TCInformationDF.Angle, TCInformationDF.Location, pd.Series(Colors), Solid_Plot_Path, file.split(".")[0] + '_Solid')
                elif folder.split("_")[0] == 'Fluid':
                    MakeContourPlot(TCInformationDF.Angle, TCInformationDF.Location, pd.Series(Colors), Fluid_Plot_Path, file.split(".")[0] + '_Fluid')

main()