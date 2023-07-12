############################################################
#
# getSatCorrections.py
#
############################################################
#
# Author: Seb Viret <viret@in2p3.fr>
#
# January 11, 2010
#
# Goal: 
# Recover the PMT signal when ADC is saturating (ie between 700 and ~1300 pC). 
#
# Input parameters are:
#
# -> doEps: provide eps plots in addition to default png graphics
#  
# -> useBoxPMT: take the PMT/BoxPMT ratio inst. of PMT/Diode
#
# -> minPts: the minimum number of points requested to use a channel 
#
# For more info on the LASER system : http://atlas-tile-laser.web.cern.ch
#
#############################################################



from src.GenericWorker import *
from src.oscalls import *
import ROOT
import time
import math

class getSatCorrections(GenericWorker):
    "Correct the ADC saturation"

    def __init__(self, useBoxPMT=False, doEps = False, minPts=15):
        self.usePM       = useBoxPMT
        self.doEps       = doEps
        self.PMTool      = LaserTools()                      
        self.drawer_list = []
        self.minPts      = minPts

        self.outputTag = outputTag # global variable to tag output histogram file name
        self.dir    = getPlotDirectory(subdir=self.outputTag)

        for i in range(256):
            self.drawer_list.append([]) 



    def ProcessRegion(self, region):

        for event in region.GetEvents():

            if 'slope' in event.data and 'is_OK' in event.data and not event.data['isBad']:
                            
                # Store the events in container depending on their drawer

                #[part_num, i, j, w] = self.PMTool.GetNumber(event.data['region'])
                [part_num, i, j, w] = event.region.GetNumber()
                part_num -= 1
                index = 64*part_num+i-1
                self.drawer_list[index].append(event) 
                    

    #
    # The goal here is to recover the signal when the FE electronic is
    # saturating (and the PMT is not)
    #
          
    def ProcessStop(self):

        self.window   = ROOT.TH2F('window', '',100, 600, 1900, 100, 600., 1900.)
        self.identity = ROOT.TF1("fa1","x",600,1900)                
        self.cor_func = ROOT.TProfile('hprof', 'measured vs corrected signal',200, 600, 1900)
        
        self.res_1D   = ROOT.TH1F('residual_1D', '',200, -50, 50)
        self.res_2D   = ROOT.TH2F('residual_2D', '',100, 700., 1900.,200, -50, 50)
        
        for i_part in range(4):
            
            for i_drawer in range(64):

                drawer_events = self.drawer_list[64*i_part+i_drawer]            
                pmt_list      = []                    

                for i in range(48):
                    pmt_list.append([])


                for event in drawer_events:
                                    
                    #[part_num, i, j, w] = self.PMTool.GetNumber(event.data['region'])
                    [part_num, i, j, w] = event.region.GetNumber()
                    part_num -= 1
                    pmt = self.PMTool.get_PMT_index(part_num,i-1,j)
                    pmt_list[pmt].append(event)

                
                for i_pmt in range(48):

                    # Don't go further if the channel is not instrumented 
                    if self.PMTool.is_instrumented(i_part,i_drawer,i_pmt) == False:
                        continue

                    pmt_events   = pmt_list[i_pmt]
                    max_var      = 0
                    max_lg       = 0
                    n_pts        = 0
                    is_bad       = False
                    is_wrong     = False
                    last_res_lg  = 0 # Residual for the last LG point
                        

                    for event in pmt_events:
      
                        for i in range(8):
                            if event.data['BoxPMT'][i] != 0:
                                    
                                sig = event.data['PMT_signal'][i]
                        
                                if event.data['number_entries'][i] !=0: 
                                    norm_res = self.getRes(event,self.usePM,i)

                                    n_pts+=1
                                                        
                                    if max_var<math.fabs(norm_res):
                                        max_var = math.fabs(norm_res)


                                    if 100<sig and sig<600. and 1.<math.fabs(norm_res):
                                        is_bad = True



                    if n_pts > self.minPts and not is_bad:
                        for event in pmt_events:

                            for i in range(8):
                                if event.data['BoxPMT'][i] != 0:
                                    
                                    sig = event.data['PMT_signal'][i]
                        
                                    if sig>600: 

                                        norm_res = self.getRes(event,self.usePM,i)        
                                        self.cor_func.Fill(sig*100/(norm_res+100),sig,1.)

                                        if sig>700:
                                            self.res_1D.Fill(norm_res)
                                            self.res_2D.Fill(sig,norm_res)
                
                                        if sig>800:
                                            print(event.region.GetHash(),sig,norm_res)                            


        #
        # Then we write the lookup table in only one place (same table for all the channels)
        #
        # This table will be used afterwards, in order to update the CondDB (see WriteDB.py)
        #

        for event in self.drawer_list[0]:
                                    
            #[part_num, i, j, w] = self.PMTool.GetNumber(event.data['region'])
            [part_num, i, j, w] = event.region.GetNumber()

            if j==0 and w==0 and 'LUTx' not in event.data:

                event.data['LUTx'] = []
                event.data['LUTy'] = []       
       
                for i in range(190):
                    if self.cor_func.GetBinContent(i+10)==0.: # We start the table at 700pC
                        continue

                    event.data['LUTx'].append(self.cor_func.GetBinContent(i+10))
                    event.data['LUTy'].append(self.cor_func.GetBinCenter(i+10))


                #for i in range(len(event.data['LUTx'])):                    
                #    print event.data['LUTx'][i],event.data['LUTy'][i]

                break # Just do this once
                

        #
        # Finally the cosmetics
        #

        self.c1 = src.MakeCanvas.MakeCanvas()

        ROOT.gStyle.SetOptStat(0)
        self.c1.cd()
        
        self.c1.SetGridx(1)
        self.c1.SetGridy(1)
        self.c1.SetBorderMode(0)
        self.c1.SetFillColor(0)
        self.window.GetXaxis().SetTitle("Real signal (in pC)");
        self.window.GetXaxis().SetNdivisions(509);
        self.window.GetXaxis().SetLabelFont(42);
        self.window.GetXaxis().SetLabelOffset(0.02);
        self.window.GetXaxis().SetLabelSize(0.03);
        self.window.GetXaxis().SetTitleSize(0.05);
        self.window.GetXaxis().SetTitleOffset(1.2);
        self.window.GetXaxis().SetTitleFont(42);
        self.window.GetYaxis().SetTitle("Measured signal (in pC)");
        self.window.GetYaxis().SetNdivisions(415);
        self.window.GetYaxis().SetLabelFont(42);
        self.window.GetYaxis().SetLabelSize(0.03);
        self.window.GetYaxis().SetTitleSize(0.05);
        self.window.GetYaxis().SetTitleOffset(1.2);
        self.window.GetYaxis().SetTitleFont(42);
        self.cor_func.SetMarkerStyle(4);
        self.cor_func.SetMarkerSize(1.2);
        self.identity.SetMarkerStyle(20);
        self.identity.SetMarkerSize(1.2);
        self.identity.SetLineStyle(9);
        
        self.window.Draw()
        self.identity.Draw("same")
        self.cor_func.Draw("same")

        self.c1.Print("%s/Cor_func.png" % (self.dir))
        self.c1.Print("%s/Cor_func.eps" % (self.dir)) 
        self.c1.Print("%s/Cor_func.C" % (self.dir)) 
        
    
        self.c2 = src.MakeCanvas.MakeCanvas()
        ROOT.gStyle.SetOptStat(0)
        self.c2.cd()
        self.c2.SetBorderMode(0)
        self.c2.SetFillColor(0)
        self.res_1D.Draw()
        self.c2.Print("%s/Residual_1D.C" % (self.dir))         

    
        self.c3 = src.MakeCanvas.MakeCanvas()
        ROOT.gStyle.SetOptStat(0)
        self.c3.cd()
        self.c3.SetBorderMode(0)
        self.c3.SetFillColor(0)
        self.res_2D.Draw()
        self.c3.Print("%s/Residual_2D.C" % (self.dir)) 


    ####################################################################################
    #
    # Tools used along the worker
    #




    def getRes(self,event,PM,filt):
        signal = event.data['BoxPMT'][filt]*event.data['slope']+event.data['intercept']
        residu = event.data['PMT_signal'][filt] - signal
        
        norm_res = event.data['residual'][filt]                           
        #return norm_res
        return 100*residu/signal
