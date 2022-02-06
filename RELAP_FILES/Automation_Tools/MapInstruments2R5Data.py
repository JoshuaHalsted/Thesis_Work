### Instrument mapping file
import yaml
import pandas as pd
import re

def ImportStuff():
    import_df = pd.read_csv(r'C:\\Users\\17577\\Thesis_Work\\RELAP_FILES\\Automation_Tools\\instrumentationmap2018-09-28.csv')
    import_R5_results = pd.read_csv(r'C:\\Users\\17577\\Thesis_Work\\RELAP_FILES\\PG_28_Files\\Iteration_4\\R5_Files\\Flow_Rate_Point_4\\Output_Flow_Rate_Point_4.csv')
    import_data = pd.read_csv(r'C:\\Users\\17577\\Thesis_Work\\RELAP_FILES\\PG_28_Files\\PG28_Data_Quality.csv')
    return import_df, import_R5_results, import_data
    #return import_df, import_R5_results

def CleanupDF(df):
    df = df.drop(columns=['Instrument','Total_Uncertainty','Lower','Units'])
    df = df[df.columns.drop(list(df.filter(regex='Unnamed')))]
    df = df.dropna()
    df = df[~df.Tag_Number.str.contains("GC")]
    return df

def recur_dictify(frame):
    if len(frame.columns) == 1:
        if frame.values.size == 1: 
            return frame.values[0][0]
        return frame.values.squeeze()
    grouped = frame.groupby(frame.columns[0])
    d = {k: recur_dictify(g.iloc[:,1:]) for k,g in grouped}
    return d

def WriteDict2YAML(dataframe):
    with open(r'C:\\Users\\17577\\Thesis_Work\\RELAP_FILES\\Automation_Tools\\output.yaml', 'w') as file:
        outputs = yaml.dump(dataframe, file)

def AddList2Dataframe(List, Dataframe):
    a_series = pd. Series(List, index = Dataframe.columns)
    Dataframe = Dataframe.append(a_series, ignore_index=True)
    return Dataframe

def WriteList2File(filename, list2write):
    with open(filename, 'w') as fp:
        for item in list2write:
            # write each item on a new line
            fp.write("%s\n" % item)
        print('Done')

def main():
    print(chr(27) + "[2J")
    InstrumentMap, R5_Results, Data_Results = ImportStuff()
    #InstrumentMap, R5_Results = ImportStuff()
    df = CleanupDF(InstrumentMap)
    formatted = recur_dictify(df[['Axial_Location','Radial_Azimuthal_Location','Tag_Number','RELAP5_Model_Parameters']])
    WriteDict2YAML(formatted)
    New_R5_Results = R5_Results.rename(columns=lambda x: x.strip())
    New_R5_Results = New_R5_Results.rename(columns={"time-0" : "Time"}).drop(columns=["-plotnum", "-", ""])
    R5_Start_Time = 0.0
    New_R5_Results['Time'].values[-1] = round(New_R5_Results['Time'].values[-1]* 2.0)/2.0
    channel = 'htvat-1401009'
    instrument = 'TS-1109'
    R5_Channel_Time = New_R5_Results[channel].tolist()
    R5_Channel_Data = New_R5_Results['Time'].tolist()
    #print(R5_Channel_Time)
    #print(R5_Channel_Data)
    Number_Instrument_Time_Steps = int(New_R5_Results['Time'].values[-1]/0.5)
    Instrument_Time = Data_Results['Run_Time'].head(Number_Instrument_Time_Steps).tolist()
    Instrument_Readings = Data_Results[instrument].head(Number_Instrument_Time_Steps).tolist()
    #print(Instrument_Time)
    #print(Instrument_Readings)
    File_List = []
    for Axial_Location in formatted.keys():
        ResultsDF = pd.DataFrame()
        for Radial_Location in formatted[Axial_Location].keys():
            for instrument in formatted[Axial_Location][Radial_Location].keys():
                # First, write instrument data to dataframe
                try:
                    ResultsDF['Instrument_Time'] = Data_Results['Run_Time'].head(Number_Instrument_Time_Steps+1).tolist()
                    ResultsDF['%s'%(instrument)] = Data_Results[instrument].head(Number_Instrument_Time_Steps+1).tolist()
                except KeyError:
                    print("%s is not available in the data"%(instrument))
                channel_string = formatted[Axial_Location][Radial_Location][instrument]
                if "," in channel_string:
                    channel_list = channel_string.split(", ")
                    for channel in channel_list:
                        ResultsDF['R5_Time'] = pd.Series(New_R5_Results[channel].tolist())
                        ResultsDF['%s'%(channel)] = pd.Series(New_R5_Results['Time'].tolist())
                else:
                    ResultsDF['R5_Time'] = pd.Series(New_R5_Results[channel].tolist())
                    ResultsDF['%s'%(channel_string)] = pd.Series(New_R5_Results['Time'].tolist())
        CSV_FileName = "%s_%s_Readings.csv"%(Axial_Location, Radial_Location)
        ResultsDF.to_csv('C:\\Users\\17577\Thesis_Work\\RELAP_FILES\\Automation_Tools\\%s'%(CSV_FileName))
        File_List.append('C:/Users/17577/Thesis_Work/RELAP_FILES/Automation_Tools/%s'%(CSV_FileName))
        WriteList2File('C:\\Users\\17577\Thesis_Work\\RELAP_FILES\\Automation_Tools\\CSV_Files.txt', File_List)

main()