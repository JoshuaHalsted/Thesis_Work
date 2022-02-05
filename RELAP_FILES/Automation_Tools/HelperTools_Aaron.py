from datetime import timedelta
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math
import string
import re
import os
import sys
import pathlib
import yaml

os.system('cls' if os.name == 'nt' else 'clear')

#
# This is an undocumented, unofficial collection of subroiutines that helps
#  - create RELAP5 input files for HTTF tests
#  - make plots.
# No error handling or input checking is implemented... 
# This will crash if something unexpected happens.
#

path = pathlib.Path(__file__).parent.resolve()
os.chdir(path)

def YAML2Dict():
  with open("PG_26_Input_File.yml", 'r') as stream:
      try:
          Input_File_YAML=yaml.safe_load(stream)
      except yaml.YAMLError as exc:
          print(exc)
  return Input_File_YAML


def InitializePlot():
    #Set figure size
    figA = 10
    figB = 5

    fig = plt.figure(figsize=(figA,figB))
    ax = fig.add_subplot(111)
    return None

class Plots():
  def __init__(self, plot_dict):
    self._plot_dict = plot_dict
    self._title = plot_dict['Title']
    self._types = plot_dict['Types']
    self._instruments = plot_dict['Instruments']
    self._r5_channel = plot_dict['R5_Channel']
    self._make_plot = self.GeneratePlot()
  
  def InitializePlot(self):
      #Set figure size
      figA = 10
      figB = 5

      fig = plt.figure(figsize=(figA,figB))
      ax = fig.add_subplot(111)
      return fig, ax

  def GeneratePlot(self):
    for Line in self._types:
      fig, ax = self.InitializePlot()
      if len(self._instruments) > 1:
        scat = plt.plot(Measured['Run_Time'], [self._instruments],  'c4-' , markevery=13000, label=self._title = plot_dict['Title'], markersize=10)
    #InitializePlot()
    pass

class Analysis():
  def __init__(self, analysis_dict):
    self._dict = analysis_dict
    self._analysis_name = self._dict['Name']
    self._working_directory = self._dict['Directory']

class Subanalysis(Analysis):
  def __init__(self, analysis_dict, sub_name):
    super().__init__(analysis_dict)
    self._dict = analysis_dict['Iteration_1']
    self._sub_name = sub_name

