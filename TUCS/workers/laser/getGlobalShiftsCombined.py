############################################################
#
# getGlobalShiftsCombined.py
#
############################################################
#
# Author: Giulia, based on work from Henric <Henric.Wilkens@cern.ch> which is based on work from Seb Viret
# December, 2017
#
# Main Goal: Compute the global shift and correction associated to input light variation
#
# New features:
# -> Rute, Dec 2021: For cross-check purposes (useful for Laser Run 2 int-note) this correction is also computed  
#   - per A/C sides;
#   - for EB/LB PMTs only.
#
# Input parameters are:
# -> n_iter: the number of iterations necessary to get the offset value
# -> siglim: the number of st.dev. considered for outlier rejection (for iterations)
#
# For more info on the LASER system : http://atlas-tile-laser.web.cern.ch
#############################################################


from src.GenericWorker import *
from src.region import *
from src.stats import *
from array import *
import math

from src.laser.toolbox import *

class getGlobalShiftsCombined(GenericWorker):
    "This worker computes the global correction"

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
            cell  = region.GetCellName()
            
            if (not(layer=='D' or cell=='BC1' or cell=='BC2' or cell=='B13' or cell=='B14' or cell=='B15')):
                return
            
            [part, module, pmt, gain] = region.GetNumber(1)
            saturation_limits = [760., 12.]                          # in pC

            for event in region.GetEvents():
                if event.run.runType=='Las' and 'deviation' in event.data and 'Pisa_deviation' in event.data:

                    if event.data['status']!=0 or not event.data['is_OK']:
                        continue

                    if (event.data['calibration']<=0. or event.data['lasref_db']<=0):
                        continue

                    if (event.data['gain_Pisa']<=0. or event.data['gain_Pisaref_db']<=0.):
                        continue

                    if (event.data['HV']<10.) and (event.data['HVSet']<10.): # Emergency mode: we don't take in global correction
                        continue

                    if (abs(event.data['HV']-event.data['hv_db'])>10):       # bad HV, will bias global correction
                        continue

                    if (event.data['signal']>saturation_limits[gain]):       # Saturation limits
                        continue

                    self.run_dict[event.run.runNumber].append(event)
                    

    # We perform the analysis once the events have been collected
    def ProcessStop(self):

        for run in sorted(self.run_list, key=lambda run: run.runNumber): # We have to deal with the multi-run case

            stat = [stats(),stats(),stats(),stats(),stats()] #inclusive, A-side, C-side, EB, LB
            mean = [0,0,0,0,0]
            variance = [10.,10.,10.,10.,10.]
            error = [0.,0.,0.,0.,0.]
            # Then compute the corrections iteratively
            for iter in range(self.n_iter):

                for i in range(0,5):
                    stat[i].reset()

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
                    a = event.data['calibration']/event.data['lasref_db']
                    b = event.data['gain_Pisa']/event.data['gain_Pisaref_db']

                    #x = log((event.data['calibration']/event.data['lasref_db'])/hvgain)
                    x = log(a/(b*hvgain))
                    a_err = event.data['caliberror']/event.data['lasref_db']
                    b_err = event.data['gainerror_Pisa']/event.data['gain_Pisaref_db']

                    #s = event.data['caliberror']/event.data['calibration']
                    s = sqrt((a_err/a)*(a_err/a) + (b_err/b)*(b_err/b))

                    if math.fabs(x-mean[0]) <= self.siglim*sqrt(variance[0]) and s!=0.:
                        w = 1./(s*s)
                        stat[0].fill(x,w)

                    # A/C side split
                    if event.region.get_partition() in ['EBA','LBA']:
                        if math.fabs(x-mean[1]) <= self.siglim*sqrt(variance[1]) and s!=0.:
                            w = 1./(s*s)
                            stat[1].fill(x,w)
                    elif event.region.get_partition() in ['EBC','LBC']:
                        if math.fabs(x-mean[2]) <= self.siglim*sqrt(variance[2]) and s!=0.:
                            w = 1./(s*s)
                            stat[2].fill(x,w)
                    else:
                        print('WARNING Partition not EBA,LBA,LBC,EBC: ', event.region.get_partition())

                    # EB/LB split
                    if event.region.get_partition() in ['EBA','EBC']:
                        if math.fabs(x-mean[3]) <= self.siglim*sqrt(variance[3]) and s!=0.:
                            w = 1./(s*s)
                            stat[3].fill(x,w)
                    elif event.region.get_partition() in ['LBA','LBC']:
                        if math.fabs(x-mean[4]) <= self.siglim*sqrt(variance[4]) and s!=0.:
                            w = 1./(s*s)
                            stat[4].fill(x,w)
                    else:
                        print('WARNING Partition not EBA,LBA,LBC,EBC: ', event.region.get_partition())



                for i in range(0,5):
                    if stat[i].entries>1:
                        mean[i] = stat[i].mean()
                        variance[i] = stat[i].variance()
                        error[i] = stat[i].error()
                    
                    else:
                        mean[i] = 0.
                        variance[i] = 1.
                        error[i] = 1.

            # End of the iterations
            rms = [0.,0.,0.,0.,0.]
            for i in range(0,5):
                mean[i] = exp(mean[i])
                rms[i]  = mean[i]*sqrt(variance[i])
                error[i] =  mean[i]*error[i]

            run.data['part_var'] = mean[0]
            run.data['part_var_rms'] = rms[0]
            run.data['part_var_err'] = error[0]

            run.data['part_var_partA'] = mean[1]
            run.data['part_var_rms_partA'] = rms[1]
            run.data['part_var_err_partA'] = error[1]

            run.data['part_var_partC'] = mean[2]
            run.data['part_var_rms_partC'] = rms[2]
            run.data['part_var_err_partC'] = error[2]

            run.data['part_var_EB'] = mean[3]
            run.data['part_var_rms_EB'] = rms[3]
            run.data['part_var_err_EB'] = error[3]

            run.data['part_var_LB'] = mean[4]
            run.data['part_var_rms_LB'] = rms[4]
            run.data['part_var_err_LB'] = error[4]


            # some printouts
            if self.verbose:
                print('Run %6d: Optics is introducing a global %5.2f +/- %5.3f%% shift (sigma= %4.2f%%)' % \
                      (run.runNumber, 100.*(mean[0]-1.), 100*error[0], 100*rms[0]))
                print('Run %6d: Optics is introducing a part A %5.2f +/- %5.3f%% shift (sigma= %4.2f%%)' % \
                      (run.runNumber, 100.*(mean[1]-1.), 100*error[1], 100*rms[1]))
                print('Run %6d: Optics is introducing a part C %5.2f +/- %5.3f%% shift (sigma= %4.2f%%)' % \
                      (run.runNumber, 100.*(mean[2]-1.), 100*error[2], 100*rms[2]))
                print('Run %6d: Optics is introducing a    EB  %5.2f +/- %5.3f%% shift (sigma= %4.2f%%)' % \
                      (run.runNumber, 100.*(mean[3]-1.), 100*error[3], 100*rms[3]))
                print('Run %6d: Optics is introducing a    LB  %5.2f +/- %5.3f%% shift (sigma= %4.2f%%)' % \
                      (run.runNumber, 100.*(mean[4]-1.), 100*error[4], 100*rms[4]))
