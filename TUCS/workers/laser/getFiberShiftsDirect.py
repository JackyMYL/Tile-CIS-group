############################################################
#
# getFiberShiftsDirect.py
#
############################################################
#
# Author: Henric <Henric.Wilkens@cern.ch>, inspired by Seb Viret getFiberShifts.py
#
# Novmeber, 2011
#
# Goal: 
# Get the overall relative gain variation per patch panel fiber
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

class getFiberShiftsDirect(GenericWorker):
    "This worker computes the PP fiber variation"
    
    # make this runs eventually
    def __init__(self, siglim=2.0, n_iter=5, verbose=False):

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
            self.run_dict[run.runNumber] = [[] for x in range(384)]
        return


    def ProcessRegion(self, region):
        if len(region.GetNumber())==4:
            layer = region.GetLayerName()
            cell = region.GetCellName()
            #if (not(layer=='BC' or layer=='D' or layer=='B')):
            # During LS2 all PMTS are 'stable'
            #if (not(layer=='D' or cell=='B13' or cell=='B14' or cell=='B15')):
            #    return
            
            [part, module, pmt, gain] = region.GetNumber(1)

            if part==1 and module==14: # remove demonstrator
                return
            
            ros = part-1
            drawer = module-1
            indice = self.PMTool.get_fiber_index(ros, drawer, pmt)
            saturation_limits = [760., 12.]                         # in pC            
    
            for event in region.GetEvents():            
                # We are going to correct all channels provided they have a deviation 
                if event.run.runType=='Las' and 'deviation' in event.data:

                    # We are going to reject things to compute the corrections
#                    if (event.data['status']&0x4) or (event.data['status']&0x10) or not event.data['is_OK']:
                    if (event.data['status']&0x4) or not event.data['is_OK']:
                        continue
                
                    if (event.data['calibration']<=0. or event.data['lasref_db']<=0):
                        continue

                    if (event.data['HV']<10.) and (event.data['HVSet']<10.):# Emergnecy mode: we don't calculate fiber correction
                        continue
               
                    if (abs(event.data['HV']-event.data['hv_db'])>10):      # bad HV, will bias fiber correction
                        continue
                    
                    if (event.data['signal']>saturation_limits[gain]):      # Saturation limits
                        continue
                    
                    self.run_dict[event.run.runNumber][indice].append(event)

        return


    def ProcessStop(self):
        # print self.run_list
        for run in sorted(self.run_list, key=lambda run: run.runNumber): 
            npmt     = [0 for x in range(384)]
            mean     = [0. for x in range(384)]        
            variance = [5. for x in range(384)]
            error    = [.01 for x in range(384)]
            rms      = [.01 for x in range(384)]

            fibre_stats = [stats() for x in range(384)] 

            p_var = 1.
            if 'part_var' in run.data:
                p_var = run.data['part_var']

            for fibre in range(384):
                n_pmts = len(self.run_dict[run.runNumber][fibre])
                if n_pmts==0:
                    continue
                x = [0.] * n_pmts
                s = [0.] * n_pmts
                r = [0.] * n_pmts
                i = 0
                for event in self.run_dict[run.runNumber][fibre]:
                    # Some usefull numbers to get
                    
                    hvgain =1.
                    # if event.data.has_key('hv_db'):
                    #    if (event.data['hv_db'])!=0:
                    #                            try:
                    #                                hvgain = pow(event.data['HV']/event.data['hv_db'],6.9)                                
                    #                            except:
                    #                                pass
                    
                    # Arithmetique mean.... 
                    # x = event.data['calibration']/(event.data['lasref_db']*p_var)
                    # s = event.data['caliberror']/(event.data['lasref_db']*p_var)
                    
                    # Geometric mean...
                    x[i] = log(event.data['calibration']/(event.data['lasref_db']*p_var*hvgain))
                    s[i] = event.data['caliberror']/event.data['calibration']
                    i=i+1
          
                # Compute the corrections iteratively
                for iter in range(self.n_iter):
                    fibre_stats[fibre].reset()

                    if iter==0:
                        for i in range(n_pmts):
                            if s[i]!=0: # Use all events
                                w = 1/(s[i]*s[i])
                                fibre_stats[fibre].fill(x[i], w)
                    else:                   # remove worste events one by one, if beyond the cut 
                        for i in range(n_pmts): # build array of residuals
                            r[i] = math.fabs(x[i] - mean[fibre]) 
                        r1, x1, s1 = list(zip(*sorted(zip(r, x, s), reverse=True))) # Sorts list r, x, and s by decreasing residual 

                        for i in range(n_pmts):
                            if r1[i]< self.siglim*sqrt(variance[fibre]) or i>iter:
                                w = 1/(s1[i]*s1[i])
                                fibre_stats[fibre].fill(x1[i], w)
                            else:
                                # Outlier removal, and wheighted mean intermediate sums
                                # print "removing ", event.region.GetHash(), " from ",self.PMTool.get_fiber_name(fibre), x, mean[fibre], siglim*sqrt(variance[fibre])
                                pass
                        
                    npmt[fibre] = fibre_stats[fibre].entries
                    if fibre_stats[fibre].entries>1:                    
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
                    if len(self.run_dict[event.run.runNumber][fibre])==0:
                        continue
                    print('Run %6d: Mixing is introducing a %5.2f +/- %5.3f%% shift (sigma= %4.2f%%) shift in fiber %s using %d pmts' % \
                        ( run.runNumber,
                          100*(mean[fibre]-1),
                          100*error[fibre],
                          100*rms[fibre],
                          self.PMTool.get_fiber_name(fibre),
                          npmt[fibre]))
        return

    
        
