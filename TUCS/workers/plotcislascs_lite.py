# Author: Marco van Woerden, February 2011 (mwoerden@gmail.com)
# This worker creates overview and time evolution plots for all three calibration types.

from src.GenericWorker import *					# IMPORT ALL MODULES FROM GENERICWORKER
import ROOT							# IMPORT ROOT MODULES AND ATTRIBUTES
import time							# IMPORT TIME MODULES AND ATTRIBUTES
import math							# IMPORT MATH MODULES AND ATTRIBUTES
#from ROOT import *                                              # IMPORT ALL MODULES FROM ROOT
from array import *						# IMPORT ALL MODULES FROM ARRAY
#import numpy							# IMPORT NUMPY MODULES AND ATTRIBUTES
from src.oscalls import *

class plotcislascs_lite(GenericWorker):
    "Plot TILECAL's calibration systems."

    def __init__(self, region='', t0norm = False):
        # SOME USEFUL GLOBAL VARIABLES
        self.part_nr   = -1					# PARTITION/BARREL NUMBER
        self.part_nm   = ''					# PARTITION/BARREL NAME
        self.partnms   = ['LBA','LBC','EBA','EBC']		# PARTITION NAMES
        self.draw      = -1					# DRAWER/MODULE NUMBER
        self.pmt       = -1					# PMT NUMBER
        self.gain_nr   = -1					# GAIN VALUE
        self.gain_nm   = ['_lowgain','_highgain']		# GAIN NAMES
        self.limit     = 1.					# GRAPH YAXIS LIMIT
        self.n_run     = 0					# NUMBER OF RUNS
        self.eventtime = 0					# EVENT TIME
        self.time_max  = 0					# MAXIMAL VALUE ON TIME AXIS
        self.time_min  = 1000000000000000			# MINIMAL VALUE ON TIME AXIS
        self.c_w       = 1100					# WIDTH OF THE CANVAS
        self.c_h       = 900					# HEIGHT OF THE CANVAS
        self.region    = region					# REGION
        self.save2file = True					# IF DATA IS FOUND, THIS BOOLEAN BECOMES TRUE
        self.printpng  = True					# PRINT PNG IN PLOT DIRECTORY
        self.t0norm    = t0norm					# TIME = ZERO NORMALISATION

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
        self.drawer_cs      = []				# DRAWER LIST FOR CS RUNS
        self.drawer_laslow  = []				# DRAWER LIST FOR LOWGAIN LAS RUNS
        self.drawer_lashigh = []				# DRAWER LIST FOR HIGHGAIN LAS RUNS
        self.drawer_cislow  = []				# DRAWER LIST FOR LOWGAIN CIS RUNS
        self.drawer_cishigh = []				# DRAWER LIST FOR HIGHGAIN CIS RUNS
        self.run_list   = []					# LIST OF RUNS TO USE
        self.eventlist  = []					# CREATE EMPTY EVENT LIST
        self.canvas     = []					# CREATE EMPTY LIST OF CANVASES
        self.problems   = []					# CREATE LIST OF KNOWN PROBLEMS

        # SOME USEFUL LISTS OF LISTS
        for i in range(257):					# STORE LISTS OF LISTS
            self.drawer_cs.append([])				# LIST OF LISTS OF CESIUM RUNS
            self.drawer_cislow.append([])			# LIST OF LISTS OF LOWGAIN CIS RUNS
            self.drawer_cishigh.append([])			# LIST OF LISTS OF HIGHGAIN CIS RUNS
            self.drawer_laslow.append([])			# LIST OF LISTS OF LOWGAIN LAS RUNS
            self.drawer_lashigh.append([])			# LIST OF LISTS OF HIGHGAIN LAS RUNS

        # SOME TOOLS
        self.PMTool     = LaserTools()				# LASER TOOLS
        self.origin     = ROOT.TDatime()			# SET TIME AXIS TIME SETTINGS
        self.dir        = getPlotDirectory()			# DIRECTORY WHERE PLOTS ARE STORED

    def ProcessRegion(self,region):				# PROCESS REGION
        a = region.GetHash().split('_')                         # SPLIT IT UP
        if len(a) > 1:                                      	# CHECK DEFINITION   
            pn = a[1]						# STORE BARREL NAME
            p = -1						# THIS WILL STORE THE SELECTED PARTITION
            if pn == 'LBA':                                 	# IF LBA
                p = 0                                       	# STORE BARREL NUMBER
            elif pn == 'LBC':                               	# IF LBC
                p = 1                                       	# STORE BARREL NUMBER
            elif pn == 'EBA':                               	# IF EBA
                p = 2                                       	# STORE BARREL NUMBER
            elif pn == 'EBC':                               	# IF EBC
                p = 3                                       	# STORE BARREL NUMBER
            if self.part_nr != -1 and p != self.part_nr:        # THIS IS NOT THE RIGHT PARTITION
                return						# DISMISS REGION
            if len(a) > 2:                                  	# CHECK DEFINITION
                d = int(a[2][1]+a[2][2])                    	# STORE MODULE NUMBER
                if self.draw != -1 and d != self.draw:          # THIS IS NOT THE RIGHT DRAWER
                    return					# DISMISS REGION
            if len(a) > 3:                                  	# CHECK DEFINITION   
                ch  = int(a[3][1]+a[3][2])                  	# STORE PMT NUMBER 
                if self.pmt != -1 and ch != self.pmt:		# THIS IS NOT THE RIGHT PMT
                    return					# DISMISS REGION

        for event in region.GetEvents():			# LOOP OVER EVENTS IN REGION
            if 'problems' in event.data:			# IF THERE ARE PROBLEMS KNOWN
                for problem in event.data['problems']:		# LOOP OVER THESE PROBLEMS
                    if problem not in self.problems:		# IF PROBLEMS NOT YET STORED
                        self.problems.append(problem)		# STORE PROBLEM
        ### CIS ###
            if 'deviation' in event.data and event.runType == 'CIS' and 'region' in event.data:
                if 'highgain' in region.GetHash():		# IF THIS IS A HIGHGAIN EVENT
                    self.AppendEvent(self.drawer_cishigh,event,region.GetHash())
                if 'lowgain' in region.GetHash():		# IF THIS IS A LOWGAIN EVENT
                    self.AppendEvent(self.drawer_cislow,event,region.GetHash())
        for event in region.GetEvents():			# LOOP OVER EVENTS IN REGION
        ### LASER ###
            if 'deviation' in event.data and event.runType == 'Las' and 'region' in event.data:
                if 'highgain' in region.GetHash():		# IF THIS IS A HIGHGAIN EVENT
                    self.AppendEvent(self.drawer_lashigh,event,region.GetHash())
                if 'lowgain' in region.GetHash():		# IF THIS IS A LOWGAIN EVENT
                    self.AppendEvent(self.drawer_laslow,event,region.GetHash())
        ### CESIUM ###
        for event in region.GetEvents():
            if 'csRun' in event.data       and     'calibration' in event.data and \
            'f_cesium_db' in event.data and 'source' not in event.data and \
            event.data['calibration'] != None    and     event.data['f_cesium_db'] != None:
                for physchan in region.GetChildren('readout'):	# LOOP OVER ALL CHANNELS
                    [p,m,c,w]=physchan.GetNumber(1)		# RETRIEVE P(ARTITION),M(ODULE),C(HANNEL),GAIN
                    p -= 1					# RETRIEVED PARTITION NUMBER, LOWER 1
                    c -= 1					# RETRIEVED CHANNEL NUMBER, LOWER 1
                    if self.part_nr != -1 and p != self.part_nr:# IF JUST ONE PARTITION IS SELECTED
                        continue				# CONTINUE
                    if self.draw != -1 and m != self.draw:	# IF JUST ONE DRAWER IS SELECTED
                        continue				# CONTINUE
                    event.data['deviation'] = float(event.data['calibration'])/float(event.data['f_cesium_db'])-1.
                    datatime                = time.mktime(time.strptime(str(event.time), "%Y-%m-%d %H:%M:%S"))
                    event.data['time']      = datatime		# STORE EVENT DATATIME

                    i = 64*p+m					# USEFUL INDEX
                    self.drawer_cs[i].append(event)		# APPEND EVENT TO DRAWER LIST
                    self.CheckTimeAndRunList(str(event.time),datatime)

    def ProcessStop(self):
        # BIRTH OF A CANVAS
        self.HatchCanvases()
        # LOOP OVER PARTITION, DRAWER, PMT, EVENTS IN PMT TO STORE IN GRAPH
        for i_part in range(4):					# LOOP OVER ALL PARTITION NUMBERS
            if self.part_nr != -1 and i_part != self.part_nr:	# IF JUST ONE PARTITION IS SELECTED
                continue					# CONTINUE
            for i_drawer in range(64):				# LOOP OVER ALL DRAWERS
                if self.draw != -1 and i_drawer != self.draw:	# IF JUST ONE DRAWER IS SELECTED
                    continue					# CONTINUE
                ROOT.gStyle.SetTimeOffset(self.origin.Convert())# SET XAXIS OFFSET
                lashigh_events = self.drawer_lashigh[64*i_part+i_drawer]
                laslow_events  = self.drawer_laslow[64*i_part+i_drawer]
                cs_events      = self.drawer_cs[64*i_part+i_drawer]
                cishigh_events = self.drawer_cishigh[64*i_part+i_drawer]
                cislow_events  = self.drawer_cislow[64*i_part+i_drawer]
                if self.part_nr == -1 and self.draw == -1 and self.pmt == -1:
                    self.plot_name = "%s_history" % (self.PMTool.get_module_name(i_part,i_drawer))
                else:						# IF PARTITION OR DRAWER OR PMT IS SPECIFIED
                    self.plot_name = "%s_history" % (self.PMTool.get_module_name(i_part,i_drawer-1))
                ### LET'S CREATE SOME HISTOGRAM LISTS HERE ###
                n_pmt              = 0				# NUMBER OF PMTS
                laslow_pmt_list    = []				# LIST OF PMTS INVOLVED IN LASER EVENTS
                lashigh_pmt_list   = []				# LIST OF PMTS INVOLVED IN LASER EVENTS
                cs_pmt_list        = []				# LIST OF PMTS INVOLVED IN CS EVENTS
                cislow_pmt_list    = []				# LIST OF PMTS INVOLVED IN CIS EVENTS
                cishigh_pmt_list   = []				# LIST OF PMTS INVOLVED IN CIS EVENTS
                for i in range(48):				# LOOP OVER NUMBER OF PMTS
                    laslow_pmt_list.append([])			# APPEND EMPTY LIST TO LASER PMT LIST
                    lashigh_pmt_list.append([])			# APPEND EMPTY LIST TO LASER PMT LIST
                    cs_pmt_list.append([])			# APPEND EMPTY LIST TO CESIUM PMT LIST
                    cislow_pmt_list.append([])			# APPEND EMPTY LIST TO CESIUM PMT LIST
                    cishigh_pmt_list.append([])			# APPEND EMPTY LIST TO CESIUM PMT LIST
                convenient_list = [[cislow_events,cislow_pmt_list],[cishigh_events,cishigh_pmt_list],\
                                   [laslow_events,laslow_pmt_list],[lashigh_events,lashigh_pmt_list],\
                                   [cs_events,cs_pmt_list]]
                for [dummy_one,dummy_two] in convenient_list:	# LOOP OVER TYPES
                    for event in dummy_one:			# LOOP OVER EVENTS OF CERTAIN TYPE
                        [p,m,pmt,w] = event.region.GetNumber(1)
                        if c <= 48:				# CHECK THAT INDICES MAKE SENSE
                            dummy_two[pmt].append(event)	# APPEND EVENT TO PMT LIST OF CERTAIN TYPE
                for i_pmt in range(48):				# LOOP OVER ALL PMTS IN THIS DRAWER
                    if self.pmt != -1 and i_pmt != self.pmt:	# CHECK THAT PMT IS SPECIFIED
                        continue				# OTHERWISE, CONTINUE
                    if self.PMTool.is_instrumented(i_part,i_drawer,i_pmt) == False:
                        continue				# CONTINUE IF PMT IS NOT INSTRUMENTED
                    pmt_events = [cislow_pmt_list[i_pmt],cishigh_pmt_list[i_pmt],\
                                  laslow_pmt_list[i_pmt],lashigh_pmt_list[i_pmt],cs_pmt_list[i_pmt]]
                    print(("EVENTS FOUND",len(pmt_events[0]),len(pmt_events[1]),len(pmt_events[2]),\
                                         len(pmt_events[3]),len(pmt_events[4])))
                    max_dev        = [0.,0.,0.,0.,0.]		# MAXIMUM VARIATION IN CIS/LAS/CS CONSTANTS
                    max_cst        = [0.,0.,0.,0.,0.]		# MAXIMUM CIS/LAS/CS CALIBRATION CONSTANTS
                    ave_dev        = [0.,0.,0.,0.,0.]		# AVERAGE
                    ave_cst        = [0.,0.,0.,0.,0.]		# AVERAGE
                    t0_norm        = [1.,1.,1.,1.,1.,1.,1.,1.,1.,1.]
                    t0_done        = [False,False,False,False,False,False,False,False,False,False]
                    t0_name        = ["","","","","","","","","",""]
                    self.n_points  = [0.,0.,0.,0.,0.]		# NUMBER OF POINTS FOR THIS PMT
                    for tp in range(0,5):			# LOOP OVER TYPES CIS/LAS/CS
                        for event in pmt_events[tp]:		# LOOP OVER EVENTS
                            if len(pmt_events[tp]) != 0:	# IF NUMBER OF EVENTS IS NONZERO
                                self.n_points[tp] += 1.		# COUNT NUMBER OF POINTS
                                ave_dev[tp] += abs(math.fabs(event.data['deviation']))/float(len(pmt_events[tp]))
                                ave_cst[tp] += abs(math.fabs(event.data['calibration']))/float(len(pmt_events[tp]))
                                if max_dev[tp]  < abs(math.fabs(event.data['deviation'])):
                                    max_dev[tp] = abs(math.fabs(event.data['deviation']))
                                if max_cst[tp]  < abs(math.fabs(event.data['calibration'])):
                                    max_cst[tp] = abs(math.fabs(event.data['calibration']))
                                if t0_done[tp] == False and self.t0norm == True:
                                    if abs(math.fabs(event.data['deviation'])) != 0:
                                        t0_norm[tp]   = abs(math.fabs(event.data['deviation']))
                                        t0_done[tp]   = True	# TIME = ZERO VALUE STORED
                                        t0_name[tp]   = "_t0norm"
                                    if abs(math.fabs(event.data['calibration'])):
                                        t0_norm[tp+5] = abs(math.fabs(event.data['calibration']))
                                        t0_done[tp+5] = True	# TIME = ZERO VALUE STORED
                                        t0_name[tp+5] = "_t0norm"
                        print(("N,AVE,AVE",self.n_points[tp],ave_dev[tp],ave_cst[tp]))
                    # FOR EVERY PMT, WE ADD APPEND A HISTOGRAM TO STORE THE CONSTANTS IN #
                    naam = "%s_m%02i_c%02i_"%(self.part_nm,i_drawer,i_pmt)
                    self.nick = [[["lowgain_cis_deviation_absolute"     + t0_name[0],[]  ,1.5*max_dev[0]/t0_norm[0]] , \
                                  ["lowgain_cis_deviation_normalised"   + t0_name[0],[]  ,1.5/t0_norm[0]           ]], \
                                 [["highgain_cis_deviation_absolute"    + t0_name[1],[]  ,1.5*max_dev[1]/t0_norm[1]] , \
                                  ["highgain_cis_deviation_normalised"  + t0_name[1],[]  ,1.5/t0_norm[1]           ]], \
                                 [["lowgain_laser_deviation_absolute"   + t0_name[2],[]  ,1.5*max_dev[2]/t0_norm[2]] , \
                                  ["lowgain_laser_deviation_normalised" + t0_name[2],[]  ,1.5/t0_norm[2]           ]], \
                                 [["highgain_laser_deviation_absolute"  + t0_name[3],[]  ,1.5*max_dev[3]/t0_norm[3]] , \
                                  ["highgain_laser_deviation_normalised"+ t0_name[3],[]  ,1.5/t0_norm[3]           ]], \
                                 [["cs_deviation_absolute"              + t0_name[4],[]  ,1.5*max_dev[4]/t0_norm[4]] , \
                                  ["cs_deviation_normalised"            + t0_name[4],[]  ,1.5/t0_norm[4]           ]], \
                                 [["lowgain_cis_constant_absolute"      + t0_name[5],[]  ,1.5*max_cst[0]/t0_norm[5]] , \
                                  ["lowgain_cis_constant_normalised"    + t0_name[5],[]  ,1.5/t0_norm[5]           ]], \
                                 [["highgain_cis_constant_absolute"     + t0_name[6],[]  ,1.5*max_cst[1]/t0_norm[6]] , \
                                  ["highgain_cis_constant_normalised"   + t0_name[6],[]  ,1.5/t0_norm[6]           ]], \
                                 [["lowgain_laser_constant_absolute"    + t0_name[7],[]  ,1.5*max_cst[2]/t0_norm[7]] , \
                                  ["lowgain_laser_constant_normalised"  + t0_name[7],[]  ,1.5/t0_norm[7]           ]], \
                                 [["highgain_laser_constant_absolute"   + t0_name[8],[]  ,1.5*max_cst[3]/t0_norm[8]] , \
                                  ["highgain_laser_constant_normalised" + t0_name[8],[]  ,1.5/t0_norm[8]           ]], \
                                 [["cs_constant_absolute"               + t0_name[9],[]  ,1.5*max_cst[4]/t0_norm[9]] , \
                                  ["cs_constant_normalised"             + t0_name[9],[]  ,1.5/t0_norm[9]           ]]]
                    for [[a1,b1,c1],[a2,b2,c2]] in self.nick:
                        b1.append([ROOT.TH2F(naam+a1,naam+a1,500,0,self.time_max-self.time_min+1,100,-1.*c1,c1),\
                                   ROOT.TH2F(naam+a2,naam+a2,500,0,self.time_max-self.time_min+1,100,-1.*c2,c2)])
                    ### FILL CIS GRAPH ###
                    for type_index in range(0,5):		# LOOP OVER ALL TYPES
                        for event in pmt_events[type_index]: 	# LOOP OVER ALL PMT EVENTS OF CERTAIN TYPE
                            if 'deviation' in event.data and 'calibration' in event.data:
                                if ave_dev[type_index]*ave_cst[type_index] != 0.:
                                    WhereIsTheTime = event.data['time']-self.time_min
                                    self.nick[type_index+0][0][1][n_pmt][0].Fill(WhereIsTheTime,event.data['deviation']  /t0_norm[type_index+0])
                                    self.nick[type_index+0][0][1][n_pmt][1].Fill(WhereIsTheTime,event.data['deviation']  /ave_dev[type_index+0]/t0_norm[type_index+0]-1.)
                                    self.nick[type_index+5][0][1][n_pmt][0].Fill(WhereIsTheTime,event.data['calibration']/t0_norm[type_index+5])
                                    self.nick[type_index+5][0][1][n_pmt][1].Fill(WhereIsTheTime,event.data['calibration']/ave_cst[type_index+0]/t0_norm[type_index+5]-1.)
                    ### IF THERE'S DATA, DO LAYOUT BELOW ###
                    if not self.t0norm:
                        y_nm  = "PMT evolution (deviation) %s" % ('(in %)')
                        y_nm2 = "PMT evolution (calibration constant) %s" % ('(absolute)') 
                    elif self.t0norm:
                        y_nm  = "PMT evolution (deviation) %s" % ('(in A.U. normalised to t=0)')
                        y_nm2 = "PMT evolution (calibration constant) %s" % ('(in A.U. normalised to t=0)')
                    for type_index in range(0,5):
                        if self.n_points[type_index] != 0:
                            color = [1,2,3,4,6]
                            self.LayoutHist(self.nick[type_index+0][0][1][n_pmt][0],\
                                            y_nm                             ,False,2,color[type_index],1.0)
                            self.LayoutHist(self.nick[type_index+0][0][1][n_pmt][1],\
                                            y_nm + " (normalised to average)",False,2,color[type_index],1.0)
                            self.LayoutHist(self.nick[type_index+5][0][1][n_pmt][0],\
                                            y_nm2                            ,False,2,color[type_index],1.0)
                            self.LayoutHist(self.nick[type_index+5][0][1][n_pmt][1],\
                                            y_nm2+ " (normalised to average)",False,2,color[type_index],1.0)
                    ### IF THERE'S DATA AND A PARTICULAR PMT IS SELECTED, DO DRAWING BELOW ###
                    print(('CISLOW','CISHIGH','LASLOW','LASHIGH','CS',self.n_points[0],self.n_points[1],self.n_points[2],self.n_points[3],self.n_points[4]))
                    if self.pmt != -1 and self.n_points[0]+self.n_points[1]+self.n_points[2]+self.n_points[3]+self.n_points[4] != 0:
                        print(("REGION TILECAL_%s_m%02i_c%02i SELECTED"%(self.partnms[i_part],i_drawer,self.pmt)))
                        self.save2file = True			# DATA SHOULD BE SAVED TO FILE
                        self.canvas[0].SetName("TILECAL_%s_m%02i_c%02i_DEV_ABS"%(self.partnms[i_part],i_drawer,self.pmt))
                        self.canvas[1].SetName("TILECAL_%s_m%02i_c%02i_DEV_NORM"%(self.partnms[i_part],i_drawer,self.pmt))
                        self.canvas[2].SetName("TILECAL_%s_m%02i_c%02i_CST_ABS"%(self.partnms[i_part],i_drawer,self.pmt))
                        self.canvas[3].SetName("TILECAL_%s_m%02i_c%02i_CST_NORM"%(self.partnms[i_part],i_drawer,self.pmt))
                        self.DoROOTgStyle()
                        ### PLOT DEVIATION HISTOGRAMS IN CANVASES AND SAVE THEM IN THE DATA ROOT FILE ###
                        self.DrawingBusiness("%s_m%02i_c%02i"%(self.partnms[i_part],i_drawer,self.pmt),n_pmt)
                    ### IF THERE'S DATA AND NO PARTICULAR PMT IS SELECTED, DO DRAWING BELOW ###
                    elif self.pmt == -1 and n1+n2+n3+n4+n5 != 0:
                        print("NO PMT SELECTED")
                    n_pmt  += 1					# INCREMENT PMT NUMBER
                    del self.nick				# DELETE ALL HISTOGRAMS
        ### DELETE OBJECTS ###
        del self.canvas						# DELETE CANVASES
        gc.collect(2)						# GARBAGE COLLECTOR

    def AppendEvent(self,drawer_list,event,regionhash):		# CHECK EVENT AND APPEND TO LIST
        [p, m, c, w] = self.PMTool.GetNumber(regionhash)	# RETRIEVE PARTITION, MODULE, CHANNEL, GAIN
        p -= 1							# RETRIEVED PARTITION NUMBER, LOWER 1
        #m -= 1							# RETRIEVED MODULE NUMBER, LOWER 1
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
        if self.time_max<datatime:				# IF GREATEST TIME IS FOUND
            self.time_max = datatime				# STORE AS MAXIMUM
        if datatime not in self.run_list:			# IF TIME NOT YET IN RUNLIST
            self.run_list.append(datatime)			# STORE IN RUNLIST

    def LayoutHist(self,hist,title,axisrange_scale,style,color,size):
        hist.GetXaxis().SetTimeDisplay(1)			# SET TIME DISPLAY
        hist.GetXaxis().SetTimeOffset(self.origin.Convert())	# SET X AXIS OFFSET
        hist.GetXaxis().SetLabelOffset(0.09)			# SET LABEL OFFSET
        hist.GetXaxis().SetLabelSize(0.025)			# SET LABEL SIZE
        hist.GetXaxis().SetTitleSize(0.025)			# SET TITLE SIZE
        hist.GetXaxis().SetLabelFont(62)			# SET LABEL FONT
        hist.GetXaxis().SetTimeFormat("%d-%b-%Y")		# SET TIME FORMAT
        hist.GetXaxis().SetNdivisions(-503)			# SET NUMBER OF DIVISIONS
        hist.GetYaxis().SetTitle(title)				# SET TITLE
        hist.GetYaxis().SetTitleSize(0.025)			# SET TITLE SIZE
        hist.GetYaxis().SetLabelSize(0.025)			# SET LABEL SIZE
        hist.GetYaxis().SetTitleFont(42)			# SET TITLE FONT
        hist.GetYaxis().SetLabelFont(42)			# SET LABEL FONT
        hist.GetYaxis().SetTitleOffset(2)			# SET TITLE OFFSET
        if axisrange_scale:					# IF AXIS RANGE AND SCALING SHOULD BE DONE
            hist.SetAxisRange(-6.,6.,"Y")			# SET AXIS RANGE
            hist.Scale(.1)					# SCALE
        hist.GetYaxis().SetNdivisions(-416)			# SET NUMBER OF DIVISIONS
        hist.SetMarkerStyle(style)				# SET MARKER STYLE
        hist.SetMarkerColor(color)				# SET MARKER COLOR
        hist.SetMarkerSize(size)				# SET MARKER SIZE

    def HatchCanvases(self):
        for quantity in ['deviation_','calibration_']:		# LOOP OVER POSSIBLE QUANTITIES
            for scaling in ['absolute_','normalised_']:		# LOOP OVER POSSIBLE SCALINGS
                for view in ['zoom']:				# LOOP OVER POSSIBLE VIEWS
                    current = len(self.canvas)			# SELECT CURRENT CANVAS
                    self.canvas.append(ROOT.TCanvas(scaling+quantity+view,"evolution of calibration",self.c_w,self.c_h))
                    self.canvas[current].SetWindowSize(2*self.c_w-self.canvas[0].GetWw(),2*self.c_h-self.canvas[0].GetWh())
                    self.canvas[current].Range(0,0,1,1)		# SET WORLD COORDINATE SYSTEM
                    self.canvas[current].SetFillColor(0)	# SET WHITE BACKGROUND
                    self.canvas[current].SetBorderMode(0)	# REMOVE BORDERS
                    if self.pmt == -1:				# IF NO PMT IS SELECTED
                        self.canvas[current].cd()		# SET CURRENT PAD
                        self.canvas[current].Divide(6,8)	# DIVIDE INTO 48 CHANNELS

    def DrawingBusiness(self,channelname,n_pmt):
        Q = ['_deviation_','_calibration_']			# LIST OF POSSIBLE QUANTITIES
        S = ['absolute' ,'normalised']				# LIST OF POSSIBLE SCALINGS
        ROOT.gStyle.SetTimeOffset(self.origin.Convert())	# SET TIME AXIS OFFSET
        leg = [ROOT.TLegend(0.5,0.1,0.9,0.15),ROOT.TLegend(0.5,0.1,0.9,0.18),\
               ROOT.TLegend(0.5,0.1,0.9,0.15),ROOT.TLegend(0.5,0.1,0.9,0.18)]
        txt = ROOT.TPaveText(0.23,0.9,0.98,0.98,"brNDC")
        txt.SetTextColor(1)
        #txt.SetTextSize(0.01)
        text = ""
        for problem in self.problems:
            text += " *** " + problem
        txt.AddText(text)
        firsthistogram = [True,True,True,True]			# IS THIS THE FIRST HISTOGRAM
        for type_index in range(0,5):				# LOOP OVER TYPES
            if self.pmt != -1:					# IF SPECIFIC PMT IS SELECTED
                for quantity in range(0,2):			# LOOP OVER QUANTITIES
                    for scaling in range(0,2):			# LOOP OVER SCALING 
                        self.canvas[quantity+scaling*2].cd()	# SET CURRENT PAD
                        if self.nick[type_index+5*quantity][0][1][n_pmt][scaling].GetEntries() != 0.:
                            leg[quantity+scaling*2].AddEntry(self.nick[type_index+5*quantity][0][1][n_pmt][scaling])
                            leg[quantity+scaling*2].SetTextSize(.02)
                            leg[quantity+scaling*2].SetFillColor(0)
                            print((type_index,quantity,scaling,firsthistogram,self.nick[type_index+5*quantity][0][1][n_pmt][scaling].GetEntries() != 0.))
                            if firsthistogram[quantity+scaling*2]:
                                self.nick[type_index+5*quantity][0][1][n_pmt][scaling].Draw()
                                txt.Draw("SAME")		# DRAW PROBLEMS IN SAME CANVAS
                                firsthistogram[quantity+scaling*2] = False
                            else:				# OTHERWISE
                                self.nick[type_index+5*quantity][0][1][n_pmt][scaling].Draw("SAME")
                            leg[quantity+scaling*2].Draw("SAME")	# DRAW LEGEND
                        if not self.t0norm:
                            self.canvas[quantity+scaling*2].SetName(channelname+Q[quantity]+S[scaling])
                        else:
                            self.canvas[quantity+scaling*2].SetName(channelname+Q[quantity]+S[scaling]+"_t0norm")
        for ctmp in self.canvas:				# LOOP OVER CANVASES
            ctmp.Print("%s/%s.png"%(self.dir,ctmp.GetName()))	# PRINT ON FILE

    def DoROOTgStyle(self):
        ROOT.gStyle.SetOptStat(0)				# SET HISTOGRAM STATS OFF
        ROOT.gStyle.SetStatX(0.78)				# SET DEFAULT STATS PARAMETER
        ROOT.gStyle.SetStatY(0.83)				# SET DEFAULT STATS PARAMETER
        ROOT.gStyle.SetTimeOffset(self.origin.Convert())	# SET TIME AXIS OFFSET
