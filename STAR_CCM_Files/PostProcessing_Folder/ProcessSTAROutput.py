import os
import sys
from typing import List
import yaml
import numpy as np
import glob
from pathlib import Path
from yaml.loader import SafeLoader
sys.path.insert(1, '/path/to/application/app/folder')

with open("C:\\Users\\17577\\Thesis_Work\\STAR_CCM_Files\\PostProcessing_Folder\\Plots\\TC_Info.yml") as f:
    data = yaml.load(f, Loader=SafeLoader)

directory_path = os.getcwd()

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

def WriteFile2List(StringList, Filename, append = None):
    if append:
        with open(Filename, 'a') as my_list_file:
    
        #looping over the each ist element
        
            for element in StringList:
        
                #writing to file line by line
        
                my_list_file.write('%s\n' % element)
    else:
        with open(Filename, 'w') as my_list_file:
    
        #looping over the each ist element
        
            for element in StringList:
        
                #writing to file line by line
        
                my_list_file.write('%s\n' % element)
    my_list_file.close()

def AccessNestedDictValue(Dict, value):
    return Dict[value]

def WriteOverleafTable(OverleafTableTemplate, OverleafTableFilled, Dict, key_list = None, Append=None, NumberRepeats=None):
    try:
        ListofStrings = ReadFile2List(OverleafTableTemplate)
    except FileNotFoundError:
        ListofStrings = ReadFile2List(FindFileinDirectory(OverleafTableTemplate, '.sty'))
    
    def CheckforRewrite(ListofStrings, OverleafTableTemplate, Dict, Key_List = None, Append=False):
        New_List = []
        Flag = ''
        for i, _ in enumerate(ListofStrings):
            if '<' in ListofStrings[i]:
                Flag = 'Set'
                for key in Dict.keys():
                    line = '\t' + str((ListofStrings[i].split("<")[1]).split(">")[0])
                    columns = line.split('&')
                    new_line = ''
                    for j, _ in enumerate(columns):
                        string_split = columns[j].split(".")
                        string_split[0] = str(key)
                        new_string = ''
                        if len(string_split) > 1:
                            for string in string_split:
                                new_string += string + '.'
                        if j == 0:
                            new_line += '\t' + str(key).replace('_', '-') + ' & '
                        else:
                            new_line += '$$' + new_string.split("$$")[0] + '$$' + ' & '
                    New_List.append(new_line)
            else:
                New_List.append(ListofStrings[i])
        if Flag == 'Set':
            if Append:
                WriteFile2List(New_List, OverleafTableTemplate, append = True)
            else:
                WriteFile2List(New_List, OverleafTableTemplate)
        else:
            pass
        ListofStrings = ReadFile2List(FindFileinDirectory(OverleafTableTemplate, '.sty'))
        return ListofStrings

    if Append:
        ListofStrings = CheckforRewrite(ListofStrings, OverleafTableTemplate, Dict, Append = True)
    else:
        ListofStrings = CheckforRewrite(ListofStrings, OverleafTableTemplate, Dict)

    def ReplaceDoubleDollarSigns(ListofStrings, Dict):
        New_Dict = Dict
        NewStringList = []
        for i, _ in enumerate(ListofStrings):
            #print(ListofStrings[i])
            if "$" in ListofStrings[i]:
                line = ListofStrings[i].split("&")
                line_start = ListofStrings[i].split("&")[0]
            else:
                line = ListofStrings[i]
                line_start = ListofStrings[i]
            New_Line = []
            New_Line.append(line_start)
            for j, _ in enumerate(line):
                if '$$' in line[j]:
                    parameter = (line[j].split('$$')[1]).split('$$')[0]
                    #print("This is the string of the line to parse: %s"%parameter)
                    token_list = parameter.split(".")
                    #print(token_list)
                    for k, _ in enumerate(token_list):
                        try:
                            New_Dict = AccessNestedDictValue(New_Dict, token_list[k])
                            if type(New_Dict) is not dict:
                                if j == len(line) - 1:
                                    New_Line.append(str(New_Dict) + ' \\' + '\\')
                                else:
                                    New_Line.append(str(New_Dict))
                                New_Dict = Dict
                        except:
                            if type(New_Dict) is not dict:
                                if j == len(line) - 1:
                                    New_Line.append(str(New_Dict) + ' \\' + '\\')
                                else:
                                    New_Line.append(str(New_Dict))
                                New_Dict = Dict
            new_string = ''
            if '$' in ListofStrings[i]:
                for m, _ in enumerate(New_Line):
                    if m == len(New_Line)-1:
                        new_string += str(New_Line[m])
                    else:
                        new_string += str(New_Line[m]) + ' & '
            else:
                for m, _ in enumerate(New_Line):
                    new_string += str(New_Line[m])
            NewStringList.append(new_string)
        return NewStringList

    
    #WriteFile2List(ReplaceDoubleDollarSigns(ListofStrings, Dict), FindFileinDirectory(OverleafTableFilled, '.sty'))

for key in data.keys():
    instrument_list = []
    for instrument in data[key].keys():
        instrument_list.append(instrument)
    print(instrument_list)
    WriteOverleafTable("STAR_TC_Error.sty", "STAR_TC_Error_Filled.sty", data[key], key_list = None, Append=True, NumberRepeats = len(instrument_list))