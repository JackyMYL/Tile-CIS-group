############################################################
#
# compute_mean_cell_var.py
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

class compute_mean_cell_var(GenericWorker):
    "Produce summary plots"

    def ProcessStart(self):
        global EBScale ## correction in %
        print("Using run #", self.runNumber," for cell map")
        filename = "data_cells_var_%s.txt" % (self.gname)
        self.outfile = open(os.path.join(getResultDirectory(),filename), 'w')
        

    def __init__(self, limit=2, gain=0,runNumber=0,ComputeEBScale=True):

        global EBScale
        if (ComputeEBScale):
            EBScale = 0.0
        self.ComputeEBScale = ComputeEBScale
        self.limit = limit
        self.runNumber=runNumber
        graph_lim  = 5*self.limit
        graph_lim_calib_up = 0
        graph_lim_calib_down = 0

        self.gain  = gain

        if self.gain == 0:
            self.gname = 'lg'
            graph_lim_calib_up = 1
            graph_lim_calib_down = -0.05
        if self.gain == 1:
            self.gname = 'hg'
            graph_lim_calib_up = 0.01
            graph_lim_calib_down = -0.002
        if self.gain == 2:
            self.gname = 'global'
        
        self.outputTag = outputTag # global variable to tag output histogram file name
        self.dir    = getPlotDirectory(subdir=self.outputTag)
        self.PMTool = LaserTools()

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
            self.part_bchan.append(ROOT.TH2F("%s bad"%(pname),"",500,0.,65.,500,0.,49.))
            self.part_wchan.append(ROOT.TH2F("%s warn"%(pname),"",500,0.,65.,500,0.,49.))
            self.part_nochan.append(ROOT.TH2F("%s nodat"%(pname),"",500,0.,65.,500,0.,49.))

        self.ch  = ROOT.TH1F('channel variation', '', 100, -graph_lim, graph_lim)
        self.calib = ROOT.TH1F('real channel variation', '', 100, graph_lim_calib_down, graph_lim_calib_up)

        # DB : added these histo to split in cell for LB
        self.chA  = ROOT.TH1F('channel variation A', '', 100, -graph_lim/3, graph_lim/3)
        self.chB  = ROOT.TH1F('channel variation B', '', 100, -graph_lim/3, graph_lim/3)
        self.chD  = ROOT.TH1F('channel variation D', '', 100, -graph_lim/3, graph_lim/3)

        # DB : added these histo to split in cell for EB
        self.chEA  = ROOT.TH1F('channel variation EB A', '', 100, -graph_lim/3, graph_lim/3)
        self.chEB  = ROOT.TH1F('channel variation EB B', '', 100, -graph_lim/3, graph_lim/3)
        self.chED  = ROOT.TH1F('channel variation EB D', '', 100, -graph_lim/3, graph_lim/3)

        # DB : added histo specific to A cells : drifting cells with lumi
        self.chA12  = ROOT.TH1F('channel variation A12', '', 50, -graph_lim/3, graph_lim/3)
        self.chA34  = ROOT.TH1F('channel variation A34', '', 50, -graph_lim/3, graph_lim/3)
        self.chA56  = ROOT.TH1F('channel variation A56', '', 50, -graph_lim/3, graph_lim/3)
        self.chA78  = ROOT.TH1F('channel variation A78', '', 50, -graph_lim/3, graph_lim/3)
        self.chA90  = ROOT.TH1F('channel variation A90', '', 50, -graph_lim/3, graph_lim/3)


        for i in range(10): #A Cells

            name_h = "cell_deviation_a %d" % (i)
            self.chans.append(ROOT.TH1F(name_h, '', 400, -14, +14))

        for i in range(9): #BC Cells

            name_h = "cell_deviation_BC %d" % (i)
            self.chans.append(ROOT.TH1F(name_h, '', 400, -12, +12))

        for i in range(4): #D Cells

            name_h = "cell_deviation_d %d" % (i)
            self.chans.append(ROOT.TH1F(name_h, '', 400, -12, +12))

        for i in range(5): #EA Cells

            name_h = "cell_deviation_ea %d" % (i)
            self.chans.append(ROOT.TH1F(name_h, '', 300, -14, +14))

        for i in range(6): #EB Cells + C10

            name_h = "cell_deviation_eb %d" % (i)
            self.chans.append(ROOT.TH1F(name_h, '', 400, -12, +12))

        for i in range(3): #ED Cells

            name_h = "cell_deviation_ed %d" % (i)
            self.chans.append(ROOT.TH1F(name_h, '', 400, -12, +12))

        for i in range(4): #gap E Cells

            name_h = "cell_deviation_egap %d" % (i)
            self.chans.append(ROOT.TH1F(name_h, '', 400, -40, +40))

            
        self.fib = ROOT.TH1F('fiber variation'  , '', 100, -graph_lim, graph_lim)

        # Finally the file containing the bad channel list




    # Here we deal with all the necessary cosmetics

    def ProcessStop(self):
        
        global EBScale;

        for i in range(41):

            cvar=0.0

            if (i < 37):
                self.chans[i].Fit("gaus","Q0","",-7.5,+7.5)
            else:
                self.chans[i].Fit("gaus","Q0","",-25.5,+25.5)

            self.ch_fit= ROOT.TVirtualFitter.Fitter(self.chans[i])
            
            if (abs(self.ch_fit.GetParameter(1)-self.chans[i].GetMean())>0.4):
                cvar=self.chans[i].GetMean()*100

                print('WARNING WARNING, printed a control plot for cell',i)
                self.c1 = src.MakeCanvas.MakeCanvas()
                self.c1.SetFillColor(0)
                self.c1.SetBorderMode(0)                    
                self.c1.cd()
                self.chans[i].Draw()
                self.c1.Print("%s/%d.eps" % (self.dir,i))
                self.c1.Print("%s/%d.root" % (self.dir,i))
                self.c1.Delete()

            else:
                cvar=self.ch_fit.GetParameter(1)*100
                
            if (cvar == 0):
                cvar=1
                    
            print(' -- cell ',i,' mean deviation = ',self.chans[i].GetMean(),'% Fitted mean ', self.ch_fit.GetParameter(1),' % (will use: ',cvar,') ',self.chans[i].GetEntries(),' entries..')

            ## EBScale = A10/A13 = 110/113 or A10/A14 = 110/114

            if (self.ComputeEBScale):
                if (i==9):
                    #                EBScale = EBScale+self.ch_fit.GetParameter(1)
                    EBScale = EBScale+(cvar/100.0)
                    print(" x ",self.ch_fit.GetParameter(1),(cvar/100.0))
                if (i==25):
                    #                EBScale = EBScale-self.ch_fit.GetParameter(1)
                    EBScale = EBScale-(cvar/100.0)
                    print(" / ",self.ch_fit.GetParameter(1),(cvar/100.0))

            self.chans[i].Scale(0.0)

