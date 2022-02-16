import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
import numpy as np
import pandas as pd
import os

TCLocationFolder = r"C:/Users/17577/Thesis_Work/RELAP_FILES/Automation_Tools/Thermocouple_Locations/Solid"
Plot_Path = r"C:/Users/17577/Thesis_Work/RELAP_FILES/Automation_Tools/Experimental_Data/PG_28/Plots/RXC/Block_Temps"
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

def MakeContourPlot(theta, r, colors, name):
    print(name)
    i = 8000
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
    plt.savefig(os.path.join(Plot_Path,name+str(i)+'Relap'+'.png'),dpi=300,format='png',transparent=True)
    plt.close()
    pass


def main():
    experimental_Data = DataUnitConversions(ImportStuff(Data_File))
    for file in os.listdir(Base_Directory):
        TCInformationDF = ImportStuff(os.path.join(Base_Directory, file))
        colors = []
        for index, row in TCInformationDF.iterrows():
            instrument = row['Instrument']
            try:
                if 'TS' in instrument:
                    some_column = experimental_Data['%s'%(instrument)]
            except:
                print("Could not find %s"%(instrument))
            colors.append(some_column.iloc[16001])
        MakeContourPlot(TCInformationDF.Angle, TCInformationDF.Location, pd.Series(colors), file.split(".")[0])


main()