# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# March 24, 2009
#

from src.ReadGenericCalibration import *
from src.region import *

class ScanRMSvsScan(ReadGenericCalibration):
    "See the comparison between errors on CIS scans with error on mean verus rms"

    def ProcessRegion(self, region):
        for event in region.GetEvents():
            if event.run.runType == 'CIS':
                if 'scan' in event.data and event.data['scan'] and\
                       'scan_rms' in event.data and event.data['scan_rms']:
                    gscan = event.data['scan']
                    gscan_rms = event.data['scan_rms']

                    for i in range(gscan.GetN()):
                        # sqrt(60) ~= 7.745
                        if not 7.74 < gscan_rms.GetErrorY(i)/gscan.GetErrorY(i) < 7.75:
                            print(gscan_rms.GetErrorY(i), gscan.GetErrorY(i), gscan_rms.GetErrorY(i)/gscan.GetErrorY(i))
                        
                             
