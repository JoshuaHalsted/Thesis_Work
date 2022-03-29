import os
import sys
from typing import List
import yaml
import numpy as np
import glob
from pathlib import Path

sys.path.insert(1, 'C:\\Users\\17577\\Thesis_Work\\STAR_CCM_Files\\PostProcessing_Folder')

import ProcessSTAROutput

print(chr(27) + "[2J")

directory_path = os.getcwd()
os.chdir(directory_path)
print("My current directory is : " + directory_path)
folder_name = os.path.basename(directory_path)
print("My directory name is : " + folder_name)

#STAR_RESULTS_YAML = "C:\\Users\\17577\\Thesis_Work\\STAR_CCM_Files\\PostProcessing_Folder\\GCI_Study\\Input_File.yml"

STAR_RESULTS_YAML = os.path.join(directory_path ,"STAR_CCM_Files/PostProcessing_Folder/GCI_Study/Test_Input_File.yml")


#STAR_RESULTS_YAML = os.path.join(directory_path,'Input_File.yml')
TOTAL_SIM_VOLUME = 0.359392
#GCI_RESULTS_YAML = os.path.join(directory_path,'GCI_Results.yml')

GCI_RESULTS_YAML = "C:\\Users\\17577\\Thesis_Work\\STAR_CCM_Files\\PostProcessing_Folder\\GCI_Study\\GCI_Results.yml"

def FindFileinDirectory(filename, extension):
    pathlist = Path(directory_path).glob('**/*%s'%(extension))
    myfile = filename
    for path in pathlist:
        if path.name == myfile:
            return path

def ReadFile2List(Filename):
    my_file = open(Filename, "r")
    data = my_file.read()
    data_into_list = data.split("\n")
    return data_into_list

def WriteFile2List(StringList, Filename):
    with open(Filename, 'w') as my_list_file:
 
    #looping over the each ist element
    
        for element in StringList:
    
            #writing to file line by line
    
            my_list_file.write('%s\n' % element)
    my_list_file.close()


def CreateRatio(Sim1, Sim2):
    return Sim1._char_size/Sim2._char_size

def CompareRatios(Sim_List):
    iteration = 0
    ratio_list = []
    while True:
        if iteration < 2:
            ratio_list.append(CreateRatio(Sim_List[iteration], Sim_List[iteration+1]))
            iteration += 1
        else:
            break
    return ratio_list

def AccessNestedDictValue(Dict, value):
    return Dict[value]

## Class definitions

class Simulation():
    def __init__(self, sim_dict, sim, region):
        self._sim = sim
        self._region = region
        self._sim_dict = self.ParseSTAROutput(sim_dict, self._sim, self._region)
        self._num_cells = float(self._sim_dict['Number_Cells'])
        self._phi = self._sim_dict['Variable_of_Interest']['Value']
        #self._char_size = (TOTAL_SIM_VOLUME/self._num_cells)**(1/3)
        self._char_size = (TOTAL_SIM_VOLUME/self._num_cells)**(1)

    def ParseSTAROutput(self, Analysis_Dict, sim, region):
        '''
        DESC: Obtain the number of cells in each region, and the parameters of interest.
        ARGS:
            Analysis_Dict: the dictionary representing the YAML file to be filled in
            ListofStrings: the strings representing the STAR output file
        RETURNS:
            Analysis_Dict (filled out)
        '''
        try:
            ListofStrings = ReadFile2List(Analysis_Dict['Report_Name'])
        except FileNotFoundError:
            ListofStrings = ReadFile2List(FindFileinDirectory(Analysis_Dict['Report_Name'], '.txt'))
    

        def GetNumberCells(ListofStrings, String):
            for i, _ in enumerate(ListofStrings):
                if 'cells' in ListofStrings[i]:
                    if String in ListofStrings[i]:
                        NumberCells = ListofStrings[i].split()[1]
            return NumberCells

        def GetPhi(ListofStrings, PhiTag):
            for i, _ in enumerate(ListofStrings):
                if PhiTag in ListofStrings[i]:
                    Reading = ListofStrings[i].split()[1]
            return Reading

        Analysis_Dict['Number_Cells'] = int(float(GetNumberCells(ListofStrings, region)))
        Analysis_Dict['Variable_of_Interest']['Value'] = round(float(GetPhi(ListofStrings, Analysis_Dict['Variable_of_Interest']['Tag'])), 3)
        return Analysis_Dict

