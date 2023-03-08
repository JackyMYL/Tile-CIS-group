############################################################
#
# ReadLaserHV_REF.py
#
###########################################################################
#
# Author: Andrey Kamenshchikov <akamensh@cern.ch>
#
# 27.05.2013
#
# Functionality:
#	Read HV references from ASCII files.
#
# Options:
#	folder - String describes folder with files (initialized 
#	by default)
#
# Data keys:
#	HV_REF - HV reference for given region (float);
#
###########################################################################

from src.ReadGenericCalibration import *
from src.run import *
import random
import time

# For using the LASER tools
from src.laser.toolbox import *


class ReadLaserHV_REF(ReadGenericCalibration):
    "The Laser HV Reference Data Reader"


    def __init__(self, folder="/afs/cern.ch/user/t/tilecali/w0/ntuples/cs/2009/hv/"):
        self.PMTool         = LaserTools()
        self.folder=folder
        return


    def ProcessRegion(self, region):

        for event in region.GetEvents():
            if len(event.region.GetNumber(1))==3:
                [part, mod, pmt]=event.region.GetNumber(1)
            elif len(event.region.GetNumber(1))==4:
                [part, mod, pmt, gain]=event.region.GetNumber(1)
            else:
                continue
                
            str_mod='%02i' % (mod)
            filestring=self.folder+self.PMTool.get_partition_name(part-1)+str_mod+".hv"
            f = open(filestring)
            n=0
            for line in f:
                n+=1
                if n==abs(pmt):
                    event.data['HV_REF']=float(line)
        return    
