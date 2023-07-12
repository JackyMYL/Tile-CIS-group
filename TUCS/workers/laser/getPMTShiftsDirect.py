############################################################
#
# getPMTShiftsDirect.py
#
############################################################
#
# Author: Henric Wilkens following work by Seb Viret <viret@in2p3.fr>
#
# July 06, 2009
#
# Goal: 
# Get the overall relative gain variation per PMT and
# compute the calibration coefficient to be applied to data
# (convertion from pC to LASER_pC)
#
# Input parameters are:
#
# -> useDB: correct the variation with the DB value (if existing)
#          DEFAULT VAL = False (this option is just used for crosschecking the DB update)
#
# For more info on the LASER system : http://atlas-tile-laser.web.cern.ch
#
#############################################################

from src.GenericWorker import *
from src.region import *

class getPMTShiftsDirect(GenericWorker):
    "This worker computes the stability of laser constants between two runs"    
        
    def __init__(self, useDB=False, useGlobal=True, usePisa=False, correctHV=False, verbose=False):
        self.useDB  = useDB                     
        self.PMTool = LaserTools()
        self.useGlobal = useGlobal
        self.usePisa = usePisa
        self.correctHV = correctHV
        self.verbose = verbose

    def ProcessRegion(self, region):
                     
        for event in region.GetEvents():
            if event.run.runType != 'Las':
                continue
            
#            event.data['f_laser']  = 1.
            
#            [part_num, module, channel, gain] = region.GetNumber()
#            pmt = self.PMTool.get_PMT_index(part_num-1,module-1,channel) 
            [part_num, module, pmt, gain] = region.GetNumber(1)
            fibre = self.PMTool.get_fiber_index(part_num-1,module-1,pmt)
            
            if 'deviation' in event.data:
                
                if self.useDB and 'part_var_db' in event.run.data: 
                    event.data['deviation'] = event.data['deviation'] - event.run.data['part_var_db'] # Obsolete hasn't been maintained
                else:
                    correction1 = 1.
                    correction2 = 1.
                    correction3 = 1.
                    error1 = 0.
                    error2 = 0.
                    if 'part_var' in event.run.data and self.useGlobal:
                        correction1 = event.run.data['part_var']
                        error1 = event.run.data['part_var_err']

                    if 'fiber_var' in event.run.data:
                        correction2 = event.run.data['fiber_var'][fibre]
                        error2 = event.run.data['fiber_var_err'][fibre]

                    # HV correction
                    if 'HV' in event.data and 'hv_db' in event.data and 'HVSet' in event.data:
                        deltagain = 0
                        beta = 6.9
                        if 'beta' in event.data: beta = event.data['beta']
                        if self.correctHV:
                            if (event.data['HV']>10.) and (event.data['hv_db']>10.) and (event.data['HVSet']>10.): 
                                correction3 = pow(event.data['HV']/event.data['hv_db'],beta)
                                deltagain = 100*(correction3-1.)
                            if self.verbose:
                                print("Run {}: {} HV is {} hv_db is {} beta is {} and correction is {} with deltagain {}".format(event.run.runNumber,region.GetHash(),event.data['HV'],event.data['hv_db'],beta,correction3,deltagain))

                    
                    try:
                        a = event.data['calibration']/event.data['lasref_db']
                        b = event.data['caliberror']/event.data['lasref_db']
                        c = correction1*correction2*correction3
                        event.data['deviation'] = 100 * (a/c-1.)          # Deviation corrected (in %)
                        event.data['deverr']    = 100 * sqrt( b*b/(c*c) +
                                                              a*a* ( error1*error1/(correction2*correction2) +
                                                                     error2*error2/(correction1*correction1) ) )

                        if a>0.:
                            f_laser = c/a
                            if 'part_var_pisa' in event.run.data and self.usePisa:
                                f_laser =  f_laser / event.run.data['part_var_pisa']
                                event.data['deviation'] = 100.*(1/f_laser-1.)
                        else:
                            f_laser = 1.

                        event.data['f_laser'] = f_laser

                        
#                        if event.run.data.has_key('part_var_pisa') and self.usePisa:
#                            event.data['f_laser'] = event.run.data['part_var_pisa']*a/c
#                        else:
#                            event.data['f_laser'] = a/c
                        
#                        if event.data['f_laser'] ==0.:
#                            print "f_laser=0: ",region.GetHash(), correction1, correction2, event.data['lasref_db'], event.data['number_entries']
#                            event.data['f_laser'] = 1.
                    except:
                        print("Exception: ",correction1, correction2, event.data['lasref_db'], event.data['number_entries'])
                        event.data['deviation'] = -100.
                        event.data['deverr']    = 0.

#                    if event.data.has_key('problems'):
#                        if 'No HV' in event.data['problems']:
#                            event.data['deviation'] = -100.
#                            event.data['deverr']    = 0.
#                            event.data['f_laser']   = 1.
# The End