class Calculation():
    def __init__(self, phi, ratio_list, analysis_dict, region):
        self._phi = phi
        self._ratio_list = ratio_list
        self._epsilon = self.CalculateEpsilon()
        self._analysis_dict = analysis_dict
        ApparentOrder = float((1/np.log(ratio_list[1]))*np.abs(np.abs(self._epsilon[1]/self._epsilon[0])+np.log((ratio_list[0]-1)/(ratio_list[1]-1))))
        self._analysis_dict[region]['ApparentOrder'] = "{:.4e}".format(ApparentOrder)
        phi21ext = float(ratio_list[0]**ApparentOrder * self._phi[0]-self._phi[1])/(ratio_list[0]**ApparentOrder - 1)
        self._analysis_dict[region]['phi21ext'] = round(phi21ext, 2)
        phi32ext = float(ratio_list[1]**ApparentOrder * self._phi[1]-self._phi[2])/(ratio_list[1]**ApparentOrder - 1)
        self._analysis_dict[region]['phi32ext'] = round(phi32ext,2)
        error21_a = float(np.abs((self._phi[0]-self._phi[1])/self._phi[0]))
        self._analysis_dict[region]['error21_a'] = "{:.4e}".format(error21_a)
        error21_ext = float(np.abs((phi21ext-self._phi[0])/phi21ext))
        self._analysis_dict[region]['error21_ext'] = "{:.4e}".format(error21_ext)
        error32_a = float(np.abs((self._phi[1]-self._phi[2])/self._phi[1]))
        self._analysis_dict[region]['error32_a'] = "{:.4e}".format(error32_a)
        error32_ext = float((np.abs((phi32ext-self._phi[1])/phi32ext)))
        self._analysis_dict[region]['error32_ext'] = "{:.4e}".format(error32_ext)
        GCI_21_Fine = float(1.25 * error21_a / (ratio_list[0]**ApparentOrder - 1))
        self._analysis_dict[region]['GCI_21_Fine'] = "{:.4e}".format(GCI_21_Fine)
        GCI_32_Fine = float(1.25 * error32_a / (ratio_list[1]**ApparentOrder - 1))
        self._analysis_dict[region]['GCI_32_Fine'] = "{:.4e}".format(GCI_32_Fine)
    def CalculateEpsilon(self):
        epsilon = []
        for i, _ in enumerate(self._phi):
            if i < (len(self._phi)-1):
                epsilon.append(self._phi[i+1]-self._phi[i])
        return epsilon

    def ReturnDict(self):
        return self._analysis_dict


def main():
    with open(STAR_RESULTS_YAML) as fh:
        Analysis_Dict = yaml.load(fh, Loader=yaml.FullLoader)
    for region in Analysis_Dict.keys():
        print("*************************************************")
        print("Performing GCI analysis on %s"%region)
        print("*************************************************")
        Sim_List = []
        Phi = []
        for item in Analysis_Dict[region]:
            if item == 'Fluid_Volume':
                Fluid_Volume = Analysis_Dict[region]['Fluid_Volume']
            elif 'Sim' in item:
                Sim_Instance = Simulation(Analysis_Dict[region][item], item, region)
                Sim_List.append(Sim_Instance)
                Phi.append(Sim_Instance._phi)
        Sim_List.append(Sim_List[0])
        ratio_list = CompareRatios(Sim_List)
        Analysis_Dict = Calculation(Phi, ratio_list, Analysis_Dict, region).ReturnDict()
    with open(GCI_RESULTS_YAML, 'w') as file:
        outputs = yaml.dump(Analysis_Dict, file)
        print(Analysis_Dict)
    ProcessSTAROutput.WriteOverleafTable("Discretization_Error_Table.sty", "Discretization_Error_Table_Filled.sty", Analysis_Dict)

main()