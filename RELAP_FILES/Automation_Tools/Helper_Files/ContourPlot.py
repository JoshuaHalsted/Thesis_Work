import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
import numpy as np
import pandas as pd

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

def MakeContourPlot(theta, r, colors):
    i = 8000
    fig = plt.figure(figsize=(15,10))
    ax = fig.add_subplot(111, projection='polar')
    ax.add_artist(Wedge((0.5,0.5), 0.53, 0, 60, width=0.2, transform=ax.transAxes, color='blue',alpha=0.5, zorder=0))  # I had problems that the color wedges always appeared ON TOP of the data points. The 'zorder' attribute makes sure they are always UNDER the data points.
    ax.add_artist(Wedge((0.5,0.5), 0.53, 120,180, width=0.2, transform=ax.transAxes, color='green',alpha=0.5, zorder=0))
    ax.set_yticklabels([])
    sectors = ["Primary Sector", "Secondary Sector"]
    lines, labels = plt.thetagrids([0,140],(sectors), fontsize=30, fontweight='bold')
    ax.set_title('Core-Block#1 (Experiment) @ {}'.format(round(i/3600))+'hours',fontsize=30,fontweight='bold')
    c = ax.scatter(theta, r, c=colors, s=500,cmap='Reds',alpha=1.0, vmin=500, vmax=1000)

    cbar = plt.colorbar(c, shrink=0.5, orientation='horizontal', use_gridspec=False, anchor=(0.5, 0.5), ticks=[500, 750, 1000])
    cbar.ax.tick_params(labelsize=25)
    plt.tight_layout()
    ax.set_rgrids(np.arange(0,0.8,0.1),fontsize=20,fontweight='bold')
    plt.savefig('B1_rel_Temp'+str(i)+'Relap'+'.png',dpi=300,format='png',transparent=True)
    pass


def main():
    data_frame = ImportStuff(r'C:/Users/17577/Thesis_Work/RELAP_FILES/Automation_Tools/Helper_Files/CoreThermoCoupleLocations.csv')
    experimental_Data = ImportStuff(r"C:/Users/17577/Thesis_Work/RELAP_FILES/Automation_Tools/Experimental_Data/PG_28/PG28_Data_Quality.csv")
    experimental_Data = DataUnitConversions(experimental_Data)
    print(type(data_frame.Angle))
    colors = []
    for index, row in data_frame.iterrows():
        instrument = row['Instrument']
        some_column = experimental_Data['%s'%(instrument)]
        colors.append(some_column.iloc[16001])
    colorsSeries = pd.Series(colors)
    MakeContourPlot(data_frame.Angle, data_frame.Location, colorsSeries)




main()