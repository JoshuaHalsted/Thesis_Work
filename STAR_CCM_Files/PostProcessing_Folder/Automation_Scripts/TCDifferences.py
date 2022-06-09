import numpy as np
import pandas as pd
import os

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

STAR_FILE = r"C:/Users/17577/Thesis_Work/STAR_CCM_Files/PostProcessing_Folder/Automation_Scripts/STAR_TC_Results.csv"
TC_DATA_FILE = r"C:/Users/17577/Thesis_Work/STAR_CCM_Files/PostProcessing_Folder/Automation_Scripts/Experimental_TC_Data.csv"

STAR_RESULTS = ImportStuff(STAR_FILE)
TC_RESULTS = ImportStuff(TC_DATA_FILE)

TC_List = STAR_RESULTS.columns

string_list = []
string_list.append("Mesh_Setting_1:")
for column in STAR_RESULTS:
    try:
        ABS_DIFF = float(TC_RESULTS[column][0])+273.15-float(STAR_RESULTS[column][0])
        REL_DIFF = 100* ABS_DIFF/(float(TC_RESULTS[column][0])+273.15)
        string_list.append("\t%s:"%(column))
        string_list.append("\t\tPG-28 result: %s Kelvin"%(np.round(float(TC_RESULTS[column][0])+273.15,5)))
        string_list.append("\t\tSTAR result: %s Kelvin"%(np.round(float(STAR_RESULTS[column][0]),5)))
        string_list.append("\t\tAbsolute difference is %s Kelvin"%(np.round(ABS_DIFF,4)))
        string_list.append("\t\tRelative difference is %s percent"%(np.abs(np.round(REL_DIFF,4))))
    except:
        pass

#print(string_list)
with open(os.path.join("C:/Users/17577/Thesis_Work/STAR_CCM_Files/PostProcessing_Folder/Automation_Scripts",'STAR_LP_TC_Results.txt'), 'w') as f:
    for line in string_list:
        f.write(line)
        f.write('\n')
