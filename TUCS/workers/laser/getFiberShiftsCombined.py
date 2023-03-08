############################################################
#
# getFiberShiftsCombined.py
#
############################################################
#
# Author: Giulia <giulia.di.gregorio@cern.ch>, inspired by Henric Wilkens getFiberShiftsHenric.py
#
# December, 2017
#
# Goal: 
# Get the overall optics correction per patch panel fiber
#
# Input parameters are:
#
# -> n_iter: the number of iterations necessary to get the offset value 
#  
# -> siglim: the number of st.dev. considered for outlier rejection (for iterations) 
#         
#
# For more info on the LASER system : http://atlas-tile-laser.web.cern.ch
#
#############################################################


from src.GenericWorker import *
from src.region import *
from src.stats import *
from array import *
import math

from src.laser.toolbox import *

class getFiberShiftsCombined(GenericWorker):
    "This worker computes the PP fiber variation"
    
    # make this runs eventually
    def __init__(self, siglim=2.0, n_iter=5, verbose=True):

        self.siglim   = siglim
        self.n_iter   = n_iter
        self.verbose  = verbose

        self.PMTool   = LaserTools()
        self.run_dict = {}
        self.run_list = []


    def ProcessStart(self):
        
        global run_list
        for run in run_list.getRunsOfType('Las'):
            self.run_list.append(run)
            self.run_dict[run.runNumber] = []
        print("Run dictionary ", self.run_list)

        return


    def ProcessRegion(self, region):
        if len(region.GetNumber())==4:
            layer = region.GetLayerName()
            cell= region.GetCellName()
            [part, module, pmt, gain] = region.GetNumber(1)

            if (not(layer=='BC' or layer=='D' or layer=='B' or layer=='A')):
            #if (not(cell=='D0' or cell=='D1' or cell=='D2' or cell=='D3' or cell=='BC1' or cell=='BC2' or cell=='D4' or cell=='D6' or cell=='B13' or cell=='B14' or cell=='B15' or cell=='D5')):
            
                return
            
            [part, module, pmt, gain] = region.GetNumber(1)
            saturation_limits = [760., 12.]                         # in pC            
    
            for event in region.GetEvents():            
                # We are going to correct all channels provided they have a deviation 
                if event.run.runType=='Las' and 'deviation' in event.data and 'Pisa_deviation' in event.data:

                    # We are going to reject things to compute the corrections
                    if (event.data['status']&0x4) or (event.data['status']&0x10) or not event.data['is_OK']:
                        continue
                
                    if (event.data['calibration']<=0. or event.data['lasref_db']<=0):
                        continue
                    
                    if (event.data['gain_Pisaref_db']<=0 or event.data['gain_Pisa']<=0):
                        continue

                    if (event.data['HV']<10.) and (event.data['HVSet']<10.):# Emergnecy mode: we don't calculate fiber correction
                        continue
               
                    if (abs(event.data['HV']-event.data['hv_db'])>10):      # bad HV, will bias fiber correction
                        continue
                    
                    if (event.data['signal']>saturation_limits[gain]):      # Saturation limits
                        continue

                    self.run_dict[event.run.runNumber].append(event)
        return


    def ProcessStop(self):
        n =0
        nruns = len (self.run_list)
        
        for run in sorted(self.run_list, key=lambda run: run.runNumber): 
            npmt     = [0 for x in range(384)]
            mean     = [0. for x in range(384)]        
            variance = [5. for x in range(384)]
            error    = [.01 for x in range(384)]
            rms      = [.01 for x in range(384)]

            fibre_stats = [stats() for x in range(384)]
        
            Delta_G = 1.
            Delta_G_err = 0.
            if 'part_var' in run.data:
                Delta_G = run.data['part_var']
                Delta_G_err = run.data['part_var_err']
            
            # Compute the corrections iteratively
            for iter in range(self.n_iter):
                for indice in range(384):

                    fibre_stats[indice].reset()
                
                for event in self.run_dict[run.runNumber]:
                    # Some usefull numbers to get
                    [part, module, pmt, gain] = event.region.GetNumber(1)
                    ros = part-1
                    drawer = module-1
                    indice = self.PMTool.get_fiber_index(ros, drawer, pmt)
                    

                    # Geometric mean...
                    a = event.data['calibration']/event.data['lasref_db']
                    b = event.data['gain_Pisa']/event.data['gain_Pisaref_db']
                    b_err = event.data['gainerror_Pisa']/event.data['gain_Pisaref_db']
                    x = log ( a/(b*Delta_G) )
                    
                    a_err = event.data['caliberror']/event.data['lasref_db']

                    s = sqrt(pow(a_err/a, 2) + pow(b_err/b, 2) + pow(Delta_G_err/Delta_G, 2))
        
                    # Outlier removal, and wheighted mean intermediate sums
                    if math.fabs(x - mean[indice]) <= self.siglim*sqrt(variance[indice]) and s!=0:                        
                        w = 1/(s*s)
                        fibre_stats[indice].fill(x, w)
                        
                    
                for fibre in range(384):                    
                    npmt[fibre] = fibre_stats[fibre].entries
                    #if fibre_stats[fibre].entries>1: 
                    if fibre_stats[fibre].entries>0:
                        mean[fibre] = fibre_stats[fibre].mean()
                    if fibre_stats[fibre].entries>2:
                        variance[fibre] = fibre_stats[fibre].variance()                    
                        error[fibre] = fibre_stats[fibre].error()


            # Iterations are over, store results
            for fibre in range(384):
                mean[fibre]  = exp(mean[fibre])
                error[fibre] = mean[fibre]*error[fibre]
                rms[fibre]   = mean[fibre]*sqrt(variance[fibre])

        
            run.data['fiber_var']     = mean
            run.data['fiber_var_err'] = error
            run.data['fiber_var_rms'] = rms
          
    
            # Some printouts
            if self.verbose: 
                for fibre in range(384):
                    print('Run %6d: Mixing is introducing a %5.2f +/- %5.3f%% shift (sigma= %4.2f%%) shift in fiber %s using %d pmts' % \
                        ( run.runNumber,
                          100*(mean[fibre]-1),
                          100*error[fibre],
                          100*rms[fibre],
                          self.PMTool.get_fiber_name(fibre),
                          npmt[fibre]))
            n = n+1
        return

   




    
    
    
