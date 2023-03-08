#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Cora Fischer
#
# A Mbias macro to produce plots: lumi coefficient vs eta for A,BC,D and E cells
#

import os, sys
os.chdir(os.getenv('TUCS','.'))

exec(open('src/mbias/getDatesForCool.py').read(), globals())

exec(open('src/load.py').read(), globals()) # don't remove this!


# the region is not given by the user, we use all the cells we have to produce the plot
# the command line reads: python macros/mbias/getCoeffficient.py --region=cellName

runs =[]

selected_region = "EBC_m40_c12_highgain" #just any region

print region
Cell = region # input from command line
print Cell


flag2015 = False
flag2015_no = False
flag2016 = True
#runs.append(201269)
#runs.append(201289)
#runs.append(202660)
#runs.append(202789)
#runs.append(203027)
#runs.append(203258)
#runs.append(203336)
#runs.append(203353)
#runs.append(203719)#
	
#runs.append(206955)
#runs.append(215456)
#runs.append(202668)
#runs.append(201257)

#these runs in 2012
#runs.append(207490)
#runs.append(209899)
#runs.append(203027)#c
#runs.append(210302)
#runs.append(209787)#c
#runs.append(212172)
#runs.append(202668)#c
#runs.append(204955)
#runs.append(203277)
#runs.append(209995)
#runs.append(214777)
#runs.append(207306)
#runs.append(206248)
#runs.append(203636)
#runs.append(212144)
#runs.append(209183)
#runs.append(202798)#b
#runs.append(214390)
#runs.append(212967)
#runs.append(215473)
#runs.append(200863)#c#b
#runs.append(213900)
#runs.append(203258)
#runs.append(207696)
#runs.append(206253)


#runs.append(266904)
#runs.append(266919)
#runs.append(267073)
#runs.append(267152)
#runs.append(267638)
#runs.append(267639)
#runs.append(270448)
#runs.append(270588)
#runs.append(270953)
#runs.append(271048)
#runs.append(271298)
##runs.append(271421)
#runs.append(271516)
#runs.append(271595)
#runs.append(271744)
#runs.append(272531)


#runs.append(276336)
#runs.append(276330)
#runs.append(276329)
#runs.append(276262)
#runs.append(276245)
#runs.append(276212)
#runs.append(276189)
#runs.append(276181)
#runs.append(276161)
#runs.append(276147)
#runs.append(276073)

#runs.append(270448)
#runs.append(270588)
#runs.append(270953)
#runs.append(271048)
#runs.append(271298)
##runs.append(271421)
#runs.append(271516)
#runs.append(271595)
#runs.append(271744)
#runs.append(272531)

#runs.append(276336)
#runs.append(276330)
#runs.append(276329)
#runs.append(276262)
#runs.append(276245)
#runs.append(276212)
#runs.append(276189)
#runs.append(276181)
#runs.append(276161)
#runs.append(276147)
#runs.append(276073)
#runs.append(276416) 
#runs.append(276511) 
#runs.append(276689)
#runs.append(276731) 
#runs.append(276778)
#runs.append(276790)
##Good 2015 data
if flag2015:

  runs.append(276336)
  runs.append(276330)
  runs.append(276329)
  runs.append(276262)
  runs.append(276245)
  #runs.append(276212)
  runs.append(276189)
  runs.append(276181)
  #runs.append(276161)
  #runs.append(276147)
  runs.append(276073)
  runs.append(276416)
  runs.append(276511)
  runs.append(276689)
  runs.append(276731)
  #runs.append(276778)
  #runs.append(276790)
  runs.append(276952)
  #runs.append(276954)
  runs.append(278880)
  runs.append(278912)
  runs.append(279169)
  #runs.append(279259)
  runs.append(279279)
  runs.append(279284)
  runs.append(279345)
  runs.append(279515)
  runs.append(279598)
  runs.append(279813)
  runs.append(279867)
  runs.append(280231)
  runs.append(280319)
  runs.append(280423)
  runs.append(280464)
  runs.append(280500)
  runs.append(280520)
  runs.append(280614)
  runs.append(280673)
  runs.append(280753)
  runs.append(280853)
  runs.append(280862)
  runs.append(280977)
  runs.append(281070)
  runs.append(281075)
  runs.append(281317)
  runs.append(281385)
  #runs.append(281411)                                                                                                                                  
  #runs.append(282625)                                                                                                                                  
  runs.append(282631)
  runs.append(282712)
  runs.append(282784)
  #runs.append(282992)                                                                                                                                  
  runs.append(283074)
  runs.append(283155)
  runs.append(283270)
  runs.append(283429)
  runs.append(283608)
  runs.append(283780)
  runs.append(284006)
  runs.append(284154)
  #runs.append(284213)                                                                                                                                  
  runs.append(284285)
  runs.append(284420)
  runs.append(284427)
  runs.append(284484)


