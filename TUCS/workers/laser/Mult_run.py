# Worker to be used to add runs to be used mainly for getLaserFlags
############################################################
#
# Mult_run.py
#
############################################################
#
# Author: Arthur Chomont (arthur.chomont@cern.ch)
#
# July 2015
#
# Goal:
# ->  From a given run returns two dates : list of runs to be used
#
# Input parameters are:
# -> A run number
#
#
# Ouput:
# -> Two dates corresponding to all runs from the one in input to -10days
# 
#
#############################################################

from src.GenericWorker import *
from src.cesium        import chanlists,csdb
import os
import time,datetime

class Mult_run(GenericWorker):
    "Select runs for TUCS to use."

    # This first of the worker is copied from the worker Use.py  

    # THIS WORKER ASSIGNS EVENTS TO EACH REGION WITH A RUN NUMBER
    # AND A RUN TYPE. THERE WILL ONLY BE ONE EVENT PER RUN.

    def __init__(self, run ,type='readout',runType='Las'):

        ### VARIABLES ###
        # SOME USEFUL GLOBAL VARIABLES
        self.type = type
        self.runs           = []				# RUN LIST
        self.runsToBeAddedToRegions        = []				# RUN LIST
 
        self.rType          = runType				# STORE REQUESTED RUNTYPE
        self.fragStr        = {}				# DIGIFLAGS FOR EACH RUN NUMBER
        self.region     = None                                  # For this we don't care of the region so we take all the detector
 
        # USEFUL LASER VARIABLES
        self.filter         = '6'				# STORE WHICH LASER FILTER IS REQUESTED
        self.amp            = '23000'				# STORE REQUESTED AMPERAGE

        prelimRunList = []
        prelimRunList = [run]

        runs = list(map(int, prelimRunList))				# MAP/TYPECAST RUNS INTO INTEGERS LIST

        # AS THE RUNS ARE NOT PARTITION WIDE
        for thisrun in runs:					# LOOP OVER RUNS
            self.mysqldb.query("""SELECT run, type, date, enddate, mbdata, digifrags FROM tile.comminfo WHERE run='%d'""" % (thisrun)) # added mbdata flag
            r = self.mysqldb.store_result()				# STORE DATABASE RESULT
            d = r.fetch_row()				# FETCH DATABASE RESULT
                
            if d == ():					# IF RESULT IS EMPTY
                rundb, rtype, date, enddate, mbdata, digifrags = thisrun, None, None, None, None, None
                print('not in database', thisrun)
            else:						# IF RESULT IS NON-EMPTY
                rundb, rtype, date, enddate, mbdata, digifrags = d[0] 	# TAKE THE FIRST RUN WITH A GIVEN RUN NUMBER
                    #print "d[0]=", d[0]
                    #print d[0][2]
                
            if runType == 'all' or runType == rtype or (mbdata == '1' and runType == 'MBias'): # if we want mbias runs, ask for mbdata==1
                if date:
                    if enddate: 
                        date=date+","+enddate
                elif enddate:
                    date=enddate
                self.runs.append([int(rundb), rtype, date])	# APPEND RUN IF RUN TYPE IS WITHIN SELECTION

        self.mysqldb.close()					# CLOSE DATABASE CONNECTION

        global ini_Date_run                                          #Two global variables which will be needed after this worker in HV workers for example
        ini_Date_run='2012-01-01'
        global fin_Date_run
        fin_Date_run='2012-01-01'
        global fin_Date
        global ini_Date

        if self.region == None or self.region == '':		# IF NO DETECTOR COMPONENT IS SPECIFIED
            print('Use: Using all the detector')			# PRINTOUT
        else:							# IF DETECTOR COMPONENT IS SPECIFIED
            print('Use: Only using region(s)', self.region)	# PRINTOUT
        runsOfThisRuntype = run_list.getRunsOfType(self.rType) 
         
        for run in sorted(self.runs):                            #Retrieve the data corresponding to the runs presented in input           
            thisrun = None
            for arun in runsOfThisRuntype:

                if arun.runNumber == run[0]:
                    thisrun = arun
                    break
            if thisrun == None:
                print("run ",run)
                thisrun = Run(runNumber=run[0],runType=run[1],time=run[2],data={})
            self.runsToBeAddedToRegions.append(thisrun)

        print(run[2])
        self.i_Date = run[len(run)-1].split(' ')[:1][0]
        
        year=''
        month=''
        day=''

        for x in range(4):                                                       #Define the two days which will be put in input of worker Use.py
            year+=self.i_Date[x]
        for x in range(5,7):
            month+=self.i_Date[x]
        for x in range(8,10):
            day+=self.i_Date[x]

        ini_y, ini_m, ini_d = int(year), int(month), int(day)
        fin_y, fin_m, fin_d = int(year), int(month), int(day)
        ini_Date_run = str(datetime.date(ini_y, ini_m, ini_d)-timedelta(days=15))
        fin_Date=datetime.date(fin_y, fin_m, fin_d)
        ini_Date=datetime.date(fin_y, fin_m, fin_d)
        fin_Date_run = str(datetime.date(fin_y, fin_m, fin_d)+timedelta(days=1))

    def ProcessStart(self):
   
        print(ini_Date_run)
        print(fin_Date_run)

            
    def ProcessRegion(self,region):

        a=2

        return
