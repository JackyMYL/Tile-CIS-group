# Worker to be used for analysis of CIS, Cs and LAS
# - Christopher Tunnell, 2009 <tunnell@hep.uchicago.edu>
# - Brian Martin, 2009 <brian.thomas.martin@cern.ch>
# - Seb Viret, 2009 (viret@in2p3.fr)
# - Mikhail Makouski, 2009 <makouski@cern.ch>
# - Marco van Woerden, 2011 (mwoerden@gmail.com)
# - Joshua Montgomery, 2012 (Joshua.J.Montgomery@gmail.com)
# - Andrey Kamenshchikov, 2013 (akamensh@cern.ch)
# Even though its not FORTRAN, its good to beable to print....
#        1         2         3         4         5         6         7         8
#2345678901234567890123456789012345678901234567890123456789012345678901234567890
from __future__ import print_function
from src.GenericWorker import *
from src.cesium        import chanlists,csdb

import sys
if sys.version_info[:1][0]==3: # python 3
    mypath="/afs/cern.ch/user/t/tilebeam/offline/lib/python%d.%d/site-packages" % sys.version_info[:2]
    sys.path.append(mypath)
    import pymysql
    python3 = True
else: # python 2
#    
    import _mysql,MySQLdb
    python3 = False

import os
import time,datetime

class Use(GenericWorker):
    "Select runs for TUCS to use."

    # THIS WORKER ASSIGNS EVENTS TO EACH REGION WITH A RUN NUMBER
    # AND A RUN TYPE. THERE WILL ONLY BE ONE EVENT PER RUN.

    def __init__(self, run, run2='', type='readout', region=None, 
                 useDateProg=True, verbose=0, runType='all', 
                 keepOnlyActive=True, filter=' ',
                 amp='15000', getLast = False, updateSpecial = True,
                 updateC10 = True, specialFile='./specialcells.txt',#akamensh
                 badmodulesFile='./badmodules.txt',
                 allowC10Errors = False, cscomment='', TWOInput= False, 
                 preprocessing=False):

        ### PARSE RUNS SELECTION ###
        (run, run2, TWOInput) = self.Translate_Runs(run, run2, TWOInput)

        ### REGION SELECTION ###
        if region != None and len(region)>0:			# CHECK WHETHER REGION IS SPECIFIED
            if ',' in region: 					# IF REGION IS A LIST OF REGIONS
                self.region = region.split(',')			# SEPERATE THE DIFFERENT SPECIFIED REGIONS
            elif isinstance(region,str): 			# A SINGLE REGION IS SPECIFIED AS STRING
                self.region = [region]				# SAVE REGION AS A LIST
            elif isinstance(region,list):			# MULTIPLE REGIONS ARE SPECIFIED AS LIST
                self.region = region				# STORE LIST
            if self.region[0][0] == 'H': 			# LIST OF REGIONS IS IN CELL HASH FORM
                from workers.noise.NoiseWorker import ConvertCellHash2TucsHash
                self.region = [ ConvertCellHash2TucsHash(int(hash[1:])) for hash in self.region ]
        else:							# NO REGION IS SPECIFIED
            self.region     = None				# EQUAL REGION TO NONE

        print("Starting mysql service")
        if python3:
            self.pymysqldb = pymysql.connect(host='pcata007.cern.ch', user='reader')    # CONNECT TO DATABASE