if flag2016:

  runs.append(298633)
  """
  runs.append(299584)##2206 ##May20
  runs.append(300415)##517
  runs.append(300487)##591
  runs.append(300540)##783
  runs.append(300571)##523
  runs.append(300600)##177
  runs.append(300687)##1131
  runs.append(300784)##33
  runs.append(300800)##882
  runs.append(300863)##1105
  runs.append(300908)##694                                                                                                                                                                                        
  runs.append(301932)##1335
  runs.append(301973)##1689
  runs.append(302053)##1173
  runs.append(302137)##558
  runs.append(302265)##379
  runs.append(302269)##183
  runs.append(302300)##1532
  runs.append(302347)##572
  runs.append(302380)##269                             
  runs.append(302391)##358
  runs.append(302393)##1801
  runs.append(302737)##214
#  runs.append(302829)##1531
  runs.append(302831)##117
  runs.append(302872)##2427
  runs.append(302919)##325
  runs.append(302925)##372
  runs.append(302956)##968
  runs.append(303007)##46
#  runs.append(303059)##205
  runs.append(303079)##279
  runs.append(303201)##243
  runs.append(303208)##1609
  runs.append(303264)##165
  runs.append(303266)##800
  runs.append(303291)##421
  runs.append(303304)##1486
  runs.append(303338)##1585
  runs.append(303499)##1396
  runs.append(303560)##873
  runs.append(303638)##1380
#  runs.append(303726)##754
#  runs.append(303811)##227 
  runs.append(303832)##407
  runs.append(303846)##1607 
  runs.append(303892)##1473
  runs.append(303943)##1419
  runs.append(304006)##352
  runs.append(304008)##1335 
  runs.append(304178)##1210 
  runs.append(304198)##407
  runs.append(304211)##296
  runs.append(304243)##1051
  runs.append(304308)##66
  runs.append(304337)##1082
  runs.append(304409)##209
  runs.append(304431)##289
  runs.append(304494)##116
#  runs.append(305359)##405
  runs.append(305380)##694
  runs.append(305543)##926
  runs.append(305618)##811
  runs.append(305723)##770
  runs.append(305777)##838
  runs.append(305811)##648
  runs.append(305920)##594
  runs.append(306269)##335
  runs.append(306278)##1022
  runs.append(306384)##558
  runs.append(306451)##881       
  """

#runs = '2015-06-10'
#runs2 = '2015-11-02' # for some reason no effect for us, we have a requirement on the runNumber in the worker to avoid crashes
run_type = "MBias" 

#now we loop over all cells when calling the worker GetLumiCoefficient.py
processors = []

processors.append(Use(run=runs,region=selected_region, runType=run_type))
processors.append(ReadMBias_2015(doSingleRun=False, doRatio=False, checkCell=Cell))
processors.append(GetLumiCoefficient_2015(checkCell=Cell))


#A cells

#for i in range(1,2):
#   cellName="A"+str(i)
#   print cellName
#   processors.append(ReadMBias(doSingleRun=False, doRatio=False, checkCell=cellName))
#   processors.append(GetLumiCoefficient(checkCell=cellName))

#BC cells

#for i in range(1,9):
#   cellName="BC"+str(i)
#   print cellName
#   processors.append(ReadMBias(doSingleRun=False, doRatio=False, checkCell=cellName))
#   processors.append(GetLumiCoefficient(checkCell=cellName))

#for i in range(9,16):
#   cellName="B"+str(i)
#   if i=10: cellName="C"+str(i)
#   print cellName
#   processors.append(ReadMBias(doSingleRun=False, doRatio=False, checkCell=cellName))
#   processors.append(GetLumiCoefficient(checkCell=cellName))

#D cells

#for i in range(1,7):
#   cellName="D"+str(i)
#   print cellName
#   processors.append(ReadMBias(doSingleRun=False, doRatio=False, checkCell=cellName))
#   processors.append(GetLumiCoefficient(checkCell=cellName))

#E cells

#for i in range(1,5):
#   cellName="E"+str(i)
#   print cellName
#   processors.append(ReadMBias(doSingleRun=False, doRatio=False, checkCell=cellName))
#   processors.append(GetLumiCoefficient(checkCell=cellName))


# final worker that will produce the plots from the inputs
#processors.append(PlotCoefficientVsEta())



Go(processors)




