import os
import yaml

os.system('cls' if os.name == 'nt' else 'clear')
path = r"C:\\Users\\17577\\Thesis_Work\\RELAP_FILES\\Automation_Tools\\Experimental_Data\\PG_28"

def YAML2Dict(YAMLFileName):
  with open(os.path.join(path, YAMLFileName), 'r') as stream:
      try:
          Input_File_YAML=yaml.safe_load(stream)
      except yaml.YAMLError as exc:
          print(exc)
  return Input_File_YAML

def ReadFile2List(Filepath):
    ReadFile = open(Filepath, "r")
    StringList = ReadFile.read().split("\n")
    ReadFile.close() 
    return StringList

def WriteFile(Filepath, List2Write):
    NewFile=open(Filepath,'w')
    for items in List2Write:
        NewFile.writelines([items])

def UpdateYAML(OriginalFile, NewFileName):
    NewLines = []
    for line in ReadFile2List(OriginalFile):
        if "<#include " in line:
            NewLines.append(line.split(":")[0] + ":" + "\n")
            for line2 in ReadFile2List((line.split("<#include ")[1]).split('"')[0]):
                NewLines.append(((len(line) - len(line.lstrip())) * " ") + "    " + line2 + "\n")
        else:
            NewLines.append(line + "\n")
    WriteFile(os.path.join(path, NewFileName), NewLines)
    return os.path.join(path, NewFileName)

#def main():
    #NewYAML = UpdateYAML(os.path.join(path, "ProvideThis.yml"), "UpdatedYAML.yml")

#main()
