#!/bin/sh
#case_array=(Point_625 Point_5625 Point_5 Point_4375 Point_375 Point_3125 Point_25)
case_array=(Point_5625)
cd R5_Files
for path in ${case_array[@]}
    do
        echo "${path}"
        cd Flow_Rate_"$path"/
        ~/RELAP5_3D_Files/relap5.x -i PG28_filled_"$path"_SS_heat.i -O outdta.o -r restart_"$path".r
        rm outdta.o
        rm restart_"$path".plt
        ~/RELAP5_3D_Files/relap5.x -i PG28_filled_"$path"_rst_test_heat.i -O PG28_filled_"$path"_Output.o -r restrt -p new
        rm restart_"$path".r
        rm PG28_filled_"$path"_Output.o
        ~/RELAP5_3D_Files/relap5.x -i Strip.i -o ooo -p hello
        rm ooo
        sed 's/$/,/' stripf > strippedit
        rm stripf
        sed 's/,,/,/' strippedit > Output_Flow_Rate_"$path".o
        rm strippedit
        rm restart_"$path".plt
        cd ..
    done