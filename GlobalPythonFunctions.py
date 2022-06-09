import os
import sys
import yaml

def ClearTerminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def GetWorkingDirectory():
    pass

def YAML2Dict(path, YAMLFileName):
  with open(os.path.join(path, YAMLFileName), 'r') as stream:
      try:
          Input_File_YAML=yaml.safe_load(stream)
      except yaml.YAMLError as exc:
          print(exc)
  return Input_File_YAML

def WorkSetup():
    ClearTerminal()
    GetWorkingDirectory()