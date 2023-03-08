#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Cora Fischer
#
# A Mbias macro to produce current over inst. lumi plots
#

import os, sys
os.chdir(os.getenv('TUCS','.'))

exec(open('src/mbias/getDatesForCool.py').read(), globals())

exec(open('src/load.py').read(), globals()) # don't remove this!


# if you want the current for a specific cell averaged over A and C side and all modules, specify --region="Cellname" in command line, if you want the current of a special pmt, then give region as usual in
# format part_mXX_cXX, if you do not specify anything, the default selected_region EBC_m40_c12_highgain will be analysed (no particular reason for that), so please specify a region!
# you can specify the number of consecutive entries to average over by --num=X, or if you choose 1 it will not average
# the command line reads: python macros/mbias/plotPMTCurrentVsInstLumi.py --region="XXX" --num=X
# runs are fixed for the moment....

if region.startswith("EB") or region.startswith("LB"): # if partition is given but nothing else
   if 'm' not in region or 'c' not in region:
        print "you have to specify a module and channel if you don't give a cell name!"
        sys.exit(2)

runs =[]

#selected_region = "EBC_m40_c12_highgain" #just any region
selected_region = region
Cell = None
print region 
#distinguish different kind of inputs: specific pmts (Part_mXX_cXX) and cells
if "m" in region:
   selected_region=region
else:
   Cell = region 
print Cell

runs.append(298633)
#runs.append(298687)
#runs.append(298690)
#runs.append(298771)
#runs.append(298773)
#runs.append(298862)
#runs.append(298967)

flag2015 = True
"""
#runs.append(201269)
#runs.append(201289)
#runs.append(202660)
#runs.append(202789)
#runs.append(203027)
#runs.append(203258)
#runs.append(203336)
#runs.append(203353)
#runs.append(203719)
	
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
runs.append(202660)#b
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


runs.append(295147)
runs.append(295213)
runs.append(297041)
runs.append(297083)
runs.append(297170)
runs.append(297447)
runs.append(297931)
runs.append(298595)
runs.append(298609)
runs.append(298633)
runs.append(298687)
runs.append(298690)
runs.append(298771)
runs.append(298773)
runs.append(298862)
runs.append(298967)
runs.append(299055)
runs.append(299144)
runs.append(299147)
runs.append(299184)
runs.append(299241)
runs.append(299243)
runs.append(299278)
runs.append(299288)
runs.append(299315)
runs.append(299340)
runs.append(299343)
runs.append(299390)
runs.append(299584)
runs.append(300279)
runs.append(300287)
runs.append(300345)
runs.append(300415)
runs.append(300418)
runs.append(300487)
runs.append(300540)
runs.append(300571)
runs.append(300600)
runs.append(300687)
runs.append(300784)
runs.append(300800)
runs.append(300863)
runs.append(300908)
runs.append(301912)
runs.append(301932)
"""

#runs = '2015-05-01'
#runs2 = '2012-12-31'
run_type = "MBias" 

#Go([ 
#      Use(run=runs, region=selected_region, runType=run_type),
#      ReadMBias_2016(processingDir="/afs/cern.ch/user/t/tilecali/w0/ntuples/mbias/2016/first_data/", doSingleRun=False, doRatio=False, checkCell=Cell),
#      PlotPMTCurrentVsInstLumi_2016(checkCell=Cell, num_average=num),
#      ])



if not flag2015:

   Go([ 
         Use(run=runs, run2=runs2, region=selected_region, runType=run_type),
         ReadMBias(doSingleRun=False, doRatio=False, checkCell=Cell),
         PlotPMTCurrentVsInstLumi(checkCell=Cell, num_average=num),
         ])
else:

   Go([ 
         Use(run=runs, region=selected_region, runType=run_type),
         ReadMBias_2015(doSingleRun=True, doRatio=False, checkCell=Cell),
         PlotPMTCurrentVsInstLumi_2015(checkCell=Cell, num_average=num),
         ])



