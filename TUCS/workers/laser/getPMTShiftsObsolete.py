############################################################
#
# getPMTShifts.py
#
############################################################
#
# Author: Seb Viret <viret@in2p3.fr>
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
#
# Last updates:
#
# - Feb 2015: LaserII functionality implemented <marius.cornelis.van.woerden@cern.ch>
#             For more information on LaserII: 
#
#############################################################


from src.GenericWorker import *
from src.region import *


class getPMTShifts(GenericWorker):
    " This worker computes the stability of laser constants between two runs "    

        
    def __init__(self, useDB=False, Threshold_LB=0, Threshold_EB=0):
        self.useDB  = useDB
        self.Threshold_LB  = Threshold_LB
        self.Threshold_EB  = Threshold_EB
        print('INFO : the threshold for LB is ',self.Threshold_LB, ' % ')
        print('INFO : the threshold for EB is ',self.Threshold_EB, ' % ')


    def ProcessRegion(self, region):
        region_name = region.GetHash()

        for event in region.GetEvents():
            if 'deviation' in event.data:
 
                p_var = 0
                f_var = 0

 

                if 'part_var' in event.data:
                    p_var = event.data['part_var']
                if 'fiber_var' in event.data:
                    f_var = event.data['fiber_var']


                event.data['deviation_raw'] = event.data['deviation']       # No correc
                deviation_raw = event.data['deviation']                     # No corrections applied                
                event.data['deviation']     = deviation_raw - f_var - p_var # Deviation corrected (in %)

                pmt_region = str(event.region)
               
                if pmt_region.find('LB')!=-1:

                    if deviation_raw>-100 and event.data['deviation']>-100:
                        if ( fabs(event.data['deviation']) < self.Threshold_LB  ):
                            event.data['deviation'] = 0
                        event.data['f_laser']   = 1./(1.+event.data['deviation']/100.)        # Calibration factor
                    else:
                        event.data['f_laser'] = -1
                 
                elif pmt_region.find('EB')!=-1:


                    if deviation_raw>-100 and event.data['deviation']>-100:
                        if ( fabs(event.data['deviation']) < self.Threshold_EB  ):
                            event.data['deviation'] = 0
                        event.data['f_laser']   = 1./(1.+event.data['deviation']/100.)        # Calibration factor
                        
                    else:
                        event.data['f_laser'] = -1

                else:
                    print('ERROR : the region is not defined')


                if self.useDB and 'pmt_var_db' in event.data:

                    if event.data['pmt_var_db']!=0 :
                        if deviation_raw > -100:
                            event.data['deviation'] = event.data['deviation'] - event.data['pmt_var_db']
                            event.data['f_laser']   = 1./(1.+event.data['deviation']/100.)

                if len(region.GetNumber())==4 and pmt_region.find('LBA10_m10')!=-1:
                    [part, module, pmt, gain] = region.GetNumber(1)
                    print(event.run.time_in_seconds, part-1, module-1, region.get_channel(), event.data['deviation'])

                    
#                if event.data['status']: #bad channels
#                    sstatus=1
#                else:
#                    sstatus=0

#                if event.data.has_key('cesium_db'):                    
#                    f_cs = event.data['cesium_db']
#                else:
#                    f_cs = 0


