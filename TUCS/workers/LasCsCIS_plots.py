############################################################
#
# LasCsCIS_plots.py
#
############################################################
#
# Author: Joshua Montgomery <Joshua.J.Montgomery@gmail.com>
# Date  : February 17, 2012
#
# Notes: Default CIS HG: 81.3669967651
#        Default CIS LG: 1.29400002956
#
######################### USER GUIDE TO DICTIONARY ############################# 
#                                                                               #
#self.Region_Dict[region] = [tgraph_cis_Default_HG  = self.Region_Dict[key][0]  #
#                            tgraph_cis_Default_LG, = self.Region_Dict[key][1]  #      
#                            tgraph_cis_DB_HG,      = self.Region_Dict[key][2]  #
#                            tgraph_cis_DB_LG,      = self.Region_Dict[key][3]  #
#                            tgraph_las_lg,         = self.Region_Dict[key][4]  #
#                            tgraph_las_hg,         = self.Region_Dict[key][5]  #
#                            tgraph_cs,             = self.Region_Dict[key][6]  #
#                            tgraph_hv,             = self.Region_Dict[key][7]  #
#                            PMT_Index              = self.Region_Dict[key][8]  #
#                            Instrumented_Channel   = self.Region_Dict[key][9]  #
#                            Region_Problems]       = self.Region_Dict[key][10] #
#                                                                               #
################################################################################   

from src.GenericWorker import *
import src.oscalls
import os.path
import src.MakeCanvas
import time
import math
import ROOT
from ROOT import TCanvas, TPad

