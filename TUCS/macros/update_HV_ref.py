#!/usr/bin/env python
#######################################################################################
#
# update_HV_ref.py
#
#######################################################################################
# Description:
# For renew the HV reference values in cesium folder of COOL db
#######################################################################################
#
# Author: Andrey Kamenshchikov <akamensh@cern.ch>
#
#######################################################################################

import os, sys
print sys.argv
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

runnumber=0
r = ReadLaserHV_DCS()
HV_datafield='DCS_HV_PREV'
if (len(sys.argv)>1):
    runnumber=int(sys.argv[1])
else:
    print "Run number is not inserted - use 0 by defult!"
if (len(sys.argv)>2):
    HV_datafield=str(sys.argv[2])
    if "DCS" in HV_datafield:
        r = ReadLaserHV_DCS()
    elif "REF" in HV_datafield:
        #r = ReadLaserHV_REF(folder="hv/")
        r = ReadLaserHV_REF()
        HV_datafield='HV_REF'
    elif "COOL" in HV_datafield:
        r = ReadLaserHV_COOL()
else:
    print "HV data field is not inserted - use 'DCS_HV_PREV' by default!"

u = Use(runnumber,keepOnlyActive=False)
w = WriteDB(useSqliteRef=True,runType='cesium',reprocessingstep=1,runNumber=runnumber,offline_tag='RUN2-HLT-UPD1-01',version=2,\
                writeHV=True,write_badHV=False,allowZeroHV=False,skipMBTS=False,HV_datakey=HV_datafield,maxHVdiff=40)
p = Print()
processors = [ u, r, w, p ]
Go(processors,withMBTS=False)
