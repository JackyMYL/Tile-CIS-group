#!/usr/bin/env python
# Author: Cora Fischer
#
# for each run, plot PMT current ratio of A13/D5 distribution, fit with gaussian, plot as function of time
#

import os


exec(open('src/mbias/getDatesForCool.py').read(), globals())
#exec(open('src/laser/laserGetOpt.py').read(), globals())
exec(open('src/load.py').read(), globals()) # don't remove this!

#print region

runs =[]
 	
#runs.append(208485)
#runs.append(206955)
#runs.append(215456)
#runs.append(213796)

#runs.append(200863)
#runs.append(202668)
#runs.append(202712)
#runs.append(203027)
#runs.append(204071)
#runs.append(204265)
#runs.append(207582)
#runs.append(208982)
#runs.append(209787)
#runs.append(210308)
#runs.append(213250)
#runs.append(213951)
#runs.append(214176)
#runs.append(214721)
#runs.append(214758)

#62 out of 64 modules have good entries EBA
#runs.append(213796)
#runs.append(203779)
#runs.append(202798)
#runs.append(206971)
#runs.append(203353)
#runs.append(202660)
#runs.append(207982)
#runs.append(206962)
#runs.append(200863)#c
#61 out of 64 modules have good entries EBA (ch 16 for D5)
#runs.append(200863)
#runs.append(201257)
#runs.append(202660)
#runs.append(202668)
#runs.append(202798)
#runs.append(203353)
#runs.append(203779)
#runs.append(204026)
#runs.append(206253)
#runs.append(206564)
#runs.append(206962)
#runs.append(206971)
#runs.append(207221)
#runs.append(207304)
#runs.append(207809)
#runs.append(207982)
#runs.append(208811)
#runs.append(209109)
#runs.append(209899)
#runs.append(212858)
#runs.append(213796)
#runs.append(214680)


#63 out of 64 modules have good entries EBC
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
#runs.append(202660)#b
#runs.append(213900)
#runs.append(203258)
#runs.append(207696)
#runs.append(206253)

#runs.append(215473)
##runs.append(206848)# no events??
#runs.append(204265)
#doSingleRun = False
#if len(runs) == 1: doSingleRun =True
#runs = '2012-04-01' 

#runs.append(266904)
#runs.append(266919)
##runs.append(267073)
##runs.append(267148)
#runs.append(267152)
##runs.append(267162)
#runs.append(267167)
#runs.append(267359)
#runs.append(267358)

##runs.append(267360)
##runs.append(267367)
##runs.append(267385)
##runs.append(267599) 

#runs.append(267638)
#runs.append(267639)

#runs.append(270448)
##not in new grl
#runs.append(270588)
#runs.append(270953)
#runs.append(271048)
#runs.append(271298)
#
###runs.append(271421)
#runs.append(271516)
#runs.append(271595)
#runs.append(271744)
#runs.append(272531)
#
#runs.append(276336)
#runs.append(276330)
#runs.append(276329)
#
#runs.append(276262)
#runs.append(276245)
###runs.append(276212)
#runs.append(276189)
#runs.append(276181)
##runs.append(276161)
##runs.append(276147)
#runs.append(276073)
#runs.append(276416) 
#runs.append(276511) 
#runs.append(276689)
#runs.append(276731) 
#runs.append(276778)
#runs.append(276790)
##new
#runs.append(276952)
#runs.append(276954)
##runs.append(278880)
#runs.append(278912)
#runs.append(279169)
#runs.append(279279)
#runs.append(279284)
#runs.append(279345)
#runs.append(279515)
##runs.append(279598)
#runs.append(279813)
#runs.append(279867)
#runs.append(280231)
#runs.append(280319)
#runs.append(280423)
#runs.append(280464)
#runs.append(280500)
#runs.append(280520)
#runs.append(280614)
#runs.append(280673)
#runs.append(280753)
#runs.append(280853)
#runs.append(280862)
#runs.append(280977)
#runs.append(281070)
#runs.append(281075)
#
#runs.append(281317)
#runs.append(281385)
##runs.append(281411)
##runs.append(282625)
#runs.append(282631)
#runs.append(282712)
#runs.append(282784)
##runs.append(282992)
#runs.append(283074)
#runs.append(283155)
#runs.append(283270)
#runs.append(283429)
#runs.append(283608)
#runs.append(283780)
#runs.append(284006)
#runs.append(284154)
##runs.append(284213)
#runs.append(284285)
#runs.append(284420)
#runs.append(284427)
#runs.append(284484)

#runs.append(296939)
#runs.append(298633)

#runs.append(294984)
#runs.append(295109)
#runs.append(295147)
#runs.append(295213)
#runs.append(295252)

##In GRL
##runs.append(296939)
##runs.append(296942)
##runs.append(297041)
##runs.append(297083)
##runs.append(297170)
###runs.append(297447)#Wrong gains setting; E-cells saturated.
###below gain 1 used
##runs.append(297931)
##From here OK for D1
#runs.append(298595)
#runs.append(298609)
#runs.append(298633)
#runs.append(298687)
#runs.append(298690)
#runs.append(298771)
#runs.append(298773)
##runs.append(298862)#VdM-esque?
#runs.append(298967)
#runs.append(299055)
#runs.append(299144)
#runs.append(299147)
#runs.append(299184)
#runs.append(299241)#low stats
##runs.append(299243)#low stats, large spread
##runs.append(299278)
##runs.append(299288)
##runs.append(299315)#VdM
##runs.append(299340)#tiny
##runs.append(299343)#odd
##runs.append(299390)#VdM
#runs.append(299584)
#runs.append(300279)
##runs.append(300287)#VdM for CMS
##runs.append(300345)#low stats
#runs.append(300415)
##runs.append(300418)#lowstats
#runs.append(300487)
#runs.append(300540)
#runs.append(300571)
#runs.append(300600)
#runs.append(300687)
#runs.append(300784)
#runs.append(300800)
#runs.append(300863)
#runs.append(300908)
##new from Loic
#runs.append(301932)
#runs.append(301973)
#runs.append(302053)
#runs.append(302137)
#runs.append(302300)
#runs.append(302347)
#runs.append(302393)
#runs.append(302829)
#runs.append(302872)

