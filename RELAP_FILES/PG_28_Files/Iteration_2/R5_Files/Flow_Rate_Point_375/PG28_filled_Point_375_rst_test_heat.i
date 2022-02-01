=base_2018-05-30QA.i HTTF system model
* base model adjusted for PG-28
*
* This model represents the High Temperature Test Facility (HTTF) (prismatic core
* design), which is being built at Oregon State University to support the Advanced
* Reactor Technologies program.
*
* This is a full system model developed to perform assessment calculations using
* experiment data from the facility. The model includes the primary pressure vessel
* and internals, the primary coolant system, the secondary coolant system, and
* the reactor cavity cooling system (RCCS).
*
* The core is modeled with three parallel channels, each representing one of the
* three rings in the annular heated region. The heater rods radiate to the
* surrounding ceramic material. The helium gap between the rods and the
* ceramic is included.
*
* The central reflector is modeled in three pieces: a solid inner ring, a middle ring
* with coolant holes, and an outer solid ring next to the heated region.
*
* The side reflector is also modeled with a solid ring next to the heated portion of
* the core, a middle ring with coolant holes, and a solid ring outside it. The
* permanent side reflector is also modeled as a solid ring.
*
* The primary coolant system includes the hot and cold ducts, the steam 
* generator plenums and tubes, the gas circulator, pressure relief and
* depressurization valves, the check valve at the steam generator inlet, the loop
* isolation valve, and connecting piping. Break valves at the end of the hot duct and
* in the cold leg piping connect to the reactor cavity simulation tank (RCST).
*
* The hot duct is split into top and bottom halves, and is extended to include all of the
* piping between the pressure vessel and the RCST.
*
* The upper volume in the RCST is modeled as a large, short volume so that both the top
* half of the hot duct and the cold duct can be connected to it. This provides a large, well-mixed
* volume of gas to be circulated back into the primary coolant system. A small
* component is added to make the connection from the large RCST volume to the
* bottom of the hot duct.
*
* The outlet plenum is divided into four components: a volume at the top that connects
* to all of the core channels, a volume between this upper volume and the top half of the
* hot duct, a vertical pipe containing most of the plenum volume (connected at the top
* to the upper volume), and a volume between the bottom half of the hot duct and the pipe.
*
* The secondary coolant system includes the feedwater pump, steam generator,
* the steam line pressure control valve, the pressure relief valve, and associated
* piping. The feedwater piping is not modeled explicitly: the approximate length and
* correct elevation change are input, as the flow resistance of the feedwater piping
* is not important to the plant response.
*
* The RCCS is modeled as a set of panels completely surrounding the primary
* pressure vessel. Flowing water cools the front side of the panels, and natural
* convection heat transfer cools the back side.
*
* The tank that provides water to the feedwater and RCCS pumps is modeled,
* along with its water supply, drain valve, and vent line.
*
* The air cavity between the primary pressure vessel and the RCCS panels is
* also included in the model.
*
* Trips and control systems are provided for the circulator, the feedwater and RCCS
* pumps, the break and loop isolation valves, the pressure relief and depressurization
* valves, and the tank water supply and drain valves.
*
* All of the vertically-oriented heat structures have 2-D conduction turned on where
* possible. Axial conduction between the core and the top and
* bottom reflectors, and in three of the four solid reflector regions, is modeled
* using conduction enclosures.
*
* -----------------------------------------------------------
* The deck is set-up to model test PG-28, a low power DCC
* -----------------------------------------------------------
*
* - Changes compared to QA basedeck HTTF_base_2018-05-30QA.i:
*   - Split hot duct has been added.
*
* - Initial conditions (from OSU-HTTF-TAR-028-R0)
* - Boundary conditions (from OSU-HTTF-TAR-028-R0)
*
*
*
*********************************************************
1 8 12 54
100 restart transnt
101 run
102 si  si
103 -1 binary restart_Point_375.r
200 0.0
201 80000.0 1.0001-12 1.0-2 3 1000 5000 5000
400
600 322
*
*******************************************************
* additional plot variables
*******************************************************
*
20800031  systms  1
20800032  systms  5
*
*******************************************************
* trips
*******************************************************
*
20600000  expanded
*
*
* Control primary and RCST system pressure
* =================================
* Primary: tmpdjun 233 mondels both, the pressurisation and depressurisation
* RCST: The pressurisation is modeled through leakage from the primary
*       valves 256 and 207, the depressurisation through tmpdjun 235

