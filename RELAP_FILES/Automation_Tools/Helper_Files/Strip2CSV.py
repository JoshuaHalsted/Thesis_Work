#test_names = ["Point_625","Point_5625","Point_5","Point_4375","Point_375","Point_3125","Point_25"]
import os
print(os.getcwd())
os.chdir("C:\\Users\\17577\Thesis_Work")
test_names = ["Point_4"]

if len(test_names) > 0:
    for test, _ in enumerate(test_names):
        fout = open("RELAP_FILES/PG_28_Files/Iteration_4/Workbooks/Output_Flow_Rate_%s.csv"%(test_names[test]), "w")
        mytemp = ""
        mytempplotnum = ""
        Output_File = "RELAP_FILES/PG_28_Files/Iteration_4/R5_Files/Flow_Rate_%s/Output_Flow_Rate_%s.o"%(test_names[test],test_names[test])
        with open(Output_File) as fp:
            count = 0
            start = False
            plotnum_treatment = False
            for l in fp:
                count += 1
                if 'plotinf' in l:
                    start = True
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