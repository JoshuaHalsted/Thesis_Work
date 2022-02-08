import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.interpolate import make_interp_spline
import os
import pathlib
import yaml

os.system('cls' if os.name == 'nt' else 'clear')
CURRENT_FILE_PATH = pathlib.Path(__file__).parent.resolve()
print(CURRENT_FILE_PATH)
os.chdir(CURRENT_FILE_PATH)

path = r"C:\\Users\\17577\\Thesis_Work\\RELAP_FILES\\Automation_Tools\\Experimental_Data\\PG_28"

def YAML2Dict():
  with open(os.path.join(path, "Plot_Input.yml"), 'r') as stream:
      try:
          Input_File_YAML=yaml.safe_load(stream)
      except yaml.YAMLError as exc:
          print(exc)
  return Input_File_YAML


Print_Value_Tables = True
savefigures = True

lfontsize= 13
lfontsizeSmall= 11

BorderBot = 0.15
BorderRig = 0.975
BorderTop = 0.94

xlimites1 = [0.0, 21943.5]



Measured = pd.read_csv(r'C:/Users/17577/Thesis_Work/RELAP_FILES\Automation_Tools/Experimental_Data/PG_28/PG28_Data_Quality.csv')

class DefaultSettings():
    def __init__(self, DefaultSettingsDict):
        self._def_set_dict = DefaultSettingsDict

class Plot(DefaultSettings):
    def __init__(self, DefaultSettingsDict, plot_dict, plot_name):
        super().__init__(DefaultSettingsDict)
        self._name = plot_name
        self._dict = plot_dict
        self._title = plot_dict['Title']
        self._instruments = self.DetermineInstruments()
        self._def_set_dict = DefaultSettingsDict
        self._instr_locations = self.GetLocations()
        self._properties = self.GetProperties()
        self._make_plot = self.MakePlot()
        self._settings = self.GetSettings()
        #print(self._instruments)

    def GetLocations(self):
        LocationList = []
        for location in self._dict['Instruments'].keys():
            LocationList.append(location)
        return LocationList

    def GetProperties(self):
        PropertyList = []
        for location in self.GetLocations():
            for property in self._dict['Instruments'][location]:
                PropertyList.append(property)
        PropertyList = list(dict.fromkeys(PropertyList))
        return PropertyList

    def DetermineInstruments(self):
        Locations = self.GetLocations()
        Properties = self.GetProperties()
        InstrumentList = []
        for location in Locations:
            for properties in Properties:
                InstrumentList.append(self._dict['Instruments'][location][properties]['Label'])
        return InstrumentList

    def GetSettings(self):
        for key in self._def_set_dict.keys():
            pass
            #print(key)

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
            instrument = self._dict['Instruments'][location][self._properties[property_index]]['Label']
            color = self._dict['Instruments'][location][self._properties[property_index]]['Color']
            X, Y = self.MakeSpline(Measured['Run_Time'], Measured[instrument])
            ax.plot(X, Y, color=color, label = instrument)
        return ax

    def MakePlot(self):
        for property, _ in enumerate(self._properties):
            if property==0:
                fig, ax1 = self.InitializeYAxis(self._properties[property])
                ax1 = self.InputDatapoints(ax1, property)
                leg = ax1.legend(bbox_to_anchor=(0.5, 1.02), fontsize=self._def_set_dict['lfontsizeSmall'])
            else:
                fig2, ax2 = self.InitializeYAxis(self._properties[property], ax1)
                ax2 = self.InputDatapoints(ax2, property)
                leg = ax2.legend(loc='center', bbox_to_anchor=(0.75, 1.02), fontsize=self._def_set_dict['lfontsizeSmall'])
            fig.tight_layout()
            plt.title(self._title, fontsize=20)
            fig.savefig(path + '/Plots/' + '%s.png'%(self._name))


def main():
    Input_File_YAML = YAML2Dict()
    Default_Settings_Dict = Input_File_YAML['Experimental_Data']['PG_28']['Default_Settings']
    SettingsInstance = DefaultSettings(Default_Settings_Dict)
    for plot in Input_File_YAML['Experimental_Data']['PG_28']['Plots']:
        PlotInstance = Plot(Default_Settings_Dict, Input_File_YAML['Experimental_Data']['PG_28']['Plots'][plot], plot)

main()