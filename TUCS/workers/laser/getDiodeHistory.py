############################################################
#
# getDiodeHistory.py
#
############################################################
#
# Author: Seb Viret <viret@in2p3.fr>
#
# December 17, 2009
#
# Goal: 
# Compute history plots for one single diode 
#
# WARNING : Diode 3 signal is not available, only alpha info
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

class getDiodeHistory(GenericWorker):
    "This worker produces LASER diode history plot"    

    c1 = None
    c2 = None
    c3 = None
    c4 = None
    c5 = None
    c6 = None
    c7 = None
    c8 = None
    
    def __init__(self, diode=0):

        self.diode = diode
        self.time_max  = 0
        self.time_min  = 10000000000000000
        if self.c1==None:
            self.c1 = src.MakeCanvas.MakeCanvas()
            #self.c1.SetTitle("Put here a nice title")
        if self.c2==None:
            self.c2 = src.MakeCanvas.MakeCanvas()
            #self.c2.SetTitle("Put here a nice title")
        if self.c3==None:
            self.c3 = src.MakeCanvas.MakeCanvas()
            #self.c3.SetTitle("Put here a nice title")
        if self.c4==None:
            self.c4 = src.MakeCanvas.MakeCanvas()
            #self.c4.SetTitle("Put here a nice title")
        if self.c5==None:
            self.c5 = src.MakeCanvas.MakeCanvas()
            #self.c5.SetTitle("Put here a nice title")
        if self.c6==None:
            self.c6 = src.MakeCanvas.MakeCanvas()
            #self.c6.SetTitle("Put here a nice title")
        if self.c7==None:
            self.c7 = src.MakeCanvas.MakeCanvas()
            #self.c7.SetTitle("Put here a nice title")
        if self.c8==None:
            self.c8 = src.MakeCanvas.MakeCanvas()
            #self.c8.SetTitle("Put here a nice title")

    def ProcessStart(self):
        
        global run_list
        for run in run_list.getRunsOfType('Las'):
            time = run.time_in_seconds
            if self.time_min > time:
                self.time_min = time
                self.origin = ROOT.TDatime(run.time)
                
            if self.time_max < time:
                self.time_max = time


   


        
    def ProcessRegion(self, region):
                                   
        if 'TILECAL' == region.GetHash():

            events      = set()

            self.outputTag = outputTag # global variable to tag output histogram file name
            self.dir    = getPlotDirectory(subdir=self.outputTag)

            self.diode_1D        = ROOT.TH1F('diode_%d'%(self.diode), '',1000, 100., 1500.) # Diode signal 
            self.diode_ped_1D    = ROOT.TH1F('dp_%d'%(self.diode), '',100, 100., 200.)      # Diode pedestal
            self.diode_pedsig_1D = ROOT.TH1F('dps_%d'%(self.diode), '',100, 4., 7.)         # Diode pedestal sigma
            self.alpha_1D        = ROOT.TH1F('a_%d'%(self.diode), '',100, 500., 1200.)      # Alpha peak
            self.pmt_1D          = ROOT.TH1F('pmt_%d'%(self.diode), '',1000, 100., 1500.)   # PMT signal
            self.ratio_1D        = ROOT.TH1F('rat_%d'%(self.diode), '',100, 0., 10.)        # PMT/Diode ratio
            self.humi_1D         = ROOT.TH1F('humid_dist', '',100,0., 20.)                  # Humidity

            self.alpha_val       = []
            
            #time_max = 0
            #time_min = 10000000000000000

            #################################################
            #
            # STEP I
            #
            # We retrieve all the distribution in order to 
            # recover mean values and time ranges
            #
            #################################################


            for event in region.RecursiveGetEvents():
                                        
                if 'PMT1' in event.data:
                    
                    events.add(event)
                        
                    # First we check whether Alpha info for this run is new or not 
                    new_alpha = True

                    if [event.data['Diode1_a'],event.data['Diode2_a'],event.data['Diode3_a'],event.data['Diode4_a']] \
                           in self.alpha_val:
                        new_alpha = False
                    else:
                        self.alpha_val.append([event.data['Diode1_a'],event.data['Diode2_a'],event.data['Diode3_a'],event.data['Diode4_a']])


                    # Then fill the distributions

                    diode_val = event.data['Diode%d'%(self.diode+1)]
                    
                    self.diode_1D.Fill(diode_val)
                    self.diode_ped_1D.Fill(event.data['Diode%d_p'%(self.diode+1)])
                    self.diode_pedsig_1D.Fill(event.data['Diode%d_sp'%(self.diode+1)])                    
                    self.pmt_1D.Fill(event.data['PMT1'])

                    if event.data['humid'] != 0:
                        self.humi_1D.Fill(event.data['humid'])

                    if diode_val != 0: 
                        self.ratio_1D.Fill(event.data['PMT1']/diode_val)

                    if new_alpha: # Alpha peak has to be corrected from pedestal
                        self.alpha_1D.Fill(event.data['Diode%d_a'%(self.diode+1)]-event.data['Diode%d_p'%(self.diode+1)])

                    #print 'test avant :',diode_val,event.data['Diode%d_p'%(self.diode+1)],event.data['Diode%d_sp'%(self.diode+1)],event.data['Diode%d_a'%(self.diode+1)]-event.data['Diode%d_p'%(self.diode+1)],event.data['PMT1'],event.data['PMT1']/diode_val,event.data['humid']

                    # And collect time infos
                        
              ##       if time_min>event.run.time_in_seconds:
