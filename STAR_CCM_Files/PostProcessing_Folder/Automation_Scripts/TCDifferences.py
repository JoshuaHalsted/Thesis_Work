import numpy as np
import pandas as pd

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

print("Mesh_Setting_1:")
for column in STAR_RESULTS:
    try:
        ABS_DIFF = float(TC_RESULTS[column][0])+273.15-float(STAR_RESULTS[column][0])
        REL_DIFF = 100*  ABS_DIFF/(float(TC_RESULTS[column][0])+273.15)
        #print("Difference is %s"%(TC_RESULTS[column][0]-STAR_RESULTS[column][0]))
        print("\t%s:"%(column))
        print("\t\tAbsolute difference is %s Kelvin\n"%(np.round(ABS_DIFF,4)))
        print("\t\tRelative difference is %s percent\n"%(np.abs(np.round(REL_DIFF,4))))
    except:
        pass
