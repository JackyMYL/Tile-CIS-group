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

#runs.append(201269)
#runs.append(201289)
runs.append(202660)
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
runs.append(207490)
runs.append(209899)
runs.append(203027)#c
runs.append(210302)
runs.append(209787)#c
runs.append(212172)
runs.append(202668)#c
runs.append(204955)
runs.append(203277)
runs.append(209995)
runs.append(214777)
runs.append(207306)
runs.append(206248)
runs.append(203636)
runs.append(212144)
runs.append(209183)
runs.append(202798)#b
runs.append(214390)
runs.append(212967)
runs.append(215473)
runs.append(200863)#c#b
runs.append(213900)
runs.append(203258)
runs.append(207696)
runs.append(206253)


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


runs = '2012-04-01'
runs2 = '2012-12-31' # for some reason no effect for us, we have a requirement on the runNumber in the worker to avoid crashes
run_type = "MBias" 

#now we loop over all cells when calling the worker GetLumiCoefficient.py
processors = []

processors.append(Use(run=runs, run2=runs2, region=selected_region, runType=run_type))
processors.append(ReadMBias(doSingleRun=False, doRatio=False, checkCell=Cell))
processors.append(GetLumiCoefficient(checkCell=Cell,num_average=num))


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


if not flag2015:

   Go(processors)

else:

   Go([ 
         Use(run=runs, region=selected_region, runType=run_type),
         ReadMBias(processingDir="/afs/cern.ch/user/t/tilecali/w0/ntuples/mbias/2015/first_data/", doSingleRun=False, doRatio=False, checkCell=Cell),
         PlotPMTCurrentVsInstLumi_2015(checkCell=Cell, num_average=num),
         ])