* Primary: Switch primary from pressurising through SV-4014 to 
*          depressurisation through SV-6201
* RCST: Switch from leakage valves to depressurisation through SV-4001
20602330 time  0 ge  null  0 1.16E+08  l * 1/6/2019 20:00:00

* Global on/off switches
* strat pressure control
20602350 time  0 ge  null  0 1.16E+08  l * strat pressure control after 5 seconds
* no more pressure control  
20602340 time  0 ge  null  0 1.16E+08  l * 1/6/2019 20:22:00
*
* primary helium blower trip
* (only used when dynamic blower control is used)
20602360 time  0 ge  null  0 1.16E+08  l * 
*
* break trips
20602050  time  0 ge  null  0 1.16E+08  l * open hot duct break valve
20602060  time  0 ge  null  0 1.16E+08  l * close hot duct break valve

20602550  time  0 ge  null  0 1.16E+08  l * open cold leg break valve
20602560  time  0 ge  null  0 1.16E+08  l * close cold leg break valve
*
* valve V-6201 trips
20602450  time  0 ge  null  0 1.16E+08  l * open valve
20602460  time  0 ge  null  0 1.16E+08  l * close valve
*
* primary coolant system relief valve trips
20602940  p 293010000 gt  null  0 1.16E+08  n * opening pressure
20602950  p 293010000 gt  null  0 1.10E+08  n * closing pressure
20612940  294 or  1295  n * initial opening or already open
20612950  1294  and -295  n * open valve
*
* primary coolant system depressurization valve trips
20602960  time  0 ge  null  0 1.16E+08  n * open valve manually
20602970  time  0 ge  null  0 1.16E+08  n * close valve manually
20612960  296 and -297  n * open valve
*
* steam generator relief valve trips
20603940  p 390010000 gt  null  0 1.16E+08  n * opening pressure
20603950  p 390010000 gt  null  0 1.16E+08  n * closing pressure
20613940  394 or  1395  n * initial opening or already open
20613950  1394  and -395  n * open valve
*
* steam generator feedwater valve trips
20603200  cntrlvar  355 lt  null,0 60.0 n  * low SG level setpoint (opening)
20603210  cntrlvar  355 gt  null,0 80.0 n  * high SG level setpoint (closing)
*
* steam generator level trip (LF-5002 = 69.13% of full to initiate PG-28)
20603220  cntrlvar  355 lt  null,0 49.45 n  * low SG level setpoint (closing)
*
* water supply valve controls for tank T-010
20604100  cntrlvar  450 lt  cntrlvar  451 0.0 n  * low liquid level setpoint
20604110  cntrlvar  450 gt  cntrlvar  452 0.0 n  * high liquid level setpoint
20604120  cntrlvar  450 gt  cntrlvar  453 0.0 n  * level above mid-range
20614090  410 or  1410  n
20614100  1409  and -412  n * open supply valve
20614110  411 or  1412  n
20614120  1411  and 412 n * close supply valve
*
*******************************************************
* hydrodynamics
*******************************************************
*
2370000 circultr  tmdpjun
2370101 235010000 240000000 0.00000
2370200 1 0
2370201 0.0 0.0 0.019323 0.0
2370202 27.0 0.0 0.01932375 0.0
2370203 100.5 0.0 0.0215715 0.0
2370204 153.0 0.0 0.02157675 0.0
2370205 208.5 0.0 0.0215805 0.0
2370206 267.5 0.0 0.02158575 0.0
2370207 330.5 0.0 0.021591 0.0
2370208 398.0 0.0 0.021594 0.0
2370209 472.0 0.0 0.021597 0.0
2370210 557.5 0.0 0.02160225 0.0
2370211 667.0 0.0 0.0216075 0.0
2370212 813.0 0.0 0.021615 0.0
2370213 1329.5 0.0 0.02165475 0.0
2370214 1404.0 0.0 0.02166375 0.0
2370215 1496.5 0.0 0.021678 0.0
2370216 1574.0 0.0 0.02169075 0.0
2370217 1613.5 0.0 0.02169375 0.0
2370218 1657.0 0.0 0.02169975 0.0
2370219 1712.0 0.0 0.0217065 0.0
2370220 1773.5 0.0 0.0217125 0.0
2370221 1879.0 0.0 0.02172375 0.0
2370222 1934.5 0.0 0.0217275 0.0
2370223 2003.0 0.0 0.02173125 0.0
2370224 2464.0 0.0 0.021702 0.0
2370225 2645.5 0.0 0.02167875 0.0
2370226 2744.0 0.0 0.02166825 0.0
2370227 2847.5 0.0 0.02165775 0.0
2370228 2946.5 0.0 0.02164875 0.0
2370229 3034.0 0.0 0.02164125 0.0
2370230 3282.0 0.0 0.021627 0.0
2370231 3435.5 0.0 0.021621 0.0
2370232 3670.0 0.0 0.0216195 0.0
2370233 4005.0 0.0 0.02162025 0.0
2370234 4644.0 0.0 0.0216255 0.0
2370235 4997.0 0.0 0.02160075 0.0
2370236 5322.0 0.0 0.0215835 0.0
2370237 5542.5 0.0 0.0215925 0.0
2370238 5688.0 0.0 0.02162025 0.0
2370239 5815.0 0.0 0.02164575 0.0
2370240 5907.5 0.0 0.021669 0.0
2370241 5976.0 0.0 0.0216915 0.0
2370242 6042.0 0.0 0.021714 0.0
2370243 6118.5 0.0 0.0217395 0.0
2370244 6241.5 0.0 0.02939925 0.0
2370245 6353.5 0.0 0.02947425 0.0
2370246 6668.5 0.0 0.02971125 0.0
2370247 6731.5 0.0 0.029772 0.0
2370248 6795.0 0.0 0.029826 0.0
2370249 6869.5 0.0 0.02987175 0.0
2370250 6931.5 0.0 0.0299235 0.0
2370251 6982.0 0.0 0.02998125 0.0
2370252 7029.0 0.0 0.030036 0.0
2370253 7128.0 0.0 0.03013275 0.0
2370254 7195.5 0.0 0.03015075 0.0
2370255 7296.0 0.0 0.03010875 0.0
2370256 7296.5 0.0 0.0301095 0.0
2370257 7424.5 0.0 0.030006 0.0
2370258 8388.5 0.0 0.028599 0.0
2370259 9894.5 0.0 0.0299745 0.0
2370260 10102.0 0.0 0.029901 0.0
2370261 10278.5 0.0 0.0298215 0.0
2370262 10420.5 0.0 0.0297975 0.0
2370263 10547.5 0.0 0.0297765 0.0
2370264 10704.0 0.0 0.02975925 0.0
2370265 10869.5 0.0 0.029751 0.0
2370266 11112.5 0.0 0.02973675 0.0
2370267 11749.5 0.0 0.0297315 0.0
2370268 11943.5 0.0 0.02977275 0.0
2370269 12059.5 0.0 0.02979825 0.0
2370270 12210.5 0.0 0.029865 0.0
2370271 12286.5 0.0 0.0298965 0.0
2370272 12378.5 0.0 0.0376185 0.0
2370273 12460.0 0.0 0.0377055 0.0
2370274 12536.0 0.0 0.037812 0.0
2370275 12619.5 0.0 0.03790275 0.0
2370276 12758.5 0.0 0.037884 0.0
2370277 13606.5 0.0 0.0359385 0.0
2370278 15001.5 0.0 0.038064 0.0
2370279 15316.5 0.0 0.038127 0.0
2370280 16231.5 0.0 0.037716 0.0
2370281 17703.0 0.0 0.03769425 0.0
2370282 17839.0 0.0 0.03773025 0.0
2370283 17928.5 0.0 0.0377625 0.0
2370284 18000.0 0.0 0.0377985 0.0
2370285 18158.5 0.0 0.04561425 0.0
2370286 18378.0 0.0 0.0457575 0.0
2370287 18619.5 0.0 0.04593 0.0
2370288 18978.0 0.0 0.0460485 0.0
2370289 19137.5 0.0 0.04582425 0.0
2370290 19318.5 0.0 0.04525275 0.0
2370291 19449.5 0.0 0.04456425 0.0
2370292 19522.0 0.0 0.04427325 0.0
2370293 19600.0 0.0 0.04405275 0.0
2370294 19723.0 0.0 0.04350825 0.0
2370295 19859.0 0.0 0.04301475 0.0
2370296 19975.0 0.0 0.04287375 0.0
*
* pressure in preimary loop
*
20220000 reac-t
20220001 0.0 210000.0
20220002 447.5 210400.0
20220003 523.5 210600.0
20220004 855.5 210100.0
20220005 895.5 210300.0
20220006 1042.5 210700.0
20220007 1121.0 210200.0
20220008 1121.5 210800.0
20220009 1343.0 210300.0
20220010 1345.0 210200.0
20220011 1791.0 210700.0
20220012 1996.5 210600.0
20220013 2239.0 210400.0
20220014 2686.5 210500.0
20220015 2994.0 210700.0
20220016 3134.5 210200.0
20220017 3256.5 210100.0
20220018 3582.5 210400.0
20220019 3678.0 210700.0
20220020 4030.0 210300.0
20220021 4421.0 210400.0
20220022 4478.0 210500.0
20220023 4926.0 210100.0
20220024 5327.5 210200.0
20220025 5373.5 210000.0
20220026 5596.5 210400.0
20220027 5619.0 209900.0
20220028 5821.5 210400.0
20220029 5957.0 209300.0
20220030 5957.5 209800.0
20220031 6269.5 210000.0
20220032 6717.0 210000.0
20220033 6952.0 209800.0
20220034 7165.0 209800.0
20220035 7613.0 209800.0
20220036 7714.0 209900.0
20220037 7763.5 210300.0
20220038 8060.5 210300.0
20220039 8508.5 209000.0
20220040 8518.0 209300.0
20220041 8568.0 208800.0
20220042 8956.5 209100.0
20220043 9341.0 209500.0
20220044 9404.0 209200.0
20220045 9450.0 209500.0
20220046 9450.5 208900.0
20220047 9852.0 208900.0
20220048 10076.0 208600.0
20220049 10300.0 209000.0
20220050 10393.0 208900.0
20220051 10546.0 208100.0
20220052 10570.5 209000.0
20220053 10581.0 208500.0
20220054 10747.5 208700.0
20220055 10843.5 208300.0
20220056 10844.0 208800.0
20220057 11195.5 208200.0
20220058 11643.0 208000.0
20220059 11696.0 208400.0
20220060 11944.5 208000.0
20220061 12091.0 207700.0
20220062 12539.0 207600.0
20220063 12945.5 207700.0
20220064 12986.5 207600.0
20220065 13434.5 207100.0
20220066 13534.5 207600.0
20220067 13663.0 207200.0
20220068 13882.5 206700.0
20220069 14330.0 206300.0
20220070 14738.5 205500.0
20220071 14778.0 205700.0
20220072 15226.0 205800.0
20220073 15583.0 205500.0
20220074 15673.5 205500.0
20220075 15756.0 205400.0
20220076 15916.0 205100.0
20220077 16121.5 205000.0
20220078 16327.0 204900.0
20220079 16341.5 204500.0
20220080 16569.5 204700.0
20220081 17017.0 204500.0
20220082 17465.0 204000.0
20220083 17762.0 203300.0
20220084 17913.0 203600.0
20220085 18360.5 203300.0
20220086 18367.0 203000.0
20220087 18808.5 203200.0
20220088 18845.5 203000.0
20220089 19256.5 202600.0
20220090 19593.5 202000.0
20220091 19594.0 202600.0
20220092 19704.0 202400.0
20220093 19811.5 202400.0
20220094 20152.0 201500.0
20220095 20600.0 200900.0
20220096 21047.5 201000.0
20220097 21176.0 200600.0
20220098 21495.5 201000.0
20220099 21943.5 200300.0
*
* pressure in RCST
* 
20220100 reac-t
20220101 0.0 195900.0
20220102 447.5 195900.0
20220103 895.5 195900.0
20220104 1343.0 196000.0
20220105 1736.0 196000.0
20220106 1791.0 196000.0
20220107 2239.0 196000.0
20220108 2686.5 196100.0
20220109 3134.5 196100.0
20220110 3582.5 196100.0
20220111 4030.0 196100.0
20220112 4046.0 196100.0
20220113 4382.0 196200.0
20220114 4382.5 196100.0
20220115 4398.0 196200.0
20220116 4400.0 196200.0
20220117 4409.5 196200.0
20220118 4411.0 196200.0
20220119 4414.5 196200.0
20220120 4416.0 196200.0
20220121 4418.5 196200.0
20220122 4422.0 196200.0
20220123 4422.5 196100.0
20220124 4423.0 196200.0
20220125 4425.0 196200.0
20220126 4432.0 196200.0
20220127 4436.0 196100.0
20220128 4437.5 196100.0
20220129 4438.0 196200.0
20220130 4465.0 196200.0
20220131 4478.0 196100.0
20220132 4926.0 196200.0
20220133 5373.5 196200.0
20220134 5821.5 196200.0
20220135 6086.5 196300.0
20220136 6269.5 196300.0
20220137 6717.0 196300.0
20220138 7165.0 196300.0
20220139 7613.0 196400.0
20220140 8060.5 196400.0
20220141 8339.0 196400.0
20220142 8340.5 196400.0
20220143 8344.5 196400.0
20220144 8356.0 196400.0
20220145 8508.5 196400.0
20220146 8956.5 196500.0
20220147 9404.0 196500.0
20220148 9852.0 196500.0
20220149 10300.0 196600.0
20220150 10445.5 196600.0
20220151 10460.5 196600.0
20220152 10747.5 196600.0
20220153 11195.5 196600.0
20220154 11643.0 196700.0
20220155 12091.0 196700.0
20220156 12367.5 196700.0
20220157 12369.5 196700.0
20220158 12373.5 196700.0
20220159 12377.0 196700.0
20220160 12388.0 196700.0
20220161 12389.5 196700.0
20220162 12539.0 196700.0
20220163 12986.5 196800.0
20220164 13434.5 196800.0
20220165 13882.5 196800.0
20220166 14330.0 196900.0
20220167 14778.0 196900.0
20220168 15226.0 196900.0
20220169 15673.5 197000.0
20220170 16121.5 197000.0
20220171 16569.5 197000.0
20220172 17017.0 197100.0
20220173 17465.0 197100.0
20220174 17913.0 197100.0
20220175 18360.5 197200.0
20220176 18808.5 197200.0
20220177 19256.5 197200.0
20220178 19657.0 197300.0
20220179 19671.0 197200.0
20220180 19671.5 197300.0
20220181 19676.0 197300.0
20220182 19679.0 197300.0
20220183 19679.5 197200.0
20220184 19680.0 197300.0
20220185 19682.5 197300.0
20220186 19684.5 197300.0
20220187 19692.5 197300.0
20220188 19696.0 197300.0
20220189 19698.0 197300.0
20220190 19702.0 197300.0
20220191 19704.0 197300.0
20220192 19727.0 197300.0
20220193 19732.5 197300.0
20220194 19735.5 197300.0
20220195 20152.0 197300.0
20220196 20600.0 197300.0
20220197 21047.5 197300.0
20220198 21495.5 197400.0
20220199 21943.5 197400.0
*
* Core delta T measured
20222000 reac-t
20222001 0.0 220.76165555555517
20222002 447.5 220.76165555555517
20222003 895.5 220.76165555555517
20222004 900.0 220.75339444444404
20222005 900.5 220.76165555555517
20222006 954.5 221.6704888888885
20222007 1343.0 223.78119999999885
20222008 1791.0 224.91817777777695
20222009 2239.0 225.72552777777668
20222010 2686.5 226.11400555555434
20222011 3134.5 226.4182833333323
20222012 3582.5 226.6851111111098
20222013 3778.5 226.76802777777698
20222014 4030.0 226.8890944444433
20222015 4478.0 227.10474444444384
20222016 4826.5 227.22904444444376
20222017 4926.0 227.24970555555512
20222018 5373.5 227.32569444444357
20222019 5761.5 227.4185055555548
20222020 5821.5 227.4301277777768
20222021 6269.5 228.01603888888778
20222022 6287.0 228.1076722222211
20222023 6689.0 230.629116666665
20222024 6717.0 230.82593333333165
20222025 7165.0 233.17255555555377
20222026 7613.0 233.17346666666617
20222027 8060.5 232.36298888888865
20222028 8258.5 231.74102222222197
20222029 8332.5 231.51696666666646
20222030 8508.5 231.15211666666642
20222031 8956.5 230.93952777777758
20222032 9404.0 230.54564999999945
20222033 9852.0 228.49126111111002
20222034 9948.5 227.90168888888755
20222035 10300.0 225.67764444444313
20222036 10732.0 222.80219444444307
20222037 10747.5 222.6890111111098
20222038 11195.5 219.58334999999917
20222039 11476.0 217.7663444444437
20222040 11643.0 216.78753333333282
20222041 11779.0 215.99048888888814
20222042 12017.5 214.6037777777764
20222043 12091.0 214.16930555555444
20222044 12274.5 213.1090111111106
20222045 12509.5 212.67323888888833
20222046 12539.0 212.72083333333282
20222047 12571.5 212.7805277777774
20222048 12986.5 213.6395722222215
20222049 13053.0 213.75061111111
20222050 13086.5 213.80276111111007
20222051 13434.5 212.89803888888736
20222052 13471.5 212.6118888888873
20222053 13689.5 210.79544444444318
20222054 13854.5 209.46149999999886
20222055 13882.5 209.25166666666556
20222056 13939.5 208.86099999999908
20222057 14330.0 207.03890555555463
20222058 14778.0 204.79312222222129
20222059 14927.5 203.45484444444355
20222060 15169.5 200.69359444444365
20222061 15184.5 200.50599999999918
20222062 15226.0 199.99627777777695
20222063 15673.5 194.72794444444386
20222064 15796.5 193.4621111111103
20222065 15870.0 192.7341666666659
20222066 16121.5 190.36544444444357
20222067 16569.5 186.50144444444337
20222068 16580.5 186.41211111110997
20222069 17017.0 182.83199999999943
20222070 17204.0 181.32016666666638
20222071 17465.0 179.2293333333327
20222072 17554.0 178.50983333333292
20222073 17913.0 175.61705555555528
20222074 18133.0 173.84699999999992
20222075 18344.0 172.16050000000018
20222076 18360.5 172.01700000000025
20222077 18493.0 170.78911111111125
20222078 18808.5 167.54638888888894
20222079 18811.5 167.51344444444456
20222080 18847.5 167.12711111111093
20222081 19045.0 164.85716666666625
20222082 19175.0 163.26466666666616
20222083 19205.5 162.90877777777732
20222084 19256.5 162.3176666666661
20222085 19340.0 161.37883333333286
20222086 19519.5 159.4462777777772
20222087 19704.0 157.55727777777727
20222088 19883.0 155.82305555555476
20222089 19945.0 155.27566666666584
20222090 20000.0 154.83416666666577
20222091 20036.5 154.5613888888881
20222092 20114.5 154.0592222222212
20222093 20152.0 153.86716666666587
20222094 20526.0 152.69983333333192
20222095 20549.5 152.64094444444297
20222096 20600.0 152.49405555555404
20222097 21047.5 149.87133333333202
20222098 21495.5 143.99061111111018
20222099 21943.5 138.39199999999894
*
* power in heater 101
*
20290100  power
20290101 0.0 0.0
*
* power in heater 102
*
20290200  power
20290201 0.0 0.0
*
* power in heater 103
*
20290300  power
20290301 0.0 0.0
*
* power in heater 104
*
20290400  power
20290401 0.0 0.0
*
* power in heater 105
*
20290500  power
20290501 0.0 0.0
*
* power in heater 106
*
20290600  power
20290601 0.0 0.0
*
* power in heater 107
*
20290700 power 
20290701 0.0 24234.75714
20290702 275.5 23779.17889
20290703 278.5 23756.1736
20290704 457.0 23679.98641
20290705 497.0 23848.08416
20290706 536.5 23919.41013
20290707 914.0 23701.36449
20290708 1065.5 23799.42146
20290709 1098.5 23951.54817
20290710 1115.5 24060.94939
20290711 1371.0 24450.15727
20290712 1543.0 23852.81494
20290713 1727.5 23769.33623
20290714 1808.5 23673.02429
20290715 1828.5 23611.62575
20290716 1898.0 23686.76038
20290717 1967.5 23801.20677
20290718 2081.0 23656.16601
20290719 2121.0 23683.88765
20290720 2285.5 24074.93254
20290721 2742.5 23561.55343
20290722 2836.0 23613.34254
20290723 3200.0 24095.83754
20290724 3657.0 23929.98135
20290725 3817.0 23540.02087
20290726 4114.0 23730.32443
20290727 4571.5 23544.15053
20290728 4943.5 23908.21495
20290729 5007.5 23930.85056
20290730 5028.5 24173.89419
20290731 5406.0 23867.11608
20290732 5458.5 23819.83294
20290733 5476.0 23580.47775
20290734 5485.5 23753.30207
20290735 5943.0 23492.27246
20290736 6319.5 23602.69077
20290737 6400.0 23225.65548
20290738 6857.0 23204.93683
20290739 7314.5 23676.06714
20290740 7771.5 23559.41947
20290741 8228.5 23419.93542
20290742 8685.5 23081.58732
20290743 9143.0 23049.8911
20290744 9207.5 23019.89724
20290745 9227.5 22706.27843
20290746 9228.0 22831.35014
20290747 9600.0 22828.32352
20290748 10057.0 22990.96555
20290749 10514.5 22853.27583
20290750 10971.5 22709.18363
20290751 11286.0 22933.46103
20290752 11428.5 22462.17143
20290753 11545.0 22720.61985
20290754 11546.0 22483.49119
20290755 11576.5 22887.86582
20290756 11775.5 22730.44989
20290757 11886.0 22708.40278
20290758 11989.0 22814.45458
20290759 12343.0 23229.85006
20290760 12800.0 22799.77895
20290761 13257.5 22702.90017
20290762 13697.5 22532.44604
20290763 13714.5 22565.73101
20290764 14171.5 22567.3949
20290765 14578.5 22535.61512
20290766 14588.0 22473.73629
20290767 14590.5 22391.71648
20290768 14629.0 22858.84576
20290769 14716.5 22503.00521
20290770 14755.5 22839.23257
20290771 15086.0 23071.59859
20290772 15543.0 22707.29432
20290773 16000.0 23276.76112
20290774 16457.5 23387.9723
20290775 16914.5 23204.30506
20290776 17371.5 23264.75143
20290777 17829.0 23394.88994
20290778 18286.0 23556.6345
20290779 18604.0 23293.186
20290780 18743.0 23388.50008
20290781 19199.0 22935.77533
20290782 19200.5 23114.16117
20290783 19307.5 22985.70338
20290784 19364.0 23122.29246
20290785 19431.0 23052.45125
20290786 19657.5 23205.94009
20290787 20114.5 22807.49487
20290788 20161.0 22973.70512
20290789 20318.5 23163.71774
20290790 20572.0 22742.32974
20290791 20620.5 22905.25008
20290792 20643.0 23098.99563
20290793 21029.0 23442.41113
20290794 21486.0 23416.56496
20290795 21665.5 23366.30329
20290796 21666.0 23273.1941
20290797 21943.5 22922.24963
*
* power in heater 108
*
20290800  power
20290801 0.0 0.0
*
* power in heater 109
*
20290900  power
20290901 0.0 0.0
*
* power in heater 110
*
20291000  power
20291001 0.0 0.0
*
.