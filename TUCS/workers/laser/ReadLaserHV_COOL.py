#######################################################################################
#
# ReadLaserHV_COOL.py
#
#######################################################################################
#
# Author: Andrey Kamenshchikov <akamensh@cern.ch>
#
# 27.05.2013
#
# Functionality:
#    Read HV (HVSET) information from COOL with IOV covering 
#    start- and end- time of current run and add new 
#    data to event.
#
# Options:
#    constring - String of connection to COOL (initialized 
#    by default)
#    foldstring - String of folder in COOL (initialized 
#    by default): if */HV - suffix='HV', if */HVSET - suffix='HVSET'
#
# Data keys:
#    COOL_+suffix+_PREV - suffix with IOV covering run.time(start time) (float);
#    COOL_+suffix+_PREV_IOV - IOV of COOL_+suffix+_PREV in localtime (string);
#    COOL_+suffix+_NEXT - suffix with IOV covering run.endtime (end time)(float);
#    COOL_+suffix+_NEXT_IOV - IOV of COOL_+suffix+_NEXT in localtime (string).
#
#######################################################################################

from src.ReadGenericCalibration import *
from src.run import *
from src.oscalls import *
import random
from datetime import datetime, timedelta
import time
from PyCool import cool

# For using the LASER tools
from src.laser.toolbox import *

# For using the COOL tools
from CoolConvUtilities.AtlCoolTool import connect

class ReadLaserHV_COOL(ReadGenericCalibration):
    "The Laser HV COOL Data Reader"


    def __init__(self, constring="oracle://ATLAS_COOLPROD;schema=ATLAS_COOLOFL_DCS;dbname=CONDBR2", foldstring="/TILE/DCS/HV"):
        self.PMTool         = LaserTools()
        self.constring=constring
        self.foldstring=foldstring
        return

    def ProcessStart(self):

        ######
        ### Open up a DB connection
        ######

        try:
            dbstring = self.constring
            db, connectString = connect( dbstring )
            print("Connected to COOL successfully")
            self.coolFolder = db.getFolder(self.foldstring)
        except Exception as e:
            print("ReadCalFromDCS: Failed to open a COOL database connection")
            print(e)
            sys.exit(-1)
        
        ######
        ### Open up a PartDrawer-channel mapping file (recieved from COOL: "listchans /TILE/DCS/HV") and load appropriate dictionary
        ######

        suffix=(self.foldstring).split("/")[3]
        RUN2=('CONDBR2' in self.constring)
        if suffix=="HVSET":
            if (RUN2):
                f = open(os.path.join(getTucsDirectory(),"data/DCSChHVSETInCOOLR2_a.dat"))
            else:
                f = open(os.path.join(getTucsDirectory(),"data/DCSChHVSETInCOOL_a.dat"))
        else:
            if (RUN2):
                f = open(os.path.join(getTucsDirectory(),"data/DCSChHVInCOOLR2_a.dat"))
            else:
                f = open(os.path.join(getTucsDirectory(),"data/DCSChHVInCOOL_a.dat"))
        
        
        self.PartDrawer_channel={}
        try:
            for line in f:
                parts=line.split(" ");
                self.PartDrawer_channel[parts[2]]=int(parts[1])
        except:
            print("Mapping's reading failed")
        
        finally:
            f.close()
        return


    def ProcessRegion(self, region):

        unix2cool = 1000000000
        for event in region.GetEvents():
            if len(region.GetNumber())==3:
                [part, mod, chan]=region.GetNumber()
            elif len(region.GetNumber())==4:
                [part, mod, chan, gain]=region.GetNumber()
            else:
                continue

            suffix=(self.foldstring).split("/")[3]
            str1={2: "ATLTILLV02_Drawer",1: "ATLTILLV01_Drawer",3: "ATLTILLV00_Drawer",4: "ATLTILLV03_Drawer"}
            pmt=self.PMTool.get_PMT_index(part-1,mod-1,chan)
            str_PartDrawer=str1[part]+str(mod)
            channel=self.PartDrawer_channel[str_PartDrawer]
            if suffix=="HVSET":
                Cool_pmt="hvOut"+str(abs(pmt))
            else:
                Cool_pmt="HVOUT"+str(abs(pmt))

            t1_dt=time.strptime(event.run.time,"%Y-%m-%d %H:%M:%S")
            t1_ValKey=cool.ValidityKey(int(time.mktime(t1_dt))*unix2cool)
            obj1 = self.coolFolder.findObject(t1_ValKey,channel)
            payload1 = obj1.payload()
            (since_struct_1, until_struct_1)=(time.localtime(obj1.since()//unix2cool), time.localtime(obj1.until()//unix2cool))
            (since_1, until_1)=(strftime("%Y-%m-%d %H:%M:%S",since_struct_1), strftime("%Y-%m-%d %H:%M:%S", until_struct_1))
            
            t2_dt=time.strptime(event.run.endtime,"%Y-%m-%d %H:%M:%S")
            t2_ValKey=cool.ValidityKey(int(time.mktime(t2_dt))*unix2cool)
            obj2 = self.coolFolder.findObject(t2_ValKey,channel)
            payload2 = obj2.payload()
            (since_struct_2, until_struct_2)=(time.localtime(obj2.since()//unix2cool), time.localtime(obj2.until()//unix2cool))
            (since_2, until_2)=(strftime("%Y-%m-%d %H:%M:%S",since_struct_2), strftime("%Y-%m-%d %H:%M:%S", until_struct_2))
            (event.data['COOL_'+suffix+'_PREV'], event.data['COOL_'+suffix+'_PREV_IOV'], event.data['COOL_'+suffix+'_NEXT'], event.data['COOL_'+suffix+'_NEXT_IOV'])=(payload1[Cool_pmt], since_1+" -> "+until_1, payload2[Cool_pmt], since_2+" -> "+until_2)
        return
