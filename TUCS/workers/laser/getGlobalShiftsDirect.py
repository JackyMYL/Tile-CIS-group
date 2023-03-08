############################################################
#
# getGlobalShiftsDirect.py
#
############################################################
#
# Author: Henric <Henric.Wilkens@cern.ch> based on work from Seb Viret
#
# November, 2011
#
# Goal:
# Get the overall relative gain variation (not per partition)
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

class getGlobalShiftsDirect(GenericWorker):
    "This worker computes the partition variation"

    # make this runs eventually
    def __init__(self, siglim=3.0, n_iter=2, verbose=False):
        self.siglim   = siglim
        self.n_iter   = n_iter
        self.verbose  = verbose
        self.events   = set()
        self.PMTool   = LaserTools()
        self.run_dict = {}
        self.run_list = []


    def ProcessStart(self):

        global run_list
        for run in run_list.getRunsOfType('Las'):
            self.run_list.append(run)
            self.run_dict[run.runNumber] = []

    # Collect the events for run region

    def ProcessRegion(self, region):
        if len(region.GetNumber())==4:
            layer = region.GetLayerName()
            
#            if (not(layer=='BC' or layer=='D' or layer=='B')):
            if (not(layer=='D')):
                return
            
            [part, module, pmt, gain] = region.GetNumber(1)
            saturation_limits = [760., 12.]                          # in pC

            for event in region.GetEvents():
                if event.run.runType=='Las' and 'deviation' in event.data:

                    if event.data['status']!=0 or not event.data['is_OK']:
                        continue

                    if (event.data['calibration']<=0. or event.data['lasref_db']<=0):
                        continue

                    if (event.data['HV']<10.) and (event.data['HVSet']<10.): # Emergnecy mode: we don't take in global correction
                        continue

                    if (abs(event.data['HV']-event.data['hv_db'])>10):       # bad HV, will bias fiber correction
                        continue

                    
                    if (event.data['signal']>saturation_limits[gain]):       # Saturation limits
                        continue

                #if layer=='BC' or layer=='D' or layer=='B':
                    self.run_dict[event.run.runNumber].append(event)
                    

    # We perform the analysis once the events have been collected

    def ProcessStop(self):

        for run in sorted(self.run_list, key=lambda run: run.runNumber): # We have to deal with the multi-run case

            stat = stats()
            stat_pisa = stats()
            mean = 0
            variance = 10.
            pisa_mean = 0.
            # Then compute the corrections iteratively
            for iter in range(self.n_iter):

                stat.reset()
                stat_pisa.reset()

                for event in self.run_dict[run.runNumber]:
                    # Arithmetic mean...
                    # x = event.data['calibration']/event.data['lasref_db']
                    # s = event.data['caliberror']/event.data['lasref_db']

                    hvgain =1.
                    if 'hv_db' in event.data:
                        if (event.data['hv_db'])!=0:
                            try:
                                hvgain = pow(event.data['HV']/event.data['hv_db'],6.9)
                            except:
                                pass

                    # Geometric mean...
                    x = log((event.data['calibration']/event.data['lasref_db'])/hvgain)
                    s = event.data['caliberror']/event.data['calibration']
                    
                    if math.fabs(x-mean) <= self.siglim*sqrt(variance) and s!=0.:
                        w = 1./(s*s)                        
                        stat.fill(x,w)

                        if 'gain_Pisa' in event.data:
                            try:
                                pisa_x = log(event.data['gain_Pisa']/event.data['gain_Pisaref_db'])

                                if pisa_x<0.1:
                                    pisa_s = event.data['gainerror_Pisa']/event.data['gain_Pisa']
                                    pisa_w = 1./(pisa_s*pisa_s)

                                    stat_pisa.fill(pisa_x, pisa_w)                                    
                            except:
                                print("Math Error: log or /:", event.data['gain_Pisa'], event.data['gain_Pisaref_db'])
                                pass

                if stat.entries>1:
                    mean = stat.mean()
                    variance = stat.variance()
                    error = stat.error()
                    
                    if stat_pisa.sumweight>0.:
                        # stat_pisa.dump()
                        pisa_mean  = stat_pisa.mean()
                        pisa_var   = stat_pisa.variance()
                        pisa_error = stat_pisa.error()
                        pisa_var = stat_pisa.variance()
                        pisa_error = stat_pisa.error()
                    else:
                        pisa_mean = 0.
                else:
                    mean = 0.
                    variance = 1.
                    error = 1.
            # End of the iterations
            mean = exp(mean)
            rms  = mean*sqrt(variance)
            error =  mean*error

            run.data['part_var'] = mean
            run.data['part_var_rms'] = rms
            run.data['part_var_err'] = error
            if pisa_mean!=0.:
                pisa_mean = exp(pisa_mean)
                pisa_rms = pisa_mean*sqrt(pisa_var)
                pisa_error = pisa_mean*pisa_error
                run.data['part_var_pisa'] = pisa_mean
                run.data['part_var_pisa_rms'] = pisa_rms
                run.data['part_var_pisa_err'] = pisa_error
                

            # some printouts
            if self.verbose:
                if pisa_mean==0.:
                    print('Run %6d: Optics is introducing a global %5.2f +/- %5.3f%% shift (sigma= %4.2f%%)' % \
                        (run.runNumber, 100.*(mean-1.), 100*error, 100*rms))
                else:
                    print('Run %6d: Optics is introducing a global %5.2f +/- %5.3f%% shift (sigma= %4.2f%%), Pisa mean  %5.2f [%d]  Pisa-CF %5.2f%%' % \
                        (run.runNumber, 100.*(mean-1.), 100*error, 100*rms, 100.*(pisa_mean-1.), int(stat_pisa.neff()), 100*(pisa_mean-mean)))



