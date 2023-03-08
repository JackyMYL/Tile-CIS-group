# Author: Marco van Woerden, February 2011 (mwoerden@gmail.com)
# This worker creates overview and time evolution plots for all three calibration types.

from src.GenericWorker import *					# IMPORT ALL MODULES FROM GENERICWORKER
import ROOT							# IMPORT ROOT MODULES AND ATTRIBUTES
import time							# IMPORT TIME MODULES AND ATTRIBUTES
import math							# IMPORT MATH MODULES AND ATTRIBUTES
#from ROOT import *                                              # IMPORT ALL MODULES FROM ROOT
from array import *						# IMPORT ALL MODULES FROM ARRAY
import numpy							# IMPORT NUMPY MODULES AND ATTRIBUTES
from numpy import *						# IMPORT ALL MODULES FROM NUMPY
from src.oscalls import *

class saveonfile(GenericWorker):
    "Plot TILECAL's calibration systems."

    def __init__(self, region='', filename = 'calibration_tree.root', runtype = None):
        # SOME USEFUL GLOBAL VARIABLES
        self.treeformat= "time/D:constant/D:constant_db/D:deviation/D:runType/D:partition/D:drawer/D:pmt/D"
        self.filename  = filename				# STORE NAME OF ROOTFILE
        self.runtype   = runtype				# STORE SOUGHT RUNTYPE
        self.part_nr   = -1					# PARTITION/BARREL NUMBER
        self.part_nm   = ''					# PARTITION/BARREL NAME
        self.partnms   = ['LBA','LBC','EBA','EBC']		# PARTITION NAMES
        self.draw      = -1					# DRAWER/MODULE NUMBER
        self.pmt       = -1					# PMT NUMBER
        self.gain_nr   = -1					# GAIN VALUE
        self.gain_nm   = ['_lowgain','_highgain']		# GAIN NAMES
        self.n_run     = 0					# NUMBER OF RUNS
        self.eventtime = 0					# EVENT TIME
        self.region    = region					# REGION
        self.time_max  = 0					# MAXIMAL VALUE ON TIME AXIS
        self.time_min  = 1000000000000000			# MINIMAL VALUE ON TIME AXIS

        # STORE REGION
        if True:						# IF THERE'S ONLY ONE SPECIFIED REGION
            a = self.region.split('_')				# SPLIT IT UP
            if len(a) > 1:					# CHECK DEFINITION
                self.part_nm = a[1]				# STORE BARREL NAME
                if self.part_nm == 'LBA':			# IF LBA
                    self.part_nr = 0				# STORE BARREL NUMBER
                elif self.part_nm == 'LBC':			# IF LBC
                    self.part_nr = 1				# STORE BARREL NUMBER
                elif self.part_nm == 'EBA':			# IF EBA
                    self.part_nr = 2				# STORE BARREL NUMBER
                elif self.part_nm == 'EBC':			# IF EBC
                    self.part_nr = 3				# STORE BARREL NUMBER
                if len(a) > 2:					# CHECK DEFINITION
                    self.draw = int(a[2][1]+a[2][2])		# STORE MODULE NUMBER
                if len(a) > 3:					# CHECK DEFINITION
                    self.pmt  = int(a[3][1]+a[3][2])		# STORE PMT NUMBER
                if 'highgain' in a:				# CHECK FOR GAIN
                    self.gain_nr = 1				# STORE GAIN VALUE
                if 'lowgain' in a:				# CHECK FOR GAIN
                    self.gain_nr = 0				# STORE GAIN VALUE

        # STORE LISTS
        self.drawer  = []					# DRAWER LIST FOR CS RUNS
        self.run_list   = []					# LIST OF RUNS TO USE
        self.eventlist  = []					# CREATE EMPTY EVENT LIST

        # SOME USEFUL LISTS OF LISTS
        for i in range(257):					# STORE LISTS OF LISTS
            self.drawer.append([])				# LIST OF LISTS OF CESIUM RUNS

        # SOME TOOLS
        self.PMTool     = LaserTools()				# LASER TOOLS
        self.origin     = ROOT.TDatime()			# SET TIME AXIS TIME SETTINGS
        self.dir        = getPlotDirectory()			# DIRECTORY WHERE PLOTS ARE STORED

    def ProcessRegion(self,region):
        if not self.region and not region in self.region:
            print((self.region,"!=",region))
            return
        for event in region.GetEvents():			# LOOP OVER EVENTS IN REGION
        ### CIS ###
            if self.runtype == 'CIS' or self.runtype == None or self.runtype == '':
                if 'deviation' in event.data and event.run.runType == 'CIS':
                    self.AppendEvent(self.drawer,event,region.GetHash())
        for event in region.GetEvents():			# LOOP OVER EVENTS IN REGION
        ### LASER ###
            if self.runtype == 'Las' or self.runtype == None or self.runtype == '':
                if 'deviation' in event.data and event.run.runType == 'Las':
                    self.AppendEvent(self.drawer,event,region.GetHash())
        ### CESIUM ###
        for event in region.GetEvents():
            if self.runtype == 'Cs' or self.runtype == None or self.runtype == '':
                if 'csRun' in event.data       and     'calibration' in event.data and \
                'f_cesium_db' in event.data and 'source' not in event.data and \
                event.data['calibration'] != None    and     event.data['f_cesium_db'] != None:
                    for physchan in region.GetChildren('readout'):	# LOOP OVER ALL CHANNELS
                        [p,m,c,w]=physchan.GetNumber(1)		# RETRIEVE P(ARTITION),M(ODULE),C(HANNEL),GAIN
                        p -= 1					# RETRIEVED PARTITION NUMBER, LOWER 1
                        if self.part_nr != -1 and p != self.part_nr:# IF JUST ONE PARTITION IS SELECTED
                            continue				# CONTINUE
                        if self.draw != -1 and m != self.draw:	# IF JUST ONE DRAWER IS SELECTED
                            continue				# CONTINUE
                        event.data['deviation'] = float(event.data['calibration'])/float(event.data['f_cesium_db'])-1.
                        datatime                = time.mktime(time.strptime(str(event.time), "%Y-%m-%d %H:%M:%S"))
                        event.data['time']      = datatime	# STORE TIME IN EVENT DATA

                        i = 64*p+m				# USEFUL INDEX
                        self.drawer[i].append(event)		# APPEND EVENT TO DRAWER LIST
                        self.CheckTimeAndRunList(str(event.time),datatime)

    def ProcessStop(self):
        # OPENING OF A FILE
        print(("CREATING FILE...",self.filename))			# PRINTOUT
        f = ROOT.TFile(os.path.join(getPlotDirectory(),self.filename),"UPDATE")	# OPEN FILE
        f.cd()							# CHANGE CURRENT DIRECTORY	
        # LOOP OVER PARTITION, DRAWER, PMT, EVENTS IN PMT TO STORE IN GRAPH
        for i_part in range(4):					# LOOP OVER ALL PARTITION NUMBERS
            if self.part_nr != -1 and i_part != self.part_nr:	# IF SPECIFIC DETECTOR PARTITION IS SELECTED
                continue					# CONTINUE
            for i_drawer in range(64):				# LOOP OVER ALL DRAWERS
                if self.draw != -1 and i_drawer != self.draw:	# IF SPECIFIC DRAWER IS SELECTED
                    continue					# CONTINUE IF JUST ONE DRAWER IS SELECTED
                treename  = "TILECAL_%s_m%02i"%(self.partnms[i_part],i_drawer)
                print(("CREATING ROOT TREE FOR DETECTOR PARTITION...",treename))
                tree = ROOT.TTree(treename, "TILECAL_%s"%self.partnms[i_part])
                events = self.drawer[64*i_part+i_drawer]	# STORE LASER EVENTS
                n_pmt          = 0				# NUMBER OF PMTS
                pmt_list   = []					# LIST OF PMTS INVOLVED IN LASER EVENTS
                for i in range(48):				# LOOP OVER NUMBER OF PMTS
                    pmt_list.append([])				# APPEND EMPTY LIST TO LASER PMT LIST
                for event in events:				# LOOP OVER EVENTS FOR THIS DRAWER
                    [p,m,pmt,w] = event.region.GetNumber(1)
                    pmt_list[pmt].append(event)		       # APPEND EVENT TO CIS PMT LIST
                for i_pmt in range(48):				# LOOP OVER ALL PMTS IN THIS DRAWER
                    evdata = zeros(8, dtype=float)		# CREATE NUMBY ARRAY
                    branchname = "c%02i"%(i_pmt)		# SET BRANCH NAME
                    print(("CREATING ROOT BRANCH FOR DETECTOR PARTITION...",branchname))
                    branch = tree.Branch(branchname,evdata,self.treeformat,64000)
                    #if self.pmt != -1 and i_pmt != self.pmt:# IF JUST ONE PMT IS SELECTED
                    #    continue				# CONTINUE
                    if self.PMTool.is_instrumented(i_part,i_drawer,i_pmt) == False:
                        continue				# CONTINUE IF PMT IS INSTRUMENTED
                    eventslist  =  pmt_list[i_pmt]		# GET ALL CESIUM EVENTS FOR THIS PMT
                    ### FILL TREE FOR CESIUM ###
                    for event in eventslist: 			# LOOP OVER ALL CESIUM PMT EVENTS\
                        if 'csRun' in event.data:		# IF CESIUM RUN TYPE
                            evdata[0] = float(event.data['time'])
                            evdata[1] = float(event.data['calibration'])
                            evdata[2] = float(event.data['f_cesium_db'])
                            evdata[3] = float(event.data['deviation'])
                            evdata[4] = float(3)		# STORE RUNTYPE IN TLEAF
                            evdata[5] = float(i_part)		# STORE PART IN TLEAF
                            evdata[6] = float(i_drawer)		# STORE DRAWER IN TLEAF
                            evdata[7] = float(i_pmt)		# STORE PMT IN TLEAF
                            tree.Fill()				# FILL TTREE
                    ### FILL TREE FOR CIS ###
                    for event in eventslist: 			# LOOP OVER ALL LASER PMT EVENTS
                        if 'deviation' in event.data and event.run.runType == 'CIS':
                            evdata[0] = float(event.data['time'])
                            evdata[1] = float(event.data['calibration'])
                            evdata[2] = float(event.data['f_cesium_db'])
                            evdata[3] = float(event.data['deviation'])
                            evdata[4] = float(0)		# STORE RUNTYPE IN TLEAF
                            evdata[5] = float(i_part)		# STORE PART IN TLEAF
                            evdata[6] = float(i_drawer)		# STORE DRAWER IN TLEAF
                            evdata[7] = float(i_pmt)		# STORE PMT IN TLEAF
                            tree.Fill()				# FILL TTREE
                    ### FILL TREE FOR LASER ###
                    for event in eventslist: 			# LOOP OVER ALL LASER PMT EVENTS
                        if 'wheelpos' in event.run.data:	# CHECK IF KEY WHEELPOS IS PRESENT
                            if event.run.data['wheelpos'] == 6:	
                                evdata[0] = float(event.data['time'])
                                evdata[1] = float(event.data['calibration'])
                                evdata[2] = float(event.data['lasref_db'])
                                evdata[3] = float(event.data['deviation'])
                                evdata[4] = float(1)		# STORE RUNTYPE IN TLEAF
                                evdata[5] = float(i_part)	# STORE PART IN TLEAF
                                evdata[6] = float(i_drawer)	# STORE DRAWER IN TLEAF
                                evdata[7] = float(i_pmt)	# STORE PMT IN TLEAF
                                tree.Fill()			# FILL TTREE
                            if event.run.data['wheelpos'] == 8:
                                evdata[0] = float(event.data['time'])
                                evdata[1] = float(event.data['calibration'])
                                evdata[2] = float(event.data['lasref_db'])
                                evdata[3] = float(event.data['deviation'])
                                evdata[4] = float(2)		# STORE RUNTYPE IN TLEAF
                                evdata[5] = float(i_part)	# STORE PART IN TLEAF
                                evdata[6] = float(i_drawer)	# STORE DRAWER IN TLEAF
                                evdata[7] = float(i_pmt)	# STORE PMT IN TLEAF
                                tree.Fill()			# FILL TTREE
        f.Write()						# WRITE TTREES ON FILE
        f.Close()						# CLOSE FILE
        ### GARBAGE ###
        gc.collect(2)						# GARBAGE COLLECTOR

    def AppendEvent(self,drawer_list,event,regionhash):		# CHECK EVENT AND APPEND TO LIST
        [p, m, c, w] = self.PMTool.GetNumber(regionhash)	# RETRIEVE PARTITION, MODULE, CHANNEL, GAIN
        p -= 1							# RETRIEVED PARTITION NUMBER, LOWER 1
        doorgaan = True						# CONTINUE? TRUE!
        if self.part_nr != -1 and p != self.part_nr:		# IF JUST ONE PARTITION IS SELECTED
            doorgaan = False					# DISCONTINUE
        if self.draw != -1 and m != self.draw:			# IF JUST ONE DRAWER IS SELECTED
            doorgaan = False					# DISCONTINUE
        if doorgaan:						# IF CONTINUE (DOORGAAN)
            i = 64*p+m						# USEFUL INDEX
            drawer_list[i].append(event)			# APPEND EVENT TO DRAWER LIST
            self.CheckTimeAndRunList(event.time,event.data['time'])

    def CheckTimeAndRunList(self,evtime,datatime):		# FIND EXTREME VALUES OF TIME AND APPEND TO RUNLIST
        if self.time_min>datatime:				# IF SMALLEST TIME IS FOUND
            self.time_min = datatime				# STORE AS MINIMUM
            self.origin = ROOT.TDatime(evtime)			# STORE AS OFFSET
            time = open(os.path.join(getResultDirectory(),'time'),'w')	# OPEN TEMPORARY TIME FILE
            time.write("%i,%i,%s"%(self.time_min,self.time_max,str(evtime)))
            time.close()					# CLOSE FILE
        if self.time_max<datatime:				# IF GREATEST TIME IS FOUND
            self.time_max = datatime				# STORE AS MAXIMUM
        if datatime not in self.run_list:			# IF TIME NOT YET IN RUNLIST
            self.run_list.append(datatime)			# STORE IN RUNLIST
