import os
import sys
import yaml

print(chr(27) + "[2J")

STAR_RESULTS_YAML = 'C:\\Users\\17577\Thesis_Work\\Other_Calculations\GCI_Study\\Input_File.yml'
TOTAL_SIM_VOLUME = 0.359392

class Simulation():
    def __init__(self, sim_dict):
        self._name = sim_dict['Name']
        self._num_cells = sim_dict['Number_Cells']
        #self._char_size = (TOTAL_SIM_VOLUME/self._num_cells)**(1/3)
        self._char_size = (TOTAL_SIM_VOLUME/self._num_cells)**(1)

def CreateRatio(Sim1, Sim2):
    return Sim1._char_size/Sim2._char_size

def CompareRatios(Sim_List):
    iteration = 0
    ratio_list = []
    while True:
        print(len(Sim_List))
        #if iteration < (len(Sim_List)-1):
        if iteration < 1:
            ratio_list.append(CreateRatio(Sim_List[iteration+1], Sim_List[iteration]))
            if ratio_list[iteration] < 1.3:
                print("Grid %s needs to be refined"%(Sim_List[iteration+1]._name))
            else:
                print("This is acceptable")
            iteration += 1
        else:
            break
    return ratio_list

def main():
    with open(STAR_RESULTS_YAML) as fh:
        Analysis_Dict = yaml.load(fh, Loader=yaml.FullLoader)
    simulation_list = []
    for region in Analysis_Dict.keys():
        Sim_List = []
        for item in Analysis_Dict[region]:
            if item == 'Fluid_Volume':
                Fluid_Volume = Analysis_Dict[region]['Fluid_Volume']
            else:
                Sim_Instance = Simulation(Analysis_Dict[region][item])
                Sim_List.append(Sim_Instance)
        Sim_List.append(Sim_List[0])
        ratio_list = CompareRatios(Sim_List)
        print(ratio_list)

main()