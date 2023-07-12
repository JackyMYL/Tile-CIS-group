############################################################
#
# compareCs_with_Las.py
#
############################################################
#
# Author: Seb Viret <viret@in2p3.fr>
#
# April 20, 2010
#
# Goal: 
# This macros provides a comparison of the LASER constants with the Cesium ones
# LASER is supposed to compensate the channel variation between two Cs updates
# So, comparing the LASER variation obtained before the Cs update with the Cs variation,
# there should be a correlation
#
# The way to do that (you need to use specific runs)
# is described in PROCEDURE 9 of the LASER webpage
#
#
# Input parameters are:
#
# -> run_bef: the LASER run number corresponding to the time of the Cs runs 
#             contains the corrct LASER info and the old Cs constants
#
# -> run_aft: a LASER run number recorded after the Cs update, thus containing the new Cs values 
#             
#
# For more info on the LASER system : http://atlas-tile-laser.web.cern.ch
#
#############################################################



from src.GenericWorker import *
from src.oscalls import *
from src.region import *
from array import *
import ROOT
import math
import src.MakeCanvas

class compareCs_with_Las(GenericWorker):
    "This worker compares the Cesium with the LASER"    
        
    c1 = None
    c2 = None
    
    def __init__(self, run_bef=146962, run_aft=153250):
        self.run_bef  = run_bef
        self.run_aft  = run_aft

        self.outputTag = outputTag # global variable to tag output histogram file name
        self.dir    = getPlotDirectory(subdir=self.outputTag)        
        self.summary_cs = ROOT.TH2F('summary_cs', '',\
                                    2000, 0., 1.5, 2000, 0., 1.5)

        self.ratio_cs = ROOT.TH1F('ratio_cs', '',\
                                    100, 0.9, 1.1)

        if self.c1==None:
            self.c1 = src.MakeCanvas.MakeCanvas()
            #self.c1.SetTitle("Put here a nice title")

        
    def ProcessStop(self):

        
        self.c1.SetFrameFillColor(0)
        self.c1.SetFillColor(0);
        self.c1.SetBorderMode(0); 
        self.c1.SetGridx(1);
        self.c1.SetGridy(1);
        
        self.c1.cd()
        ROOT.gStyle.SetOptStat(0) 

        self.summary_cs.GetXaxis().SetLabelOffset(0.015)
        self.summary_cs.GetXaxis().SetLabelSize(0.04)
        self.summary_cs.GetXaxis().SetTitleOffset(1.1)
        self.summary_cs.GetXaxis().SetTitle("Channel variation from LASER system")
        self.summary_cs.GetYaxis().SetLabelOffset(0.015)
        self.summary_cs.GetYaxis().SetLabelSize(0.04)
        self.summary_cs.GetYaxis().SetTitleOffset(1.2)
        self.summary_cs.GetYaxis().SetTitle("Channel variation from Cesium system")
        self.summary_cs.Draw()

        self.c1.Print("%s/Las_vs_Cs.C" % (self.dir))
        self.c1.Print("%s/Las_vs_Cs.eps" % (self.dir))
        self.c1.Print("%s/Las_vs_Cs.png" % (self.dir))

        
        self.c2.SetFrameFillColor(0)
        self.c2.SetFillColor(0);
        self.c2.SetBorderMode(0); 
        self.c2.SetGridx(1);
        self.c2.SetGridy(1);
        
        self.c2.cd()
        ROOT.gStyle.SetOptStat(0)
        
        self.ratio_cs.GetXaxis().SetLabelOffset(0.015)
        self.ratio_cs.GetXaxis().SetLabelSize(0.04)
        self.ratio_cs.GetYaxis().SetLabelSize(0.04)
        self.ratio_cs.GetXaxis().SetTitle("Cesium over LASER")
        self.ratio_cs.Draw()


        self.ratio_cs.Fit("gaus","Q")
        self.ratio_cs_fit= ROOT.TVirtualFitter.Fitter(self.ratio_cs)
        self.pt_ratio_cs = ROOT.TPaveText(0.62,0.54,0.88,0.65,"brNDC")
        self.pt_ratio_cs.SetFillColor(5)
        self.pt_ratio_cs.SetTextSize(0.04)
        self.pt_ratio_cs.SetTextFont(42)                        
        self.pt_ratio_cs.AddText("ratio = %.3f #pm %.3f\n" \
                                 % (self.ratio_cs_fit.GetParameter(1),self.ratio_cs_fit.GetParameter(2)))
        self.pt_ratio_cs.Draw()

        self.c2.Print("%s/Las_over_Cs.C" % (self.dir))
        self.c2.Print("%s/Las_over_Cs.eps" % (self.dir))
        self.c2.Print("%s/Las_over_Cs.png" % (self.dir))
        
    def ProcessRegion(self, region):


        self.oldCs = 0.
        self.newCs = 0.
        
        self.oldLas = 0.
        self.newLas = 0.
                     
        for event in region.GetEvents():
            if 'deviation' in event.data:

                p_var = 0
                f_var = 0
                
                if 'part_var' in event.data:
                    p_var = event.data['part_var']
                if 'fiber_var' in event.data:
                    f_var = event.data['fiber_var']
                        
                event.data['deviation']     = event.data['deviation'] - f_var - p_var # Deviation corrected (in %)
                event.data['f_laser']       = 1./(1.+event.data['deviation']/100.)        # Calibration factor

                if event.runNumber==self.run_bef and not event.data['isBad'] and \
                       (event.data['calibration']>0.1 and  event.data['calibration']<0.8 and \
                        event.data['wheelpos']==6):
                    self.oldCs  = event.data['cesium_db']
                    self.oldLas = event.data['f_laser']

                if event.runNumber==self.run_aft and not event.data['isBad'] and \
                       (event.data['calibration']>0.1 and  event.data['calibration']<0.8 and \
                        event.data['wheelpos']==6):
                    self.newCs  = event.data['cesium_db']
        
        # Once we got all the info, produce the plots

        if self.oldCs!=0 and self.oldLas!=0 and self.newCs!=0:

            [p, i, j, w] = region.GetNumber()

            # Remove the special Cs cells

            specC10  = ( (p==3 or p==4) and ((i>=39 and i<=42) or (i>=55 and i<=58)) )
            specD4   = ( (p==3 and i==15) or (p==4 and i==18) )
            gapCrack = ( not specD4 and (p==3 or p==4) and (j==0 or j==1 or j==12 or j==13) ) or \
                       ( specD4 and (j==13 or j==14 or j==18 or j==19) )
            specC10  = ( specC10 and (j==4 or j==5) )

            if specD4 or gapCrack or specC10:
                return
            
            self.summary_cs.Fill(1/self.oldLas,self.newCs/self.oldCs)
            self.ratio_cs.Fill((1/self.oldLas)/(self.newCs/self.oldCs))
            
            #if (p==1 and i==21 and j==19) or \
            #       (p==2 and i==12 and j==17) or \
            #       (p==2 and i==12 and j==23) or \
            #       (p==2 and i==21 and j==47) or \
            #       (p==2 and i==36 and j==24) or \
            #       (p==3 and i==12 and j==30) or \
            #       (p==4 and i==62 and j==0) or \
            #       (p==4 and i==64 and j==32):
                #print region.GetHash(),1/self.oldLas,self.newCs/self.oldCs,(1/self.oldLas)/(self.newCs/self.oldCs)

