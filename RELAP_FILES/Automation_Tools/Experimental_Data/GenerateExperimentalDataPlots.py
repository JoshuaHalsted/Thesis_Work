import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.interpolate import make_interp_spline
import os
import pathlib
import yaml
import ModifyYAML
#import GlobalPythonFunctions

os.system('cls' if os.name == 'nt' else 'clear')
CURRENT_FILE_PATH = pathlib.Path(__file__).parent.resolve()
os.chdir(CURRENT_FILE_PATH)

#GlobalPythonFunctions.ClearTerminal()

path = r"C:\\Users\\17577\\Thesis_Work\\RELAP_FILES\\Automation_Tools\\Experimental_Data\\PG_28"

lfontsize= 13
lfontsizeSmall= 11

BorderBot = 0.15
BorderRig = 0.975
BorderTop = 0.94

xlimites1 = [0.0, 21943.5]

Measured = pd.read_csv(r'C:/Users/17577/Thesis_Work/RELAP_FILES\Automation_Tools/Experimental_Data/PG_28/PG28_Data_Quality.csv')

for (colname,colval) in Measured.iteritems():
    if "DP" in colname:
        Measured[colname] = colval.values
    elif "PT" in colname:
        Measured[colname] = colval.values
    elif "TF" or "TS" in colname:
         Measured[colname] = colval.values + 273.15

def MakeDir(FullPath):
    try:
        os.mkdir(FullPath)
    except:
        pass
    return FullPath

class DefaultSettings():
    def __init__(self, DefaultSettingsDict):
        self._def_set_dict = DefaultSettingsDict

class Plot(DefaultSettings):
    def __init__(self, DefaultSettingsDict, plot_dict, region, plot_name):
        super().__init__(DefaultSettingsDict)
        self._name = plot_name
        self._dict = plot_dict
        #self._region = region
        self._directory = MakeDir(path + '/Plots/' + '%s'%(region))
        self._def_set_dict = DefaultSettingsDict
        self._settings_dict = self.GetSettings()
        self._instr_locations = self.GetLocations()
        self._properties = self.GetProperties()
        self._instruments = self.DetermineInstruments()
        self._make_plot = self.MakePlot()

    def GetLocations(self):
        LocationList = []
        for location in self._dict['Instruments'].keys():
            LocationList.append(location)
        return LocationList

    def GetProperties(self):
        PropertyList = []
        for location in self.GetLocations():
            for property in self._dict['Instruments'][location]:
                PropertyList.append("%s (%s)"%(property, self._dict['Instruments'][location][property]['Units']))
        PropertyList = list(dict.fromkeys(PropertyList))
        return PropertyList

    def DetermineInstruments(self):
        InstrumentList = []
        for location in  self._instr_locations:
            for properties in self._properties:
                InstrumentList.append(self._dict['Instruments'][location][properties.split(" ")[0]]['Label'])
        return InstrumentList

    def GetSettings(self):
        settings_dict = {}
        for key, value in self._def_set_dict.items(): 
            settings_dict[key] = value
        return settings_dict

    def MakeSpline(self, X_Column, Y_Column):

        # Convert dataframe columns to numpy arrays
        X_Array = X_Column.to_numpy()
        Y_Array = Y_Column.to_numpy()

        X_Y_Spline = make_interp_spline(X_Array, Y_Array)
        X_ = np.linspace(X_Array.min(), X_Array.max(), 1000)
        Y_ = X_Y_Spline(X_)
        return X_, Y_

    def InitializeYAxis(self, y_label, ax1=None):
        if ax1 is not None:
            axis = ax1.twinx()
            fig = None
        else:
            fig, axis = plt.subplots()
        color = 'tab:gray'
        axis.set_xlabel('Time (s)')
        axis.set_ylabel('%s'%(y_label), color=color)
        axis.tick_params(axis='y', labelcolor=color)
        return fig, axis

    def InputDatapoints(self, ax, property_index):
        for location in self._instr_locations:
            try:
                instrument = self._dict['Instruments'][location][self._properties[property_index].split(" ")[0]]['Label']
                color = self._dict['Instruments'][location][self._properties[property_index].split(" ")[0]]['Color']
                X, Y = self.MakeSpline(Measured['Run_Time'], Measured[instrument])
                ax.plot(X, Y, color=color, label = instrument)
            except:
                pass
        return ax

    def MakePlot(self):
        for property, _ in enumerate(self._properties):
            if property==0:
                fig, ax1 = self.InitializeYAxis(self._properties[property])
                ax1 = self.InputDatapoints(ax1, property)
                leg = ax1.legend(bbox_to_anchor=(0.25, 1.25), fontsize=self._settings_dict['lfontsizeSmall'])
            else:
                fig2, ax2 = self.InitializeYAxis(self._properties[property], ax1)
                ax2 = self.InputDatapoints(ax2, property)
                leg = ax2.legend(bbox_to_anchor=(1.0, 1.25), fontsize=self._settings_dict['lfontsizeSmall'])
            fig.tight_layout()
            plt.title(self._dict['Title'], fontsize=16)
            fig.savefig(self._directory + '/%s.png'%(self._name))
            plt.close()
            #close(fig)


def main():
    ModifyYAML.UpdateYAML(os.path.join(path, "IntoThis.yml"), "UpdatedYAML.yml")
    Input_File_YAML = ModifyYAML.YAML2Dict(os.path.join(path, "UpdatedYAML.yml"))
    Default_Settings_Dict = Input_File_YAML['Experimental_Data']['PG_28']['Default_Settings']
    Test_Dict = Input_File_YAML['Experimental_Data']['PG_28']
    for region in Test_Dict['Plots']:
        for plot in Test_Dict['Plots'][region]:
            PlotInstance = Plot(Default_Settings_Dict, Test_Dict['Plots'][region][plot], region, plot)

#main()