class LasCsCIS_plots(GenericWorker):
    "This worker generates fractional response plots with combined TileCal calibration systems."

    def __init__(self, Region, plotdirectory=None):


        self.time_max          = None
        self.time_min          = None
        self.Given_Regions     = Region
        self.PMTool            = LaserTools()
        self.origin            = ROOT.TDatime()
        self.dir               = src.oscalls.getPlotDirectory()
        self.c1                = src.MakeCanvas.MakeCanvas()
        self.Region_Dict       = dict()
        self.Restrict_Region   = self.Build_Regions(self.Given_Regions)        
        self.plotdirectory     = plotdirectory
        
        if self.plotdirectory: 
            self.dir = os.path.join(self.dir, 'Combined_Tool', self.plotdirectory)
        else:
            self.dir = os.path.join(self.dir, 'Combined_Tool')

        src.oscalls.createDir(self.dir)
        PMT_Index_Slot         = None
        Instrumented_Channel   = False
        ChannelProblems        = []
      
        tgraph_cis_Default_HG  = ROOT.TGraphErrors()
        tgraph_cis_Default_LG  = ROOT.TGraphErrors()
        tgraph_cis_DB_HG       = ROOT.TGraphErrors()
        tgraph_cis_DB_LG       = ROOT.TGraphErrors()        
        tgraph_las_lg          = ROOT.TGraphErrors()
        tgraph_las_hg          = ROOT.TGraphErrors()
        tgraph_cs              = ROOT.TGraphErrors()
        tgraph_hv              = ROOT.TGraph()
      
      
        if isinstance(self.Restrict_Region, list):
            for region in self.Restrict_Region:
                self.Region_Dict[region] = [ROOT.TGraphErrors(),
                                            ROOT.TGraphErrors(),
                                            ROOT.TGraphErrors(),
                                            ROOT.TGraphErrors(),
                                            ROOT.TGraphErrors(),
                                            ROOT.TGraphErrors(),
                                            ROOT.TGraphErrors(),
                                            ROOT.TGraph(),
                                            PMT_Index_Slot,
                                            Instrumented_Channel,
                                            ChannelProblems]
                                            
        elif isinstance(self.Restrict_Region, str):
            self.Region_Dict[self.Restrict_Region] = [tgraph_cis_Default_HG,
                                            tgraph_cis_Default_LG,        
                                            tgraph_cis_DB_HG,
                                            tgraph_cis_DB_LG,
                                            tgraph_las_lg,
                                            tgraph_las_hg,
                                            tgraph_cs,
                                            tgraph_hv,
                                            PMT_Index_Slot,
                                            Instrumented_Channel,
                                            ChannelProblems]
        else:
            raise exception('Regions variable is being given to this program as an  \
                   incorrect type. It must be a string, or list of strings.')
            
        
    def ProcessStart(self):
        run_times = []
        global run_list
        for run in run_list.getRunsOfType('Las')+run_list.getRunsOfType('cesium')+run_list.getRunsOfType('CIS'):
            if run.time == None: continue
                
            run_times.append((run.time, run.time_in_seconds))

        if not run_times:
            raise exception('ERROR: Either runs are missing time data, or runs list is not \
                   being handed off to this worker.')

        self.time_max = max(run_times, key = lambda x: x[1])[1]
        self.time_min = min(run_times, key = lambda x: x[1])[1]
        self.origin   = ROOT.TDatime(str(min(run_times, key = lambda x: x[1])[0]))



    def ProcessRegion(self, region):
        
        
        use_region = False
        use_key    = None
        for key in self.Region_Dict:
            if key in region.GetHash():
                use_region = True
                use_key    = key
                self.Region_Dict[key][9] = True
        if not use_region:
            return
        
        
        numbers = region.GetNumber()
        if len(numbers)==4:
            [part, module, channel, gain] = numbers
        elif len(numbers)==3:
            [part, module, channel] = numbers
        else:
            return 

        self.Region_Dict[use_key][8] = self.PMTool.get_index(part-1,module-1,channel,0)

        for event in region.GetEvents():
            if event.run.runType=='Las':
                if 'deviation' not in event.data:
                    print(('Run {0}:  Las has no deviation info for {1}'.format(event.run.runNumber, region.GetHash())))
                    continue
                
                if gain:                           # FILL LASER HIGH GAIN TGRAPH
                    
                    value_las_HG   = 1.+event.data['deviation']/100.
                    npoints_las_HG = self.Region_Dict[use_key][5].GetN()
                    self.Region_Dict[use_key][5].SetPoint(npoints_las_HG,
                                    event.run.time_in_seconds-self.time_min,
                                    value_las_HG) 
                    
                else:                              # FILL LASER LOW GAIN TGRAPH
                    
                    value_las_LG   = 1.+event.data['deviation']/100.
                    npoints_las_LG = self.Region_Dict[use_key][4].GetN()
                    self.Region_Dict[use_key][4].SetPoint(npoints_las_LG,
                                    event.run.time_in_seconds-self.time_min,
                                    value_las_LG) 
                    
                if 'HV' in event.data:       # FILL HIGH VOLTAGE TGRAPH
                    if (event.data['HVSet'])!=0:
                        npoints_HV = self.Region_Dict[use_key][7].GetN()

                        beta = 6.9
                        if 'beta' in event.region.GetParent().data:
                            beta = event.region.GetParent().data['beta']
                        
                        value_HV   = 1+beta*(event.data['HV']-event.data['HVSet']
                                            )/event.data['HVSet']
                        self.Region_Dict[use_key][7].SetPoint(npoints_HV,
                                                event.run.time_in_seconds-self.time_min,
                                                value_HV)
                else:
                    print(('Run {0}: Laser event data missing HV info for {1}'.format(event.run.runNumber, region.GetHash())))
            
        
            elif event.run.runType=='cesium':      # FILL CESIUM TGRAPH

                if 'calibration' not in event.data:
                    print(('Run {0}: no Cs calibration data filled for {1}'.format(event.run.runNumber, region.GetHash())))
                    continue
                if not event.data['calibration']:
                    print(('Run {0}: None Type Cs calibration data filled for {1}'.format(event.run.runNumber, region.GetHash())))                    
                    continue
                    
                value_Cs   = event.data['calibration']/event.data['f_integrator_db']
                npoints_Cs = self.Region_Dict[use_key][6].GetN()
                self.Region_Dict[use_key][6].SetPoint(npoints_Cs,
                                event.run.time_in_seconds-self.time_min,
                                value_Cs)
            
            
            elif event.run.runType=='CIS':
                if 'gain' not in region.GetHash():
                    print(('Run {0}: Warning: CIS event with no gain tag! region: {1}'.format(event.run.runNumber, region.GetHash())))
                    continue
                if 'calibration' not in event.data:
                    print(('Run {0}: Event Data Dictionary missing calibration key: {1}'.format(event.run.runNumber, region.GetHash())))
                    continue
                if 'deviation' not in event.data:
                    print(('Run {0}: Event Data Dictionary missing deviation key: {1}'.format(event.run.runNumber, region.GetHash())))
                    continue


                if gain:                         # FILL CIS HIGH GAIN TGRAPHS
                    
                    valueDB_HG    = event.data['deviation'] + 1.
                    npointsDB_HG  = self.Region_Dict[use_key][2].GetN()
                    self.Region_Dict[use_key][2].SetPoint(npointsDB_HG,
                                    event.run.time_in_seconds-self.time_min,
                                    valueDB_HG)                
                
                    valueDFT_HG   = (event.data['calibration']/81.3669967651)
                    npointsDFT_HG = self.Region_Dict[use_key][0].GetN()
                    self.Region_Dict[use_key][0].SetPoint(npointsDFT_HG,
                                    event.run.time_in_seconds-self.time_min,
                                    valueDFT_HG)

                else:                           # FILL CIS LOW GAIN TGRAPHS

                    valueDB_LG    = event.data['deviation'] + 1.
                    npointsDB_LG  = self.Region_Dict[use_key][3].GetN()
                    self.Region_Dict[use_key][3].SetPoint(npointsDB_LG,
                                    event.run.time_in_seconds-self.time_min,
                                    valueDB_LG)                

                    valueDFT_LG   = (event.data['calibration']/1.29400002956)
                    npointsDFT_LG = self.Region_Dict[use_key][1].GetN()                
                    self.Region_Dict[use_key][1].SetPoint(npointsDFT_LG,
                                    event.run.time_in_seconds-self.time_min,
                                    valueDFT_LG)
                
            
            
            else:
                print(('Run {0}: Warning -- unsorted event: {1}'.format(event.run.runNumber, region.GetHash())))
                continue
            
            #print 'Getting Problems'
            if 'problems' in event.data:
                for problem in event.data['problems']:
                    #print problem
                    self.Region_Dict[use_key][10].append(problem)

 
    def ProcessStop(self):
        
        for key in self.Region_Dict:
            if self.Region_Dict[key][9]:
                self.Process_Graphs(self.Region_Dict[key][0], 
                                self.Region_Dict[key][1], self.Region_Dict[key][2],
                                self.Region_Dict[key][3], self.Region_Dict[key][4],
                                self.Region_Dict[key][5], self.Region_Dict[key][6],
                                self.Region_Dict[key][7], self.Region_Dict[key][8],
                                self.Region_Dict[key][10],key)
                                # refer to users guide at top for Region_Dict definitions
 
            else:
                print(('WARNING: NO DETECTOR REGION CORRESPONDING TO', key))
                print('ARE YOU SURE THIS IS AN INSTRUMENTED CHANNEL?')
 
        return
 
 
 
    def Process_Graphs(self, CIS_Default_HG, CIS_Default_LG, CIS_DB_HG, CIS_DB_LG,
                       LAS_LG, LAS_HG, CS_Plot, HV_Plot, PMT_Index, ChannelProblems, Channel_Index):

        self.c1.Clear()
        
        self.c1.SetWindowSize(1000,600)
        tpad0 = ROOT.TPad("0","plot pad",0.0,0.0,0.7,1.0)
        tpad1 = ROOT.TPad("1","info pad",0.7,0.0,1.0,1.0)
        tpad0.Draw()
        tpad1.Draw()
        
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetStatX(0.78)
        ROOT.gStyle.SetStatY(0.83)

        ROOT.gStyle.SetOptTitle(1)
        ROOT.gStyle.SetTitleX(0.15)
        ROOT.gStyle.SetTitleW(0.2)
        ROOT.gStyle.SetTitleBorderSize(0)                                          
        ROOT.gStyle.SetTitleFontSize(0.1)
        ROOT.gStyle.SetEndErrorSize(0.)

        ROOT.gStyle.SetTimeOffset(self.origin.Convert());

        CS_Plot.SetMarkerStyle(20)
        CS_Plot.SetMarkerColor(ROOT.kViolet)
        CS_Plot.SetMarkerSize(0.8)

        HV_Plot.SetLineColor(ROOT.kGreen + 3)

        CIS_DB_HG.SetMarkerStyle(23)        
        CIS_DB_HG.SetMarkerColor(ROOT.kBlue - 4)
        CIS_DB_HG.SetMarkerSize(0.8)
        
        CIS_DB_LG.SetMarkerStyle(32)        
        CIS_DB_LG.SetMarkerColor(ROOT.kBlue + 2)
        CIS_DB_LG.SetMarkerSize(0.9)
        
        CIS_Default_HG.SetMarkerStyle(22)
        CIS_Default_HG.SetMarkerColor(ROOT.kRed - 4)
        CIS_Default_HG.SetMarkerSize(0.8)
        
        CIS_Default_LG.SetMarkerStyle(26)        
        CIS_Default_LG.SetMarkerColor(ROOT.kRed + 1)
        CIS_Default_LG.SetMarkerSize(0.9)

        LAS_HG.SetMarkerStyle(21)
        LAS_HG.SetMarkerSize(0.8)
        
        LAS_LG.SetMarkerStyle(25)
        LAS_LG.SetMarkerSize(0.8)        

        histtitle = 'PMT: {0}    ADC: {1}'.format(self.PMTool.get_pmt_name_index(PMT_Index), Channel_Index)
        
        cadre_xmin = -43200.
        cadre_xmax = self.time_max-self.time_min+43200.
        cadre_ymin = 0.97
        cadre_ymax = 1.03
        cadre      = ROOT.TH2F('CadreSignal', '',\
                          100, cadre_xmin, cadre_xmax,
                          100, cadre_ymin, cadre_ymax )

        cadre.GetXaxis().SetTimeDisplay(1)
        cadre.GetYaxis().SetTitleOffset(1.1)
        cadre.GetXaxis().SetLabelOffset(0.03)
        cadre.GetYaxis().SetLabelOffset(0.01)
        cadre.GetXaxis().SetLabelSize(0.04)
        cadre.GetYaxis().SetLabelSize(0.04)           
        cadre.GetXaxis().SetTimeFormat("#splitline{%Y}{%d/%m}")
        cadre.GetXaxis().SetNdivisions(-503)
        cadre.GetYaxis().SetTitle("Fractional Response")
        cadre.GetYaxis().CenterTitle()
        
        tpad0.cd()
        cadre.Draw()
        
        option = 'L,same'
        for tgraph in [HV_Plot, LAS_HG, LAS_LG, CS_Plot, CIS_DB_HG,
                       CIS_DB_LG, CIS_Default_HG, CIS_Default_LG]:
            
            if tgraph.GetN()>0:
                tgraph.GetXaxis().SetTimeDisplay(1)
                tgraph.GetXaxis().SetLabelSize(0.04)
                tgraph.GetXaxis().SetTimeFormat("#splitline{%Y}{%d/%m}")
                tgraph.GetXaxis().SetNdivisions(-503)

                tgraph.GetYaxis().SetLabelOffset(0.01)
                tgraph.GetYaxis().SetTitleOffset(1.1)
                tgraph.GetYaxis().SetTitle("calibration")
                tgraph.GetYaxis().SetLabelSize(0.04)  
                tgraph.Sort()
                tgraph.Draw(option)
            option = 'P,same'
        
        
        tpad1.cd() 
        
        title=ROOT.TLatex()
        title.SetNDC()
        title.SetTextSize(0.08)
        title.DrawLatex(0.0,0.9, 'Covering Channels:');
        
        title0=ROOT.TLatex()
        title0.SetNDC()
        title0.SetTextSize(0.08)
        pmt_title=histtitle.split()[0]+' '+histtitle.split()[1]
        title0.DrawLatex(0.0,0.85, pmt_title);

        title1=ROOT.TLatex()
        title1.SetNDC()
        title1.SetTextSize(0.08)
        adc_title=histtitle.split()[2]+' '+histtitle.split()[3]
        title1.DrawLatex(0.0,0.80, adc_title);
        
        legend = ROOT.TLegend(0.0,0.5,0.7,0.75)
        legend.SetTextSize(0.05)
        legend.AddEntry(LAS_HG,"Laser Highgain (filter 8)","p")
        legend.AddEntry(LAS_LG,"Laser Lowgain (filter 6)","p")
        legend.AddEntry(CS_Plot,"Cesium","p")
        legend.AddEntry(HV_Plot,"Gain variation from HV","L")
        legend.AddEntry(CIS_DB_HG,"Highgain from CIS DB value","p")
        legend.AddEntry(CIS_DB_LG,"Lowgain from CIS DB value","p")
        legend.AddEntry(CIS_Default_HG,"Highgain from CIS Det Avg","p")
        legend.AddEntry(CIS_Default_LG,"Lowgain from CIS Det Avg","p")
        
        legend.Draw()
        
        #draw text with known problems in channel
        problem_title=ROOT.TLatex()
        problem_title.SetNDC()
        problem_title.SetTextSize(0.08)
        problem_title.DrawLatex(0.1,0.4, "Known Problems:");
        
        
        problembox=ROOT.TPaveText(0.1,0.2,0.9,0.35,"brNDC")
        problembox.SetBorderSize(0)
        problembox.SetFillColor(0)
        problembox.SetTextSize(0.08)
        problembox.SetTextFont(42)
        #print ChannelProblems
        if ChannelProblems==[]: 
            problembox.AddText("No Problems")
        else:
            #print ChannelProblems
            ProblemSet = set(ChannelProblems)
            for problem in ProblemSet:
                problembox.AddText(problem)

                
        problembox.Draw()


        
        self.c1.Modified()       
        plot_name = "channel_%s_LasCsCIS_history" % \
                    (self.PMTool.get_pmt_name_index(PMT_Index))
        self.c1.Print("%s/%s.eps" % (self.dir, plot_name))
        self.c1.Print("%s/%s.pdf" % (self.dir, plot_name))
        #self.c1.Print("%s/%s.C" % (self.dir, plot_name))
        #self.c1.Print("%s/%s.png" % (self.dir, plot_name))



    def Build_Regions(self, region_list):
        'Re-formats user-created run list to computer-readable runlist'
        
        Useable_Regions = []
        for region in region_list:
            if not '_m' in region:
                for mod in range(1,65):
                    for chan in range(48):
                        Useable_Regions.append('{0}_m{1:02d}_c{2:02d}'.format(region, mod, chan))
            elif not '_c' in region:
                for chan in range(48):
                    Useable_Regions.append('{0}_c{1:02d}'.format(region, chan))
            else:
                Useable_Regions.append(region)
                
        return Useable_Regions
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
