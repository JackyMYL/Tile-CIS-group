############################################################################
#
# ReadLaserHV_DCS.py
#
############################################################################
#
# Author: Andrey Kamenshchikov <akamensh@cern.ch>
#
# 27.05.2013
#
# Functionality: 
#     Read HV information from DCS Oracle with TS closest 
#    to start- and end- time of current run (in intervals: 
#     starttime-2h -> starttime and endtime -> endtime+2h 
#    appropriately) and add new data to event.
#
# Options:
#    constring - String of connection to DCSOracle using 
#    cx_Oracle (initialized by default)
# 
#
# Data keys:
#    DCS_HV_PREV - HV with TS closest to run.time(start time) before it;
#    DCS_HV_PREV_TS - local time for TS of DCS_HV_PREV (string);
#    DCS_HV_NEXT - HV with TS closest to run.endtime (end time) after it;
#    DCS_HV_NEXT_TS - local time for TS of DCS_HV_NEXT (string).
#
# For more info on the LASER system : http://atlas-tile-laser.web.cern.ch
#
############################################################################

from src.ReadGenericCalibration import *
from src.run import *
import random
from datetime import datetime, timedelta
import time
import calendar
import cx_Oracle

# For using the LASER tools
from src.laser.toolbox import *

class ReadLaserHV_DCS(ReadGenericCalibration):
    "The Laser HV DCS Data Reader"


    def __init__(self, constring='ATLAS_PVSS_READER/PVSSRED4PRO@ATLAS_PVSSPROD'):
        self.PMTool         = LaserTools()
        self.constring=constring

    def ProcessStart(self):
        pass
        ######
        ### Open up a DB connection
        ######

        try:
            self.dcsdb=cx_Oracle.connect(self.constring)
        except Exception as e:
            print("ReadCalFromDCS: Failed to open a database connection, this can be an AFS token issue")
            print(e)
            sys.exit(-1)    


    def ProcessRegion(self, region):
        str1={2: "ATLTILLV02:Drawer",1: "ATLTILLV01:Drawer",3: "ATLTILLV00:Drawer",4: "ATLTILLV03:Drawer"}
        for event in region.GetEvents():
            if len(region.GetNumber())==3:
                [part, mod, chan]=region.GetNumber()
            elif len(region.GetNumber())==4:
                [part, mod, chan, gain]=region.GetNumber()
            else:
                continue
            
            pmt=self.PMTool.get_PMT_index(part-1,mod-1,chan)
            strf=str1[part]

            try:
                t1_dt=datetime.datetime.strptime(event.run.time,"%Y-%m-%d %H:%M:%S")
            except Exception as e:
                t1_dt=datetime.datetime.now()
            t1_t=time.gmtime(time.mktime(t1_dt.timetuple()))#time UTC
            t1=time.strftime("%d-%b-%Y %I:%M:%S %p",t1_t)
            t1_shifted_dt=t1_dt+timedelta(hours=-2)
            t1_shifted_t=time.gmtime(time.mktime(t1_shifted_dt.timetuple()))#time UTC
            t1_shifted=time.strftime("%d-%b-%Y %I:%M:%S %p",t1_shifted_t)
            try:
                t2_dt=datetime.datetime.strptime(event.run.endtime,"%Y-%m-%d %H:%M:%S")
            except Exception as e:
                t2_dt=datetime.datetime.now()
            t2_t=time.gmtime(time.mktime(t2_dt.timetuple()))#time UTC
            t2=time.strftime("%d-%b-%Y %I:%M:%S %p",t2_t)
            t2_shifted_dt=t2_dt+timedelta(hours=+2)
            t2_shifted_t=time.gmtime(time.mktime(t2_shifted_dt.timetuple()))#time UTC
            t2_shifted=time.strftime("%d-%b-%Y %I:%M:%S %p",t2_shifted_t)

            statement1  = "SELECT archive#, start_time, end_time FROM ATLAS_PVSSTIL.arc_archive WHERE "
            statement1 += "(end_time > \'"
            statement1 += t1_shifted
            statement1 += "\' OR end_time is null) AND (start_time < \'"
            statement1 += t1
            statement1 += "\' AND start_time > '01-JAN-2000') ORDER BY start_time desc"  
            cur1=self.dcsdb.cursor()
            cur1.execute(statement1)
            res1=cur1.fetchone()
            if res1!=None:
                n=(8*'0'+str(res1[0]))[-8:]
                stringValue=strf + str(mod) + ".Readings.Monitoring.hvOut" + str(pmt) + ".value"
                statement="SELECT ELEMENTS.ELEMENT_NAME, EVENTHISTORY_"
                statement+=str(n)
                statement+=".TS, EVENTHISTORY_"
                statement+=str(n)
                statement+=".VALUE_NUMBER FROM ATLAS_PVSSTIL.ELEMENTS, ATLAS_PVSSTIL.EVENTHISTORY_"
                statement+=str(n)
                statement+=" WHERE EVENTHISTORY_"
                statement+=str(n)
                statement+=".ELEMENT_ID=ELEMENTS.ELEMENT_ID AND EVENTHISTORY_"
                statement+=str(n)
                statement+=".ELEMENT_ID IN   ( SELECT ELEMENT_ID FROM ATLAS_PVSSTIL.ELEMENTS WHERE ELEMENT_NAME like \'"
                statement+=stringValue
                statement+="\') AND (TS >= \'"
                statement+=t1_shifted
                statement+="\' AND TS <= \'"
                statement+=t1
                statement+="\')"
                statement += " ORDER BY TS desc"
                cur=self.dcsdb.cursor()
                cur.execute(statement)
                res=cur.fetchone()    #take only first row from results
                if res!=None:
                    event.data['DCS_HV_PREV']=res[2]
                    ts_oracle_1=time.localtime(calendar.timegm(res[1].timetuple()))
                    ts_str_1=time.strftime("%Y-%m-%d %H:%M:%S", ts_oracle_1)
                    event.data['DCS_HV_PREV_TS']=ts_str_1
                cur.close()
            cur1.close()

            statement2  = "SELECT archive#, start_time, end_time FROM ATLAS_PVSSTIL.arc_archive WHERE "
            statement2 += "(end_time > \'"
            statement2 += t2
            statement2 += "\' OR end_time is null) AND (start_time < \'"
            statement2 += t2_shifted
            statement2 += "\' AND start_time <> '01-JAN-1970 010000 AM') ORDER BY start_time asc"
            cur2=self.dcsdb.cursor()
            cur2.execute(statement2)
            res2=cur2.fetchone()
            if res2!=None:
                n1=(8*'0'+str(res2[0]))[-8:]
                stringValue=strf + str(mod) + ".Readings.Monitoring.hvOut" + str(pmt) + ".value"
                statement3="SELECT ELEMENTS.ELEMENT_NAME, EVENTHISTORY_"
                statement3+=str(n1)
                statement3+=".TS, EVENTHISTORY_"
                statement3+=str(n1)
                statement3+=".VALUE_NUMBER FROM ATLAS_PVSSTIL.ELEMENTS, ATLAS_PVSSTIL.EVENTHISTORY_"
                statement3+=str(n1)
                statement3+=" WHERE EVENTHISTORY_"
                statement3+=str(n1)
                statement3+=".ELEMENT_ID=ELEMENTS.ELEMENT_ID AND EVENTHISTORY_"
                statement3+=str(n1)
                statement3+=".ELEMENT_ID IN   ( SELECT ELEMENT_ID FROM ATLAS_PVSSTIL.ELEMENTS WHERE ELEMENT_NAME like \'"
                statement3+=stringValue
                statement3+="\') AND (TS >= \'"
                statement3+=t2
                statement3+="\' AND TS <= \'"
                statement3+=t2_shifted
                statement3+="\')"
                statement3 += " ORDER BY TS asc"
                cur3=self.dcsdb.cursor()
                cur3.execute(statement3)
                res3=cur3.fetchone()  #take only first row from results
                if res3!=None:
                    event.data['DCS_HV_NEXT']=res3[2]
                    ts_oracle_2=time.localtime(calendar.timegm(res3[1].timetuple()))
                    ts_str_2=time.strftime("%Y-%m-%d %H:%M:%S", ts_oracle_2)
                    event.data['DCS_HV_NEXT_TS']=ts_str_2
                cur3.close()
            cur2.close()
        return    
