import os
import sys
import numpy as np
import yaml

class Table():
    def __init__(self, ):
        self._table_name = "TC_Table"
        self._yaml_name = "TC_Table.yml"

    def CreateYAML(self):
        pass

    def BuildOverleafTable(self):
        pass

def main():
    res = []
    dir_path = "C:\\Users\\17577\\Thesis_Work\\STAR_CCM_Files\\PostProcessing_Folder\\Tables\\Overleaf_Template_Files"
    for path in os.listdir(dir_path):
        # check if current path is a file
        if os.path.isfile(os.path.join(dir_path, path)):
            res.append(path)
    print(res)

main()