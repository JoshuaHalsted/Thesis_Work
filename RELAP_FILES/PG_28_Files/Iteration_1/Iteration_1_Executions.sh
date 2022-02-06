#!/bin/sh
case_array=(1_Point_5 1_Point_25 1 Point_75)
cd R5_Files
for path in ${case_array[@]}
    do
        cd Flow_Rate_"$path"/
        ~/RELAP5_3D_Files/relap5.x -i PG28_filled_"$path".i -O PG28_filled_"$path".o -r restart_"$path".r
        rm restart_"$path".r
        ~/RELAP5_3D_Files/relap5.x -i Strip.i -O ooo
        rm ooo
        sed 's/$/,/' stripf > strippedit
        rm stripf
        sed 's/,,/,/' strippedit > Output_Flow_Rate_"$path".o
        rm strippedit
        cd ..
    done