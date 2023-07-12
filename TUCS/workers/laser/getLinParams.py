############################################################
#
# getLinParams.py
#
############################################################
#
# Author: Seb Viret <viret@in2p3.fr>
#
# November 26, 2009, modified on March 22nd, 2010
#
# Goal: 
# Fit the linearity distributions for all the TileCal PMTs 
# !!! There is ONE fit per run and per PMT
# 
# Input parameters are:
#
# -> verbose: displays lot of infos (DEFAULT is FALSE)
#  
# -> useBoxPMT: take the LASER box PMT signal instead of PMT/BoxPMT ratio 
#
# -> minpoints: the minimum number of points requested for a run (maximum possible is 8)
#
# -> nEvtCut: the minimum number of event per position
#
# -> minLG/maxLG/minHG/maxHG : the HG/LG windows within which the fit is done
#
# For more info on the LASER system : http://atlas-tile-laser.web.cern.ch
#
#############################################################


from src.GenericWorker import *
from src.region import *
from array import *
import math
import src.MakeCanvas

from src.laser.toolbox import *

class getLinParams(GenericWorker):
    "This worker computes the linearity parameters over corrected data"
    
    
    # make this runs eventually
    def __init__(self, verbose=False, useBoxPMT=False, minpoints=5,nEvtCut=500,minLG=50,maxLG=600,minHG=0.5,maxHG=8.):
        self.verbose   = verbose
        self.usePM     = useBoxPMT
        self.minpts    = minpoints
        self.ncut      = nEvtCut
        self.maxLG     = maxLG
        self.minLG     = minLG
        self.maxHG     = maxHG
        self.minHG     = minHG 
        self.PMTool    = LaserTools()
         
        # Some histograms are available (only in verbose mode)
        #
        # !!! FOR DEBUGGING PURPOSES ONLY !!!

        if self.verbose:
            self.c1 = src.MakeCanvas.MakeCanvas()
            self.c2 = src.MakeCanvas.MakeCanvas()
            self.c3 = src.MakeCanvas.MakeCanvas()

            self.chi_hist_1 = ROOT.TH1F('', '',100, 0, 1.)
            self.chi_hist_2 = ROOT.TH1F('', '',100, 0, 1.)
            self.chi_hist_3 = ROOT.TH1F('', '',100, 0, 1.) 
            
            self.prob_1     = ROOT.TH1F('p1', '',100, 0, 1.)
            self.prob_2     = ROOT.TH1F('p2', '',100, 0, 1.)
            self.prob_3     = ROOT.TH1F('p3', '',100, 0, 1.)
            
            self.sl_lg      = ROOT.TH1F('r1', 'r1',2000, -1, 1.)
            self.sl_hg      = ROOT.TH1F('r2', 'r2',2000, -0.1, 0.1)
            self.hg_lg      = ROOT.TH2F('r3', 'r3',2000, -0.1, 0.1,2000, -.1, .1)
            
            self.res_1v     = ROOT.TH2F('r1v', 'r1v',100, 0, 500.,100, -5, 5.)
            self.res_2v     = ROOT.TH2F('r2v', 'r2v',100, 0, 500.,100, -5, 5.)
            self.res_3v     = ROOT.TH2F('r3v', 'r3v',100, 0, 500.,100, -5, 5.)

        
    def ProcessStop(self):

        if self.verbose:
            self.c1.cd()
            self.prob_1.Draw()
            self.c1.Print("Residual_1.C")
            
            self.c2.cd()
            self.prob_2.Draw()
            self.c2.Print("Residual_2.C")
            
            self.c3.cd()
            self.hg_lg.Draw()
            self.c3.Print("Residual_3.C")
            
    def ProcessRegion(self, region):

        self.events    = set()

        # First, retrieve the events 
                   
        for event in region.GetEvents():
            if 'requamp' in event.data and 'is_OK' in event.data:
                self.events.add(event)

        # new PMT, reset fit parameters

        mean_prob  = 0
        n_run      = 0

        for event in self.events:

            npts       = 0.
            varx_REF   = 0.
            varx_BOX   = 0.            
            vary_PM    = 0.
            vary_RATIO = 0.
            
            # First get the scaling factor bet. variances
            # <-- Necessary to fit with errors on both X and Y axis -->
            # We follow the method described in Numerical Recipes, part 15.3 (p.660)

            for i in range(8):
                
                if not self.selector(event,i):
                    continue
                    
                varx_BOX   += event.data['BoxPMT_std'][i]*event.data['BoxPMT_std'][i]
                varx_REF   += event.data['r_PMT_signal_std'][i]*event.data['r_PMT_signal_std'][i]
                vary_PM    += event.data['PMT_signal_std'][i]*event.data['PMT_signal_std'][i]
                vary_RATIO += event.data['PMTvP_signal_std'][i]*event.data['PMTvP_signal_std'][i]                   
                npts       += 1

            # If we don't have enough points, we forget this event
            if npts<self.minpts:            
                continue

            n_run      += 1
            
            varx_BOX   /= npts 
            varx_REF   /= npts 
            vary_PM    /= npts 
            vary_RATIO /= npts 

            # Get the scaling factors for the different situations

            scale_REF = sqrt(varx_REF/vary_PM)    # Fit with the reference PMT
            scale_RAT = sqrt(varx_BOX/vary_RATIO) # Fit of the ratio with the box PMT 
            scale_BOX = sqrt(varx_BOX/vary_PM)    # Fit of the PMT signal with the box PMT


            # Initialize everything
                    
            slope     = [0 for x in range(3)]
            intercept = [0 for x in range(3)]
            det       = [0 for x in range(3)]
        
            chisquare = [0 for x in range(3)]
            residual  = [0 for x in range(3)]
        
            v0        = [0 for x in range(3)]
            v1        = [0 for x in range(3)]
            m00       = [0 for x in range(3)]
            m10       = [0 for x in range(3)]
            m11       = [0 for x in range(3)]

            # Collect the info
            
            for i in range(8):

                if not self.selector(event,i):
                    continue

                px1 = event.data['BoxPMT'][i]
                px2 = event.data['r_PMT_signal'][i]                

                py1 = event.data['PMT_signal'][i]*scale_BOX
                py2 = event.data['PMT_signal'][i]*scale_REF
                py3 = event.data['PMTvP_signal'][i]*scale_RAT
                
                sx1 = event.data['BoxPMT_std'][i]
                sx2 = event.data['r_PMT_signal_std'][i]                

                sy1 = event.data['PMT_signal_std'][i]*scale_BOX
                sy2 = event.data['PMT_signal_std'][i]*scale_REF
                sy3 = event.data['PMTvP_signal_std'][i]*scale_RAT

                w1  = event.data['number_entries'][i]/(sx2*sx2+sy2*sy2)  # Ref PMT vs PMT
                w2  = event.data['number_entries'][i]/(sx1*sx1+sy1*sy1)  # Box PMT vs PMT
                w3  = event.data['number_entries'][i]/(sx1*sx1+sy3*sy3)  # Box PMT vs Ratio
                
                v0[0]     += w1*py2
                v1[0]     += w1*py2*px2
                m00[0]    += w1
                m10[0]    += w1*px2
                m11[0]    += w1*px2*px2

                v0[1]     += w2*py1
                v1[1]     += w2*py1*px1
                m00[1]    += w2
                m10[1]    += w2*px1
                m11[1]    += w2*px1*px1

                v0[2]     += w3*py3
                v1[2]     += w3*py3*px1
                m00[2]    += w3
                m10[2]    += w3*px1
                m11[2]    += w3*px1*px1
                     

            # Get the slopes and intercepts

            for i in range(3):
                det[i]       = m00[i]*m11[i]-m10[i]*m10[i]

                if det[i]!=0:
                    slope[i]     = ((v1[i]*m00[i]-v0[i]*m10[i])/det[i])
                    intercept[i] = ((v0[i]*m11[i]-v1[i]*m10[i])/det[i])
                else:
                    slope[i]     = 0.
                    intercept[i] = 0.                 
           
            slope[0]     = slope[0]/scale_REF
            intercept[0] = intercept[0]/scale_REF

            slope[1]     = slope[1]/scale_BOX
            intercept[1] = intercept[1]/scale_BOX

            slope[2]     = slope[2]/scale_RAT
            intercept[2] = intercept[2]/scale_RAT

            if slope[1]!=0:
                event.data['slope']     = slope[1]
                event.data['intercept'] = intercept[1]
                
            if 'slope' not in event.data:
                continue

            # Then compute the chi-square value
             
            for i in range(8):

                if not self.selector(event,i):
                    continue
                 
                px1 = event.data['BoxPMT'][i]
                px2 = event.data['r_PMT_signal'][i]                

                py1 = event.data['PMT_signal'][i]
                py2 = event.data['PMT_signal'][i]
                py3 = event.data['PMTvP_signal'][i]
                
                sx1 = event.data['BoxPMT_std'][i]
                sx2 = event.data['r_PMT_signal_std'][i]                

                sy1 = event.data['PMT_signal_std'][i]
                sy2 = event.data['PMT_signal_std'][i]
                sy3 = event.data['PMTvP_signal_std'][i]

                w1  = event.data['number_entries'][i]/(slope[0]*slope[0]*sx2*sx2+sy2*sy2)  # Ref PMT vs PMT
                w2  = event.data['number_entries'][i]/(slope[1]*slope[1]*sx1*sx1+sy1*sy1)  # Box PMT vs PMT
                w3  = event.data['number_entries'][i]/(slope[2]*slope[2]*sx1*sx1+sy3*sy3)  # Box PMT vs Ratio
                
                residual[0]   = py2-(px2*slope[0]+intercept[0])
                residual[1]   = py1-(px1*slope[1]+intercept[1])
                residual[2]   = py3-(px1*slope[2]+intercept[2])
                
                chisquare[0] += residual[0]*residual[0]*w1                           
                chisquare[1] += residual[1]*residual[1]*w2
                chisquare[2] += residual[2]*residual[2]*w3                           

                event.data['residual'][i] = (residual[1]/(1/sqrt(w2)))

            if self.verbose:
                print("RESULTS")
                print(chisquare[0],npts,ROOT.TMath.Prob(chisquare[0],int(npts-2)))
                print(chisquare[1],npts,ROOT.TMath.Prob(chisquare[1],int(npts-2)))
                print(chisquare[2],npts,ROOT.TMath.Prob(chisquare[2],int(npts-2)))
                print("")
                self.prob_1.Fill(ROOT.TMath.Prob(chisquare[0],int(npts-2)))
                self.prob_2.Fill(ROOT.TMath.Prob(chisquare[1],int(npts-2)))
                self.prob_3.Fill(ROOT.TMath.Prob(chisquare[2],int(npts-2)))

            mean_prob += ROOT.TMath.Prob(chisquare[1],int(npts-2))

            # For the event info, we put the result of the fit w.r.t. the box PMT
            
            event.data['ndof']      = npts-2
            event.data['chisquare'] = chisquare[1]

        if n_run == 0:
            return

        # At the end just fill the mean chisquare probability
    
        mean_prob = mean_prob/n_run

        slope     = [0 for x in range(2)]
        intercept = [0 for x in range(2)]
        det       = [0 for x in range(2)]
        
        chisquare = [0 for x in range(2)]
        residual  = [0 for x in range(2)]
        
        v0        = [0 for x in range(2)]
        v1        = [0 for x in range(2)]
        m00       = [0 for x in range(2)]
        m10       = [0 for x in range(2)]
        m11       = [0 for x in range(2)]

        npts      = [0 for x in range(2)]


        # SV: For debugging, we look at the residuals slopes obtained for low gain and high gain values
            
        for event in self.events:
            event.data['prob'] = mean_prob
            event.data['sl_lg'] = 0.
            event.data['sl_hg'] = 0.
            
            if 'slope' not in event.data:
                continue

            for i in range(8):
            
                if not self.selector(event,i):
                    continue

                norm_res = self.getRes(event,True,i)
                if norm_res==0:
                    continue

                px = event.data['PMT_signal'][i]
                py = norm_res                
                w  = event.data['number_entries'][i]
                
                if event.data['gain'][i] == 0:
                    v0[0]     += w*py
                    v1[0]     += w*py*px
                    m00[0]    += w
                    m10[0]    += w*px
                    m11[0]    += w*px*px
                    npts[0]   += 1
                
                if event.data['gain'][i] == 1:
                    v0[1]     += w*py
                    v1[1]     += w*py*px
                    m00[1]    += w
                    m10[1]    += w*px
                    m11[1]    += w*px*px
                    npts[1]   += 1

        for i in range(2):
            det[i]       = m00[i]*m11[i]-m10[i]*m10[i]

            if npts[i]>=3:
                slope[i]     = ((v1[i]*m00[i]-v0[i]*m10[i])/det[i])
                intercept[i] = ((v0[i]*m11[i]-v1[i]*m10[i])/det[i])

        event.data['sl_lg'] = slope[0]   
        event.data['sl_hg'] = slope[1]   

        if slope[0] != 0 and  slope[1] != 0 and self.verbose:
            self.sl_lg.Fill(slope[0])
            self.sl_hg.Fill(slope[1])
            self.hg_lg.Fill(slope[0],slope[1])
            
            
    
    #   
    # Method for event selection
    #
    
    def selector(self,event,i):

        # Sanity check 1
        if event.data['BoxPMT'][i] == 0:
            return False   

        # Sanity check 2
        if event.data['gain'][i] == -1:
            return False

        # Sanity check 3
        if event.data['r_PMT_signal'][i] == 0:
            return False

        # Cut on the number of events
        if event.data['number_entries'][i] < self.ncut:
            return False   

        # Select events belonging to the correct LG window
        if (event.data['PMT_signal'][i] > self.maxLG or event.data['PMT_signal'][i] < self.minLG) \
               and event.data['gain'][i] == 0:
            return False

        # Select events belonging to the correct HG window
        if (event.data['PMT_signal'][i] < self.minHG or event.data['PMT_signal'][i] > self.maxHG) \
               and event.data['gain'][i] == 1:
            return False

        return True


    # Method computing the normalized residual value (in %)            
    
    def getRes(self,event,PM,filt):
        signal = event.data['BoxPMT'][filt]*event.data['slope']+event.data['intercept']
        residu = event.data['PMT_signal'][filt] - signal
        
        norm_res = event.data['residual'][filt]                           
        #return norm_res
        return 100*residu/signal



                