#            if (i>=23 and not self.ComputeEBScale):
#                cvar = cvar+(EBScale*100)

            text = "%d\n" % (cvar)
            self.outfile.write(text)
            
        self.outfile.close()        

        

        print("Correction in % for EB = ", EBScale)

    # Here we fill the histograms and the bad channel list
    def ProcessRegion(self, region):
                          
#        if 'TILECAL' == region.GetHash() or true:

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

                if w!=self.gain and self.gain!=2:
                    continue

                if first and self.gain!=2:
                    self.runno = event.run.runNumber

#                        text = "# Summary for run %d\n" % (event.run.runNumber)
#                        self.outfile.write(text)
#                        text = "# Date of the run: %s\n" % (event.run.time_in_seconds)

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


#                        if event.data['isBad']:
#                            no_las_list_K.append(index)
#                            no_las_event_K.append(event)
#                        else:
                    no_las_list.append(index)
                    no_las_event.append(event)     

                else:
                    pmt    = self.PMTool.get_PMT_index(p-1,i-1,j)                          
                    indice = self.PMTool.get_fiber_index(p-1,i-1,pmt)


#                        if event.data.has_key('part_var') and p-1 not in partition_list:
#                            print self.PMTool.get_partition_name(p-1),"global variation =", event.data['part_var'],"%"
#                            partition_list.add(p-1)
                            
#                        if event.data.has_key('fiber_var') and indice not in fib_list:
#                            fib_list.add(indice)
#                            self.fib.Fill(event.data['fiber_var'])

#                            if indice not in bad_fib_list and self.limit<math.fabs(event.data['fiber_var']):
#                                bad_fib_list.append(indice)
                                                        
##                        if not event.data['isBad'] and not event.data['status']:   # Don't put event on summary plot if already on BC list
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
                                    
                                #print " part = ",p-1," PMT = ",pmt," cell = ",Celln
                                #print 'deviation in do_summary_plot (before fill) :',event.data['deviation']
                            self.ch.Fill(event.data['deviation'])
                                
                                #print 'deviation in do_summary_plot (after fill):',event.data['deviation']




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