class Test(Subanalysis):
  def __init__(self, analysis_dict, sub_name, test_name):
    super().__init__(analysis_dict, sub_name)
    self._analysis_dict = analysis_dict
    self._subanalysis_dict = self._analysis_dict[sub_name]
    self._test_dict = self._subanalysis_dict[test_name]
    self._initial_condition = self._test_dict['Initial_Time']
    self._sub_name = sub_name
    self._test_name = test_name
    self._test_directory = os.path.join(self._analysis_dict['Directory'], '%s\\R5_Files\\'%(sub_name) + self._test_name)
    self._r5_template_file = os.path.join(self._test_directory, self._test_dict['Files']['R5_Template_File'])
    self._r5_filled_file = os.path.join(self._test_directory, self._test_dict['Files']['R5_Filled_File'])
    self._r5_strip_input = os.path.join(self._test_directory, self._test_dict['Files']['R5_Strip_Input'])
    self._r5_strip_output = os.path.join(self._test_directory, self._test_dict['Files']['R5_Strip_Output'])
    self._init_cond_file = os.path.join(self._test_directory, self._test_dict['Files']['Initial_Cond_File'])
    self._inst_map_file = os.path.join(self._test_directory, self._test_dict['Files']['Instrument_Map_File'])
    self._measured_data_quality = os.path.join(self._test_directory, self._test_dict['Files']['Measured_Data_Quality'])
    self._measured_data_trend = os.path.join(self._test_directory, self._test_dict['Files']['Measured_Data_Trend'])
    self._generate_list_of_replecements = self.GenerateListofReplacements()
    self._check_if_channels_are_in_file = self.CheckChannelsinFile()
    self._write_input_file = self.WriteInputFile()
    self._write_strip_file = self.WriteStripFile()
    self._make_plots = self._test_dict['Actions']['Figures']['make_plots']
    self._allPlots = self._test_dict['Actions']['Figures']['allPlots']
    self._printTitles = self._test_dict['Actions']['Figures']['printTitles']
    self._print_value_tables = self._test_dict['Actions']['Figures']['print_value_tables']
    
    self._test_function = self.MakePlotInstances()

  def GenerateListofReplacements(self):
    if self._subanalysis_dict[self._test_name]['Actions']['generate_list_of_replecements'] is True:
      varlist = []
      with open(self._r5_template_file) as R5in:
        for l in R5in:
          if "$" in l:
            for elem in l.split():
              if "$" in elem:
                varlist.append(elem)
      with open(self._init_cond_file,'w') as VLin:
        VLin.write("RELAP_channel,Source_formula\n")
        for elem in varlist:
          print(elem)
          VLin.write(elem[1:] + '\n')

  # check_if_channels_are_in_file
  # ----------------------------------------------------------------
  # This checks if the instruments listed in the mapping are in the data output file.
  # It also indicates if instruments in the data file are not in the mapping.
  # It also indicates which RELAP channels in the input are in the mapping and which are not
  def CheckChannelsinFile(self):
    if self._subanalysis_dict[self._test_name]['Actions']['check_if_channels_are_in_file']:
      R5vars = pd.read_csv(self._init_cond_file)
      instruments = pd.read_csv(self._inst_map_file, encoding = "UTF-8")
      # drop empty lines (rows)
      instruments.dropna(subset=['Tag_Number'], inplace=True)
      Measured = pd.read_csv(self._measured_data_trend, encoding = "UTF-8")

      # Instruments listed in self._inst_map_file in Measured data?
      number_of_instruments_in_data = len(Measured.columns.intersection(instruments['Tag_Number']))
      #print('Number of instruments in map file: ' + str(len(instruments['Tag_Number'])))
      #print('Number of measurements in data file: ' + str(len(Measured.columns)))
      #print('Number of instruments in map available in data: ' + str(number_of_instruments_in_data))
      #print('List of instruments (in map) NOT in data: ')
      printcount = 0
      totcount = 0
      for elem in instruments['Tag_Number']:  # .difference(Measured.columns):
        if elem not in Measured.columns:
          #print(elem, end=' ')
          printcount += 1
          totcount += 1
          if printcount == 10:
            #print(' ')
            printcount = 0
      #print('\nNumber of instruments (in map) NOT in data: ' + str(totcount))
      
      #print('List of data NOT in instrument map: ' )
      printcount = 0
      totcount = 0
      for elem in Measured.columns.difference(instruments['Tag_Number']):
    #    if elem not in instruments['Tag_Number'][:]:
        #print(elem, end=' ')
        printcount += 1
        totcount += 1
        if printcount == 10:
          #print(' ')
          printcount = 0
      print('\nNumber of data NOT in instrument map: ' + str(totcount))

  def WriteInputFile(self):
    # write_input_file
    # ----------------------------------------------------------------
    # This writes the RELAP5 input file
    # 1. Reads the RELAP5 template input file and identifies initial and boundary conditions to be replaced 
    # 2. Reads the test data file and identifies the data to be put in the RELAP5 input file
    if self._subanalysis_dict[self._test_name]['Actions']['write_input_file']:
      # Read RELAP input file and get list of variables to be replaced
      # This is also the template file for replacements

      # INSERT INITIAL CONDITIONS
      # = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
      #print("Treating initial conditions")
      #print("==========================================")
      varlist = []
      with open(self._r5_template_file) as R5in:
        R5temp = string.Template(R5in.read())
        R5in.seek(0) # rewind the file
        for l in R5in:
          if "$" in l:
            for elem in l.split():
              if "$" in elem:
                varlist.append(elem.split('$')[-1])
      # Read data file
      Measured = pd.read_csv(self._measured_data_quality)
      # Read mapping (RELAP input channel to Measured data instrument)
      Mapping = pd.read_csv(self._init_cond_file)
      #print(Mapping)
      # Generate the dict with the mappings (the actual numbers to be placed in the RELAP input)
      Mappingdict = {}
      for to_be_replaced in varlist: 
        # find the replacement rule in the mapping file
        #print(to_be_replaced)
        # check if the variable in the RELAP input has a mapping rule
        if to_be_replaced not in Mapping.RELAP_channel.values:
          #print("For the variable on the line above, there is no rule in " + IInitial_Cond_File )
          quit()
        print(to_be_replaced)
        rep_rule = Mapping.loc[Mapping['RELAP_channel'] == to_be_replaced, 'Source_formula'].iloc[0] 
        # find needed data in Measured data
        MyVars_in_formula = {}
        for look_for_this in re.findall(r'\w\w\d\d\d\d' ,rep_rule):
          print(look_for_this)
          look_for_this.strip()
          # already found? Formulas may use the same variable multiple times
          if look_for_this in MyVars_in_formula:
            continue
          look_for_this_in_data = look_for_this[:2] + '-' + look_for_this[2:]    
          # check if needed data is in Measured values
          if look_for_this_in_data not in Measured.columns:
            print("For the variable on the line above, the requested Measured value " + look_for_this_in_data + " is not in Measured data!")
            quit()

          data_point =  Measured.loc[Measured['Run_Time'] == self._initial_condition, look_for_this_in_data].iloc[0]
          MyVars_in_formula[look_for_this] = data_point

        # evaluate folmula
        Mappingdict[to_be_replaced] = eval(rep_rule, MyVars_in_formula)

      # Substitute values
      R5outTxt = R5temp.substitute(Mappingdict) 

      # INSERT BOUNDARY CONDITIONS
      # = = = = = = = = = = = = = = = = = = = = = = = = = = = = 
      #print("Treating boundary conditions")
      #print("==========================================")

      # Heater powers
      Heaters_used = [4]
      # The heaters have been renumbered between the creation of the input deck and the test
      # new to old number
      # new number      1  2   3  4  5  6  7  8  9  10
      heater_corr = [0, 1, 6, 10, 7, 3, 4, 8, 9, 5, 2] 
      #print("Updating heaters")
      #print("Used heatres specified in Heaters_used")
      count = 0
      for heater in range(10):
        print(heater)
        if (heater+1) in Heaters_used:
          #print("Updating heater " + str(heater+1))
          if heater+1 == 10:
            HeaterInstrumentNumber = '0'
          else:
            HeaterInstrumentNumber = str(heater+1)
          try:
            POW =  Measured['CT-10' + HeaterInstrumentNumber + '1'] * Measured['VT-10' + HeaterInstrumentNumber + '1'] + \
              Measured['CT-10' + HeaterInstrumentNumber + '2'] * Measured['VT-10' + HeaterInstrumentNumber + '2']
          except KeyError:
            POW = 0
          # Integrate Measured power 
          dt = Measured['Run_Time'].diff().fillna(0)
          oldval = 0.0
          val = []
          for newval in POW:
            #print('z')
            #print(newval)
            val.append((oldval + newval)/2) 
            oldval = newval

          POW_bits = val * dt
          # cumulative sum
          POW_integral = POW_bits.cumsum()

          # Smooth Measured data => Simple Moving Average (30min window, 3600pts 0.5sec each)
          POW_SMA = POW.rolling(window=3600).mean().fillna(0)
          # No SMA for the portion when the DCC starts
          anf = 0
          end = 10000
          count += 1
          print('**************************************')
          POW_SMA[anf:end] = POW[anf:end]

          #print(POW_SMA)
          print('Loop count is: %s' %count)
          print('**************************************')

          # Select 99 points for RELAP5: Not just random sampling, 
          #                              49 pts maximum change in slope (max gradient change), and 49 pts uniform 

          # 1. Compute second derivative of smoothened data
          dPOW_SMA = POW_SMA.diff().fillna(0)
          dPOW_SMA_dt = dPOW_SMA / dt

          ddPOW_SMA = dPOW_SMA_dt.diff().fillna(0)
          ddPOW_SMA_dt2 = ddPOW_SMA / dt

          # 2. Select (49 pts) biggest gradient change points
          sort_val = ddPOW_SMA_dt2.abs().sort_values(ascending=False)
          sort_val_indexes = sort_val[:48].index
          # 3. Add (49 pts) equally distibuted. The 49 max grad change points might be clustered in one region.
          sort_val_indexes = sort_val_indexes.append(pd.Index(np.linspace(0, len(Measured['Run_Time'])-1, 49).astype(int)))
          # 4. Grab the 98 selected points from SMA or directly  Measured data 
          Ntime = [0.0]
          Nval  = [POW[0]]
          for point in sort_val_indexes.sort_values():
            Ntime.append(Measured['Run_Time'][point])
            # zero power is zero power
            if POW[point] < 1000.0: # If Measured power is < 1kW, take that value insted of the SMA. This captures hearet on/off better
              if POW[point] < 0.0:  # No negative power
                Nval.append(0.0)
              else:
                Nval.append(POW[point])
            else:
              Nval.append(POW_SMA[point])
          Ntime = pd.Series(Ntime)
          Nval  = pd.Series(Nval)
          # 5. Renormalise new 98 pts Series to preserve original Integral.
          # Integrate re-sampled curve
          dt_resample = Ntime.diff().fillna(0)  
          oldval = 0.0
          val = []
          for newval in Nval:
            val.append((oldval + newval)/2) 
            oldval = newval

          Nval_bits = val * dt_resample
          # cumulative sum
          Nval_integral = Nval_bits.cumsum()
          # Scale it!
          Nval_scaling = POW_integral.iloc[-1] / Nval_integral.iloc[-1]
          Nval_scaled = Nval * Nval_scaling
          
          # 6. Write it into the RELAP5 input
          heaterString = "2029" + str(heater_corr[heater+1]).zfill(2) + "00  power\n"
          for i in range(len(Ntime)-1):
            heaterString = heaterString + "2029" + str(heater_corr[heater+1]).zfill(2) + str(i+1).zfill(2) + " " + str(Ntime[i+1]) + " " + str(Nval_scaled[i+1]) + "\n"
          R5outTxt = R5outTxt.replace("2029" + str(heater_corr[heater+1]).zfill(2) + "00  power\n"   ,heaterString)
        else:
          #print("Heater set to zero. Not in used heater list: " + str(heater+1))
          heaterString = "2029" + str(heater_corr[heater+1]).zfill(2) + "00  power\n2029" + str(heater_corr[heater+1]).zfill(2) + "01 0.0 0.0\n"
          R5outTxt = R5outTxt.replace("2029" + str(heater_corr[heater+1]).zfill(2) + "00  power\n"   ,heaterString)
      
      # Primary pressure 
      print("Updating primary and RCST pressures")
      Press_Prim =  Measured['PT-6001'] * 1000
      Press_RCST =  Measured['PT-4001'] * 1000

      dt = Measured['Run_Time'].diff().fillna(1)

      dPress_Prim = Press_Prim.diff().fillna(0)
      dPress_Prim_dt = dPress_Prim / dt
      ddPress_Prim = dPress_Prim_dt.diff().fillna(0)
      ddPress_Prim_dt2 = ddPress_Prim / dt

      dPress_RCST = Press_RCST.diff().fillna(0)
      dPress_RCST_dt = dPress_RCST / dt
      ddPress_RCST = dPress_RCST_dt.diff().fillna(0)
      ddPress_RCST_dt2 = ddPress_RCST / dt

      # Select points
      sort_val_Press_Prim = ddPress_Prim_dt2.abs().sort_values(ascending=False)
      sort_val_Press_RCST = ddPress_RCST_dt2.abs().sort_values(ascending=False)
      sort_val_indexes_Prim = sort_val_Press_Prim[:49].index
      sort_val_indexes_RCST = sort_val_Press_RCST[:49].index

      sort_val_indexes_Prim = sort_val_indexes_Prim.append(pd.Index(np.linspace(0, len(Measured['Run_Time'])-1, 47).astype(int)))
      #sort_val_indexes_Prim = sort_val_indexes_Prim.append(pd.Index([179950*2, 180100*2, 180300*2]))
      sort_val_indexes_RCST = sort_val_indexes_RCST.append(pd.Index(np.linspace(0, len(Measured['Run_Time'])-1, 47).astype(int)))
      #sort_val_indexes_RCST = sort_val_indexes_RCST.append(pd.Index([179950*2, 180100*2, 180300*2]))

      # Primary pressure
      Ntime = [0.0]
      Nval  = [0.0]
      for point in sort_val_indexes_Prim.sort_values():
      # Construct new Series
        Ntime.append(Measured['Run_Time'][point])
        Nval.append(Press_Prim[point])
      Ntime_Prim = pd.Series(Ntime)
      Nval_Prim  = pd.Series(Nval)
      Nval_Prim[0] = Nval_Prim[1]

      # RCST pressure
      Ntime = [0.0]
      Nval  = [0.0]
      for point in sort_val_indexes_RCST.sort_values():
        Ntime.append(Measured['Run_Time'][point])
        Nval.append(Press_RCST[point])
      Ntime_RCST = pd.Series(Ntime)
      Nval_RCST  = pd.Series(Nval)
      Nval_RCST[0] = Nval_RCST[1]

      # Write primary into relap input
      pressString = "20220000 reac-t\n"
      for i in range(len(Ntime_Prim)-1):
        pressString = pressString + "202200" + str(i+1).zfill(2) + " " + str(Ntime_Prim[i+1]) + " " + str(Nval_Prim[i+1]) + "\n"
      R5outTxt = R5outTxt.replace("20220000 reac-t\n" ,pressString)

      # Write RCST into relap input
      pressString = "20220100 reac-t\n"
      for i in range(len(Ntime_RCST)-1):
        pressString = pressString + "202201" + str(i+1).zfill(2) + " " + str(Ntime_RCST[i+1]) + " " + str(Nval_RCST[i+1]) + "\n"
      R5outTxt = R5outTxt.replace("20220100 reac-t\n" ,pressString)

      # RCCS BCs (inlet temperature and mass flow)
      print("Updating RCCS inlte temperature and mass flow")
      # Read Measured trend data
      Measured_trend = pd.read_csv(self._measured_data_trend)
      # MASS FLOW RATE
      RCCS_mDot =  Measured_trend['FT-9001'] / 60.0
      RCCS_mDot_SMA = RCCS_mDot.rolling(window=1800).mean().fillna(0)
      RCCS_mDot_SMA[RCCS_mDot_SMA < 0.0] = 0.0
      dt = Measured_trend['Run_Time'].diff().fillna(1)

      dRCCS_mDot = RCCS_mDot_SMA.diff().fillna(0)
      dRCCS_mDot_dt = dRCCS_mDot / dt
      ddRCCS_mDot = dRCCS_mDot_dt.diff().fillna(0)
      ddRCCS_mDot_dt2 = ddRCCS_mDot / dt

      # Select points
      sort_val_RCCS_mDot = ddRCCS_mDot_dt2.abs().sort_values(ascending=False)
      sort_val_indexes_RCCS_mDot = sort_val_RCCS_mDot[:49].index

      sort_val_indexes_RCCS_mDot = sort_val_indexes_RCCS_mDot.append(pd.Index(np.linspace(0, len(Measured_trend['Run_Time'])-1, 47).astype(int)))
      # RCCS m_dot
      Ntime = [0.0]
      Nval  = [0.0]
      for point in sort_val_indexes_RCCS_mDot.sort_values():
      # Construct new Series
        Ntime.append(Measured_trend['Run_Time'][point])
        Nval.append(RCCS_mDot_SMA[point])
      Ntime_RCCS_mDot = pd.Series(Ntime)
      Nval_RCCS_mDot  = pd.Series(Nval)
      Nval_RCCS_mDot[0] = Nval_RCCS_mDot[1]
      # Write primary into relap input
      pressStringR = "9200201  0.0  0.0  0.0  0.0\n"
      pressString = ""
      for i in range(len(Ntime_RCCS_mDot)-1):
        pressString = pressString + "92002" + str(i+1).zfill(2) + " " + str(Ntime_RCCS_mDot[i+1]) + " " + str(Nval_RCCS_mDot[i+1]) + " 0.0 0.0\n"
      R5outTxt = R5outTxt.replace(pressStringR ,pressString)
      # TEMPRATURE
      RCCS_T = Measured['TF-9003'] + 273.15
      RCCS_T_SMA = RCCS_T.rolling(window=1800).mean().fillna(0)
      RCCS_T_SMA[0:1800] = RCCS_T_SMA[1801]
      dt = Measured['Run_Time'].diff().fillna(1)

      dRCCS_T = RCCS_T_SMA.diff().fillna(0)
      dRCCS_T_dt = dRCCS_T / dt
      ddRCCS_T = dRCCS_T_dt.diff().fillna(0)
      ddRCCS_T_dt2 = ddRCCS_T / dt

      # Select points
      sort_val_RCCS_T = ddRCCS_T_dt2.abs().sort_values(ascending=False)
      sort_val_indexes_RCCS_T = sort_val_RCCS_T[:49].index

      sort_val_indexes_RCCS_T = sort_val_indexes_RCCS_T.append(pd.Index(np.linspace(0, len(Measured['Run_Time'])-1, 47).astype(int)))
      # RCCS T
      Ntime = [0.0]
      Nval  = [0.0]
      for point in sort_val_indexes_RCCS_T.sort_values():
      # Construct new Series
        Ntime.append(Measured['Run_Time'][point])
        Nval.append(RCCS_T_SMA[point])
      Ntime_RCCS_T = pd.Series(Ntime)
      Nval_RCCS_T = pd.Series(Nval)
      Nval_RCCS_T[0] = Nval_RCCS_T[1]
      # Write primary into relap input
      pressStringR = "9150201 0.0 0.0 0.0\n"
      pressString = ""
      for i in range(len(Ntime_RCCS_T)-1):
        pressString = pressString + "91502" + str(i+1).zfill(2) + " " + str(Ntime_RCCS_T[i+1]) + " 1.0e5 " + str(Nval_RCCS_T[i+1]) + "\n"
      R5outTxt = R5outTxt.replace(pressStringR ,pressString)

      # CORE DT
      Core_DT = Measured['TF-2311'] - Measured['TF-6101']
      Core_DT_SMA = Core_DT.rolling(window=1800).mean().fillna(0)
      Core_DT_SMA[0:1800] = Core_DT_SMA[1801]
      dt = Measured['Run_Time'].diff().fillna(1)

      dCore_DT = Core_DT_SMA.diff().fillna(0)
      dCore_DT_dt = dCore_DT / dt
      ddCore_DT = dCore_DT_dt.diff().fillna(0)
      ddCore_DT_dt2 = ddCore_DT / dt

      # Select points
      sort_val_Core_DT = ddCore_DT_dt2.abs().sort_values(ascending=False)
      sort_val_indexes_Core_DT = sort_val_Core_DT[:49].index

      sort_val_indexes_Core_DT = sort_val_indexes_Core_DT.append(pd.Index(np.linspace(0, len(Measured['Run_Time'])-1, 47).astype(int)))
      #sort_val_indexes_Core_DT = sort_val_indexes_Core_DT.append(pd.Index([179950*2, 180100*2]))
      # 
      Ntime = [0.0]
      Nval  = [0.0]
      for point in sort_val_indexes_Core_DT.sort_values():
      # Construct new Series
        Ntime.append(Measured['Run_Time'][point])
        Nval.append(Core_DT_SMA[point])
      Ntime_Core_DT = pd.Series(Ntime)
      Nval_Core_DT  = pd.Series(Nval)
      Nval_Core_DT[0] = Nval_Core_DT[1]
      # Write into relap input
      pressStringR = "20222000 reac-t\n"
      pressString = pressStringR
      for i in range(len(Ntime_Core_DT)-1):
        pressString = pressString + "202220" + str(i+1).zfill(2) + " " + str(Ntime_Core_DT[i+1]) + " " + str(Nval_Core_DT[i+1]) + "\n"
      R5outTxt = R5outTxt.replace(pressStringR ,pressString)

      # CORE inlet temperature
      Core_T = Measured['TF-6202'] + 273.15
      Core_T_SMA = Core_T.rolling(window=1800).mean().fillna(0)
      Core_T_SMA[0:1800] = Core_T_SMA[1801]
      dt = Measured['Run_Time'].diff().fillna(1)

      dCore_T = Core_T_SMA.diff().fillna(0)
      dCore_T_dt = dCore_T / dt
      ddCore_T = dCore_T_dt.diff().fillna(0)
      ddCore_T_dt2 = ddCore_T / dt

      # Select points
      sort_val_Core_T = ddCore_T_dt2.abs().sort_values(ascending=False)
      sort_val_indexes_Core_T = sort_val_Core_T[:49].index

      sort_val_indexes_Core_T = sort_val_indexes_Core_T.append(pd.Index(np.linspace(0, len(Measured['Run_Time'])-1, 47).astype(int)))
      # 
      Ntime = [0.0]
      Nval  = [0.0]
      for point in sort_val_indexes_Core_T.sort_values():
      # Construct new Series
        Ntime.append(Measured['Run_Time'][point])
        Nval.append(Core_T_SMA[point])
      Ntime_Core_T = pd.Series(Ntime)
      Nval_Core_T  = pd.Series(Nval)
      Nval_Core_T[0] = Nval_Core_T[1]
      # Write into relap input
      pressStringR = "20223000 reac-t\n"
      pressString = pressStringR
      for i in range(len(Ntime_Core_T)-1):
        pressString = pressString + "202230" + str(i+1).zfill(2) + " " + str(Ntime_Core_T[i+1]) + " " + str(Nval_Core_T[i+1]) + "\n"
      R5outTxt = R5outTxt.replace(pressStringR ,pressString)

      # write the output file back
      with open(self._r5_filled_file, 'w') as R5out:
        R5out.write(R5outTxt)

  def WriteStripFile(self):
      # # write_strip_file
    # ----------------------------------------------------------------
    # This writes a RELAP strip file to extract the needed data from the 
    #    RELAP binary output file
    # 1. Read the HTTF instrunments vs. RELAP5 channels mapping file
    # 2. Extract all needed RELAP5 channels and write RELAp strip file
    if self._subanalysis_dict[self._test_name]['Actions']['write_strip_file']:
      # Read mapping file
      instruments = pd.read_csv(self._inst_map_file)
      # drop empty lines (rows)
      instruments.dropna(subset=['Tag_Number'], inplace=True)

      # Create list with RELAP channels (no duplicates)
      RELAP_variable_list = []
      for instrument in instruments['RELAP5_Model_Parameters']:
        # No RELAP channels for this instrument
        if pd.isnull(instrument):
          continue

        # There might be more than one RELAP channel per instrument
        for inst in instrument.split(','):
          if inst in RELAP_variable_list:
            continue
          RELAP_variable_list.append(inst.strip())

      # Write Strip file
      with open(self._r5_strip_input, 'w') as R5strip:
        R5strip.write('=CSV strip input for HTTF\n* Strip the needed data into a CSV\n100 strip fmtout\n103 0 binary plotfl\n104 csv\n*\n* Variables\n')
        counter = 1001
        for inst in RELAP_variable_list:
          R5strip.write(str(counter) + ' ' + inst.split('-')[0] + ' ' + inst.split('-')[1] + '\n')
          counter += 1
        R5strip.write('.\n')
    pass

  def MakePlotInstances(self):
    for instance in self._test_dict['Actions']['Figures']['Instance']:
        PlotInstance = Plots(self._test_dict['Actions']['Figures']['Instance'][instance])
        for i, _ in enumerate(PlotInstance._instruments):
          pass
        #print(PlotInstance._instruments)
    print('z')

  def MakePlots(self):
      # # make_plots
    # ----------------------------------------------------------------
    # This makes plots with Measured data and corresponding RELAP5 results
    # 1. Read the HTTF instrunments vs. RELAP5 channels mapping file
    # 2. Make a plot for each HTTF instrument 

    if self._make_plots:
      # Set some global stuff for the plots
      # - - - - - - - - - - - - - - - - - - - - - -
      plt.rcParams.update({'figure.max_open_warning': 0})

      font = {'family'  : 'sans-serif',
              'style'   : 'normal',
              'variant' : 'normal',
              'weight'  : 'normal',
              'size'    :  20}
              # was        12
      plt.rc('font', **font)

      # was 9
      lfontsize= 13
      lfontsizeSmall= 11

      # end time is 262707.0
      xlimites1 = [0.0, 262700.0]
      #xlimites1 = [0, 31536000]

      #figuresize
      figA = 10
      figB = 5

      # boreders
      BorderBot = 0.15
      BorderRig = 0.975
      BorderTop = 0.94

      mymarkers = {'Measured': 'g>-', 'Average': 'b<-'}
    #  mylables = {'20kW_6000CFM': '20kW 2000CFM', '40kW_6000CFM': '40kW 6000CFM', '60kW_6000CFM': '60kW 6000CFM'}
      instr_units = {'TS': ['Temperature [K]', 1.0, 273.15], 'TF': ['Temperature [K]', 1.0, 273.15], 'GC': ['Quality []', 0.01, 0.0],
                     'DP': ['Pressure [Pa]', 1000.0, 0.0], 'PT': ['Pressure [Pa]', 1000.0, 0.0], 'LF': ['Level [%]', 1.0, 0.0], 'FT': ['Vol. flow [m3/s]', 1.66667e-5, 0.0], 
                     'OA': ['O2 [ppm] -> TBD', 1.0, 0.0], 'KW': ['TBD', 1.0, 0.0], 'CV': ['Opening fraction []', 0.01, 0.0], 'MS': ['Speed fraction []', 0.01, 0.0],
                     'HO': ['Power [W]', 1000.0, 0.0], 'SV': ['TBD', 1.0, 0.0], 'ME': ['TBD', 1.0, 0.0], 'CR': ['TBD', 1.0, 0.0], 'ES': ['TBD', 1.0, 0.0],
                     'PL': ['TBD', 1.0, 0.0], 'LL': ['TBD', 1.0, 0.0], 'OT': ['TBD', 1.0, 0.0], 'MF': ['TBD', 1.0, 0.0], 'MC': ['TBD', 1.0, 0.0]}

      #fixy = True
      savefigures = True
      # - - - - - - - - - - - - - - - - - - - - - -
      # Make the plots 
      # - - - - - - - - - - - - - - - - - - - - - -

      # Read mapping file
      instruments = pd.read_csv(self._inst_map_file)
      # drop empty lines (rows)
      instruments.dropna(subset=['Tag_Number'], inplace=True)

      # Read Measured quality data file
      Measured = pd.read_csv(self._measured_data_quality)
      # Read Measured trend data
      Measured_trend = pd.read_csv(self._measured_data_trend)

      # Read RELAP5 output data
      # -----------------------------------
      # Reformat RELAP output so that is can be read by pd.read_csv
      fout = open("tempout.csv", "w")
      mytemp = ""
      mytempplotnum = ""
      with open(self._r5_strip_output) as fp:
        count = 0
        start = False
        plotnum_treatment = False
        for l in fp:
          count += 1
          if 'plotinf' in l:
            start = True
            #print(l)
          if 'plotnum' in l:
            plotnum_treatment = True 
          if 'plotrec' in l:
            if plotnum_treatment:
              # we create the header line for the csv file
              mytempsplit = mytemp.split(',')
              mytempplotnum = mytempplotnum.split(',')
              mytemp = ""
              for alf, num in zip(mytempsplit, mytempplotnum):
                mytemp = mytemp + alf.strip() + '-' + num.strip() + ', '  
              plotnum_treatment = False

            fout.write(mytemp + '\n')
            mytemp = ""
          if start & (count > 3):
            if plotnum_treatment:
              mytempplotnum = mytempplotnum + l.rstrip()
              print(mytempplotnum)
            else:
              mytemp = mytemp + l.rstrip()
        # write last line
        fout.write(mytemp + '\n')
      fout.close()

      # read the formatted data into pandas dataframe
      R5data = pd.read_csv('tempout.csv')
      #os.remove('tempout.csv')
      # remove whitespaces in colum names 
      R5data.rename(columns=lambda x: x.strip(), inplace=True)

      # make a plot for each instrument
      if self._allPlots:
        for instrument in instruments['Tag_Number']:
          print(instrument)

          # units and unit conversion
          instr_identifier = instrument[:2]
          print("Units: " + instr_units[instr_identifier][0])
          print("Unit conversion: RELAP = HTTF * mult + add"  )
          print("mult : " + str(instr_units[instr_identifier][1]))
          print("add  : " + str(instr_units[instr_identifier][2]))

          # check if instrumet has Measured data recorded
          if instrument not in Measured:
            print("Not in Measured Data.. skipping..")
            continue
          
          # check if this instrument has relap channels associated
          R5channels = instruments.loc[instruments['Tag_Number']==instrument, 'RELAP5_Model_Parameters'].iloc[0]
          if R5channels == '' or pd.isnull(R5channels):
            print("For this instrument, no Relap channes are associated.. skipping.. ")
            continue
          R5channels = [i.strip() for i in R5channels.split(',')]

          # make plot
          fig = plt.figure(figsize=(figA,figB))
          ax = fig.add_subplot(111)
          # plot the Measured data
          scat = plt.plot(Measured['Run_Time'], Measured[instrument] * instr_units[instr_identifier][1] + instr_units[instr_identifier][2], mymarkers['Measured'], markevery=13000, label=instrument, markersize=10)
          # plot the RELAP channels
          for R5chan in  R5channels:
            # check if this is in RELAP outputs
            if R5chan not in R5data:
              print(R5chan + " not in Relap output file?")
              print("This should not happen... unpade instrument map, rerun write_strip_file and StripAll.sh")
              quit()
            scat = plt.plot(R5data['time-0'], R5data[R5chan], markevery=200, label=R5chan, markersize=10)
          # plot average of channels
          scat = plt.plot(R5data['time-0'], R5data[R5channels].mean(axis=1), mymarkers['Average'], markevery=200, label="RELAP average", markersize=10)

          labx = plt.xlabel('Time [s]')
          laby = plt.ylabel(instr_units[instr_identifier][0])
    #  title = plt.title("Case 0 RO split " + plots)
    #  ax2 = ax.twinx()
    #  scat4 = ax2.plot(mydata[plots][1:,Time], mydata[plots][1:,Y_WRF_electricity_0], 'kp', label='WRF elctricity usage')
    #  laby = ax2.set_ylabel('kWh')
          xlim = plt.xlim(xlimites1)
            #lns = scat1 + scat2 + scat3 + scat4
            #labs = [l.get_label() for l in lns]
            #ax.legend(lns, labs, loc='best')
          leg = ax.legend(loc='best', fontsize=lfontsize)
          if savefigures == True:
            fig.savefig(path + '/Plots/' + instrument + '.png')

      # Make some production plots
      # ==========================================================
      print("PRODUCTION PLOTS")
      print("==============================")

      #print(R5data)

      # Initialise dictionalries for Table outputs
      C = {} # Calcaulted values
      C['SST'] = {}
      C['MAX'] = {}
      C['DCC'] = {}
      for k in C.keys():
        C[k]['TOP'] = {}
        C[k]['MID'] = {}
        C[k]['LOW'] = {}
        for kk in C[k].keys():
          C[k][kk]['RI'] = np.zeros(2)
          C[k][kk]['FU'] = np.zeros(2)
          C[k][kk]['RO'] = np.zeros(2)

      E = {} # Experimental values
      E['SST'] = {}
      E['MAX'] = {}
      E['DCC'] = {}
      for k in C.keys():
        E[k]['TOP'] = {}
        E[k]['MID'] = {}
        E[k]['LOW'] = {}
        for kk in C[k].keys():
          E[k][kk]['RI'] = np.zeros(2)
          E[k][kk]['FU'] = np.zeros(2)
          E[k][kk]['RO'] = np.zeros(2)

      # Primary fluid inlet temps
      # = = = = = = = = = = = = = = = = = = = = = = = =
      print("Primary fluid inlet temp")
      fig = plt.figure(figsize=(figA,figB))
      ax = fig.add_subplot(111)
      # plot the Measured data
      scat = plt.plot(Measured['Run_Time'], Measured['TF-6101'] + 273.15, 'g>-', markevery=13000, label="TF-6101 Lower cold duct", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['TF-6102'] + 273.15, 'rs-' , markevery=13000, label="TF-6102 Upper cold duct", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['TF-7201'] + 273.15, 'bo-' , markevery=13000, label="TF-7201 Lower riser", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured[['TF-8201', 'TF-8202', 'TF-8203', 'TF-8204', 'TF-8206', 'TF-8207', 'TF-8208', 'TF-8209', 'TF-8210', 'TF-8211', 'TF-8212', 'TF-8102', 'TF-8103', 'TF-8105', 'TF-8107', 'TF-8108', 'TF-8109', 'TF-8110', 'TF-8111', 'TF-8112']].mean(axis=1) + 273.15, 'c4-' , markevery=13000, label="TF-8xxx Upper plenum avg.", markersize=10)
    #  scat = plt.plot(Measured['Run_Time'], Measured[['TF-8201', 'TF-8202', 'TF-8203', 'TF-8204', 'TF-8206', 'TF-8207', 'TF-8208', 'TF-8209', 'TF-8210', 'TF-8211', 'TF-8212', 'TF-8102', 'TF-8103', 'TF-8105', 'TF-8107', 'TF-8108', 'TF-8109', 'TF-8110', 'TF-8111', 'TF-8112']].max(axis=1) + 273.15, 'y>-' , markevery=13000, label="TF-8xxx Upper plenum max.", markersize=10)
    #  scat = plt.plot(Measured['Run_Time'], Measured[['TF-8201', 'TF-8202', 'TF-8203', 'TF-8204', 'TF-8206', 'TF-8207', 'TF-8208', 'TF-8209', 'TF-8210', 'TF-8211', 'TF-8212', 'TF-8102', 'TF-8103', 'TF-8105', 'TF-8107', 'TF-8108', 'TF-8109', 'TF-8110', 'TF-8111', 'TF-8112']].min(axis=1) + 273.15, 'k>-' , markevery=13000, label="TF-8xxx Upper plenum min.", markersize=10)
      # plot the RELAP channels
      scat = plt.plot(R5data['time-0'], R5data['tempg-270040000'], 'k>-', markevery=200, label="tempg-270040000 Cold duct", markersize=10)
      scat = plt.plot(R5data['time-0'], R5data['tempg-115040000'], 'ks-', markevery=200, label="tempg-115040000 Lower riser", markersize=10)
      scat = plt.plot(R5data['time-0'], R5data['tempg-120010000'], 'ko-', markevery=200, label="tempg-120010000 Upper plenum", markersize=10)

      labx = plt.xlabel('Time [s]')
      laby = plt.ylabel("Temperature [K]")
      if self._print_value_tables:
        title = plt.title("Core inlet Helium temperature")
      else:
        fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
      xlim = plt.xlim(xlimites1)
      ylim = plt.ylim([250.0, 750.0])
      leg = ax.legend(loc='best', fontsize=lfontsize)
      if savefigures == True:
        fig.savefig(path + '/Plots/' + 'Prod_TempHE_core_inlet.png')

      # Primary fluid/solid core TOP (Block 7) 
      # = = = = = = = = = = = = = = = = = = = = = = = =
      print("Primary fluid core TOP")
      fig = plt.figure(figsize=(figA,figB))
      ax = fig.add_subplot(111)
      # plot the Measured data
      scat = plt.plot(Measured['Run_Time'], Measured['TF-1704'] + 273.15, 'g>-', markevery=13000, label="TF-1704 Block 7, Inner Fuel, Sect 1", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['TF-1718'] + 273.15, 'r>-', markevery=13000, label="TF-1718 Block 7, Inner Fuel, Sect 2", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['TF-1732'] + 273.15, 'b>-', markevery=13000, label="TF-1732 Block 7, Inner Fuel, Sect 3", markersize=10)
    #  scat = plt.plot(Measured['Run_Time'], Measured[['TF-1704', 'TF-1718', 'TF-1732']].mean(axis=1) + 273.15, 'm>-', markevery=13000, label="TF-17xx Block 7, Inner Fuel, avg", markersize=10)
    #  scat = plt.plot(Measured['Run_Time'], Measured['TF-1706'] + 273.15, 'g<-', markevery=13000, label="TF-1706 Block 7, Middle Fuel, Sect 1", markersize=10)
    #  scat = plt.plot(Measured['Run_Time'], Measured['TF-1720'] + 273.15, 'r<-', markevery=13000, label="TF-1720 Block 7, Middle Fuel, Sect 2", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['TF-1734'] + 273.15, 'bs-', markevery=13000, label="TF-1734 Block 7, Middle Fuel, Sect 3", markersize=10)
    #  scat = plt.plot(Measured['Run_Time'], Measured[['TF-1734']].mean(axis=1) + 273.15, 'm<-', markevery=13000, label="TF-17xx Block 7, Middle Fuel, avg", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['TF-1708'] + 273.15, 'go-', markevery=13000, label="TF-1708 Block 7, Outer Fuel, Sect 1", markersize=10)
    #  scat = plt.plot(Measured['Run_Time'], Measured['TF-1722'] + 273.15, 'ro-', markevery=13000, label="TF-1722 Block 7, Outer Fuel, Sect 2", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['TF-1736'] + 273.15, 'bo-', markevery=13000, label="TF-1736 Block 7, Outer Fuel, Sect 3", markersize=10)
    #  scat = plt.plot(Measured['Run_Time'], Measured[['TF-1708', 'TF-1736']].mean(axis=1) + 273.15, 'mo-', markevery=13000, label="TF-17xx Block 7, Outer Fuel, avg", markersize=10)
      # plot the RELAP channels
      scat = plt.plot(R5data['time-0'], R5data['tempg-140060000'], 'k>-', markevery=200, label="tempg-140060000 Block 7, Inner Fuel", markersize=10)
      scat = plt.plot(R5data['time-0'], R5data['tempg-145060000'], 'ks-', markevery=200, label="tempg-145060000 Block 7, Middle Fuel", markersize=10)
      scat = plt.plot(R5data['time-0'], R5data['tempg-150060000'], 'ko-', markevery=200, label="tempg-150060000 Block 7, Outer Fuel", markersize=10)

      labx = plt.xlabel('Time [s]')
      laby = plt.ylabel("Temperature [K]")
      if self._print_value_tables:
        title = plt.title("Core Block 7 TOP Helium temperatures")
      else:
        fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
      xlim = plt.xlim(xlimites1)
      ylim = plt.ylim([200.0, 1800.0])
      ytcs = ax.set_yticks([200.0, 600.0, 1000.0, 1400.0, 1800.0 ])
      leg = ax.legend(loc='best', fontsize=lfontsizeSmall)
      if savefigures == True:
        fig.savefig(path + '/Plots/' + 'Prod_TempHE_core_TOP.png')

      print("Primary solid core TOP inner refl")
      fig = plt.figure(figsize=(figA,figB))
      ax = fig.add_subplot(111)
      # plot the Measured data
      scat = plt.plot(Measured['Run_Time'], Measured['TS-1701'] + 273.15, 'g>-', markevery=13000, label="TS-1701 Block 7, Central Refl Inner", markersize=10)
    #  scat = plt.plot(Measured['Run_Time'], Measured['TS-1730'] + 273.15, 'r>-', markevery=13000, label="TS-1730 Block 7, Central Refl Middle", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['TS-1702'] + 273.15, 'bo-', markevery=13000, label="TS-1702 Block 7, Central Refl Outer", markersize=10)
      # plot the RELAP channels
      scat = plt.plot(R5data['time-0'], R5data['httemp-130000601'], 'k>-', markevery=200, label="httemp-130000601 Block 7, Central Refl Inner", markersize=10)
      scat = plt.plot(R5data['time-0'], R5data['htvat-1320006'], 'ks-', markevery=200, label="htvat-1320006 Block 7, Central Refl Middle", markersize=10)
      scat = plt.plot(R5data['time-0'], R5data['htvat-1340006'], 'ko-', markevery=200, label="htvat-1340006 Block 7, Central Refl Outer", markersize=10)

      labx = plt.xlabel('Time [s]')
      laby = plt.ylabel("Temperature [K]")
      if self._print_value_tables:
        title = plt.title("Core Block 7 TOP Solid temperatures Inner Refl.")
      else:
        fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
      xlim = plt.xlim(xlimites1)
      ylim = plt.ylim([200.0, 1800.0])
      ytcs = ax.set_yticks([200.0, 600.0, 1000.0, 1400.0, 1800.0 ])
      leg = ax.legend(loc='best', fontsize=lfontsize)
      if savefigures == True:
        fig.savefig(path + '/Plots/' + 'Prod_TempSOLID_core_TOPInnerRefl.png')

      # Get table data
      CIndex = R5data['time-0'].iloc[(R5data['time-0'] - runtime_for_initial_cond).abs().argsort()[:2]].index[0]
      C['SST']['TOP']['RI'][0] = R5data['httemp-130000601'][CIndex]
      C['SST']['TOP']['RI'][1] = R5data['htvat-1340006'][CIndex]
      C['MAX']['TOP']['RI'][0] = R5data['httemp-130000601'].max()
      C['MAX']['TOP']['RI'][1] = R5data['htvat-1340006'].max()
      C['DCC']['TOP']['RI'][0] = C['MAX']['TOP']['RI'][0] - R5data['httemp-130000601'].iloc[-1]
      C['DCC']['TOP']['RI'][1] = C['MAX']['TOP']['RI'][1] - R5data['htvat-1340006'].iloc[-1]
      EIndex = Measured['Run_Time'].iloc[(Measured['Run_Time'] - runtime_for_initial_cond).abs().argsort()[:2]].index[0]
      E['SST']['TOP']['RI'][0] = Measured['TS-1701'][EIndex] + 273.15
      E['SST']['TOP']['RI'][1] = Measured['TS-1702'][EIndex] + 273.15
      E['MAX']['TOP']['RI'][0] = Measured['TS-1701'].max() + 273.15
      E['MAX']['TOP']['RI'][1] = Measured['TS-1702'].max() + 273.15
      E['DCC']['TOP']['RI'][0] = E['MAX']['TOP']['RI'][0] - (Measured['TS-1701'].iloc[-1] + 273.15)
      E['DCC']['TOP']['RI'][1] = E['MAX']['TOP']['RI'][1] - (Measured['TS-1702'].iloc[-1] + 273.15)

      print("Primary solid core TOP fuel")
      fig = plt.figure(figsize=(figA,figB))
      ax = fig.add_subplot(111)
      # plot the Measured data
      scat = plt.plot(Measured['Run_Time'], Measured[['TS-1703', 'TS-1717', 'TS-1731']].mean(axis=1) + 273.15, 'g>-', markevery=13000, label="TS-17xx block 7, inner fuel, sector avg", markersize=10)
    #  scat = plt.plot(Measured['Run_Time'], Measured[['TS-1711', 'TS-1725', 'TS-1739']].mean(axis=1) + 273.15, 'g<-', markevery=13000, label="TS-17xx block 7, inner fuel pin, sect avg", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured[['TS-1705', 'TS-1719', 'TS-1733']].mean(axis=1) + 273.15, 'rs-', markevery=13000, label="TS-17xx block 7, middle fuel, sect avg", markersize=10)
    #  scat = plt.plot(Measured['Run_Time'], Measured['TS-1740'] + 273.15, 'b<-', markevery=13000, label="TS-1740 block 7, middle fuel pin, sect 3", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured[['TS-1735', 'TS-1707']].mean(axis=1) + 273.15, 'bo-', markevery=13000, label="TS-17xx block 7, outer fuel, sect avg", markersize=10)
    #  scat = plt.plot(Measured['Run_Time'], Measured[['TS-1712']].mean(axis=1) + 273.15, 'go-', markevery=13000, label="TS-17xx block 7, outer fuel pin, sect avg", markersize=10)
      # plot the relap channels
      scat = plt.plot(R5data['time-0'], R5data['htvat-1401004'], 'k>-', markevery=200, label="htvat-1401004 block 7, inner fuel", markersize=10)
    #  scat = plt.plot(R5data['time-0'], R5data['httemp-140300401'], 'kp-', markevery=200, label="httemp-140300401 block 7, inner fuel pin", markersize=10)
      scat = plt.plot(R5data['time-0'], R5data['htvat-1451004'], 'ks-', markevery=200, label="htvat-1451004 block 7, middle fuel", markersize=10)
    #  scat = plt.plot(R5data['time-0'], R5data['httemp-145300501'], 'kd-', markevery=200, label="httemp-145300501 block 7, middle fuel pin", markersize=10)
      scat = plt.plot(R5data['time-0'], R5data['htvat-1501004'], 'ko-', markevery=200, label=" htvat-1501004 block 7, outer fuel", markersize=10)
    #  scat = plt.plot(R5data['time-0'], R5data['httemp-150300401'], 'kh-', markevery=200, label="httemp-150300401 block 7, outer fuel pin", markersize=10)

      labx = plt.xlabel('Time [s]')
      laby = plt.ylabel("Temperature [k]")
      if self._print_value_tables:
        title = plt.title("Core Block 7 TOP Solid temperatures Fuel")
      else:
        fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
      xlim = plt.xlim(xlimites1)
      ylim = plt.ylim([200.0, 1800.0])
      ytcs = ax.set_yticks([200.0, 600.0, 1000.0, 1400.0, 1800.0 ])
      leg = ax.legend(loc='best', fontsize=lfontsize)
      if savefigures == True:
        fig.savefig(path + '/Plots/' + 'Prod_tempSOLID_core_TOPFuel.png')

      # Get table data
      CIndex = R5data['time-0'].iloc[(R5data['time-0'] - runtime_for_initial_cond).abs().argsort()[:2]].index[0]
      C['SST']['TOP']['FU'][0] = R5data['htvat-1401004'][CIndex]
      C['SST']['TOP']['FU'][1] = R5data['htvat-1501004'][CIndex]
      C['MAX']['TOP']['FU'][0] = R5data['htvat-1401004'].max()
      C['MAX']['TOP']['FU'][1] = R5data['htvat-1501004'].max()
      C['DCC']['TOP']['FU'][0] = C['MAX']['TOP']['FU'][0] - R5data['htvat-1401004'].iloc[-1]
      C['DCC']['TOP']['FU'][1] = C['MAX']['TOP']['FU'][1] - R5data['htvat-1501004'].iloc[-1]
      EIndex = Measured['Run_Time'].iloc[(Measured['Run_Time'] - runtime_for_initial_cond).abs().argsort()[:2]].index[0]
      E['SST']['TOP']['FU'][0] = Measured[['TS-1703', 'TS-1717', 'TS-1731']].mean(axis=1)[EIndex] + 273.15
      E['SST']['TOP']['FU'][1] = Measured[['TS-1735', 'TS-1707']].mean(axis=1)[EIndex] + 273.15
      E['MAX']['TOP']['FU'][0] = Measured[['TS-1703', 'TS-1717', 'TS-1731']].mean(axis=1).max() + 273.15
      E['MAX']['TOP']['FU'][1] = Measured[['TS-1735', 'TS-1707']].mean(axis=1).max() + 273.15
      E['DCC']['TOP']['FU'][0] = E['MAX']['TOP']['FU'][0] - (Measured[['TS-1703', 'TS-1717', 'TS-1731']].mean(axis=1).iloc[-1] + 273.15)
      E['DCC']['TOP']['FU'][1] = E['MAX']['TOP']['FU'][1] - (Measured[['TS-1735', 'TS-1707']].mean(axis=1).iloc[-1] + 273.15)

      print("primary solid core TOP Outer Refl.")
      fig = plt.figure(figsize=(figA,figB))
      ax = fig.add_subplot(111)
      # plot the Measured data
      scat = plt.plot(Measured['Run_Time'], Measured[['TS-1709', 'TS-1723', 'TS-1737']].mean(axis=1) + 273.15, 'g>-', markevery=13000, label="TS-17xx block 7, side refl, sect avg", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured[['TS-1710', 'TS-1724', 'TS-1738']].mean(axis=1) + 273.15, 'rs-', markevery=13000, label="TS-17xx block 7, perm refl, sect avg", markersize=10)
      # plot the relap channels
      scat = plt.plot(R5data['time-0'], R5data['htvat-1600006'], 'k>-', markevery=200, label="htvat-1600006 block 7, side refl", markersize=10)
      scat = plt.plot(R5data['time-0'], R5data['htvat-1660006'], 'ks-', markevery=200, label="htvat-1660006 block 7, perm refl", markersize=10)

      labx = plt.xlabel('Time [s]')
      laby = plt.ylabel("Temperature [k]")
      if self._print_value_tables:
        title = plt.title("Core block 7 TOP Solid temperatures Outer Refl.")
      else:
        fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
      xlim = plt.xlim(xlimites1)
      ylim = plt.ylim([200.0, 1800.0])
      ytcs = ax.set_yticks([200.0, 600.0, 1000.0, 1400.0, 1800.0 ])
      leg = ax.legend(loc='best', fontsize=lfontsize)
      if savefigures == True:
        fig.savefig(path + '/Plots/' + 'Prod_tempSOLID_core_TOPOuterRefl.png')

      # Get table data
      CIndex = R5data['time-0'].iloc[(R5data['time-0'] - runtime_for_initial_cond).abs().argsort()[:2]].index[0]
      C['SST']['TOP']['RO'][0] = R5data['htvat-1600006'][CIndex]
      C['SST']['TOP']['RO'][1] = R5data['htvat-1660006'][CIndex]
      C['MAX']['TOP']['RO'][0] = R5data['htvat-1600006'].max()
      C['MAX']['TOP']['RO'][1] = R5data['htvat-1660006'].max()
      C['DCC']['TOP']['RO'][0] = C['MAX']['TOP']['RO'][0] - R5data['htvat-1600006'].iloc[-1]
      C['DCC']['TOP']['RO'][1] = C['MAX']['TOP']['RO'][1] - R5data['htvat-1660006'].iloc[-1]
      EIndex = Measured['Run_Time'].iloc[(Measured['Run_Time'] - runtime_for_initial_cond).abs().argsort()[:2]].index[0]
      E['SST']['TOP']['RO'][0] = Measured[['TS-1709', 'TS-1723', 'TS-1737']].mean(axis=1)[EIndex] + 273.15
      E['SST']['TOP']['RO'][1] = Measured[['TS-1710', 'TS-1724', 'TS-1738']].mean(axis=1)[EIndex] + 273.15
      E['MAX']['TOP']['RO'][0] = Measured[['TS-1709', 'TS-1723', 'TS-1737']].mean(axis=1).max() + 273.15
      E['MAX']['TOP']['RO'][1] = Measured[['TS-1710', 'TS-1724', 'TS-1738']].mean(axis=1).max() + 273.15
      E['DCC']['TOP']['RO'][0] = E['MAX']['TOP']['RO'][0] - (Measured[['TS-1709', 'TS-1723', 'TS-1737']].mean(axis=1).iloc[-1] + 273.15)
      E['DCC']['TOP']['RO'][1] = E['MAX']['TOP']['RO'][1] - (Measured[['TS-1710', 'TS-1724', 'TS-1738']].mean(axis=1).iloc[-1] + 273.15)

      # Primary fluid/solid core Middle (Block 5) 
      # = = = = = = = = = = = = = = = = = = = = = = = =
      print("Primary fluid core MID")
      fig = plt.figure(figsize=(figA,figB))
      ax = fig.add_subplot(111)
      # plot the Measured data
      scat = plt.plot(Measured['Run_Time'], Measured['TF-1504'] + 273.15, 'g>-', markevery=13000, label="TF-1504 Block 5, Inner Fuel, Sect 1", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['TF-1518'] + 273.15, 'r>-', markevery=13000, label="TF-1518 Block 5, Inner Fuel, Sect 2", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['TF-1532'] + 273.15, 'b>-', markevery=13000, label="TF-1532 Block 5, Inner Fuel, Sect 3", markersize=10)
    #  scat = plt.plot(Measured['Run_Time'], Measured[['TF-1504', 'TF-1518', 'TF-1532']].mean(axis=1) + 273.15, 'm>-', markevery=13000, label="TF-15xx Block 5, Inner Fuel, avg", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['TF-1506'] + 273.15, 'gs-', markevery=13000, label="TF-1506 Block 5, Middle Fuel, Sect 1", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['TF-1520'] + 273.15, 'rs-', markevery=13000, label="TF-1520 Block 5, Middle Fuel, Sect 2", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['TF-1534'] + 273.15, 'bs-', markevery=13000, label="TF-1534 Block 5, Middle Fuel, Sect 3", markersize=10)
    #  scat = plt.plot(Measured['Run_Time'], Measured[['TF-1506', 'TF-1520', 'TF-1534']].mean(axis=1) + 273.15, 'm<-', markevery=13000, label="TF-15xx Block 5, Middle Fuel, avg", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['TF-1508'] + 273.15, 'go-', markevery=13000, label="TF-1508 Block 5, Outer Fuel, Sect 1", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['TF-1522'] + 273.15, 'ro-', markevery=13000, label="TF-1522 Block 5, Outer Fuel, Sect 2", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['TF-1536'] + 273.15, 'bo-', markevery=13000, label="TF-1536 Block 5, Outer Fuel, Sect 3", markersize=10)
    #  scat = plt.plot(Measured['Run_Time'], Measured[['TF-1508', 'TF-1522', 'TF-1536']].mean(axis=1) + 273.15, 'mo-', markevery=13000, label="TF-15xx Block 5, Outer Fuel, avg", markersize=10)
      # plot the RELAP channels
      scat = plt.plot(R5data['time-0'], R5data['tempg-140080000'], 'k>-', markevery=200, label="tempg-140080000 Block 5, Inner Fuel", markersize=10)
      scat = plt.plot(R5data['time-0'], R5data['tempg-145080000'], 'ks-', markevery=200, label="tempg-145080000 Block 5, Middle Fuel", markersize=10)
      scat = plt.plot(R5data['time-0'], R5data['tempg-150080000'], 'ko-', markevery=200, label="tempg-150080000 Block 5, Outer Fuel", markersize=10)

      labx = plt.xlabel('Time [s]')
      laby = plt.ylabel("Temperature [K]")
      if self._print_value_tables:
        title = plt.title("Core Block 5 MID Helium temperatures")
      else:
        fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
      xlim = plt.xlim(xlimites1)
      ylim = plt.ylim([200.0, 1800.0])
      ytcs = ax.set_yticks([200.0, 600.0, 1000.0, 1400.0, 1800.0 ])
      leg = ax.legend(loc='best', fontsize=lfontsizeSmall)
      if savefigures == True:
        fig.savefig(path + '/Plots/' + 'Prod_TempHE_core_MID.png')

      print("Primary solid core MID inner refl")
      fig = plt.figure(figsize=(figA,figB))
      ax = fig.add_subplot(111)
      # plot the Measured data
      scat = plt.plot(Measured['Run_Time'], Measured['TS-1501'] + 273.15, 'g>-', markevery=13000, label="TS-1501 Block 5, Central Refl Inner", markersize=10)
    #  scat = plt.plot(Measured['Run_Time'], Measured['TS-1530'] + 273.15, 'r>-', markevery=13000, label="TS-1530 Block 5, Central Refl Middle", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['TS-1502'] + 273.15, 'bo-', markevery=13000, label="TS-1502 Block 5, Central Refl Outer", markersize=10)
      # plot the RELAP channels
      scat = plt.plot(R5data['time-0'], R5data['httemp-130000801'], 'k<-', markevery=200, label="httemp-130000801 Block 5, Central Refl Inner", markersize=10)
      scat = plt.plot(R5data['time-0'], R5data['htvat-1320008'], 'ks-', markevery=200, label="htvat-1320008 Block 5, Central Refl Middle", markersize=10)
      scat = plt.plot(R5data['time-0'], R5data['htvat-1340008'], 'ko-', markevery=200, label="htvat-1340008 Block 5, Central Refl Outer", markersize=10)

      labx = plt.xlabel('Time [s]')
      laby = plt.ylabel("Temperature [K]")
      if self._print_value_tables:
        title = plt.title("Core Block 5 MID Solid temperatures Inner Refl.")
      else:
        fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
      xlim = plt.xlim(xlimites1)
      ylim = plt.ylim([200.0, 1800.0])
      ytcs = ax.set_yticks([200.0, 600.0, 1000.0, 1400.0, 1800.0 ])
      leg = ax.legend(loc='best', fontsize=lfontsize)
      if savefigures == True:
        fig.savefig(path + '/Plots/' + 'Prod_TempSOLID_core_MIDInnerRefl.png')

      # Get table data
      CIndex = R5data['time-0'].iloc[(R5data['time-0'] - runtime_for_initial_cond).abs().argsort()[:2]].index[0]
      C['SST']['MID']['RI'][0] = R5data['httemp-130000801'][CIndex]
      C['SST']['MID']['RI'][1] = R5data['htvat-1340008'][CIndex]
      C['MAX']['MID']['RI'][0] = R5data['httemp-130000801'].max()
      C['MAX']['MID']['RI'][1] = R5data['htvat-1340008'].max()
      C['DCC']['MID']['RI'][0] = C['MAX']['MID']['RI'][0] - R5data['httemp-130000801'].iloc[-1]
      C['DCC']['MID']['RI'][1] = C['MAX']['MID']['RI'][1] - R5data['htvat-1340008'].iloc[-1]
      EIndex = Measured['Run_Time'].iloc[(Measured['Run_Time'] - runtime_for_initial_cond).abs().argsort()[:2]].index[0]
      E['SST']['MID']['RI'][0] = Measured['TS-1501'][EIndex] + 273.15
      E['SST']['MID']['RI'][1] = Measured['TS-1502'][EIndex] + 273.15
      E['MAX']['MID']['RI'][0] = Measured['TS-1501'].max() + 273.15
      E['MAX']['MID']['RI'][1] = Measured['TS-1502'].max() + 273.15
      E['DCC']['MID']['RI'][0] = E['MAX']['MID']['RI'][0] - (Measured['TS-1501'].iloc[-1] + 273.15)
      E['DCC']['MID']['RI'][1] = E['MAX']['MID']['RI'][1] - (Measured['TS-1502'].iloc[-1] + 273.15)

      print("Primary solid core MID fuel")
      fig = plt.figure(figsize=(figA,figB))
      ax = fig.add_subplot(111)
      # plot the Measured data
    #  scat = plt.plot(Measured['Run_Time'], Measured[['TS-1503', 'TS-1517', 'TS-1531']].mean(axis=1) + 273.15, 'm>-', markevery=13000, label="TS-15xx Block 5, Inner Fuel, Sector avg", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured[['TS-1503', 'TS-1517']].mean(axis=1) + 273.15, 'g>-', markevery=13000, label="TS-15xx Block 5, Inner Fuel, Sector avg", markersize=10)
    #  scat = plt.plot(Measured['Run_Time'], Measured[['TS-1511', 'TS-1525', 'TS-1539']].mean(axis=1) + 273.15, 'g<-', markevery=13000, label="TS-15xx Block 5, Inner Fuel Pin, Sect avg", markersize=10)
    #  scat = plt.plot(Measured['Run_Time'], Measured[['TS-1525', 'TS-1539']].mean(axis=1) + 273.15, 'g<-', markevery=13000, label="TS-15xx Block 5, Inner Fuel Pin, Sect avg", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured[['TS-1505', 'TS-1519', 'TS-1533']].mean(axis=1) + 273.15, 'rs-', markevery=13000, label="TS-15xx Block 5, Middle Fuel, Sect avg", markersize=10)
    #  scat = plt.plot(Measured['Run_Time'], Measured['TS-1540'] + 273.15, 'b<-', markevery=13000, label="TS-1540 Block 7, Middle Fuel Pin, Sect 3", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured[['TS-1535', 'TS-1507', 'TS-1521']].mean(axis=1) + 273.15, 'bo-', markevery=13000, label="TS-15xx Block 5, Outer Fuel, Sect avg", markersize=10)
    #  scat = plt.plot(Measured['Run_Time'], Measured[['TS-1526', 'TS-1512']].mean(axis=1) + 273.15, 'go-', markevery=13000, label="TS-15xx Block 5, Outer Fuel Pin, Sect avg", markersize=10)
        # plot the RELAP channels
      scat = plt.plot(R5data['time-0'], R5data['htvat-1401006'], 'k>-', markevery=200, label="htvat-1401006 Block 5, Inner Fuel", markersize=10)
    #  scat = plt.plot(R5data['time-0'], R5data['httemp-140300601'], 'kP-', markevery=200, label="httemp-140300601 Block 5, Inner Fuel Pin", markersize=10)
      scat = plt.plot(R5data['time-0'], R5data['htvat-1451006'], 'ks-', markevery=200, label="htvat-1451006 Block 5, Middle Fuel", markersize=10)
    #  scat = plt.plot(R5data['time-0'], R5data['httemp-145300601'], 'kD-', markevery=200, label="httemp-145300601 Block 5, Middle Fuel Pin", markersize=10)
      scat = plt.plot(R5data['time-0'], R5data['htvat-1501006'], 'ko-', markevery=200, label=" htvat-1501006 Block 5, Outer Fuel", markersize=10)
    #  scat = plt.plot(R5data['time-0'], R5data['httemp-150300601'], 'kh-', markevery=200, label="httemp-150300601 Block 5, Outer Fuel Pin", markersize=10)

      labx = plt.xlabel('Time [s]')
      laby = plt.ylabel("Temperature [K]")
      if self._print_value_tables:
        title = plt.title("Core Block 5 MID Solid temperatures Fuel")
      else:
        fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
      xlim = plt.xlim(xlimites1)
      ylim = plt.ylim([200.0, 1800.0])
      ytcs = ax.set_yticks([200.0, 600.0, 1000.0, 1400.0, 1800.0 ])
      leg = ax.legend(loc='best', fontsize=lfontsize)
      if savefigures == True:
        fig.savefig(path + '/Plots/' + 'Prod_TempSOLID_core_MIDFuel.png')

      # Get table data
      CIndex = R5data['time-0'].iloc[(R5data['time-0'] - runtime_for_initial_cond).abs().argsort()[:2]].index[0]
      C['SST']['MID']['FU'][0] = R5data['htvat-1401006'][CIndex]
      C['SST']['MID']['FU'][1] = R5data['htvat-1501006'][CIndex]
      C['MAX']['MID']['FU'][0] = R5data['htvat-1401006'].max()
      C['MAX']['MID']['FU'][1] = R5data['htvat-1501006'].max()
      C['DCC']['MID']['FU'][0] = C['MAX']['MID']['FU'][0] - R5data['htvat-1401006'].iloc[-1]
      C['DCC']['MID']['FU'][1] = C['MAX']['MID']['FU'][1] - R5data['htvat-1501006'].iloc[-1]
      EIndex = Measured['Run_Time'].iloc[(Measured['Run_Time'] - runtime_for_initial_cond).abs().argsort()[:2]].index[0]
      E['SST']['MID']['FU'][0] = Measured[['TS-1503', 'TS-1517']].mean(axis=1)[EIndex] + 273.15
      E['SST']['MID']['FU'][1] = Measured[['TS-1535', 'TS-1507', 'TS-1521']].mean(axis=1)[EIndex] + 273.15
      E['MAX']['MID']['FU'][0] = Measured[['TS-1503', 'TS-1517']].mean(axis=1).max() + 273.15
      E['MAX']['MID']['FU'][1] = Measured[['TS-1535', 'TS-1507', 'TS-1521']].mean(axis=1).max() + 273.15
      E['DCC']['MID']['FU'][0] = E['MAX']['MID']['FU'][0] - (Measured[['TS-1503', 'TS-1517']].mean(axis=1).iloc[-1] + 273.15)
      E['DCC']['MID']['FU'][1] = E['MAX']['MID']['FU'][1] - (Measured[['TS-1535', 'TS-1507', 'TS-1521']].mean(axis=1).iloc[-1] + 273.15)

      print("Temperature selection ")
      fig = plt.figure(figsize=(figA,figB))
      ax = fig.add_subplot(111)
      # plot the Measured data
    #  scat = plt.plot(Measured['Run_Time'], Measured[['TS-1503', 'TS-1517', 'TS-1531']].mean(axis=1) + 273.15, 'm>-', markevery=13000, label="TS-15xx Block 5, Inner Fuel, Sector avg", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured[['TS-1503', 'TS-1517']].mean(axis=1) + 273.15, 'g>-', markevery=13000, label="TS-15xx Block 5, Inner Fuel, Sector avg", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured[['TS-1535', 'TS-1507', 'TS-1521']].mean(axis=1) + 273.15, 'r>-', markevery=13000, label="TS-15xx Block 5, Outer Fuel, Sect avg", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['TF-2211'] + 273.15, 'bs-', markevery=13000, label="TF-2211 Lower hot duct", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['TF-2311'] + 273.15, 'cs-', markevery=13000, label="TF-2311 Upper hot duct", markersize=10)
      scat1 = plt.plot(Measured['Run_Time'], Measured['TF-6101'] + 273.15, 'mo-', markevery=13000, label='TF-6101 Lower cold duct', markersize=10) # Rake #1 lower
      scat2 = plt.plot(Measured['Run_Time'], Measured['TF-6102'] + 273.15, 'yo-', markevery=13000,label='TF-6102 Upper cold duct', markersize=10) # Rake #1 upper
        # plot the RELAP channels

      labx = plt.xlabel('Time [s]')
      laby = plt.ylabel("Temperature [K]")
      if self._print_value_tables:
        title = plt.title("Selected temperatures ")
      else:
        fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
      xlim = plt.xlim(xlimites1)
      ylim = plt.ylim([200.0, 1800.0])
      ytcs = ax.set_yticks([200.0, 600.0, 1000.0, 1400.0, 1800.0 ])
      leg = ax.legend(loc='best', fontsize=lfontsize)
      if savefigures == True:
        fig.savefig(path + '/Plots/' + 'Prod_Temp_Selection_only_measured.png')

      print("Primary solid core MID Outer Refl.")
      fig = plt.figure(figsize=(figA,figB))
      ax = fig.add_subplot(111)
      # plot the Measured data
      scat = plt.plot(Measured['Run_Time'], Measured[['TS-1509', 'TS-1523', 'TS-1537']].mean(axis=1) + 273.15, 'g>-', markevery=13000, label="TS-15xx Block 5, Side Refl, Sect avg", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured[['TS-1510', 'TS-1524', 'TS-1538']].mean(axis=1) + 273.15, 'rs-', markevery=13000, label="TS-15xx Block 5, Perm Refl, Sect avg", markersize=10)
      # plot the RELAP channels
      scat = plt.plot(R5data['time-0'], R5data['htvat-1600008'], 'k>-', markevery=200, label="htvat-1600008 Block 5, Side Refl", markersize=10)
      scat = plt.plot(R5data['time-0'], R5data['htvat-1660008'], 'ks-', markevery=200, label="htvat-1660008 Block 5, Perm Refl", markersize=10)

      labx = plt.xlabel('Time [s]')
      laby = plt.ylabel("Temperature [K]")
      if self._print_value_tables:
        title = plt.title("Core Block 5 MID Solid temperatures Outer Refl.")
      else:
        fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
      xlim = plt.xlim(xlimites1)
      ylim = plt.ylim([200.0, 1800.0])
      ytcs = ax.set_yticks([200.0, 600.0, 1000.0, 1400.0, 1800.0 ])
      leg = ax.legend(loc='best', fontsize=lfontsize)
      if savefigures == True:
        fig.savefig(path + '/Plots/' + 'Prod_TempSOLID_core_MIDOuterRefl.png')

      # Get table data
      CIndex = R5data['time-0'].iloc[(R5data['time-0'] - runtime_for_initial_cond).abs().argsort()[:2]].index[0]
      C['SST']['MID']['RO'][0] = R5data['htvat-1600008'][CIndex]
      C['SST']['MID']['RO'][1] = R5data['htvat-1660008'][CIndex]
      C['MAX']['MID']['RO'][0] = R5data['htvat-1600008'].max()
      C['MAX']['MID']['RO'][1] = R5data['htvat-1660008'].max()
      C['DCC']['MID']['RO'][0] = C['MAX']['MID']['RO'][0] - R5data['htvat-1600008'].iloc[-1]
      C['DCC']['MID']['RO'][1] = C['MAX']['MID']['RO'][1] - R5data['htvat-1660008'].iloc[-1]
      EIndex = Measured['Run_Time'].iloc[(Measured['Run_Time'] - runtime_for_initial_cond).abs().argsort()[:2]].index[0]
      E['SST']['MID']['RO'][0] = Measured[['TS-1509', 'TS-1523', 'TS-1537']].mean(axis=1)[EIndex] + 273.15
      E['SST']['MID']['RO'][1] = Measured[['TS-1510', 'TS-1524', 'TS-1538']].mean(axis=1)[EIndex] + 273.15
      E['MAX']['MID']['RO'][0] = Measured[['TS-1509', 'TS-1523', 'TS-1537']].mean(axis=1).max() + 273.15
      E['MAX']['MID']['RO'][1] = Measured[['TS-1510', 'TS-1524', 'TS-1538']].mean(axis=1).max() + 273.15
      E['DCC']['MID']['RO'][0] = E['MAX']['MID']['RO'][0] - (Measured[['TS-1509', 'TS-1523', 'TS-1537']].mean(axis=1).iloc[-1] + 273.15)
      E['DCC']['MID']['RO'][1] = E['MAX']['MID']['RO'][1] - (Measured[['TS-1510', 'TS-1524', 'TS-1538']].mean(axis=1).iloc[-1] + 273.15)

      # Primary fluid/solid core Low (Block 3) 
      # = = = = = = = = = = = = = = = = = = = = = = = =
      print("Primary fluid core LOW")
      fig = plt.figure(figsize=(figA,figB))
      ax = fig.add_subplot(111)
      # plot the Measured data
    #  scat = plt.plot(Measured['Run_Time'], Measured['TF-1304'] + 273.15, 'g>-', markevery=13000, label="TF-1304 Block 3, Inner Fuel, Sect 1", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['TF-1318'] + 273.15, 'r>-', markevery=13000, label="TF-1318 Block 3, Inner Fuel, Sect 2", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['TF-1332'] + 273.15, 'b>-', markevery=13000, label="TF-1332 Block 3, Inner Fuel, Sect 3", markersize=10)
    #  scat = plt.plot(Measured['Run_Time'], Measured[['TF-1304', 'TF-1318', 'TF-1332']].mean(axis=1) + 273.15, 'm>-', markevery=13000, label="TF-13xx Block 3, Inner Fuel, avg", markersize=10)
    #  scat = plt.plot(Measured['Run_Time'], Measured[['TF-1318', 'TF-1332']].mean(axis=1) + 273.15, 'm>-', markevery=13000, label="TF-13xx Block 3, Inner Fuel, avg", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['TF-1306'] + 273.15, 'gs-', markevery=13000, label="TF-1306 Block 3, Middle Fuel, Sect 1", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['TF-1320'] + 273.15, 'rs-', markevery=13000, label="TF-1320 Block 3, Middle Fuel, Sect 2", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['TF-1334'] + 273.15, 'bs-', markevery=13000, label="TF-1334 Block 3, Middle Fuel, Sect 3", markersize=10)
    #  scat = plt.plot(Measured['Run_Time'], Measured[['TF-1306', 'TF-1320', 'TF-1334']].mean(axis=1) + 273.15, 'm<-', markevery=13000, label="TF-13xx Block 3, Middle Fuel, avg", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['TF-1308'] + 273.15, 'go-', markevery=13000, label="TF-1308 Block 3, Outer Fuel, Sect 1", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['TF-1322'] + 273.15, 'ro-', markevery=13000, label="TF-1322 Block 3, Outer Fuel, Sect 2", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['TF-1336'] + 273.15, 'bo-', markevery=13000, label="TF-1336 Block 3, Outer Fuel, Sect 3", markersize=10)
    #  scat = plt.plot(Measured['Run_Time'], Measured[['TF-1308', 'TF-1322', 'TF-1336']].mean(axis=1) + 273.15, 'mo-', markevery=13000, label="TF-13xx Block 3, Outer Fuel, avg", markersize=10)
      # plot the RELAP channels
      scat = plt.plot(R5data['time-0'], R5data['tempg-140100000'], 'k>-', markevery=200, label="tempg-140100000 Block 3, Inner Fuel", markersize=10)
      scat = plt.plot(R5data['time-0'], R5data['tempg-145100000'], 'ks-', markevery=200, label="tempg-145100000 Block 3, Middle Fuel", markersize=10)
      scat = plt.plot(R5data['time-0'], R5data['tempg-150100000'], 'ko-', markevery=200, label="tempg-150100000 Block 3, Outer Fuel", markersize=10)

      labx = plt.xlabel('Time [s]')
      laby = plt.ylabel("Temperature [K]")
      if self._print_value_tables:
        title = plt.title("Core Block 3 LOW Helium temperatures")
      else:
        fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
      xlim = plt.xlim(xlimites1)
      ylim = plt.ylim([200.0, 1800.0])
      ytcs = ax.set_yticks([200.0, 600.0, 1000.0, 1400.0, 1800.0 ])
      leg = ax.legend(loc='best', fontsize=lfontsizeSmall)
      if savefigures == True:
        fig.savefig(path + '/Plots/' + 'Prod_TempHE_core_LOW.png')

      print("Primary solid core LOW inner refl.")
      fig = plt.figure(figsize=(figA,figB))
      ax = fig.add_subplot(111)
      # plot the Measured data
      scat = plt.plot(Measured['Run_Time'], Measured['TS-1301'] + 273.15, 'g>-', markevery=13000, label="TS-1301 Block 3, Central Refl Inner", markersize=10)
    #  scat = plt.plot(Measured['Run_Time'], Measured['TS-1330'] + 273.15, 'r>-', markevery=13000, label="TS-1330 Block 3, Central Refl Middle", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['TS-1302'] + 273.15, 'bo-', markevery=13000, label="TS-1302 Block 3, Central Refl Outer", markersize=10)
      # plot the RELAP channels
      scat = plt.plot(R5data['time-0'], R5data['httemp-130001001'], 'k>-', markevery=200, label="httemp-130001001 Block 3, Central Refl Inner", markersize=10)
      scat = plt.plot(R5data['time-0'], R5data['htvat-1320010'], 'ks-', markevery=200, label="htvat-1320010 Block 3, Central Refl Middle", markersize=10)
      scat = plt.plot(R5data['time-0'], R5data['htvat-1340010'], 'ko-', markevery=200, label="htvat-1340010 Block 3, Central Refl Outer", markersize=10)

      labx = plt.xlabel('Time [s]')
      laby = plt.ylabel("Temperature [K]")
      if self._print_value_tables:
        title = plt.title("Core Block 3 LOW Solid temperatures Inner Refl.")
      else:
        fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
      xlim = plt.xlim(xlimites1)
      ylim = plt.ylim([200.0, 1800.0])
      ytcs = ax.set_yticks([200.0, 600.0, 1000.0, 1400.0, 1800.0 ])
      leg = ax.legend(loc='best', fontsize=lfontsize)
      if savefigures == True:
        fig.savefig(path + '/Plots/' + 'Prod_TempSOLID_core_LOWInnerRefl.png')

      # Get table data
      CIndex = R5data['time-0'].iloc[(R5data['time-0'] - runtime_for_initial_cond).abs().argsort()[:2]].index[0]
      C['SST']['LOW']['RI'][0] = R5data['httemp-130001001'][CIndex]
      C['SST']['LOW']['RI'][1] = R5data['htvat-1340010'][CIndex]
      C['MAX']['LOW']['RI'][0] = R5data['httemp-130001001'].max()
      C['MAX']['LOW']['RI'][1] = R5data['htvat-1340010'].max()
      C['DCC']['LOW']['RI'][0] = C['MAX']['LOW']['RI'][0] - R5data['httemp-130001001'].iloc[-1]
      C['DCC']['LOW']['RI'][1] = C['MAX']['LOW']['RI'][1] - R5data['htvat-1340010'].iloc[-1]
      EIndex = Measured['Run_Time'].iloc[(Measured['Run_Time'] - runtime_for_initial_cond).abs().argsort()[:2]].index[0]
      E['SST']['LOW']['RI'][0] = Measured['TS-1301'][EIndex] + 273.15
      E['SST']['LOW']['RI'][1] = Measured['TS-1302'][EIndex] + 273.15
      E['MAX']['LOW']['RI'][0] = Measured['TS-1301'].max() + 273.15
      E['MAX']['LOW']['RI'][1] = Measured['TS-1302'].max() + 273.15
      E['DCC']['LOW']['RI'][0] = E['MAX']['LOW']['RI'][0] - (Measured['TS-1301'].iloc[-1] + 273.15)
      E['DCC']['LOW']['RI'][1] = E['MAX']['LOW']['RI'][1] - (Measured['TS-1302'].iloc[-1] + 273.15)

      print("Primary solid core LOW fuel")
      fig = plt.figure(figsize=(figA,figB))
      ax = fig.add_subplot(111)
      # plot the Measured data
      scat = plt.plot(Measured['Run_Time'], Measured[['TS-1303', 'TS-1317', 'TS-1331']].mean(axis=1) + 273.15, 'g>-', markevery=13000, label="TS-13xx Block 3, Inner Fuel, Sector avg", markersize=10)
    #  scat = plt.plot(Measured['Run_Time'], Measured[['TS-1311', 'TS-1325', 'TS-1339']].mean(axis=1) + 273.15, 'g<-', markevery=13000, label="TS-13xx Block 3, Inner Fuel Pin, Sect avg", markersize=10)
    #  scat = plt.plot(Measured['Run_Time'], Measured[['TS-1311']].mean(axis=1) + 273.15, 'g<-', markevery=13000, label="TS-13xx Block 3, Inner Fuel Pin, Sect avg", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured[['TS-1305', 'TS-1319', 'TS-1333']].mean(axis=1) + 273.15, 'rs-', markevery=13000, label="TS-13xx Block 3, Middle Fuel, Sect avg", markersize=10)
    #  scat = plt.plot(Measured['Run_Time'], Measured['TS-1340'] + 273.15, 'b<-', markevery=13000, label="TS-1340 Block 7, Middle Fuel Pin, Sect 3", markersize=10)
    #  scat = plt.plot(Measured['Run_Time'], Measured[['TS-1335', 'TS-1307', 'TS-1321']].mean(axis=1) + 273.15, 'm<-', markevery=13000, label="TS-13xx Block 3, Outer Fuel, Sect avg", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured[['TS-1307', 'TS-1321']].mean(axis=1) + 273.15, 'bo-', markevery=13000, label="TS-13xx Block 3, Outer Fuel, Sect avg", markersize=10)
    #  scat = plt.plot(Measured['Run_Time'], Measured[['TS-1326', 'TS-1312']].mean(axis=1) + 273.15, 'go-', markevery=13000, label="TS-13xx Block 3, Outer Fuel Pin, Sect avg", markersize=10)
      # plot the RELAP channels
      scat = plt.plot(R5data['time-0'], R5data['htvat-1401008'], 'k>-', markevery=200, label="htvat-1401008 Block 3, Inner Fuel", markersize=10)
    #  scat = plt.plot(R5data['time-0'], R5data['httemp-140300801'], 'kP-', markevery=200, label="httemp-140300801 Block 3, Inner Fuel Pin", markersize=10)
      scat = plt.plot(R5data['time-0'], R5data['htvat-1451008'], 'ks-', markevery=200, label="htvat-1451008 Block 3, Middle Fuel", markersize=10)
    #  scat = plt.plot(R5data['time-0'], R5data['httemp-145300801'], 'kD-', markevery=200, label="httemp-145300801 Block 3, Middle Fuel Pin", markersize=10)
      scat = plt.plot(R5data['time-0'], R5data['htvat-1501008'], 'ko-', markevery=200, label=" htvat-1501008 Block 3, Outer Fuel", markersize=10)
    #  scat = plt.plot(R5data['time-0'], R5data['httemp-150300801'], 'kh-', markevery=200, label="httemp-150300801 Block 3, Outer Fuel Pin", markersize=10)

      labx = plt.xlabel('Time [s]')
      laby = plt.ylabel("Temperature [K]")
      if self._print_value_tables:
        title = plt.title("Core Block 3 LOW Solid temperatures Fuel")
      else:
        fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
      xlim = plt.xlim(xlimites1)
      ylim = plt.ylim([200.0, 1800.0])
      ytcs = ax.set_yticks([200.0, 600.0, 1000.0, 1400.0, 1800.0 ])
      leg = ax.legend(loc='best', fontsize=lfontsize)
      if savefigures == True:
        fig.savefig(path + '/Plots/' + 'Prod_TempSOLID_core_LOWFuel.png')

      # Get table data
      CIndex = R5data['time-0'].iloc[(R5data['time-0'] - runtime_for_initial_cond).abs().argsort()[:2]].index[0]
      C['SST']['LOW']['FU'][0] = R5data['htvat-1401008'][CIndex]
      C['SST']['LOW']['FU'][1] = R5data['htvat-1501008'][CIndex]
      C['MAX']['LOW']['FU'][0] = R5data['htvat-1401008'].max()
      C['MAX']['LOW']['FU'][1] = R5data['htvat-1501008'].max()
      C['DCC']['LOW']['FU'][0] = C['MAX']['LOW']['FU'][0] - R5data['htvat-1401008'].iloc[-1]
      C['DCC']['LOW']['FU'][1] = C['MAX']['LOW']['FU'][1] - R5data['htvat-1501008'].iloc[-1]
      EIndex = Measured['Run_Time'].iloc[(Measured['Run_Time'] - runtime_for_initial_cond).abs().argsort()[:2]].index[0]
      E['SST']['LOW']['FU'][0] = Measured[['TS-1303', 'TS-1317', 'TS-1331']].mean(axis=1)[EIndex] + 273.15
      E['SST']['LOW']['FU'][1] = Measured[['TS-1307', 'TS-1321']].mean(axis=1)[EIndex] + 273.15
      E['MAX']['LOW']['FU'][0] = Measured[['TS-1303', 'TS-1317', 'TS-1331']].mean(axis=1).max() + 273.15
      E['MAX']['LOW']['FU'][1] = Measured[['TS-1307', 'TS-1321']].mean(axis=1).max() + 273.15
      E['DCC']['LOW']['FU'][0] = E['MAX']['LOW']['FU'][0] - (Measured[['TS-1303', 'TS-1317', 'TS-1331']].mean(axis=1).iloc[-1] + 273.15)
      E['DCC']['LOW']['FU'][1] = E['MAX']['LOW']['FU'][1] - (Measured[['TS-1307', 'TS-1321']].mean(axis=1).iloc[-1] + 273.15)

      print("Primary solid core LOW Outer Refl.")
      fig = plt.figure(figsize=(figA,figB))
      ax = fig.add_subplot(111)
      # plot the Measured data
      scat = plt.plot(Measured['Run_Time'], Measured[['TS-1309', 'TS-1323', 'TS-1337']].mean(axis=1) + 273.15, 'g>-', markevery=13000, label="TS-13xx Block 3, Side Refl, Sect avg", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured[['TS-1310', 'TS-1324', 'TS-1338']].mean(axis=1) + 273.15, 'rs-', markevery=13000, label="TS-13xx Block 3, Perm Refl, Sect avg", markersize=10)
      # plot the RELAP channels
      scat = plt.plot(R5data['time-0'], R5data['htvat-1600010'], 'k>-', markevery=200, label="htvat-1600010 Block 3, Side Refl", markersize=10)
      scat = plt.plot(R5data['time-0'], R5data['htvat-1660010'], 'ks-', markevery=200, label="htvat-1660010 Block 3, Perm Refl", markersize=10)

      labx = plt.xlabel('Time [s]')
      laby = plt.ylabel("Temperature [K]")
      if self._print_value_tables:
        title = plt.title("Core Block 3 LOW Solid temperatures Outer Refl.")
      else:
        fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
      xlim = plt.xlim(xlimites1)
      ylim = plt.ylim([200.0, 1800.0])
      ytcs = ax.set_yticks([200.0, 600.0, 1000.0, 1400.0, 1800.0 ])
      leg = ax.legend(loc='best', fontsize=lfontsize)
      if savefigures == True:
        fig.savefig(path + '/Plots/' + 'Prod_TempSOLID_core_LOWOuterRefl.png')

      # Get table data
      CIndex = R5data['time-0'].iloc[(R5data['time-0'] - runtime_for_initial_cond).abs().argsort()[:2]].index[0]
      C['SST']['LOW']['RO'][0] = R5data['htvat-1600010'][CIndex]
      C['SST']['LOW']['RO'][1] = R5data['htvat-1660010'][CIndex]
      C['MAX']['LOW']['RO'][0] = R5data['htvat-1600010'].max()
      C['MAX']['LOW']['RO'][1] = R5data['htvat-1660010'].max()
      C['DCC']['LOW']['RO'][0] = C['MAX']['LOW']['RO'][0] - R5data['htvat-1600010'].iloc[-1]
      C['DCC']['LOW']['RO'][1] = C['MAX']['LOW']['RO'][1] - R5data['htvat-1660010'].iloc[-1]
      EIndex = Measured['Run_Time'].iloc[(Measured['Run_Time'] - runtime_for_initial_cond).abs().argsort()[:2]].index[0]
      E['SST']['LOW']['RO'][0] = Measured[['TS-1309', 'TS-1323', 'TS-1337']].mean(axis=1)[EIndex] + 273.15
      E['SST']['LOW']['RO'][1] = Measured[['TS-1310', 'TS-1324', 'TS-1338']].mean(axis=1)[EIndex] + 273.15
      E['MAX']['LOW']['RO'][0] = Measured[['TS-1309', 'TS-1323', 'TS-1337']].mean(axis=1).max() + 273.15
      E['MAX']['LOW']['RO'][1] = Measured[['TS-1310', 'TS-1324', 'TS-1338']].mean(axis=1).max() + 273.15
      E['DCC']['LOW']['RO'][0] = E['MAX']['LOW']['RO'][0] - (Measured[['TS-1309', 'TS-1323', 'TS-1337']].mean(axis=1).iloc[-1] + 273.15)
      E['DCC']['LOW']['RO'][1] = E['MAX']['LOW']['RO'][1] - (Measured[['TS-1310', 'TS-1324', 'TS-1338']].mean(axis=1).iloc[-1] + 273.15)

      # Primary fluid outlet temps
      # = = = = = = = = = = = = = = = = = = = = = = = =
      print("Primary fluid outlet temp")
      fig = plt.figure(figsize=(figA,figB))
      ax = fig.add_subplot(111)
      # plot the Measured data
      scat = plt.plot(Measured['Run_Time'], Measured['TF-2211'] + 273.15, 'g>-', markevery=13000, label="TF-2211 Lower hot duct", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['TF-2311'] + 273.15, 'rs-', markevery=13000, label="TF-2311 Upper hot duct", markersize=10)
      # plot the RELAP channels
      scat = plt.plot(R5data['time-0'], R5data['tempg-206070000'], 'k>-', markevery=200, label="tempg-206070000 Lower hot duct", markersize=10)
      scat = plt.plot(R5data['time-0'], R5data['tempg-200010000'], 'ks-', markevery=200, label="tempg-200010000 Upper hot duct", markersize=10)

      labx = plt.xlabel('Time [s]')
      laby = plt.ylabel("Temperature [K]")
      if self._print_value_tables:
        title = plt.title("Core outlet Helium temperature")
      else:
        fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
      xlim = plt.xlim(xlimites1)
      ylim = plt.ylim([300.0, 850.0])
      leg = ax.legend(loc='best', fontsize=lfontsize)
      if savefigures == True:
        fig.savefig(path + '/Plots/' + 'Prod_TempHE_core_Xoutlet.png')

      # Core delta T
      # = = = = = = = = = = = = = = = = = = = = = = = =
      print("Core DT")
      fig = plt.figure(figsize=(figA,figB))
      ax = fig.add_subplot(111)
      # plot the Measured data
      scat = plt.plot(Measured['Run_Time'], Measured['TF-3001'] - Measured['TF-6001'], 'g>-', markevery=13000, label="TF-xxxx Core DT", markersize=10)
      # plot the RELAP channels
      scat = plt.plot(R5data['time-0'], R5data['tempg-200010000'] - R5data['tempg-270040000'], 'k>-', markevery=200, label="tempg-xxxx Core DT", markersize=10)

      labx = plt.xlabel('Time [s]')
      laby = plt.ylabel("Temperature [K]")
      if self._print_value_tables:
        title = plt.title("Core delta T")
      else:
        fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
      xlim = plt.xlim(xlimites1)
      ylim = plt.ylim([-25.0, 450.0])
      leg = ax.legend(loc='best', fontsize=lfontsize)
      if savefigures == True:
        fig.savefig(path + '/Plots/' + 'Prod_TempHE_core_DT.png')


      # Primary fluid HX inlet and outlet temps
      # = = = = = = = = = = = = = = = = = = = = = = = =
      print("Primary fluid HX in/out temp")
      fig = plt.figure(figsize=(figA,figB))
      ax = fig.add_subplot(111)
      # plot the Measured data
      scat = plt.plot(Measured['Run_Time'], Measured['TF-2311'] + 273.15, 'g>-', markevery=13000, label="TF-2311 Upper hot duct", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['TF-6201'] + 273.15, 'rs-', markevery=13000, label="TF-6201 SG outlet", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['TF-6202'] + 273.15, 'bo-', markevery=13000, label="TF-6202 Circulator outlet", markersize=10)
      # plot the RELAP channels
      scat = plt.plot(R5data['time-0'], R5data['tempg-200010000'], 'k>-', markevery=200, label="tempg-200010000 Upper hot duct", markersize=10)
      scat = plt.plot(R5data['time-0'], R5data['tempg-230010000'], 'ks-', markevery=200, label="tempg-230010000 SG outlet", markersize=10)
      scat = plt.plot(R5data['time-0'], R5data['tempg-240010000'], 'ko-', markevery=200, label="tempg-240010000 Circulator outlet", markersize=10)

      labx = plt.xlabel('Time [s]')
      laby = plt.ylabel("Temperature [K]")
      if self._print_value_tables:
        title = plt.title("SG in/out, circ out helium temperature")
      else:
        fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
      xlim = plt.xlim(xlimites1)
      leg = ax.legend(loc='best', fontsize=lfontsize)
      if savefigures == True:
        fig.savefig(path + '/Plots/' + 'Prod_TempHE_SG_inout.png')

      # Primary fluid RCST temps
      # = = = = = = = = = = = = = = = = = = = = = = = =
      print("Primary fluid RCST temp")
      fig = plt.figure(figsize=(figA,figB))
      ax = fig.add_subplot(111)
      # plot the Measured data
      scat = plt.plot(Measured['Run_Time'], Measured['TF-4101'] + 273.15, 'g>-', markevery=13000, label="TF-4101 RCST Low", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['TF-4401'] + 273.15, 'rs-', markevery=13000, label="TF-4401 RCST High", markersize=10)
      # plot the RELAP channels
      scat = plt.plot(R5data['time-0'], R5data['tempg-280010000'], 'k>-', markevery=200, label="tempg-280010000 RCST Low", markersize=10)
      scat = plt.plot(R5data['time-0'], R5data['tempg-280020000'], 'ks-', markevery=200, label="tempg-280020000 RCST High", markersize=10)

      labx = plt.xlabel('Time [s]')
      laby = plt.ylabel("Temperature [K]")
      if self._print_value_tables:
        title = plt.title("RCST helium temperature")
      else:
        fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
      xlim = plt.xlim(xlimites1)
      leg = ax.legend(loc='best', fontsize=lfontsize)
      if savefigures == True:
        fig.savefig(path + '/Plots/' + 'Prod_TempHE_RCST.png')

      # Primary and  RCST pressures
      # = = = = = = = = = = = = = = = = = = = = = = = =
      print("Primary and RCST pressure")
      fig = plt.figure(figsize=(figA,figB))
      ax = fig.add_subplot(111)
      # plot the Measured data
      scat = plt.plot(Measured['Run_Time'], Measured['PT-3001'] * 1000.0, 'g>-', markevery=13000, label="PT-3001 Primary pressure", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['PT-4001'] * 1000.0, 'rs-', markevery=13000, label="PT-4001 RCST pressure", markersize=10)
      # plot the RELAP channels
      scat = plt.plot(R5data['time-0'], R5data['p-200020000'], 'k>-', markevery=200, label="p-200020000 Primary pressure", markersize=10)
      scat = plt.plot(R5data['time-0'], R5data['p-280020000'], 'ks-', markevery=200, label="p-280020000 RCST pressure", markersize=10)

      labx = plt.xlabel('Time [s]')
      laby = plt.ylabel("Pressure [Pa]")
      frmy = plt.ticklabel_format(axis="y", style="sci", scilimits=(0,0), useMathText=True)
      if self._print_value_tables:
        title = plt.title("Primary helium pressure")
      else:
        fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
      xlim = plt.xlim(xlimites1)
    #  ylim = plt.ylim([0.0, 350000.0])
      leg = ax.legend(loc='best', fontsize=lfontsize)
      if savefigures == True:
        fig.savefig(path + '/Plots/' + 'Prod_PressHE.png')

      fig = plt.figure(figsize=(figA,figB))
      ax = fig.add_subplot(111)
      # plot the Measured data
      scat = plt.plot(Measured['Run_Time'], Measured['PT-3001'] * 1000.0, 'g>-', markevery=13000, label="PT-3001 Primary pressure", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['PT-4001'] * 1000.0, 'rs-', markevery=13000, label="PT-4001 RCST pressure", markersize=10)
      # plot the RELAP channels

      labx = plt.xlabel('Time [s]')
      laby = plt.ylabel("Pressure [Pa]")
      frmy = plt.ticklabel_format(axis="y", style="sci", scilimits=(0,0), useMathText=True)
      if self._print_value_tables:
        title = plt.title("Primary helium pressure")
      else:
        fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
      xlim = plt.xlim(xlimites1)
      ylim = plt.ylim([0.0, 350000.0])
      leg = ax.legend(loc='best', fontsize=lfontsize)
      if savefigures == True:
        fig.savefig(path + '/Plots/' + 'Prod_PressHE_only_measured.png')

      # Delta P over the circulator 
      # ===========================================================
      print("DP over the primary circulator")
      fig = plt.figure(figsize=(figA,figB))
      ax = fig.add_subplot(111)
      # plot the Measured data
      scat = plt.plot(Measured['Run_Time'], (Measured['PT-6202'] - Measured['PT-6201']) * 1000.0, 'g>-', markevery=13000, label="PT-6202 - PT-6201 DP circulator", markersize=10)
      # plot the RELAP channels
      scat = plt.plot(R5data['time-0'], R5data['p-240010000'] - R5data['p-230010000'], 'k>-', markevery=200, label="p-240010000 - p-230010000 DP circulator", markersize=10)

      labx = plt.xlabel('Time [s]')
      laby = plt.ylabel("DP [Pa]")
      frmy = plt.ticklabel_format(axis="y", style="sci", scilimits=(0,0), useMathText=True)
      if self._print_value_tables:
        title = plt.title("Pressure drop over circulator")
      else:
        fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
      xlim = plt.xlim(xlimites1)
      leg = ax.legend(loc='best', fontsize=lfontsize)
      if savefigures == True:
        fig.savefig(path + '/Plots/' + 'Prod_DP_circ.png')

      # Delta P over the core 
      # ===========================================================
      print("DP over the core")
      fig = plt.figure(figsize=(figA,figB))
      ax = fig.add_subplot(111)
      # plot the Measured data
      scat = plt.plot(Measured['Run_Time'], Measured['DP-3001'] * 1000.0, 'g>-', markevery=13000, label="DP-3001 DP core", markersize=10)
      # plot the RELAP channels
      scat = plt.plot(R5data['time-0'], R5data['p-270030000'] - R5data['p-200020000'], 'k>-', markevery=200, label="p-270030000 - p-200020000 DP core", markersize=10)

      labx = plt.xlabel('Time [s]')
      laby = plt.ylabel("DP [Pa]")
      frmy = plt.ticklabel_format(axis="y", style="sci", scilimits=(0,0), useMathText=True)
      if self._print_value_tables:
        title = plt.title("Pressure drop over core")
      else:
        fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
      xlim = plt.xlim(xlimites1)
      ylim = plt.ylim([-250.0, 750.0])
      leg = ax.legend(loc='best', fontsize=lfontsize)
      if savefigures == True:
        fig.savefig(path + '/Plots/' + 'Prod_DP_core.png')

      # Primary mass flows
      # ===========================================================
      print("Primary helium mass flows")
      fig = plt.figure(figsize=(figA,figB))
      ax = fig.add_subplot(111)
      # plot the Measured data
      # NO MASS FLOW MEASUREMENT AVAILABLE
      # plot the RELAP channels
      try:
        scat = plt.plot(R5data['time-0'], R5data['mflowj-270020000'], 'k>-', markevery=200, label="mflowj-270020000 Cold duct", markersize=10)
        scat = plt.plot(R5data['time-0'], R5data['mflowj-200020000'], 'ks-', markevery=200, label="mflowj-200020000 Hot upper duct", markersize=10)
        scat = plt.plot(R5data['time-0'], R5data['mflowj-206050000'] * -1.0, 'ko-', markevery=200, label="mflowj-206050000 Hot lower duct", markersize=10)
        scat = plt.plot(R5data['time-0'], R5data['mflowj-237000000'], 'k4-', markevery=200, label="mflowj-237000000 Circulator", markersize=10)

        labx = plt.xlabel('Time [s]')
        laby = plt.ylabel("Mass flow [kg/s]")
        frmy = plt.ticklabel_format(axis="y", style="sci", scilimits=(0,0), useMathText=True)
        if self._print_value_tables:
          title = plt.title("Primary helium mass flows")
        else:
          fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
        xlim = plt.xlim(xlimites1)
        ylim = plt.ylim([-0.005, 0.016])
        leg = ax.legend(loc='best', fontsize=lfontsize)
        if savefigures == True:
          fig.savefig(path + '/Plots/' + 'Prod_HEmassflow.png')
      except KeyError:
        pass

      # Steam Generator inlet mass flow
      # ===========================================================
      print("Steam generator inlet mass flows")
      fig = plt.figure(figsize=(figA,figB))
      ax = fig.add_subplot(111)
      # plot the Measured data
      scat = plt.plot(Measured['Run_Time'], Measured['FT-5001'] / 60.0, 'g>-', markevery=13000, label="FT-5001 SG inlet", markersize=10)
      # plot the RELAP channels
      scat = plt.plot(R5data['time-0'], R5data['mflowj-320000000'], 'k>-', markevery=200, label="mflowj-320000000 SG inlet", markersize=10)

      labx = plt.xlabel('Time [s]')
      laby = plt.ylabel("Mass flow [kg/s]")
      if self._print_value_tables:
        title = plt.title("Steam generator inlet mass flow")
      else:
        fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
      xlim = plt.xlim(xlimites1)
      leg = ax.legend(loc='best', fontsize=lfontsize)
      if savefigures == True:
        fig.savefig(path + '/Plots/' + 'Prod_SG_massFlow.png')
      # Steam Generator inlet temperature
      # ===========================================================
      print("Steam generator inlet temperature")
      fig = plt.figure(figsize=(figA,figB))
      ax = fig.add_subplot(111)
      # plot the Measured data
      scat = plt.plot(Measured['Run_Time'], Measured['TF-5001'] + 273.15, 'g>-', markevery=13000, label="TF-5001 SG inlet temp", markersize=10)
      # plot the RELAP channels
      scat = plt.plot(R5data['time-0'], R5data['tempf-330010000'], 'k>-', markevery=200, label="tempf-330010000 SG inlet temp", markersize=10)

      labx = plt.xlabel('Time [s]')
      laby = plt.ylabel("Temperature [K]")
      if self._print_value_tables:
        title = plt.title("Steam generator inlet temperature")
      else:
        fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
      xlim = plt.xlim(xlimites1)
      leg = ax.legend(loc='best', fontsize=lfontsize)
      if savefigures == True:
        fig.savefig(path + '/Plots/' + 'Prod_SG_temp.png')
      # Steam Generator pressure
      # ===========================================================
      print("Steam generator dome pressure")
      fig = plt.figure(figsize=(figA,figB))
      ax = fig.add_subplot(111)
      # plot the Measured data
      scat = plt.plot(Measured['Run_Time'], Measured['PT-5001'] * 1000.0, 'g>-', markevery=13000, label="PT-5001 SG pressure", markersize=10)
      # plot the RELAP channels
      scat = plt.plot(R5data['time-0'], R5data['p-355010000'], 'rs-', markevery=200, label="p-355010000 SG pressure", markersize=10)

      labx = plt.xlabel('Time [s]')
      laby = plt.ylabel("Pressure [Pa]")
      frmy = plt.ticklabel_format(axis="y", style="sci", scilimits=(0,0), useMathText=True)
      if self._print_value_tables:
        title = plt.title("Steam generator pressure")
      else:
        fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
        xlim = plt.xlim(xlimites1)
      leg = ax.legend(loc='best', fontsize=lfontsize)
      if savefigures == True:
        fig.savefig(path + '/Plots/' + 'Prod_SG_press.png')
      # Steam Generator fill level
      # ===========================================================
      print("Steam generator fill level")
      fig = plt.figure(figsize=(figA,figB))
      ax = fig.add_subplot(111)
      # plot the Measured data
      scat = plt.plot(Measured['Run_Time'], Measured['LF-5002'], 'g>-', markevery=13000, label="LF-5002 SG level", markersize=10)
      # plot the RELAP channels
      scat = plt.plot(R5data['time-0'], R5data['cntrlvar-355'], 'rs-', markevery=200, label="cntrlvar-355 SG level", markersize=10)

      labx = plt.xlabel('Time [s]')
      laby = plt.ylabel("Level [%]")
      if self._print_value_tables:
        title = plt.title("Steam generator level")
      else:
        fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
      xlim = plt.xlim(xlimites1)
      leg = ax.legend(loc='best', fontsize=lfontsize)
      if savefigures == True:
        fig.savefig(path + '/Plots/' + 'Prod_SG_level.png')

      fig = plt.figure(figsize=(figA,figB))
      ax = fig.add_subplot(111)
      # plot the Measured data
      scat = plt.plot(Measured['Run_Time'], Measured['LF-5002'], 'g>-', markevery=13000, label="LF-5002 SG level", markersize=10)
      # plot the RELAP channels

      labx = plt.xlabel('Time [s]')
      laby = plt.ylabel("Level [%]")
      if self._print_value_tables:
        title = plt.title("Steam generator level")
      else:
        fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
      xlim = plt.xlim(xlimites1)
      leg = ax.legend(loc='best', fontsize=lfontsize)
      if savefigures == True:
        fig.savefig(path + '/Plots/' + 'Prod_SG_level_only_measured.png')

      # RCCS inlet mass flow
      # ===========================================================
      try:
        print("RCCS inlet mass flows")
        fig = plt.figure(figsize=(figA,figB))
        ax = fig.add_subplot(111)
        # plot the Measured data
        scat = plt.plot(Measured_trend['Run_Time'], Measured_trend['FT-9001'] / 60.0, 'g>-', markevery=13000, label="FT-9001 RCCS masss flow (TREND!)", markersize=10)
        # plot the RELAP channels
        scat = plt.plot(R5data['time-0'], R5data['mflowj-920000000'], 'k>-', markevery=200, label="mflowj-920000000 RCCS mass flow", markersize=10)

        labx = plt.xlabel('Time [s]')
        laby = plt.ylabel("Mass flow [kg/s]")
        if self._print_value_tables:
          title = plt.title("RCCS inlet mass flow")
        else:
          fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
        xlim = plt.xlim(xlimites1)
        leg = ax.legend(loc='best', fontsize=lfontsize)
        if savefigures == True:
          fig.savefig(path + '/Plots/' + 'Prod_RCCS_massFlow.png')

        fig = plt.figure(figsize=(figA,figB))
        ax = fig.add_subplot(111)
        # plot the Measured data
        scat = plt.plot(Measured_trend['Run_Time'], Measured_trend['FT-9001'] / 60.0, 'g>-', markevery=13000, label="FT-9001 RCCS masss flow (TREND!)", markersize=10)
        # plot the RELAP channels

        labx = plt.xlabel('Time [s]')
        laby = plt.ylabel("Mass flow [kg/s]")
        if self._print_value_tables:
          title = plt.title("RCCS inlet mass flow")
        else:
          fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
        xlim = plt.xlim(xlimites1)
        leg = ax.legend(loc='best', fontsize=lfontsize)
        if savefigures == True:
          fig.savefig(path + '/Plots/' + 'Prod_RCCS_massFlow_only_measured.png')
      except KeyError:
        pass

      # Heater power
      # ===========================================================
      print("Heater power")
      fig = plt.figure(figsize=(figA,figB))
      ax = fig.add_subplot(111)
      # plot the Measured data
      scat = plt.plot(Measured['Run_Time'], Measured['CT-1041'] * Measured['VT-1041'] + Measured['CT-1042'] * Measured['VT-1042'], 'g>-', markevery=13000, label="Measured heater power, bank 104", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['CT-1001'] * Measured['VT-1001'] + Measured['CT-1002'] * Measured['VT-1002'], 'rs-', markevery=13000, label="Measured heater power, bank 110", markersize=10)
      # plot the RELAP channels

      labx = plt.xlabel('Time [s]')
      laby = plt.ylabel("Power [W]")
      if self._print_value_tables:
        title = plt.title("Heater power")
      else:
        fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
      xlim = plt.xlim(xlimites1)
      ylim = plt.ylim([0.0, 35000.0])
      frmy = plt.ticklabel_format(axis="y", style="sci", scilimits=(0,0), useMathText=True)
      leg = ax.legend(loc='best', fontsize=lfontsize)
      if savefigures == True:
        fig.savefig(path + '/Plots/' + 'Prod_heater_powers_only_measured.png')

      # RCCS temperature
      # ===========================================================
      print("RCCS temperatures")
      try:
        fig = plt.figure(figsize=(figA,figB))
        ax = fig.add_subplot(111)
        # plot the Measured data
        scat = plt.plot(Measured['Run_Time'], Measured['TF-9003'] + 273.15, 'g>-', markevery=13000, label="TF-9003 RCCS inlet temp", markersize=10)
        scat = plt.plot(Measured['Run_Time'], Measured['TF-9004'] + 273.15, 'rs-', markevery=13000, label="TF-9004 RCCS outlet temp", markersize=10)
        # plot the RELAP channels
        scat = plt.plot(R5data['time-0'], R5data['tempf-945010000'], 'k>-', markevery=200, label="tempf-945010000 RCCS inlet temp", markersize=10)
        scat = plt.plot(R5data['time-0'], R5data['tempf-955010000'], 'ks-', markevery=200, label="tempf-955010000 RCCS outlet temp", markersize=10)
      except KeyError:
        pass

      labx = plt.xlabel('Time [s]')
      laby = plt.ylabel("Temperature [K]")
      if self._print_value_tables:
        title = plt.title("RCCS temperatures")
      else:
        fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
      xlim = plt.xlim(xlimites1)
      leg = ax.legend(loc='best', fontsize=lfontsize)
      if savefigures == True:
        fig.savefig(path + '/Plots/' + 'Prod_RCCS_temp.png')

      fig = plt.figure(figsize=(figA,figB))
      ax = fig.add_subplot(111)
      # plot the Measured data
      scat = plt.plot(Measured['Run_Time'], Measured['TF-9003'] + 273.15, 'g>-', markevery=13000, label="TF-9003 RCCS inlet temp", markersize=10)
      scat = plt.plot(Measured['Run_Time'], Measured['TF-9004'] + 273.15, 'rs-', markevery=13000, label="TF-9004 RCCS outlet temp", markersize=10)
      # plot the RELAP channels

      labx = plt.xlabel('Time [s]')
      laby = plt.ylabel("Temperature [K]")
      if self._print_value_tables:
        title = plt.title("RCCS temperatures")
      else:
        fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
      xlim = plt.xlim(xlimites1)
      leg = ax.legend(loc='best', fontsize=lfontsize)
      if savefigures == True:
        fig.savefig(path + '/Plots/' + 'Prod_RCCS_temp_only_measured.png')

      print("RCCS temperature diff")
      try:
        fig = plt.figure(figsize=(figA,figB))
        ax = fig.add_subplot(111)
        # plot the Measured data
        scat = plt.plot(Measured['Run_Time'], Measured['TF-9004'] -  Measured['TF-9003'], 'g>-', markevery=13000, label="TF-900x RCCS DT", markersize=10)
        # plot the RELAP channels
        scat = plt.plot(R5data['time-0'],R5data['tempf-955010000'] - R5data['tempf-945010000'], 'k>-', markevery=200, label="tempf-xxxx  RCCS DT", markersize=10)
      except KeyError:
        pass

      labx = plt.xlabel('Time [s]')
      laby = plt.ylabel("Temperature [K]")
      if self._print_value_tables:
        title = plt.title("RCCS temperature diff")
      else:
        fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
      xlim = plt.xlim(xlimites1)
      leg = ax.legend(loc='best', fontsize=lfontsize)
      if savefigures == True:
        fig.savefig(path + '/Plots/' + 'Prod_RCCS_tempDiff.png')

      try:
        print("Heat balance PCS")
        fig = plt.figure(figsize=(figA,figB))
        ax = fig.add_subplot(111)
        # plot the Measured data
        # NO MASS FLOW MEASUREMENT AVAILABLE
        # plot the RELAP channels
        scat = plt.plot(R5data['time-0'], R5data['cntrlvar-911'], 'k>-', markevery=200, label="cntrlvar-911 Core power", markersize=10)
        scat = plt.plot(R5data['time-0'], R5data['cntrlvar-95'], 'ks-', markevery=200, label="cntrlvar-95 RCCS heat loss", markersize=10)
      #  scat = plt.plot(R5data['time-0'], R5data['cntrlvar-31'], 'bo-', markevery=200, label="cntrlvar-31 SG heat loss", markersize=10)
        scat = plt.plot(R5data['time-0'], R5data['cntrlvar-1446'], 'ko-', markevery=200, label="cntrlvar-1446 Envionmental heat loss", markersize=10)

        labx = plt.xlabel('Time [s]')
        laby = plt.ylabel("Power [W]")
        frmy = plt.ticklabel_format(axis="y", style="sci", scilimits=(0,0), useMathText=True)
        if self._print_value_tables:
          title = plt.title("Heat balance PCS")
        else:
          fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
        xlim = plt.xlim(xlimites1)
        ylim = plt.ylim([0.0, 65000.0])
        leg = ax.legend(loc='best', fontsize=lfontsize)
        if savefigures == True:
          fig.savefig(path + '/Plots/' + 'Prod_heatBalancePCS.png')
      except KeyError:
        pass

      print("Lower plenum stratification")
      fig = plt.figure(figsize=(figA,figB))
      ax = fig.add_subplot(111)
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2311'] + 273.15, label='_nolegend_') # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2301'] + 273.15, label='_nolegend_') # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2201'] + 273.15, label='_nolegend_') # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2402'] + 273.15, label='_nolegend_') # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2302'] + 273.15, label='_nolegend_') # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2202'] + 273.15, label='_nolegend_') # pole 
      #scat  = plt.plot(Measured['Run_Time'], Measured['TS-2102']) # pole 
      #scat  = plt.plot(Measured['Run_Time'], Measured['TF-2403']) # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2303'] + 273.15, label='_nolegend_') # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2203'] + 273.15, label='_nolegend_') # pole 
      #scat  = plt.plot(Measured['Run_Time'], Measured['TS-2103']) # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2404'] + 273.15, label='_nolegend_') # pole
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2304'] + 273.15, label='_nolegend_') # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2204'] + 273.15, label='_nolegend_') # pole 
      #scat  = plt.plot(Measured['Run_Time'], Measured['TS-2104']) # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2405'] + 273.15, label='_nolegend_') # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2305'] + 273.15, label='_nolegend_') # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2205'] + 273.15, label='_nolegend_') # pole 
      #scat  = plt.plot(Measured['Run_Time'], Measured['TS-2105']) # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2406'] + 273.15, label='_nolegend_') # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2306'] + 273.15, label='_nolegend_') # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2206'] + 273.15, label='_nolegend_') # pole 
      #scat  = plt.plot(Measured['Run_Time'], Measured['TS-2106']) # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2407'] + 273.15, label='_nolegend_') # pole 
      #scat  = plt.plot(Measured['Run_Time'], Measured['TF-2307']) # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2207'] + 273.15, label='_nolegend_') # pole 
      #scat  = plt.plot(Measured['Run_Time'], Measured['TF-2107']) # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2308'] + 273.15, label='_nolegend_') # pole 
      #scat  = plt.plot(Measured['Run_Time'], Measured['TF-2208']) # pole
      #scat  = plt.plot(Measured['Run_Time'], Measured['TF-2409'] + 273.15, label='_nolegend_') # pole 
      #scat  = plt.plot(Measured['Run_Time'], Measured['TF-2309']) # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2209'] + 273.15, label='_nolegend_') # pole 
      #scat  = plt.plot(Measured['Run_Time'], Measured['TS-2109']) # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2410'] + 273.15, label='_nolegend_') # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2310'] + 273.15, label='_nolegend_') # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2210'] + 273.15, label='_nolegend_') # pole 
      #scat  = plt.plot(Measured['Run_Time'], Measured['TS-2110']) # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2411'] + 273.15, label='_nolegend_') # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2211'] + 273.15, label='_nolegend_') # pole 
      #scat  = plt.plot(Measured['Run_Time'], Measured['TS-2211']) # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2412'] + 273.15, label='_nolegend_') # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2312'] + 273.15, label='_nolegend_') # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2212'] + 273.15, label='_nolegend_') # pole 
      #scat  = plt.plot(Measured['Run_Time'], Measured['TS-2112']) # pole 
      #scat  = plt.plot(Measured['Run_Time'], Measured['TF-2413']) # pole 
      #scat  = plt.plot(Measured['Run_Time'], Measured['TF-2313']) # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2213'] + 273.15, label='_nolegend_') # pole 
      #scat  = plt.plot(Measured['Run_Time'], Measured['TS-2113']) # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2414'] + 273.15, label='_nolegend_') # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2314'] + 273.15, label='_nolegend_') # pole 
      #scat  = plt.plot(Measured['Run_Time'], Measured['TF-2214']) # pole 
      #scat  = plt.plot(Measured['Run_Time'], Measured['TS-2114']) # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2315'] + 273.15, label='_nolegend_') # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2215'] + 273.15, label='_nolegend_') # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2316'] + 273.15, label='_nolegend_') # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-2216'] + 273.15, label='_nolegend_') # pole 

      average_temp = Measured[['TF-2311', 'TF-2301', 'TF-2201', 'TF-2402', 'TF-2302', 'TF-2202', 'TF-2302', 'TF-2202', 'TF-2404', 'TF-2304', 'TF-2204', 'TF-2405', 'TF-2305', 'TF-2205',
                             'TF-2406', 'TF-2306', 'TF-2206', 'TF-2407', 'TF-2207', 'TF-2308', 'TF-2209', 'TF-2410', 'TF-2310', 'TF-2210', 'TF-2411', 'TF-2211',
                             'TF-2412', 'TF-2312', 'TF-2212', 'TF-2213', 'TF-2414', 'TF-2314', 'TF-2315', 'TF-2215', 'TF-2316', 'TF-2216' ]].mean(axis=1)
      scat  = plt.plot(Measured['Run_Time'], average_temp + 273.15, 'b-', linewidth=7, label='Average lower plenum') # pole 
      scat  = plt.plot(Measured['Run_Time'], Measured['TF-3001'] + 273.15, 'k-', linewidth=7, label='Hot duct') # pole 

      labx = plt.xlabel('Time [s]')
      laby = plt.ylabel("Temperature [K]")
      #frmy = plt.ticklabel_format(axis="y", style="sci", scilimits=(0,0), useMathText=True)
      if self._print_value_tables:
          title = plt.title("Lower plenum stratification")
      else:
          fig.subplots_adjust(bottom=BorderBot, right=BorderRig, top=BorderTop)
      xlim = plt.xlim(xlimites1)
      leg = ax.legend(loc='best', fontsize=lfontsize)
      if savefigures == True:
        fig.savefig(path + '/Plots/' + 'Prod_plenumStrtification_only_measured.png')

      # Print the comparison tables
      if self._print_value_tables:
        print("========== C-E and C/E Table  ===========")
        print("C       E       C-E      C/E ")
        for k in C.keys(): #loop SST, MAX, DCC
          for kk in C[k].keys(): #loop TOP, MID, LOW
            for kkk in C[k][kk].keys(): # loop RI, FU, RO
              print(k, kk, kkk, C[k][kk][kkk], E[k][kk][kkk], C[k][kk][kkk] - E[k][kk][kkk], C[k][kk][kkk] / E[k][kk][kkk]) 

      if not savefigures:
        plt.show()




def main():
  Input_File_YAML = YAML2Dict()
  Instance = Test(Input_File_YAML['Analysis'], 'Iteration_1', 'Flow_Rate_1')
main()

# Some additional inputs....
# Takes the measured value  from this time stamp in the data file
#At which transient time should the ss be?
# => After the last valve movement befeor the blower is shut down (MS-6201)
# and the transient is started (SV-6001)
# => at 6/1/19 at 8:10:40pm => 179500.0 s