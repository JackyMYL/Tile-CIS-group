############################################################
#
# getLinCorrections.py
#
############################################################
#
# Author: Seb Viret <viret@in2p3.fr>
#
# November 26, 2009
#
# Goal: 
# Get the attenuation of the filters, and rescale Diode1 and PMT1 signal
# Due to the crosstalk effect, Diode1 signal is not correct
#
# Input parameters are:
#
# -> n_iter: the number of iterations necessary to get the attenuation value 
#  
# -> n_sig: the number of st.dev. considered for outlier rejection (for iterations) 
#  
# -> useBoxPMT: take the LASER box PMT signal instead of PMT/BoxPMT ratio 
#  
# -> nEvtCut: minimum number of events to compute an attenuation
#                 
#
# For more info on the LASER system : http://atlas-tile-laser.web.cern.ch
#
#############################################################


from src.GenericWorker import *
from src.region import *
from array import *
import math

class getLinCorrections(GenericWorker):
    "This worker computes the filter attenuation factors for a given set of linearity runs"
    
    # make this runs eventually
    def __init__(self, n_sig=2, n_iter=5, verbose=False, useBoxPMT=False,nEvtCut=1500):
        self.n_sig     = n_sig
        self.n_iter    = n_iter
        self.verbose   = verbose
        self.usePM     = useBoxPMT
        self.ncut      = nEvtCut
        self.events    = set()
        self.run_list  = set()
        self.maxLG     = 650 # Low gain max
        self.minLG     = 50  # Low gain min
        self.maxHG     = 8   # High gain max
        self.minHG     = 0.1 # High gain min

        # The plots are for EXPERTS only, so they are produced only in verbose mode
        if self.verbose:
            self.c_filters   = []
            self.c_filters2  = []
            self.h_filters   = []
            self.h_filters2  = []
        
            for i in range(8):
                self.c_filters.append(src.MakeCanvas.MakeCanvas())
                self.c_filters2.append(src.MakeCanvas.MakeCanvas())   
  
         
    def ProcessRegion(self, region):
                   
        for event in region.GetEvents():
            if 'requamp' in event.data and 'is_OK' in event.data and not event.data['isBad']:
                self.events.add(event)
                    
                if event.runNumber not in self.run_list:
                    self.run_list.add(event.runNumber)

                    
    #
    # The filter attenuation calculation
    #

    def ProcessStop(self):

        for run in self.run_list: # We have to deal with the multi-run case

            # Initialize the attenuation factors arrays 
            att_FIL_n  = [0 for x in range(16)]        
            sig_FIL_n  = [100000 for x in range(16)]
                    
            # Then compute the corrections iteratively
            for iter in range(self.n_iter): 
            
                n_FIL   = [0 for x in range(16)]
                att_FIL = [0 for x in range(16)]
                sig_FIL = [0 for x in range(16)]

                for event in self.events: # First loop for the mean

                    if run != event.runNumber:
                        continue

                    # Selection proceeds as follows:
                    #
                    # Low  gain events are collected only if there signal is within a special
                    # window (to avoid ADC saturation and LG ADC uncertainty)
                    #
                    # High gain events are collected only if their signal is lower than a certain value
                    #
                    # The middle area (LG/HG transition is not accounted for at this stage)
                       
                    for i in range(8):

                        if not self.selector(event,i): # Event selection
                            continue
                               
                        att_l = 0 # Low gain attenuation
                        att_h = 0 # High gain attenuation

                                
                        if self.usePM: # Choose to use PMT
                            if event.data['gain'][i] == 0:
                                att_l = event.data['PMT_signal'][4]/event.data['PMT_signal'][i]
                            else:
                                att_h = event.data['PMT_signal'][4]/event.data['PMT_signal'][i]
                        else: # Or the ratio 
                            if event.data['gain'][i] == 0:
                                att_l = event.data['PMTvP_signal'][4]/event.data['PMTvP_signal'][i]
                            else:
                                att_h = event.data['PMTvP_signal'][4]/event.data['PMTvP_signal'][i]

                        var_l = att_l-att_FIL_n[2*i]  
                        var_h = att_h-att_FIL_n[2*i+1]  
                                
                        if att_l!=0 and math.fabs(var_l) < self.n_sig*sig_FIL_n[2*i]:
                            n_FIL[2*i] += 1
                            att_FIL[2*i] += var_l
                            
                        if att_h!=0  and math.fabs(var_h) < self.n_sig*sig_FIL_n[2*i+1]:
                            n_FIL[2*i+1] += 1
                            att_FIL[2*i+1] += var_h
                                    

                # End of first loop, compute the attenuations
                for i in range(16):
                    if n_FIL[i] != 0:
                        att_FIL[i] /= n_FIL[i]

                # Produces some plots in verbose mode and re-initialize the number of events
                for i in range(8):

                    if self.verbose and iter==self.n_iter-1:                        
                        if n_FIL[2*i]>=n_FIL[2*i+1]:
                            self.h_filters.append(ROOT.TH2F('Filter_%d'%(i+1), 'Filter_%d'%(i+1),\
                                                            100, 0, 1000, 100, 0.8*att_FIL_n[2*i], 1.2*att_FIL_n[2*i]))
                            self.h_filters2.append(ROOT.TH1F('Filter2_%d'%(i+1), 'Filter2_%d'%(i+1),\
                                                             100, 0.8*att_FIL_n[2*i], 1.2*att_FIL_n[2*i]))  
                        else:
                            self.h_filters.append(ROOT.TH2F('Filter_%d'%(i+1), 'Filter_%d'%(i+1),\
                                                            100, 0, 1000, 100, 0.8*att_FIL_n[2*i+1], 1.2*att_FIL_n[2*i+1]))
                            self.h_filters2.append(ROOT.TH1F('Filter2_%d'%(i+1), 'Filter2_%d'%(i+1),\
                                                             100, 0.8*att_FIL_n[2*i+1], 1.2*att_FIL_n[2*i+1]))   
                    n_FIL[2*i]   = 0
                    n_FIL[2*i+1] = 0


                # Do the second loop to get the RMS
                for event in self.events: # Second loop for the RMS

                    if run != event.runNumber:
                        continue
                    
                    for i in range(8):
                            
                        if not self.selector(event,i):
                            continue
                        
                        att_l = 0
                        att_h = 0
                                 
                        if self.usePM: # Choose to use PMT
                            if event.data['gain'][i] == 0:
                                att_l = event.data['PMT_signal'][4]/event.data['PMT_signal'][i]
                            else:
                                att_h = event.data['PMT_signal'][4]/event.data['PMT_signal'][i]
                        else: # Or the ratio 
                            if event.data['gain'][i] == 0:
                                att_l = event.data['PMTvP_signal'][4]/event.data['PMTvP_signal'][i]
                            else:
                                att_h = event.data['PMTvP_signal'][4]/event.data['PMTvP_signal'][i]
                                                                              
                        var_l = att_l-att_FIL[2*i]-att_FIL_n[2*i]  
                        var_h = att_h-att_FIL[2*i+1]-att_FIL_n[2*i+1]  

                        if self.verbose and iter==self.n_iter-1:
                            if att_l!=0:
                                self.h_filters[i].Fill(event.data['PMT_signal'][4],att_l)
                                self.h_filters2[i].Fill(att_l)
                            if att_h!=0: 
                                self.h_filters[i].Fill(event.data['PMT_signal'][4],att_h)
                                self.h_filters2[i].Fill(att_h)
                            
                                
                        if att_l!=0  and math.fabs(var_l) < self.n_sig*sig_FIL_n[2*i]:
                            n_FIL[2*i] += 1
                            sig_FIL[2*i] += var_l*var_l
                                
                        if att_h!=0  and math.fabs(var_h) < self.n_sig*sig_FIL_n[2*i+1]:
                            n_FIL[2*i+1] += 1
                            sig_FIL[2*i+1] += var_h*var_h

                # End of the second loop, get the sigmas
                                
                for i in range(16):
                    if n_FIL[i] > 1:
                        sig_FIL_n[i] = math.sqrt(sig_FIL[i]/(n_FIL[i]-1))
                        att_FIL_n[i]  += att_FIL[i]


            # End of the iterations

            # Now we have the filter attenuations
            # We can re-scale diode 1 and PMT 1 signals

            # First we choose the best attenuation for each filter (if two were computed)

            for i in range(8):
                reso_l = 100
                reso_h = 100

                if att_FIL_n[2*i] != 0:
                    reso_l = math.fabs(sig_FIL_n[2*i]/att_FIL_n[2*i])

                if att_FIL_n[2*i+1] != 0:
                    reso_h = math.fabs(sig_FIL_n[2*i+1]/att_FIL_n[2*i+1])

                if reso_l>0.015 and reso_h>0.015: # Both are bad (resolution worse than 1.5%)
                    att_FIL_n[2*i] = 0
                elif reso_l>reso_h: # High gain attenuation is better
                    att_FIL_n[2*i] = att_FIL_n[2*i+1]
                    sig_FIL_n[2*i] = sig_FIL_n[2*i+1]                    


            # Finally apply the filter scaling to all the events
                        
            for event in self.events:
                    
                if run != event.runNumber:
                    continue

                for i in range(8): # All filter position

                    if att_FIL_n[2*i] != 0 :                        
                        event.data['BoxDiode'][i]     = event.data['BoxDiode'][i]/att_FIL_n[2*i]
                        event.data['BoxDiode_std'][i] = event.data['BoxDiode_std'][i]/att_FIL_n[2*i]
                        event.data['BoxPMT'][i]       = event.data['BoxPMT'][i]/att_FIL_n[2*i]
                        event.data['BoxPMT_std'][i]   = event.data['BoxPMT_std'][i]/att_FIL_n[2*i]
                    else:
                        event.data['BoxDiode'][i] = 0
                        event.data['BoxPMT'][i]   = 0
                    

            if self.verbose: # some printouts

                print('Run',run)

                for i in range(8):
                    
                    self.c_filters[i].cd()
                    self.h_filters[i].Draw()
                    self.c_filters[i].Print("Filter_%d.C"%(i+1))
        
                    self.c_filters2[i].cd()
                    self.h_filters2[i].Draw()
                    self.c_filters2[i].Print("Filter2_%d.C"%(i+1))
                    
                    print('Run',run,': Filter wheel attenuation for filter '\
                          ,i, ' is equal to  %.2f +/- %.2f' % (att_FIL_n[2*i],sig_FIL_n[2*i]))

        

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

        # Cut on the reference signal (no filter position)
        if event.data['PMT_signal'][4]  > self.maxLG or event.data['PMT_signal'][4]  < 200. :
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
