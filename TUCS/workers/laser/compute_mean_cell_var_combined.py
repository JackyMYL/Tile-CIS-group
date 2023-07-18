############################################################
#
# compute_mean_cell_var_combined.py
#
############################################################
#
# Author: BDE
#
# For more info on the LASER system : http://atlas-tile-laser.web.cern.ch
#
#############################################################

from src.GenericWorker import *
from src.laser.toolbox import *
from src.oscalls import *

import src.MakeCanvas
import time
import math

class compute_mean_cell_var_combined(GenericWorker):
    "Produce summary plots"

    def ProcessStart(self):
        print("Using run {} for cell map".format("average" if self.average else self.runNumber))
        filename = "data_cells_var_%s%s%s.txt" % (self.gname,self.side,'side' if self.side != '' else '')

        self.outfile = open(os.path.join(getResultDirectory(),filename), 'w')
        

    def __init__(self, limit=2, gain=1, runNumber=0, verbose=False, ComputeEBScale=False, average=False, side=''):

        global EBScale
        if (ComputeEBScale):
            EBScale = 0.0
        self.ComputeEBScale = ComputeEBScale
        self.runNumber=runNumber
        self.verbose=verbose
        self.average=average

        graph_lim  = 5*limit
        graph_lim_calib_up = 0
        graph_lim_calib_down = 0

        self.gain = gain
        if self.gain == 0:
            self.gname = 'lg'
            graph_lim_calib_up = 1
            graph_lim_calib_down = -0.05
        if self.gain == 1:
            self.gname = 'hg'
            graph_lim_calib_up = 1
            graph_lim_calib_down = -0.05
        if self.gain == 2:
            self.gname = 'global'

        self.side  = side if side in ['','A','C'] else ''
            
        self.outputTag = outputTag # global variable to tag output histogram file name
        self.dir    = getPlotDirectory(subdir=self.outputTag)
        self.PMTool = LaserTools()

        try:
            self.HistFile.cd()
        except:
            self.initHistFile("output/Tucs.HIST{}.root".format(self.outputTag)) 
        self.HistFile.cd()
              
        self.dirname = "CellsAverage"
        ROOT.gDirectory.mkdir(self.dirname)
        ROOT.gDirectory.cd(self.dirname)

        # Create the different canvas
        self.channel = src.MakeCanvas.MakeCanvas()
        self.fiber   = src.MakeCanvas.MakeCanvas()
        self.status  = src.MakeCanvas.MakeCanvas()
            
        self.channel.SetFrameFillColor(0)
        self.channel.SetFillColor(0);
        self.channel.SetBorderMode(0);
        self.channel.SetLogy(1); 
            
        self.fiber.SetFrameFillColor(0)
        self.fiber.SetFillColor(0);
        self.fiber.SetBorderMode(0);
        self.fiber.SetLogy(1); 

        # Then create the different histograms
        self.part_bchan  = [] # partition bad channels
        self.part_wchan  = [] # partition slightly out of range channels
        self.part_nochan = [] # partition channels w/no data
        self.chans = [] # histo of cells
        
        for i in range(4):
            pname = self.PMTool.get_partition_name(i)
            sidename = '' if self.side=='' else 'side'+self.side
            self.part_bchan.append(ROOT.TH2F("%s bad%s"%(pname,sidename),"",500,0.,65.,500,0.,49.))
            self.part_wchan.append(ROOT.TH2F("%s warn%s"%(pname,sidename),"",500,0.,65.,500,0.,49.))
            self.part_nochan.append(ROOT.TH2F("%s nodat%s"%(pname,sidename),"",500,0.,65.,500,0.,49.))

        self.ch  = ROOT.TH1F('channel variation%s'%(sidename), '', 100, -graph_lim, graph_lim)
        self.calib = ROOT.TH1F('real channel variation%s'%(sidename), '', 100, graph_lim_calib_down, graph_lim_calib_up)

        # DB : added these histo to split in cell for LB
        self.chA  = ROOT.TH1F('channel variation A%s'%(sidename), '', 100, -graph_lim/3, graph_lim/3)
        self.chB  = ROOT.TH1F('channel variation B%s'%(sidename), '', 100, -graph_lim/3, graph_lim/3)
        self.chD  = ROOT.TH1F('channel variation D%s'%(sidename), '', 100, -graph_lim/3, graph_lim/3)

        # DB : added these histo to split in cell for EB
        self.chEA  = ROOT.TH1F('channel variation EB A%s'%(sidename), '', 100, -graph_lim/3, graph_lim/3)
        self.chEB  = ROOT.TH1F('channel variation EB B%s'%(sidename), '', 100, -graph_lim/3, graph_lim/3)
        self.chED  = ROOT.TH1F('channel variation EB D%s'%(sidename), '', 100, -graph_lim/3, graph_lim/3)

        # DB : added histo specific to A cells : drifting cells with lumi
        self.chA12  = ROOT.TH1F('channel variation A12%s'%(sidename), '', 50, -graph_lim/3, graph_lim/3)
        self.chA34  = ROOT.TH1F('channel variation A34%s'%(sidename), '', 50, -graph_lim/3, graph_lim/3)
        self.chA56  = ROOT.TH1F('channel variation A56%s'%(sidename), '', 50, -graph_lim/3, graph_lim/3)
        self.chA78  = ROOT.TH1F('channel variation A78%s'%(sidename), '', 50, -graph_lim/3, graph_lim/3)
        self.chA90  = ROOT.TH1F('channel variation A90%s'%(sidename), '', 50, -graph_lim/3, graph_lim/3)


        for i in range(10): #A Cells (LB)
            name_h = "cell_deviation_A%d%s" % (i+1,sidename)
            self.chans.append(ROOT.TH1F(name_h, '', 400, -14, +14))

        for i in range(9): #BC Cells (LB)
            name_h = "cell_deviation_BC%d%s" % (i+1,sidename)
            self.chans.append(ROOT.TH1F(name_h, '', 400, -12, +12))

        for i in range(4): #D Cells (LB)
            name_h = "cell_deviation_D%d%s" % (i,sidename)
            self.chans.append(ROOT.TH1F(name_h, '', 400, -12, +12))

        for i in range(5): #A Cells (EB)
            name_h = "cell_deviation_A%d%s" % (i+12,sidename)
            self.chans.append(ROOT.TH1F(name_h, '', 300, -14, +14))

        for i in range(5): #B Cells + C10
            name_h = "cell_deviation_B%d%s" % (i+11,sidename)
            self.chans.append(ROOT.TH1F(name_h, '', 400, -12, +12))
        self.chans.append(ROOT.TH1F("cell_deviation_C10", '', 400, -12, +12))

        for i in range(3): #D Cells (EB)
            name_h = "cell_deviation_ED%d%s" % (i+4,sidename)
            self.chans.append(ROOT.TH1F(name_h, '', 400, -12, +12))

        for i in range(4): #gap E Cells
            name_h = "cell_deviation_E%d%s" % (i+1,sidename)
            self.chans.append(ROOT.TH1F(name_h, '', 400, -40, +40))

            
        self.fib = ROOT.TH1F('fiber variation%s' %(sidename)  , '', 100, -graph_lim, graph_lim)


    # Here we deal with all the necessary cosmetics
    def ProcessStop(self):
        
        global EBScale;

        self.HistFile.cd(self.dirname)
        
        for i in range(41):
            cvar=0.0
            hist = self.chans[i]
            fit1 = ROOT.TF1("fit1", "gaus")
            if (i < 37):
                hist.Fit(fit1,"Q","",-12,+7.5)
            else:
                hist.Fit(fit1,"Q","",-25.5,+25.5)
            

            self.c1 = src.MakeCanvas.MakeCanvas()
            self.c1.SetFillColor(0)
            self.c1.SetBorderMode(0)                    
            self.c1.cd()
            hist.Draw()

            if (abs(fit1.GetParameter(1)-hist.GetMean())>0.4):
                cvar=hist.GetMean()*100
                print('WARNING WARNING, printed a control plot for cell',i)
                self.c1.Print("%s/%s_fitcontrol.eps" % (self.dir,hist.GetName()))
                self.c1.Print("%s/%s_fitcontrol.root" % (self.dir,hist.GetName()))

            else:
                cvar=fit1.GetParameter(1)*100
                self.c1.Print("%s/%s_fit.eps" % (self.dir,hist.GetName()))

            if (cvar == 0):
                cvar=1
                    
            if (self.verbose):
                print(' -- cell ',i,' mean deviation = ',hist.GetMean(),'% Fitted mean ', fit1.GetParameter(1),' % (will use: ',cvar,') ',hist.GetEntries(),' entries..')

            if (self.ComputeEBScale):
                if (i==9):
                    # EBScale = EBScale+self.ch_fit.GetParameter(1)
                    EBScale = EBScale+(cvar/100.0)
                    print(" x ",fit1.GetParameter(1),(cvar/100.0))
                if (i==25):
                    # EBScale = EBScale-self.ch_fit.GetParameter(1)
                    EBScale = EBScale-(cvar/100.0)
                    print(" / ",fit1.GetParameter(1),(cvar/100.0))

            hist.Write() # write hist with fit to output ROOT file
            hist.Delete()

            text = "%d\n" % (cvar)
            self.outfile.write(text)
            
        self.outfile.close()        


    # Here we fill the histograms and the bad channel list
    def ProcessRegion(self, region):

        fib_list = set()
        first = True
        first_LG = True
        first_HG = True
            
        bad_fib_list    = []
        bad_las_list    = []
        bad_las_event   = []
        no_las_list     = []
        no_las_event    = []
        bad_las_list_K  = []
        bad_las_event_K = []
        no_las_list_K   = []
        no_las_event_K  = []

            
        for event in region.GetEvents():

            if ((self.runNumber!=event.run.runNumber) and (self.runNumber>0)):
                continue
            if 'is_OK' in event.data:

                [p, i, j, w] = self.PMTool.GetNumber(event.data['region'])

                if self.side == 'A' and 'C' in self.PMTool.get_partition_name(p-1):
                    continue
                if self.side == 'C' and 'A' in self.PMTool.get_partition_name(p-1):
                    continue

                if w!=self.gain and self.gain!=2:
                    continue

                if first and self.gain!=2:
                    self.runno = event.run.runNumber
                    first=False

                elif self.gain==2:
                    if first_LG and w==0:
                        first_LG        = False
                        self.ref_LG_evt = event
                    if first_HG and w==1:
                        first_HG        = False
                        self.ref_HG_evt = event 

                if 'deviation' not in event.data: # No data
                    [p, i, j, w] = self.PMTool.GetNumber(event.data['region'])
                    index        = self.PMTool.get_index(p-1, i-1, j, w)

                    no_las_list.append(index)
                    no_las_event.append(event)     

                else:
                    pmt    = self.PMTool.get_PMT_index(p-1,i-1,j)                          
                    indice = self.PMTool.get_fiber_index(p-1,i-1,pmt)

                    if not event.data['status']:   # Don't put event on summary plot if already on BC list                            
                        # Following selection remove the events with low LASER light (fiber problem)

                        self.calib.Fill(event.data['calibration'])
                        if (event.data['calibration']>0.0001 and event.run.data['wheelpos']==8)\
                                or (event.data['calibration']>0.01 and event.run.data['wheelpos']==6):

                            Celln = self.PMTool.get_stable_cells(p-1,pmt) # Get cell name needs pmt number starting from 1
                            Celli = self.PMTool.get_cell_index(p-1,i,pmt)

                            ## corrected map
                            layer =  region.GetLayerName()                       #Use of functions to get name of layer and region for 
                            cell  =  region.GetCellName()
                                
                            Celli=0
                            if (layer=="A"):
                                Celli=100+int(cell[1:])
                            elif (layer=="B"):
                                Celli=200+int(cell[1:])
                            elif (layer=="C"):
                                Celli=216
                            elif (layer=="BC"):
                                Celli=200+int(cell[2:])
                            elif (layer=="D"):
                                Celli=400+int(cell[1:])
                            elif (layer in ['E1','E2','E3','E4']):
                                Celli=500+int(layer[1:])
                            elif (layer=="MBTS"):
                                Celli=1000 #MBTS will be ignored
                            else:
                                print("ERROR, unknown cell ",layer)
    

                            # print with average deviation instead
                            if self.average:
                                if 'deviation' in region.data:
                                    self.ch.Fill(region.data['deviation'])
                                else:
                                    print("You selected option average {} and 'deviation' in region.data is {}".format(self.average, 'deviation' in region.data))
                            else:
                                self.ch.Fill(event.data['deviation'])
    
                            ## remplissage des histos de cellules
                            for i in range(41):

                                if ( (i<10) and (Celli == i+101)):
                                    self.chans[i].Fill(event.data['deviation'])

                                if ( (i>=10) and (i<19) and (Celli == i-10+201)):
                                    self.chans[i].Fill(event.data['deviation'])

                                if ( (i>=19) and (i<23) and (Celli == i-19+400) ):
                                    self.chans[i].Fill(event.data['deviation'])

                                ## EA
                                if ( (i>=23) and (i<28) and (Celli == i-23+112)):
                                    self.chans[i].Fill(event.data['deviation'])
                                ## EB
                                if ( (i>=28) and (i<34) and (Celli == i-28+211)):
                                    self.chans[i].Fill(event.data['deviation'])
                                ## ED
                                if ( (i>=34) and (i<37) and (Celli == i-34+404)):
                                    self.chans[i].Fill(event.data['deviation'])
                                ## E GAPS
                                if ( (i>=37) and (i<41) and (Celli == i-37+501)):
                                    self.chans[i].Fill(event.data['deviation'])