##                         time_min = event.run.time_in_seconds
##                         self.origin = ROOT.TDatime(event.run.time)
                            
##                     if time_max<event.run.time_in_seconds:
##                         time_max = event.run.time_in_seconds

                
            ROOT.gStyle.SetTimeOffset(self.origin.Convert())
            ROOT.gStyle.SetOptStat(0)


            # We retrieve the mean values

            self.diode_m        = self.diode_1D.GetMean()        # Diode mean
            self.diode_ped_m    = self.diode_ped_1D.GetMean()    # Pedestal mean
            self.diode_pedsig_m = self.diode_pedsig_1D.GetMean() # Pedestal mean RMS
            self.alpha_m        = self.alpha_1D.GetMean()        # Alpha mean
            self.pmt_m          = self.pmt_1D.GetMean()          # PMT mean
            self.ratio_m        = self.ratio_1D.GetMean()        # Internal ratio mean
            self.humi_m         = self.humi_1D.GetMean()         # Humidity mean

            #print 'test :',self.diode_m,self.diode_ped_m,self.diode_pedsig_m,self.alpha_m,self.pmt_m,self.ratio_m,self.humi_m


            #################################################
            #
            # STEP II
            #
            # We now could produce the correct plots
            #
            #################################################


            # First initialize the histograms

            self.up_scale = self.time_max-self.time_min+100000 # In seconds

            self.diode_norm        = ROOT.TH1F('dnorm_%d'%(self.diode), '',70, 0.8, 1.2)
            self.diode_ped_norm    = ROOT.TH1F('dpnorm_%d'%(self.diode), '',70, 0.95, 1.05)
            self.diode_pedsig_norm = ROOT.TH1F('dpnorms_%d'%(self.diode), '',70, 0.8, 1.2)
            self.alpha_norm        = ROOT.TH1F('anorm_%d'%(self.diode), '',70, 0.95, 1.05)
            self.pmt_norm          = ROOT.TH1F('pnorm_%d'%(self.diode), '',70, 0.8, 1.2)
            self.ratio_norm        = ROOT.TH1F('rnorm_%d'%(self.diode), '',70, 0.95, 1.05)

            self.diode_vs_t        = ROOT.TH2F('d_vs_t_%d'%(self.diode), '',100, 0, self.up_scale, 70, 0.8, 1.2)
            self.diode_ped_vs_t    = ROOT.TH2F('dp_vs_t_%d'%(self.diode), '',100, 0, self.up_scale, 70, 0.95, 1.05)
            self.diode_pedsig_vs_t = ROOT.TH2F('dps_vs_t_%d'%(self.diode), '',100, 0, self.up_scale, 70, 0.8, 1.2)
            self.alpha_vs_t        = ROOT.TH2F('a_vs_t_%d'%(self.diode), '',100, 0, self.up_scale, 70, 0.95, 1.05)
            self.pmt_vs_t          = ROOT.TH2F('p_vs_t_%d'%(self.diode), '',100, 0, self.up_scale, 70, 0.8, 1.2)
            self.ratio_vs_t        = ROOT.TH2F('r_vs_t_%d'%(self.diode), '',100, 0, self.up_scale, 70, 0.95, 1.05)
            self.humi_vs_t         = ROOT.TH2F('h_vs_t_%d'%(self.diode), '',100, 0, self.up_scale, 70, 0., 2.)
            self.humi_vs_pedsig    = ROOT.TH2F('humid', '',100,0., 2.,100,0.8,1.2)


            # And finally fill them 
                            
            self.alpha_val = []
            for event in events:

                # First we check wheter Alpha info for this run is new or not 
                new_alpha = True

                if [event.data['Diode1_a'],event.data['Diode2_a'],event.data['Diode3_a'],event.data['Diode4_a']] \
                   in self.alpha_val:
                    new_alpha = False
                else:
                    self.alpha_val.append([event.data['Diode1_a'],event.data['Diode2_a'],event.data['Diode3_a'],event.data['Diode4_a']])


                # Then fill the distributions

                diode_val = event.data['Diode%d'%(self.diode+1)]
                
                if diode_val != 0 and self.diode_m != 0 and self.ratio_m != 0: 
                    var_d      = diode_val/(self.diode_m)
                    var_r      = (event.data['PMT1']/diode_val)/self.ratio_m
                    self.diode_norm.Fill(var_d)
                    self.ratio_norm.Fill(var_r)                    
                    self.diode_vs_t.Fill(event.run.time_in_seconds-self.time_min,var_d)                     
                    self.ratio_vs_t.Fill(event.run.time_in_seconds-self.time_min,var_r)
                 
                var_d_ped  = (event.data['Diode%d_p'%(self.diode+1)])/(self.diode_ped_m)
                var_d_sped = (event.data['Diode%d_sp'%(self.diode+1)])/(self.diode_pedsig_m)


                self.pmt_norm.Fill(event.data['PMT1']/self.pmt_m)
                self.diode_ped_norm.Fill(var_d_ped)
                self.diode_pedsig_norm.Fill(var_d_sped)
                self.pmt_vs_t.Fill(event.run.time_in_seconds-self.time_min,event.data['PMT1']/self.pmt_m)                    
                self.diode_ped_vs_t.Fill(event.run.time_in_seconds-self.time_min,var_d_ped)                    
                self.diode_pedsig_vs_t.Fill(event.run.time_in_seconds-self.time_min,var_d_sped)
                
                if event.data['humid'] != 0:
                    self.humi_vs_pedsig.Fill(event.data['humid']/self.humi_m,var_d_sped)
                    self.humi_vs_t.Fill(event.run.time_in_seconds-self.time_min,event.data['humid']/self.humi_m)

                if new_alpha:
                    var_alp = (event.data['Diode%d_a'%(self.diode+1)]-event.data['Diode%d_p'%(self.diode+1)])/(self.alpha_m)
                    self.alpha_norm.Fill(var_alp)
                    self.alpha_vs_t.Fill(event.run.time_in_seconds-self.time_min,var_alp)


            #################################################
            #
            # STEP III
            #
            # The cosmetics...
            #
            #################################################

            # 1. Pedestal values
         
            self.c1.cd()

            self.c1_1 = ROOT.TPad("c1_1", "newpad",0.0,0.0,0.71,1.0)
            self.c1_1.Draw()
            self.c1_1.cd()
            self.c1_1.SetBorderMode(0)
            self.c1_1.SetFillColor(0)
            self.c1_1.SetGridy()
            self.c1_1.SetFrameBorderMode(0)
            self.c1_1.SetRightMargin(0)
    
            self.diode_ped_vs_t.GetXaxis().SetTimeDisplay(1); 
            self.diode_ped_vs_t.GetXaxis().SetLabelOffset(0.02)
            self.diode_ped_vs_t.GetXaxis().SetTimeFormat("#splitline{%Y}{%d/%m}")
            self.diode_ped_vs_t.GetXaxis().SetLabelSize(0.03)
            self.diode_ped_vs_t.GetXaxis().SetNdivisions(303)
            self.diode_ped_vs_t.GetYaxis().SetNdivisions(812)
            self.diode_ped_vs_t.GetYaxis().SetTitle("Pedestal value (normalized)")
            self.diode_ped_vs_t.GetYaxis().SetTitleSize(0.04)
            self.diode_ped_vs_t.GetYaxis().SetLabelSize(0.03)
            self.diode_ped_vs_t.GetYaxis().SetTitleOffset(1.4)
            self.diode_ped_vs_t.Draw()
            
            self.pt_dpd = ROOT.TPaveText(0.73,0.24,0.94,0.31,"brNDC")
            self.pt_dpd.SetTextSize(0.04)
            self.pt_dpd.SetTextFont(42)                        
            self.pt_dpd.AddText("Diode %d"%(self.diode+1))
            self.pt_dpd.Draw()
            
            self.c1.cd()

            self.c1_2 = ROOT.TPad("c1_2", "newpad",0.71,0.,1.0,1.,-1,0)
            self.c1_2.Draw()
            self.c1_2.cd()
            self.c1_2.SetBorderMode(0)
            self.c1_2.SetFillColor(0)
            self.c1_2.SetGridy()
            self.c1_2.SetFrameBorderMode(0)
            self.c1_2.SetLeftMargin(0)
            
            self.diode_ped_norm.GetXaxis().SetLabelSize(0.0)
            self.diode_ped_norm.GetXaxis().SetNdivisions(812)
            self.diode_ped_norm.GetYaxis().SetLabelSize(0.)
            self.diode_ped_norm.SetFillColor(1)
            rms_y  = 100*self.diode_ped_norm.GetRMS()
            self.diode_ped_norm.Draw("hbar")
              
            # Then we draw the fit result on the plots
            
            self.pt_dp = ROOT.TPaveText(0.3,0.78,0.8,0.86,"brNDC")
            self.pt_dp.SetFillColor(5)
            self.pt_dp.SetTextSize(0.07)
            self.pt_dp.SetTextFont(42)                        
            self.pt_dp.AddText("#sigma = %.2f%s\n" % (rms_y,'%'))
            self.pt_dp.Draw()
        
            self.c1.cd()
            
            self.c1.Print("%s/Pedestals_%d.png" % (self.dir,self.diode+1))
            self.c1.Print("%s/Pedestals_%d.eps" % (self.dir,self.diode+1))
             

            # 2. Pedestal RMS values
         
            self.c2.cd()

            self.c2_1 = ROOT.TPad("c2_1", "newpad",0.0,0.0,0.71,1.0)
            self.c2_1.Draw()
            self.c2_1.cd()
            self.c2_1.SetBorderMode(0)
            self.c2_1.SetFillColor(0)
            self.c2_1.SetGridy()
            self.c2_1.SetFrameBorderMode(0)
            self.c2_1.SetRightMargin(0)
    
            self.diode_pedsig_vs_t.GetXaxis().SetTimeDisplay(1); 
            self.diode_pedsig_vs_t.GetXaxis().SetLabelOffset(0.02)
            self.diode_pedsig_vs_t.GetXaxis().SetTimeFormat("#splitline{%Y}{%d/%m}")
            self.diode_pedsig_vs_t.GetXaxis().SetLabelSize(0.03)
            self.diode_pedsig_vs_t.GetXaxis().SetNdivisions(303)
            self.diode_pedsig_vs_t.GetYaxis().SetNdivisions(812)
            self.diode_pedsig_vs_t.GetYaxis().SetTitle("Pedestal RMS (normalized)")
            self.diode_pedsig_vs_t.GetYaxis().SetTitleSize(0.04)
            self.diode_pedsig_vs_t.GetYaxis().SetLabelSize(0.03)
            self.diode_pedsig_vs_t.GetYaxis().SetTitleOffset(1.4)
            self.diode_pedsig_vs_t.Draw()
            
            self.pt_dpsd = ROOT.TPaveText(0.73,0.24,0.94,0.31,"brNDC")
            self.pt_dpsd.SetTextSize(0.04)
            self.pt_dpsd.SetTextFont(42)                        
            self.pt_dpsd.AddText("Diode %d"%(self.diode+1))
            self.pt_dpsd.Draw()
            
            self.c2.cd()

            self.c2_2 = ROOT.TPad("c2_2", "newpad",0.71,0.,1.0,1.,-1,0)
            self.c2_2.Draw()
            self.c2_2.cd()
            self.c2_2.SetBorderMode(0)
            self.c2_2.SetFillColor(0)
            self.c2_2.SetGridy()
            self.c2_2.SetFrameBorderMode(0)
            self.c2_2.SetLeftMargin(0)
            
            self.diode_pedsig_norm.GetXaxis().SetLabelSize(0.0)
            self.diode_pedsig_norm.GetXaxis().SetNdivisions(812)
            self.diode_pedsig_norm.GetYaxis().SetLabelSize(0.)
            self.diode_pedsig_norm.SetFillColor(1)
            rms_y  = 100*self.diode_pedsig_norm.GetRMS()
            self.diode_pedsig_norm.Draw("hbar")
              
            # Then we draw the fit result on the plots
            
            self.pt_dps = ROOT.TPaveText(0.3,0.78,0.8,0.86,"brNDC")
            self.pt_dps.SetFillColor(5)
            self.pt_dps.SetTextSize(0.07)
            self.pt_dps.SetTextFont(42)                        
            self.pt_dps.AddText("#sigma = %.2f%s\n" % (rms_y,'%'))
            self.pt_dps.Draw()
        
            self.c2.cd()
            
            self.c2.Print("%s/PedestalsSig_%d.png" % (self.dir,self.diode+1))
            self.c2.Print("%s/PedestalsSig_%d.eps" % (self.dir,self.diode+1))
            

            # 3. Alpha peaks
         
            self.c3.cd()

            self.c3_1 = ROOT.TPad("c3_1", "newpad",0.0,0.0,0.71,1.0)
            self.c3_1.Draw()
            self.c3_1.cd()
            self.c3_1.SetBorderMode(0)
            self.c3_1.SetFillColor(0)
            self.c3_1.SetGridy()
            self.c3_1.SetFrameBorderMode(0)
            self.c3_1.SetRightMargin(0)
    
            self.alpha_vs_t.GetXaxis().SetTimeDisplay(1); 
            self.alpha_vs_t.GetXaxis().SetLabelOffset(0.02)
            self.alpha_vs_t.GetXaxis().SetTimeFormat("#splitline{%Y}{%d/%m}")
            self.alpha_vs_t.GetXaxis().SetLabelSize(0.03)
            self.alpha_vs_t.GetXaxis().SetNdivisions(303)
            self.alpha_vs_t.GetYaxis().SetNdivisions(812)
            self.alpha_vs_t.GetYaxis().SetTitle("Alpha spectra mean value (normalized)")
            self.alpha_vs_t.GetYaxis().SetTitleSize(0.04)
            self.alpha_vs_t.GetYaxis().SetLabelSize(0.03)
            self.alpha_vs_t.GetYaxis().SetTitleOffset(1.4)
            self.alpha_vs_t.Draw()
            
            self.pt_ad = ROOT.TPaveText(0.73,0.24,0.94,0.31,"brNDC")
            self.pt_ad.SetTextSize(0.04)
            self.pt_ad.SetTextFont(42)                        
            self.pt_ad.AddText("Diode %d"%(self.diode+1))
            self.pt_ad.Draw()
            
            self.c3.cd()

            self.c3_2 = ROOT.TPad("c3_2", "newpad",0.71,0.,1.0,1.,-1,0)
            self.c3_2.Draw()
            self.c3_2.cd()
            self.c3_2.SetBorderMode(0)
            self.c3_2.SetFillColor(0)
            self.c3_2.SetGridy()
            self.c3_2.SetFrameBorderMode(0)
            self.c3_2.SetLeftMargin(0)
            
            self.alpha_norm.GetXaxis().SetLabelSize(0.0)
            self.alpha_norm.GetXaxis().SetNdivisions(812)
            self.alpha_norm.GetYaxis().SetLabelSize(0.)
            self.alpha_norm.SetFillColor(1)
            rms_y  = 100*self.alpha_norm.GetRMS()
            self.alpha_norm.Draw("hbar")
              
            # Then we draw the fit result on the plots
            
            self.pt_a = ROOT.TPaveText(0.3,0.78,0.8,0.86,"brNDC")
            self.pt_a.SetFillColor(5)
            self.pt_a.SetTextSize(0.07)
            self.pt_a.SetTextFont(42)                        
            self.pt_a.AddText("#sigma = %.2f%s\n" % (rms_y,'%'))
            self.pt_a.Draw()
        
            self.c3.cd()
            
            self.c3.Print("%s/Alpha_%d.png" % (self.dir,self.diode+1))
            self.c3.Print("%s/Alpha_%d.eps" % (self.dir,self.diode+1))

            
            # 4. Diode signals
         
            self.c4.cd()

            self.c4_1 = ROOT.TPad("c4_1", "newpad",0.0,0.0,0.71,1.0)
            self.c4_1.Draw()
            self.c4_1.cd()
            self.c4_1.SetBorderMode(0)
            self.c4_1.SetFillColor(0)
            self.c4_1.SetGridy()
            self.c4_1.SetFrameBorderMode(0)
            self.c4_1.SetRightMargin(0)
    
            self.diode_vs_t.GetXaxis().SetTimeDisplay(1); 
            self.diode_vs_t.GetXaxis().SetLabelOffset(0.02)
            self.diode_vs_t.GetXaxis().SetTimeFormat("#splitline{%Y}{%d/%m}")
            self.diode_vs_t.GetXaxis().SetLabelSize(0.03)
            self.diode_vs_t.GetXaxis().SetNdivisions(303)
            self.diode_vs_t.GetYaxis().SetNdivisions(812)
            self.diode_vs_t.GetYaxis().SetTitle("Diode signal (normalized)")
            self.diode_vs_t.GetYaxis().SetTitleSize(0.04)
            self.diode_vs_t.GetYaxis().SetLabelSize(0.03)
            self.diode_vs_t.GetYaxis().SetTitleOffset(1.4)
            self.diode_vs_t.Draw()
            
            self.pt_d = ROOT.TPaveText(0.73,0.24,0.94,0.31,"brNDC")
            self.pt_d.SetTextSize(0.04)
            self.pt_d.SetTextFont(42)                        
            self.pt_d.AddText("Diode %d"%(self.diode+1))
            self.pt_d.Draw()
            
            self.c4.cd()

            self.c4_2 = ROOT.TPad("c4_2", "newpad",0.71,0.,1.0,1.,-1,0)
            self.c4_2.Draw()
            self.c4_2.cd()
            self.c4_2.SetBorderMode(0)
            self.c4_2.SetFillColor(0)
            self.c4_2.SetGridy()
            self.c4_2.SetFrameBorderMode(0)
            self.c4_2.SetLeftMargin(0)
            
            self.diode_norm.GetXaxis().SetLabelSize(0.0)
            self.diode_norm.GetXaxis().SetNdivisions(812)
            self.diode_norm.GetYaxis().SetLabelSize(0.)
            self.diode_norm.SetFillColor(1)
            rms_y  = 100*self.diode_norm.GetRMS()
            self.diode_norm.Draw("hbar")
              
            # Then we draw the fit result on the plots
            
            self.pt_dd = ROOT.TPaveText(0.3,0.78,0.8,0.86,"brNDC")
            self.pt_dd.SetFillColor(5)
            self.pt_dd.SetTextSize(0.07)
            self.pt_dd.SetTextFont(42)                        
            self.pt_dd.AddText("#sigma = %.2f%s\n" % (rms_y,'%'))
            self.pt_dd.Draw()
        
            self.c4.cd()
            
            self.c4.Print("%s/Diode_%d.png" % (self.dir,self.diode+1))
            self.c4.Print("%s/Diode_%d.eps" % (self.dir,self.diode+1))


            # 5. Internal ratio (control)
         
            self.c5.cd()

            self.c5_1 = ROOT.TPad("c5_1", "newpad",0.0,0.0,0.71,1.0)
            self.c5_1.Draw()
            self.c5_1.cd()
            self.c5_1.SetBorderMode(0)
            self.c5_1.SetFillColor(0)
            self.c5_1.SetGridy()
            self.c5_1.SetFrameBorderMode(0)
            self.c5_1.SetRightMargin(0)
    
            self.ratio_vs_t.GetXaxis().SetTimeDisplay(1); 
            self.ratio_vs_t.GetXaxis().SetLabelOffset(0.02)
            self.ratio_vs_t.GetXaxis().SetTimeFormat("#splitline{%Y}{%d/%m}")
            self.ratio_vs_t.GetXaxis().SetLabelSize(0.03)
            self.ratio_vs_t.GetXaxis().SetNdivisions(303)
            self.ratio_vs_t.GetYaxis().SetNdivisions(812)
            self.ratio_vs_t.GetYaxis().SetTitle("PMT1/Diode ratio (normalized)")
            self.ratio_vs_t.GetYaxis().SetTitleSize(0.04)
            self.ratio_vs_t.GetYaxis().SetLabelSize(0.03)
            self.ratio_vs_t.GetYaxis().SetTitleOffset(1.4)
            self.ratio_vs_t.Draw()
        
            self.pt_r = ROOT.TPaveText(0.73,0.24,0.94,0.31,"brNDC")
            self.pt_r.SetTextSize(0.04)
            self.pt_r.SetTextFont(42)                        
            self.pt_r.AddText("Diode %d"%(self.diode+1))
            self.pt_r.Draw()
            
            self.c5.cd()

            self.c5_2 = ROOT.TPad("c5_2", "newpad",0.71,0.,1.0,1.,-1,0)
            self.c5_2.Draw()
            self.c5_2.cd()
            self.c5_2.SetBorderMode(0)
            self.c5_2.SetFillColor(0)
            self.c5_2.SetGridy()
            self.c5_2.SetFrameBorderMode(0)
            self.c5_2.SetLeftMargin(0)
            
            self.ratio_norm.GetXaxis().SetLabelSize(0.0)
            self.ratio_norm.GetXaxis().SetNdivisions(812)
            self.ratio_norm.GetYaxis().SetLabelSize(0.)
            self.ratio_norm.SetFillColor(1)
            rms_y  = 100*self.ratio_norm.GetRMS()
            self.ratio_norm.Draw("hbar")
              
            # Then we draw the fit result on the plots
            
            self.pt_rd = ROOT.TPaveText(0.3,0.78,0.8,0.86,"brNDC")
            self.pt_rd.SetFillColor(5)
            self.pt_rd.SetTextSize(0.07)
            self.pt_rd.SetTextFont(42)                        
            self.pt_rd.AddText("#sigma = %.2f%s\n" % (rms_y,'%'))
            self.pt_rd.Draw()
        
            self.c5.cd()
            
            self.c5.Print("%s/Ratio_%d.png" % (self.dir,self.diode+1))
            self.c5.Print("%s/Ratio_%d.eps" % (self.dir,self.diode+1))


            # 6. PMT signal
         
            self.c6.cd()

            self.c6_1 = ROOT.TPad("c6_1", "newpad",0.0,0.0,0.71,1.0)
            self.c6_1.Draw()
            self.c6_1.cd()
            self.c6_1.SetBorderMode(0)
            self.c6_1.SetFillColor(0)
            self.c6_1.SetGridy()
            self.c6_1.SetFrameBorderMode(0)
            self.c6_1.SetRightMargin(0)
    
            self.pmt_vs_t.GetXaxis().SetTimeDisplay(1); 
            self.pmt_vs_t.GetXaxis().SetLabelOffset(0.02)
            self.pmt_vs_t.GetXaxis().SetTimeFormat("#splitline{%Y}{%d/%m}")
            self.pmt_vs_t.GetXaxis().SetLabelSize(0.03)
            self.pmt_vs_t.GetXaxis().SetNdivisions(303)
            self.pmt_vs_t.GetYaxis().SetNdivisions(812)
            self.pmt_vs_t.GetYaxis().SetTitle("PMT1 signal (normalized)")
            self.pmt_vs_t.GetYaxis().SetTitleSize(0.04)
            self.pmt_vs_t.GetYaxis().SetLabelSize(0.03)
            self.pmt_vs_t.GetYaxis().SetTitleOffset(1.4)
            self.pmt_vs_t.Draw()
        
            self.pt_p = ROOT.TPaveText(0.73,0.24,0.94,0.31,"brNDC")
            self.pt_p.SetTextSize(0.04)
            self.pt_p.SetTextFont(42)                        
            self.pt_p.AddText("Diode %d"%(self.diode+1))
            #self.pt_p.Draw()
            
            self.c6.cd()

            self.c6_2 = ROOT.TPad("c6_2", "newpad",0.71,0.,1.0,1.,-1,0)
            self.c6_2.Draw()
            self.c6_2.cd()
            self.c6_2.SetBorderMode(0)
            self.c6_2.SetFillColor(0)
            self.c6_2.SetGridy()
            self.c6_2.SetFrameBorderMode(0)
            self.c6_2.SetLeftMargin(0)
            
            self.pmt_norm.GetXaxis().SetLabelSize(0.0)
            self.pmt_norm.GetXaxis().SetNdivisions(812)
            self.pmt_norm.GetYaxis().SetLabelSize(0.)
            self.pmt_norm.SetFillColor(1)
            rms_y  = 100*self.pmt_norm.GetRMS()
            self.pmt_norm.Draw("hbar")
              
            # Then we draw the fit result on the plots
            
            self.pt_pd = ROOT.TPaveText(0.3,0.78,0.8,0.86,"brNDC")
            self.pt_pd.SetFillColor(5)
            self.pt_pd.SetTextSize(0.07)
            self.pt_pd.SetTextFont(42)                        
            self.pt_pd.AddText("#sigma = %.2f%s\n" % (rms_y,'%'))
            self.pt_pd.Draw()
        
            self.c6.cd()
            
            self.c6.Print("%s/PMT.png" % (self.dir))
            self.c6.Print("%s/PMT.eps" % (self.dir))


            # Humidity vs time


            self.c7.cd()

            self.c7.SetGridx(1)
            self.c7.SetGridy(1)
            self.c7.SetBorderMode(0)
            self.c7.SetFillColor(0)
            self.humi_vs_t.GetXaxis().SetTimeDisplay(1); 
            self.humi_vs_t.GetXaxis().SetLabelOffset(0.02)
            self.humi_vs_t.GetXaxis().SetTimeFormat("#splitline{%Y}{%d/%m}")
            self.humi_vs_t.GetXaxis().SetLabelSize(0.03)
            self.humi_vs_t.GetXaxis().SetNdivisions(303)
            self.humi_vs_t.GetYaxis().SetTitle("Diode box humidity (normalized)")
            self.humi_vs_t.GetYaxis().SetTitleSize(0.04)
            self.humi_vs_t.GetYaxis().SetLabelSize(0.03)
            self.humi_vs_t.GetYaxis().SetTitleOffset(1.2)
            self.humi_vs_t.Draw()
            
            self.c7.Print("%s/Humidity_vs_t.png" % (self.dir))
            self.c7.Print("%s/Humidity_vs_t.eps" % (self.dir)) 




            # Humidity vs pedestal RMS


            self.c8.cd()

            self.c8.SetGridx(1)
            self.c8.SetGridy(1)
            self.c8.SetBorderMode(0)
            self.c8.SetFillColor(0)
            self.humi_vs_pedsig.GetXaxis().SetLabelOffset(0.02)
            self.humi_vs_pedsig.GetXaxis().SetLabelSize(0.03)
            self.humi_vs_pedsig.GetXaxis().SetTitle("Diode box humidity (normalized)")
            self.humi_vs_pedsig.GetYaxis().SetTitleSize(0.04)
            self.humi_vs_pedsig.GetYaxis().SetLabelSize(0.03)
            self.humi_vs_pedsig.GetYaxis().SetTitleOffset(1.2)
            self.humi_vs_pedsig.GetYaxis().SetTitle("Pedestal RMS (normalized)")
            self.humi_vs_pedsig.Draw()
            
            self.pt_h = ROOT.TPaveText(0.73,0.24,0.94,0.31,"brNDC")
            self.pt_h.SetTextSize(0.04)
            self.pt_h.SetTextFont(42)                        
            self.pt_h.AddText("Diode %d"%(self.diode+1))
            self.pt_h.Draw()
            
            self.c8.Print("%s/Humidity_vs_pedsig_%d.png" % (self.dir,self.diode+1))
            self.c8.Print("%s/Humidity_vs_pedsig_%d.eps" % (self.dir,self.diode+1)) 


        return 
        