#             with self.pymysqldb: # with stopped working in python3.8
                 ##setup pymysql cursor for executing queries (necessary in py3)
            self.pymysqldb_cursor = self.pymysqldb.cursor()
        else:
            self.mysqldb = _mysql.connect(host='pcata007.cern.ch', user='reader')	# CONNECT TO DATABASE
        print("done")
            ### VARIABLES ###
            # SOME USEFUL GLOBAL VARIABLES
        self.type = type
        self.runs           = []				# RUN LIST
        self.runsToBeAddedToRegions        = []				      # RUN LIST
        self.CsAtlasRunList = []         			# runnumber set
        
        self.rType          = runType				# STORE REQUESTED RUNTYPE
        self.fragStr        = {}				# DIGIFLAGS FOR EACH RUN NUMBER
        self.keepOnlyActive = keepOnlyActive			# ONLY KEEP THE ACTIVE DETECTOR PARTS
            
        # USEFUL CESIUM VARIABLES
        self.verbose        = verbose				# VERBOSE
        self.updateSpec     = updateSpecial			# SPECIFIED UPDATE
        self.allowC10Err    = allowC10Errors			# ARE ERRORS FOR C10 ALLOWED
        self.cscomment      = cscomment 			# CESIUM RUN/MAGNET DESCRIPTION
        self.updateC10      = updateC10                         # akamensh: inherited from old version
        self.specialFile    = specialFile                       # akamensh: inherited from old version
        self.badmodulesFile = badmodulesFile                    # akamensh: inherited from old version

        # USEFUL CHARGE INJECTION VARIABLES
        self.twoInputs      = TWOInput				# STORE WHETHER CIS RUNS SHOULD BE BETWEEN TWO DATES
        self.preprocessing  = preprocessing
        # USEFUL LASER VARIABLES
        self.filter         = filter				# STORE WHICH LASER FILTER IS REQUESTED
        self.amp            = amp				# STORE REQUESTED AMPERAGE
        
        prelimRunList = []
            
        if self.preprocessing:
            if python3:
                self.pymysqldb_cursor.execute("""SELECT run, type, date, digifrags FROM tile.comminfo WHERE run='%d'""" % (run[0]))
                d = self.pymysqldb_cursor.fetchone()                # STORE DATABASE RESULT
                rundate = d[2].strftime("%Y-%m-%d") if d != () else None
            else:
                self.mysqldb.query("""SELECT run, type, date, digifrags FROM tile.comminfo WHERE run='%d'""" % (run[0]))
                r = self.mysqldb.store_result()				# STORE DATABASE RESULT
                d = r.fetch_row()				# FETCH DATABASE RESULT
                rundate = d[0][2].split()[0] if d != () else None
                  
            (run, run2, self.twoInputs)=self.Translate_Runs(rundate, run2, TWOInput, preprocessing)
                
        if isinstance(run, str):
            if useDateProg:                  # We received dates
                if self.twoInputs:
                    prelimRunList = self.dateProg(run,run2)
                else:                        # Only start date was given
                    prelimRunList = self.dateProg(run,)
            elif os.path.exists(run):        # We received a filename
                f = open(run)
                for line in f.readlines():
                    line = line.rstrip()
                    prelimRunList.append(int(line))

        elif isinstance(run, int):           # We received a single run as integer
            prelimRunList = [run]

        elif isinstance(run, (list, tuple)): # We received a list or tuple of runs (have to be ints!)
            for element in run:
                if isinstance(element, int):
                    prelimRunList.append(element)               # why only int when later transforming to ints?  
		    
        runs = list(map(int, prelimRunList))				# MAP/TYPECAST RUNS INTO INTEGERS LIST
        ### SELECT ONLY THE LAST RUN (SPECIAL OPTION) ###
        if getLast and isinstance(run, str): 			# CHECK THAT ONLY THE LAST RUN IS REQUESTED
            run_max = 0						# INITIALIZE LATEST RUN NUMBER
            for thisrun in runs:					# LOOP OVER ALL RUNS
                if thisrun > run_max:				# IF GREATEST RUN NUMBER SOFAR IS FOUND
                    run_max = thisrun				# STORE AS MAXIMAL RUN NUMBER
            runs = [run_max]					# STORE LAST RUN IN INTEGER RUN NUMBER LIST

        # CESIUM: constants for E3,E4 or other special cells may come from external text file
        if self.rType=='cesium':
            print(("specfile: ",self.specialFile))
            csdb.specfile=self.specialFile
            specval = csdb.readspecialces(0,'XXX',0,0)
        # CESIUM: EACH CHANNEL MAY HAVE IT'S OWN LIST OF RUNS
        # AS THE RUNS ARE NOT PARTITION WIDE
        for thisrun in runs:					# LOOP OVER RUNS
            if self.rType=='cesium':				# CESIUM IS REQUESTED
                date = None
                if thisrun>40000:					# IF RUN NUMBER IS AN ATLAS RUN NUMBER
                    if python3:
                        self.pymysqldb_cursor.execute("""SELECT date FROM tile.comminfo WHERE run>='%d' ORDER BY run DESC LIMIT 1""" % (thisrun))
                        d = self.pymysqldb_cursor.fetchone()            # STORE DATABASE RESULT
                    else:
                        self.mysqldb.query("""SELECT date FROM tile.comminfo WHERE run>='%d' ORDER BY run DESC LIMIT 1""" % (thisrun))
                        r = self.mysqldb.store_result()			# STORE DATABASE RESULT
                        d = r.fetch_row()				# FETCH DATABASE RESULT
                else:						# IF RUN NUMBER IS SPECIAL CESIUM RUN NUMBER
                    if python3:
                        self.pymysqldb_cursor.execute("SELECT time FROM tile.runDescr WHERE run=%i" % (thisrun))
                        d = self.pymysqldb_cursor.fetchone()
                    else:
                        self.mysqldb.query("SELECT time FROM tile.runDescr WHERE run=%i" % (thisrun))
                        r = self.mysqldb.store_result()
                        d = r.fetch_row()
                if d != ():					# IF RESULT IS NON-EMPTY
                    if python3:
                        date = d[0].strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        date = d[0][0]
                self.runs.append([thisrun, self.rType, date])	# APPEND RUN NUMBER

            else:    
                if python3:
                    self.pymysqldb_cursor.execute("""SELECT run, type, date, enddate, mbdata, digifrags FROM tile.comminfo WHERE run='%d'""" % (thisrun)) # added mbdata flag
                    d = self.pymysqldb_cursor.fetchone()                # STORE DATABASE RESULT
                else:
                    self.mysqldb.query("""SELECT run, type, date, enddate, mbdata, digifrags FROM tile.comminfo WHERE run='%d'""" % (thisrun)) # added mbdata flag
                    r = self.mysqldb.store_result()				# STORE DATABASE RESULT
                    d = r.fetch_row()				# FETCH DATABASE RESULT
                
                if d == ():                    # IF RESULT IS EMPTY
                    rundb, rtype, date_dt, enddate_dt, mbdata, digifrags = thisrun, None, None, None, None, None
                    #date = date_dt.strftime("%Y-%m-%d %H:%M:%S")
                    #enddate = enddate_dt.strftime("%Y-%m-%d %H:%M:%S")
                    print('not in database', thisrun)
                else:                        # IF RESULT IS NON-EMPTY
                    if python3:
                        rundb, rtype, date_dt, enddate_dt, mbdata, digifrags = d    #  TAKE THE FIRST RUN WITH A GIVEN RUN NUMBER
                        date = date_dt.strftime("%Y-%m-%d %H:%M:%S")
                        enddate = enddate_dt.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        rundb, rtype, date, enddate, mbdata, digifrags = d[0]    #  TAKE THE FIRST RUN WITH A GIVEN RUN NUMBER
                    
                if runType == 'all' or runType == rtype or (mbdata == '1' and runType == 'MBias'): # if we want mbias runs, ask for mbdata==1
                    if date:
                        if enddate: 
                            date=date+","+enddate
                    elif enddate:
                        date=enddate
                    self.runs.append([int(rundb), rtype, date])	# APPEND RUN IF RUN TYPE IS WITHIN SELECTION
                
                if self.keepOnlyActive and ( runType == rtype or rtype == None ):
                    if self.verbose or (digifrags and len(digifrags)/6 != 256):
                        print('In run', thisrun, ', modules in readout: ',len(digifrags)//6)
                    if digifrags == None:			# IF THERE ARE NO DIGIFRAGS AVAILABLE
                        self.keepOnlyActive = False		# TURN OFF FILTER FOR ACTIVE DETECTOR ELEMENTS
                    self.fragStr[int(thisrun)] = digifrags		# STORE DIGIFRAGS

        if python3:
            self.pymysqldb_cursor.close()
            self.pymysqldb.close()                    # CLOSE DATABASE CONNECTION
        else: # python 2
            self.mysqldb.close()					# CLOSE DATABASE CONNECTION        


    def ProcessStart(self):
        if self.region == None or self.region == '':        # IF NO DETECTOR COMPONENT IS SPECIFIED
            print('Use: Using all the detector')        # PRINTOUT
        else:                            # IF DETECTOR COMPONENT IS SPECIFIED
            print('Use: Only using region(s)', self.region)    # PRINTOUT
        runsOfThisRuntype = run_list.getRunsOfType(self.rType) 
        
        for run in sorted(self.runs):      
            thisrun = None
            for arun in runsOfThisRuntype:

                if arun.runNumber == run[0]:
                    thisrun = arun
                    break
            if thisrun == None:
                print("run ",run)
                thisrun = Run(runNumber=run[0],runType=run[1],time=run[2],data={})
            self.runsToBeAddedToRegions.append(thisrun)

        # SPECIAL CESIUM
        if self.rType=='cesium':				# IF CESIUM RUNS ARE REQUESTED
            if python3:
                self.db = pymysql.connect(host='pcata007', user='reader', db='tile')
                self.c = self.db.cursor(pymysql.cursors.Cursor)     # CURSOR THAT RETURNS DATABASE ROWS AS TUPLES
                self.cc = self.db.cursor(pymysql.cursors.DictCursor) # CURSOR THAT RETURNS DATABASE ROWS AS DICTIONARIES
            else:
                self.db = MySQLdb.connect(host='pcata007', user='reader', db='tile')
                self.c = self.db.cursor(MySQLdb.cursors.Cursor)	 # CURSOR THAT RETURNS DATABASE ROWS AS TUPLES
                self.cc = self.db.cursor(MySQLdb.cursors.DictCursor) # CURSOR THAT RETURNS DATABASE ROWS AS DICTIONARIES

            self.Abad=[41,42] 					# ALLOW ERRORS FOR A16 IN SPECIAL PMTS WITH CUTOUTS
            self.MAbad=[36,61]					# ALLOW ERRORS FOR A16 IN SPECIAL MODULES WITH CUTOUTS
            self.Abad1=[7,8,11,12]                              # allow errors for A12, A13 in special modules with cutouts
            self.MAbad1=[36,37,60,61]
            if self.allowC10Err:				# CHECK IF ERRORS FOR C10 SHOULD BE ALLOWED
                self.Cbad=[5,6] 				# ALLOW ERRORS FOR C10 IN SPECIAL PMTS
            else:						# IF ERRORS FOR C10 ARE NOT ALLOWED
                self.Cbad=[0] 					# DO NOT ALLOW ERRORS FOR C10
            self.Dbad=[17,18] 					# ALLOW ERRORS FOR D5 IN SPECIAL PMTS
            self.MDbad=[15,18]					# ALLOW ERRORS FOR D5 IN SPECIAL MODULES EBA15 AND EBC18
            self.period=datetime.timedelta(days=7)		# STORE A PERIOD OF 7 DAYS IN UNIX TIME


    def ProcessRegion(self, region):
        # Check if we need to do something for this region
        useRegion = False
        if self.region:
            for reg in self.region:
                if reg in region.GetHash() or reg in region.GetHash(1):
                    useRegion = True
                    break
        else:
            useRegion = True
            
        # if not we stop here
        if not useRegion:
            return region

        # Cesium is always special
        if self.rType == 'cesium':
            num=region.GetNumber(1)
            if len(num)==3: # This is a channel
                module=region.GetParent()
#
##### THIS NEEDS FIXING FOR BEING ABLE TO HAVE MULTIPLE USE STATEMENTS
#
                if module.GetEvents()==set([]):             # No runs in the module?  Add them all
                    for run in self.runsToBeAddedToRegions:                # LOOP
                        self.FillModule(module,run)            # ADD RUN TO THE MODULE
#
##### END OF PART NEEDING FIXING
#
                for evt in module.GetEvents():        # LOOP OVER ALL EVENTS IN CURRENT MODULE
                    if num[2] in evt.data['PMT']:
                        region.AddEvent(Event(evt.run, data={'csRun':evt.data['csRun'],
                                                             'csRun_time':evt.data['csRun_time'],
                                                             'calibration':None}))

        else:                        # IF REQUESTED RUNS ARE NOT CESIUM
            for run in self.runsToBeAddedToRegions:            # LOOP
                if self.keepOnlyActive and not self.isActive(region.GetHash(), int(run.runNumber)):
                    if self.verbose:            # IF FILTER IS ON
                        print('Region not in readout, removing: ', region.GetHash())
                else:
                    if self.rType=='Las' and 'gain' not in region.GetHash():    # IF REGION IS NOT an adc
                        continue                         # SKIP REGION
                    data = {}                            # CREATE EMPTY DATA COLLECTION
                    data['region'] = region.GetHash()    # STORE CHANNEL POSITION IN 
                    region.AddEvent(Event(run, data=data))
        return region


    def ProcessStop(self):					# DEFINE PROCESSSTOP
        #Create list of runs for use in other workers
        global Use_run_list
        global Use_date_list
        Use_run_list = []
        Use_date_list=[]
        for run in sorted(self.runs):
            Use_run_list.append(run[0])
            Use_date_list.append(run[2].split()[0])
        #print "Use_date_list=", Use_date_list
        #print Use_run_list	
	
        if self.rType=='cesium':			# IF CESIUM DATABASE CONNECTIONS WERE OPENED
            self.c.close()					# CLOSE DATABASE CURSOR
            self.cc.close()					# CLOSE DATABASE CURSOR
            self.db.close()					# CLOSE DATABASE


   ### SOME FUNCTIONS THAT ARE CESIUM SPECIFIC ###
    def FillModule(self,region,run):			# DEFINE FILLMODULE
        num=region.GetNumber(1)					 # Get region numbers

        if len(num)==2: 					 # IF REGION IS A MODULE
            rlist=[run]                                          # STORE RUN NUMBER IN RUN LIST
            if run.runNumber>40000:                              # The case of an Atlas runNumber
                date=time.strptime(run.time,"%Y-%m-%d %H:%M:%S") # IF A DATE IS SPECIFIED
                rlist=self.GetCsRuns(date-self.period,date)	 # STORE RUN NUMBERS IN RUN LIST

            (pmtlist,dict)=self.GetCsDescr(rlist,region.GetParent().GetName(),num[1])

            if dict!=None:					 # IF THERE IS A DATABASE RESULT
#                print (pmtlist,dict)
                if run.runNumber>40000:				 # IF A DATE IS SPECIFIED
                    ATLASrun=run				 # STORE ATLAS RUN NUMBER
                else:						 # IF NO DATE IS SPECIFIED
                    ATLASrun=self.GetOneATLASRun(dict['time'])	 # GET ATLAS RUN NUMBER

                currentrun = None
                for arun in self.CsAtlasRunList:
##                    print datetime.datetime.strptime(arun.time,"%Y-%m-%d %H:%M:%S").year,dict['time'].year
##                    if (dict['time']<datetime.datetime.strptime(arun.time,"%Y-%m-%d %H:%M:%S")):
##                        arun.time=dict['time'].strftime("%Y-%m-%d %H:%M:%S")
                    if arun.runNumber == ATLASrun:
                        currentrun = arun
                        
                if currentrun==None:
                    currentrun = Run( ATLASrun, 'cesium', dict['time'] , None )
                    self.CsAtlasRunList.append(currentrun)
                region.AddEvent( Event(currentrun, data={'csRun':dict['run'],'csRun_time':dict['time'],'PMT':pmtlist,'source':dict['source']}) )


    def GetOneATLASRun(self,time):
        if self.c.execute("SELECT run FROM comminfo WHERE date>'%s' and  run<9999999 ORDER BY date ASC LIMIT 1"%\
                          (time.strftime("%Y-%m-%d %H:%M:%S")))>=1:
            cl=self.c.fetchall()
            for r in cl:
                return r[0]


    def GetCsRuns(self, time1, time2):
        "Given start and end time, find all Cs runs in between"
        csruns=[]
        if self.c.execute( "SELECT run FROM runDescr WHERE time>'%s' AND time<'%s' ORDER BY time DESC" % \
                          (time1.strftime("%Y-%m-%d %H:%M:%S"),time2.strftime("%Y-%m-%d %H:%M:%S")) )>=1:
            cl=self.c.fetchall()
            for r in cl:
                if not r[0] in csruns:
                    csruns.append(r[0])
        return csruns


    def GetCsDescr(self,csruns,par,mod):
        for csrun in csruns:
            #print csrun,par,mod
            # here we have list of runs and look for run/par/mod in the database
            # as runs are sorted in desc. order we get the latest cs run
            if self.cc.execute("SELECT * FROM runDescr WHERE run=%i AND partition='%s' AND module=%i"%(csrun.runNumber,par,mod))!=1:
                continue
            dbdicts = self.cc.fetchall()
##            print csrun,par,mod,dbdicts
            #it should be only one record
            d=None
            for dict in dbdicts:
                dblist=self.if_ok(dict)
##                print csrun,par,mod,dict,dblist
                return (dblist,dict)
            
        # if we get here there were no Cs runs during the previous month
        return (None,None)


    def if_ok(self,dbdict):
        retlist=[]
        par=dbdict['partition']
        mod=dbdict['module']
        if self.cscomment!=dbdict['comment'] and self.cscomment!="ANY":
            return retlist
        run=dbdict['run']
        #print "run",dbdict['run']

        badpmt=[]
        try:
            lines = open(self.badmodulesFile,"r").readlines()
            for line in lines:
                fields = line.strip().split()
                #=== ignore empty and comment lines
                if not len(fields)          : continue
                if fields[0].startswith("#"): continue

                #=== read in fields
                rnn = int(fields[0])
                prt = fields[1]
                mdn = int(fields[2])
                pmn = int(fields[3])
                if rnn == run and prt == par and mdn == mod:
                    if pmn<1 or pmn>48:
                        print('module %s'%prt,'%02i'%mdn,'in run %i'%run,'is bad module for cesium, assuming all constants are bad')
                        return retlist
                    else:
                        badpmt.append(pmn)
        
        except Exception as e:
            if self.verbose: print('file %s not found i.e. everything should be good '%self.badmodulesFile ,par,"%02i"%mod)

        for pmt in range(1,49):
            specC10  = ( (par=='EBA' or par=='EBC') and ((mod>=39 and mod<=42) or (mod>=55 and mod<=58)) )
            specD4   = ( (par=='EBA' and mod==15) or (par=='EBC' and mod==18) )
            gapCrack = ( not specD4 and (par=='EBA' or par=='EBC') and (pmt==1 or pmt==2 or pmt==13 or pmt==14) ) or \
                       ( specD4 and (pmt==13 or pmt==14 or pmt==19 or pmt==20) )
            specC10  = ( specC10 and (pmt==5 or pmt==6) )
            normC10  = ( not specC10 and (par=='EBA' or par=='EBC') and (pmt==5 or pmt==6) )

            if csdb.readspecialces(0,par,mod,pmt)>-2.0:
                print('forcing update of special channel ',par,"%02i"%mod,"%02i"%pmt)
                retlist.append(pmt)
                continue
            if gapCrack:
                if self.updateSpec:
                    if self.verbose: print('forcing update of gap/crack ',par,"%02i"%mod,"%02i"%pmt)
                    retlist.append(pmt)
                else:
                    if self.verbose: print(('do not update gap/crack ',par,"%02i"%mod,"%02i"%pmt))
                continue
            if specC10:
                if self.updateSpec:
                    if self.verbose: print(('forcing update of special C10 ',par,"%02i"%mod,"%02i"%pmt))
                    retlist.append(pmt)
                else:
                    if self.verbose: print(('do not update special C10 ',par,"%02i"%mod,"%02i"%pmt))
                continue
            if normC10:
                if self.updateC10:
                    if self.verbose: print(('forcing update of normal C10 ',par,"%02i"%mod,"%02i"%pmt))
                    retlist.append(pmt)
                else:
                    if self.verbose: print(('do not update normal C10 ',par,"%02i"%mod,"%02i"%pmt))
                continue
            if par in chanlists.deadchan and mod in chanlists.deadchan[par] and pmt in chanlists.deadchan[par][mod]:
                if self.verbose: print(('dead channel: ',par,"%02i"%mod,"%02i"%pmt))
                continue
            if par in chanlists.unstabchan and mod in chanlists.unstabchan[par] and pmt in chanlists.unstabchan[par][mod]:
                if self.verbose: print(('unstable channel, using as is',par,"%02i"%mod,"%02i"%pmt))
                retlist.append(pmt)
                continue
            if par in chanlists.wrongchan and mod in chanlists.wrongchan[par] and pmt in chanlists.wrongchan[par][mod]:
                if self.verbose: print(('wrong channel, using new value',par,"%02i"%mod,"%02i"%pmt))
                retlist.append(pmt)
                continue
            if pmt in badpmt:
                if self.verbose: print(('cs integral in run %i'%run,'for this channel is wrong ',par,"%02i"%mod,"%02i"%pmt))
                continue
            if dbdict['statusPMT'+"%02i"%pmt]=='OK' or dbdict['statusPMT'+"%02i"%pmt]=='big ped RMS' :
                retlist.append(pmt)
                continue
##            if par=='LBC' and (mod in self.MLBCbad) \
##                   and dbdict['statusPMT'+"%02i"%pmt]=='low signal':
##                if self.verbose: print 'suppressing low signal ',par,"%02i"%mod,"%02i"%pmt
##                retlist.append(pmt)
##                continue
##            if par=='EBC' and (mod in self.MEBCbad):
##                if self.verbose: print dbdict['statusPMT'+"%02i"%pmt],par,"%02i"%mod,"%02i"%pmt
##                retlist.append(pmt)
##                continue
##            if par=='EBC' and (mod in self.MEBCbad) \
##                   and dbdict['statusPMT'+"%02i"%pmt]=='low signal':
##                if self.verbose: print 'suppressing low signal ',par,"%02i"%mod,"%02i"%pmt
##                retlist.append(pmt)
##                continue
            if par[0]=='E' and (pmt in self.Cbad or (pmt in self.Dbad and mod in self.MDbad and specD4) or (pmt in self.Abad and mod in self.MAbad)) \
                   and dbdict['statusPMT'+"%02i"%pmt]=='wrong number of peaks':
                if self.verbose: print(('suppressing  wrong number of peaks ',par,"%02i"%mod,"%02i"%pmt))
                retlist.append(pmt)
                continue
            if par[0]=='E' and ((pmt in self.Abad1 and mod in self.MAbad1)):
                if dbdict['statusPMT'+"%02i"%pmt]=='integrator malfunction':
                    if self.verbose: print(('suppressing integrator malfunction ',par,"%02i"%mod,"%02i"%pmt))
                    retlist.append(pmt)
                    continue
                if dbdict['statusPMT'+"%02i"%pmt]=='overflow':
                    if self.verbose: print(('suppressing overflow ',par,"%02i"%mod,"%02i"%pmt))
                    retlist.append(pmt)
                    continue
                if dbdict['statusPMT'+"%02i"%pmt]=='low signal':
                    if self.verbose: print(('suppressing low signal ',par,"%02i"%mod,"%02i"%pmt))
                    retlist.append(pmt)
                    continue

        return retlist


    def Translate_Runs(self, runs_string, runsset2, inputs, preprocessing=False):
        'translates the string form of the runs list into a form that USE.py can use'

        runs = runs_string
        if type(runs)== type(int()) or type(runs)== type(list()): # looks
            twoInputs=False
            runs_past2=runs
            print("Use runs input is a int or list")

        elif type(runs)== type(str()):
            print("Use runs input is a string")
            if not '-' in runs: # if there is NOT '-' in runs (its a date) use date -28days
                runs_past= runs
                runs_past2=runs+'-28 days'
                twoInputs=True
            elif runs[:1]=='-': # checks string to see if it is -x days
                 twoInputs=False
                 runs_past2=runs
            else: #                 print 'im assuming runs is xxxx-xx-xx'
                return (runs_string, runsset2, inputs)

        elif type(runs)== type(tuple()): # takes tuple of date + -x days and finds runs x amount of days behind given date
            print('runs type tuple')
            if '-' in runs[1]:
                runs_past= runs[0]
                runs_past2= runs[1] # ''.join(runs) VRAM interfered 
                print(('past ',  runs_past))
                print(('past2 ',  runs_past2))
                twoInputs=True
            else: # takes the list of two dates and gets the runs inbetween them
                runs_past=runs[0]
                runs_past2=runs[1]
                print(('past ',runs[0]))
                print(('past2 ', runs[1]))
                twoInputs=True
#                print"Dumping plots for %s" % selected_region,
        else:
            twoInputs=False
            runs_past2=runs
            print('Runs is not a list string int or tuple and i dont know what to do with it')

        if twoInputs==True:
            return (runs_past2, runs_past, True)
        else:
            return (runs_past2, '', False)


    # function to get list of runs for given runtype from Use
    def GetRunList(self):
        return self.runs


    def dateProg(self, string, string2=''):			# CALL MYSQL TO GRAB RUN LIST BASED ON THE DATE

        ### GRAB DATE ###
        if ((self.twoInputs == False)):
            r = os.popen("date -d '%s' +%%Y-%%m-%%d" % string)	# OPEN OS PIPE TO GRAB THE DATE
            date = r.readline().strip('\n')			# READ THE DATE AND STORE
            print(date)
            r.close()						# CLOSE OS PIPE
        else: 							# IF TWO DATES ARE USED
            r = os.popen("date -d '%s' +%%Y-%%m-%%d" % string)	# OPEN OS PIPE TO GRAB THE DATE
            date = r.readline().strip('\n')			# READ THE DATE AND STORE
            print(date)
            r.close()						# CLOSE OS PIPE
            r = os.popen("date -d '%s' +%%Y-%%m-%%d" % string2)	# OPEN SECOND OS PIPE TO GRAB THE DATE
            date2 = r.readline().strip('\n')			# READ THE DATE AND STORE
            print(date2)
            r.close()						# CLOSE OS PIPE

        ### GRAB RUN LIST ###


        if self.rType=='Las':  # Special treatment for LASER
            if self.twoInputs:
                datequery = "date>='%s' and date<='%s'" % (date,date2)
            else:
                datequery = "date>'%s'" % (date)

            if self.filter == ' ':
                filterquery = "((lasfilter='6' and events>10000) or (lasfilter='8' and events>10000))"
            else:
                filterquery = "lasfilter='%s'" % self.filter
                if self.filter == '6':
                    filterquery = " ( lasfilter='6' and events>10000)"
                if self.filter == '8':
                    filterquery = " ( lasfilter='8' and events>10000)"
            query = "select run from tile.comminfo where %s and %s and lasreqamp='%s' and type ='Las' and not (recofrags like '%%005%%' or recofrags like '%%50%%' ) and beamfrags like '%%200017%%' and not setup='ATLAS' and comments is NULL " % (datequery,filterquery,self.amp)
            print("This query will be used to select the laser runs:")
            print(" ") 
            print(query)
            print(" ")



        elif self.rType=='cesium':				# CHECK IF REQUESTED RUN TYPE IS CESIUM

            query = "select run from tile.runDescr where time>'%s' and module<65" % (date)
            if self.cscomment!='':
                query = "%s and comment='%s'" % (query, self.cscomment)
            if self.twoInputs:
                query = "%s and time<'%s'" % (query, date2)
            query = """%s""" % query

        elif self.rType=='CIS' and self.twoInputs == True:	# CHECK IF REQUESTED RUN TYPE IS CIS WITH TWO DATES
            query = """select run from tile.comminfo where date<'%s' and date>'%s' and comments is NULL""" % (date2,date)

        elif self.rType=='L1Calo' and self.twoInputs == True:
            query = """select run from tile.comminfo where date<'%s' and date>'%s'""" % (date2,date)

        else:							# IF NOT LASER, CS, L1CALO, OR CIS WITH TWO DATES
            query = """select run from tile.comminfo where run<9999999 and date>'%s'""" % (date)

#        print query
        runs = []						# CLEAR INTEGER RUN NUMBER LIST
        if python3:
            self.pymysqldb_cursor.execute(query)

            r2 = self.pymysqldb_cursor.fetchall()

            for run in r2:
                if run[0] not in runs:                # IF RUN NUMBER IS NOT ALREADY STORED
                    runs.append(run[0])                # APPEND RUN NUMBER TO RUN NUMBER LIST
        else: # python 2
            self.mysqldb.query(query)
            r2 = self.mysqldb.store_result()					# STORE DATABASE RESULT

            for run in r2.fetch_row(maxrows=0):			# FETCH DATABASE
                if run[0] not in runs:				# IF RUN NUMBER IS NOT ALREADY STORED
                    runs.append(run[0])				# APPEND RUN NUMBER TO RUN NUMBER LIST

       
        return runs						# RETURN INTEGER RUN NUMBER LIST


    def isActive(self,hash, run):				# CHECK IF REGION IS USED IN THIS RUN
        if run not in self.fragStr or not self.fragStr[run]:
            return True						# RETURN TRUE IF REGION IS USED
        hexStr = ''						# BINARY STRING TO CHECK
        if 'B' in hash:						# CHECK IF REGION IS SOMETHING SPECIFIC
            if   'LBA' in hash:					# CHECK IF REGION IS LBA
                hexStr = '0x1'					# STORE APPROPRIATE HEXADECIMALS
            elif 'LBC' in hash:					# CHECK IF REGION IS LBC
                hexStr = '0x2'					# STORE APPROPRIATE HEXADECIMALS
            elif 'EBA' in hash:					# CHECK IF REGION IS EBA
                hexStr = '0x3'					# STORE APPROPRIATE HEXADECIMALS
            elif 'EBC' in hash:					# CHECK IF REGION IS EBC
                hexStr = '0x4'					# STORE APPROPRIATE HEXADECIMALS
            if '_m' in hash:					# CHECK IF REGION IS FURTHER SPECIFIED
                ind = hash.index('m')+1				# ADD ONE TO MODULE INDEX
                modStr = hex(int(hash[ind:ind+2])-1).lstrip('0x')
                while len(modStr)<2:				# IF ADDRESS IS SHORTER THAN TWO
                    modStr = '0'+modStr				# ADD SOME ZEROS
                hexStr += modStr				# ADD THE ADDRESSES
            return (hexStr in self.fragStr[int(run)])		# RETURN WHETHER THE ADDRESS IN THE DIGIFRAGS
        elif hash == 'TILECAL':					# IF REGION IS JUST THE ENTIRE TILECAL
            return True						# RETURN TRUE
        else:							# IF REGION IS SOMETHING ELSE
            print (('Unknown hash: ',hash))			# TELL USER THIS CANNOT BE
            return False					# RETURN FALSE

 
    # function to remove some runs for creating 
    # long-term CIS plots 
    # edited by Andrew Smith on Jan 10, 2019 ancsmith@cern.ch
    # populate a new list 'goodruns' with
    # the runs we want to use and set self.runs = goodruns

    def RemoveBadRuns(self, badruns=[]):
        goodruns = []

        print("Bad runs in RemoveBadRuns")
        print(badruns)

        for run in self.runs:
            if not (run[0] in badruns):
                goodruns.append(run)
            else:
                pass
        self.runs = goodruns