#######GRL from 01.08.16
###runs.append(297730)##NA   #not OK for D1 
###runs.append(298595)##163 #07.may.16
##runs.append(298609)##314 #07.may.16
##runs.append(298633)##687
##runs.append(298687)##480
###runs.append(298690)##46
###runs.append(298771)##166
###runs.append(298773)##160
###runs.append(298862)##663 #VdM-esque
##runs.append(298967)##582
##runs.append(299055)##555
##runs.append(299144)##422
###runs.append(299147)##329
##runs.append(299184)##768
###runs.append(299241)##150  #low stats
###runs.append(299243)##119  #low stats, large spread
###runs.append(299278)##201
##runs.append(299288)##461
###runs.append(299315)##582 #VdM
###runs.append(299340)##118 #tiny
###runs.append(299343)##112 #odd
###runs.append(299390)##464 #VdM
###commented the above
runs.append(299584)##2206 ##May20
#runs.append(300279)##115
#runs.append(300287)##413 #CMS VdM
#runs.append(300345)##53 #low stats
runs.append(300415)##517 
#runs.append(300418)##50 #low stat
runs.append(300487)##591
runs.append(300540)##783
runs.append(300571)##523
runs.append(300600)##177
#runs.append(300655)##NA
runs.append(300687)##1131
runs.append(300784)##33
runs.append(300800)##882
runs.append(300863)##1105
runs.append(300908)##694
#runs.append(301912)##NA
#runs.append(301915)##NA
#runs.append(301918)##NA
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
runs.append(302829)##1531
runs.append(302831)##117
runs.append(302872)##2427
runs.append(302919)##325
runs.append(302925)##372
runs.append(302956)##968
runs.append(303007)##46
runs.append(303059)##205
runs.append(303079)##279
runs.append(303201)##243
runs.append(303208)##1609
runs.append(303264)##165
runs.append(303266)##800
runs.append(303291)##421
runs.append(303304)##1486
runs.append(303338)##1585
#runs.append(303421)##NA
runs.append(303499)##1396
runs.append(303560)##873
runs.append(303638)##1380
runs.append(303726)##754
runs.append(303811)##227
#runs.append(303817)##NA
#runs.append(303819)##NA
runs.append(303832)##407
runs.append(303846)##1607
runs.append(303892)##1473
runs.append(303943)##1419
runs.append(304006)##352
runs.append(304008)##1335
#runs.append(304128)##NA
runs.append(304178)##1210
runs.append(304198)##407
runs.append(304211)##296
runs.append(304243)##1051
runs.append(304308)##66
runs.append(304337)##1082
runs.append(304409)##209
runs.append(304431)##289
runs.append(304494)##116
#runs.append(305293)##NA
runs.append(305359)##405
##postGRL
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
#runs.append(306556)
#runs.append(306655)
#runs.append(306714)
#runs.append(307195)
#runs.append(307259)
#runs.append(307354)
#runs.append(307454)
#runs.append(307569)
#runs.append(307656)
#runs.append(307732)
#runs.append(307861)
#runs.append(307935)
#runs.append(308047)
#runs.append(308084)
runs.append(307195)
runs.append(307259)
runs.append(307358)
runs.append(307454)
runs.append(307569)
runs.append(307601)
runs.append(307656)
runs.append(307732)
runs.append(307861)
runs.append(307935)
runs.append(308047)
runs.append(308084)
runs.append(309375)
runs.append(309390)
runs.append(309440)
runs.append(309516)
runs.append(309640)
runs.append(309674)
runs.append(309759)

##runs.append(305920)

##LIst for run-by-run comparison

##commented the above
#runs.append(299584)##2206 ##May20
#runs.append(300415)##517 
#runs.append(301932)##1335
#runs.append(304178)##1210
#runs.append(306278)##1022

runs = []
#runs.append(299584)
#runs.append(307569)
runs.append(298633)

#runs = '2015-06-01'
run_type = "MBias" 
selected_region ="EBC_m01_c11_highgain" #
#selected_region = region#"EBA_m01_c17_highgain" #here, if doRatio: only partition and channel important
singleChannel = True # if this is true and detector region is given: average over modules for given channel above, modnum=64, here: all information is saved and written to text file
detectorRegion = region #"A13" # if you want to use the same as selected_region, leave this variable to None, but better use this option, otherwise it only takes one PMT channel
side = None #you can also specify if you want only A or C-side analysed, if you leave it empty, it will average over both sides
referenceCell = "D6"
processors = []

Go([
    Use(run=runs, region=selected_region, runType=run_type),
    #ReadMBias_2015(processingDir="/afs/cern.ch/user/t/tilecali/w0/ntuples/mbias/2016/first_data/",doSingleRun=False, doRatio = True, modnum=64, detector_region=detectorRegion, detector_side=side, refCell=referenceCell, singleChannel=singleChannel),
    ReadMBias_2015(processingDir="/afs/cern.ch/work/t/tilmbias/public/2016/",doSingleRun=False, doRatio = True, modnum=64, detector_region=detectorRegion, detector_side=side, refCell=referenceCell, singleChannel=singleChannel),
    PlotRatioPMTsVsTime_2015perModule(modnum=64, detector_region=detectorRegion,refCell=referenceCell),
   ])
