#!/bin/sh
#case_array=(Point_4375 Point_4 Point_375 Point_3125)
case_array=(Point_4)
number_restarts = 10
for path in ${case_array[@]}
    do
        cd Flow_Rate_"$path"/
        ~/RELAP5_3D_Files/relap5.x -i PG28_filled_"$path"_SS_heat.i -O outdta.o -r restart_"$path".r
        #rm outdta.o
        for simulation in {1..10..1}
            do 
                echo $simulation
                ~/RELAP5_3D_Files/relap5.x -i PG28_filled_"$path"_rst_refill.i -O outdta"$simulation".o -r restart_"$path".r
                #rm outdta1.o
                rm restart_"$path".plt
                #~/RELAP5_3D_Files/relap5.x -i PG28_filled_"$path"_rst_refill.i -O outdta2.o -r restart_"$path".r
                #rm outdta2.o
                #rm restart_"$path".plt
                #~/RELAP5_3D_Files/relap5.x -i PG28_filled_"$path"_rst_refill.i -O outdta3.o -r restart_"$path".r
                #rm outdta3.o
                #rm restart_"$path".plt
                #~/RELAP5_3D_Files/relap5.x -i PG28_filled_"$path"_rst_refill.i -O outdta4.o -r restart_"$path".r
                #rm outdta4.o
                #rm restart_"$path".plt
                #~/RELAP5_3D_Files/relap5.x -i PG28_filled_"$path"_rst_refill.i -O outdta5.o -r restart_"$path".r
                #rm outdta5.o
                #rm restart_"$path".plt
                #~/RELAP5_3D_Files/relap5.x -i PG28_filled_"$path"_rst_refill.i -O outdta6.o -r restart_"$path".r
                #rm outdta6.o
                #rm restart_"$path".plt
                #~/RELAP5_3D_Files/relap5.x -i PG28_filled_"$path"_rst_refill.i -O outdta7.o -r restart_"$path".r
                #rm outdta7.o
                #rm restart_"$path".plt
            done
        ~/RELAP5_3D_Files/relap5.x -i PG28_filled_"$path"_rst_test_heat.i -O PG28_filled_"$path"_Output.o -p restart_"$path".plt
        rm restart_"$path".r
        ~/RELAP5_3D_Files/relap5.x -i Strip.i -O ooo
        #rm ooo
        sed 's/$/,/' stripf > strippedit
        rm stripf
        sed 's/,,/,/' strippedit > Output_Flow_Rate_"$path".o
        rm strippedit
        cd ..
    done