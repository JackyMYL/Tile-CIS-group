
############################################################
#
# StoreFiberShifts.py
#
############################################################
#
# Author: D. Boumediene
# Modifications :
#        Jan 2013 : D. Boumediene, E. Dubreuil
#
#
# Usage :
#           StoreFiberShift(RestoreRegion='LBC_m28')
#             # it stores fiber+global variation for LBC28 module
#           StoreFiberShift(RestoreRegion='LBC_m28_ch05') 
#             # it stores fiber+global variation for LBC28 ch05
#           StoreFiberShift(RestoreRegion='layer_E')
#             # it stores fiber+global variation for all E cells
#           StoreFiberShift(RestoreRegion='layer_E',Restore=True)
#             # it erases current fiber+global variation for all E cells
#             # using the saved one
#
#############################################################


from src.GenericWorker import *
from src.region import *
from array import *
import math

from src.laser.toolbox import *

class StoreFiberShift(GenericWorker):
    " This worker saves or restores some fiber variation.."
    
    # make this runs eventually
    def __init__(self, iFiber=-1, verbose=False, Restore=False, RestoreRegion='none'):
        self.iFiber     = iFiber
        self.RestoreRegion = RestoreRegion
        self.RestoreLayer = '0'
        self.verbose    = verbose
        self.events    = set()
        self.PMTool    = LaserTools()
        self.Restore   = Restore

        if RestoreRegion.find('layer_')!=-1 and RestoreRegion!='layer_' : # we are looking for a specific layer
            x = RestoreRegion.split("_")
            self.RestoreLayer = x[1]
            self.RestoreRegion = 'none'

    

    def ProcessRegion(self, region):

###        print 'current...',self.RestoreRegion, self.StoredFVar[0][5]

        for event in region.GetEvents():

            [part_num, imodule, pmt, gain] = event.region.GetNumber(1)
            part_num -= 1
            indice = self.PMTool.get_fiber_index(part_num,imodule-1,pmt)
            iCell = self.PMTool.get_stable_cells(part_num,pmt) #Get cell name a PMT number starting from 1
            layer = self.PMTool.get_pmt_layer(part_num, imodule, pmt)

            if self.iFiber!=-1 and indice != self.iFiber:
                if (self.Restore==False):
                    event.data['fiber_var']=0
                    event.data['part_var']=0
                continue

##

            if (self.RestoreLayer!='0'): # looking for a Layer#
                if  layer!=self.RestoreLayer:
                    if (self.Restore==False):
                        event.data['fiber_var']=0
                        event.data['part_var']=0
                    continue

            if self.RestoreRegion != 'none': # looking for a generic region (ex. LBA_m28 or LBA_m18_c0 etc)
                if event.region.GetHash().find(self.RestoreRegion)==-1:
                    if (self.Restore==False):
                        event.data['fiber_var']=0
                        event.data['part_var']=0
                    continue


            if 'deviation' not in event.data:
                continue
            
            if self.Restore != True and 'fiber_var' not in event.data:
                continue
            if self.Restore != True and 'part_var' not in event.data:
                continue

            if self.Restore == True: #restoring fiber var

                if 'fiber_var_store' not in event.data or 'part_var_store' not in event.data:
                    print('<!> ERROR, attempt to restore a fiber variation which was not stored for ',event.region.GetHash())
                else:
                    if (event.data['fiber_var_store']==0):
                        print('  --> <!> Warning, restoring a 0 correction (was ',event.data['fiber_var'],' before)')
                    if self.verbose==True:
                        print('  --> Restoring the fiber variation for ',event.region.GetHash(),'(',event.data['fiber_var'],'->',event.data['fiber_var_store'],')')
                        
                    event.data['fiber_var']=event.data['fiber_var_store']
                    
                    if (event.data['part_var_store']==0):
                        print('  --> <!> Warning, restoring a 0 part correction (was ',event.data['part_var'],' before)')
                    if self.verbose==True:
                        print('  --> Restoring the part variation for ',event.region.GetHash(),'[',event.data['part_var'],'->',event.data['part_var_store'],'] ',layer,event.data['deviation']-event.data['part_var_store']-event.data['fiber_var_store'])
                        
                    event.data['part_var']=event.data['part_var_store']



            else: ## Storing fiber var

                event.data['fiber_var_store']=event.data['fiber_var']
                event.data['part_var_store']=event.data['part_var']
                

    def ProcessStop(self):

        if self.Restore == True:
            if (self.iFiber!=-1):
                print("  Fiber variation for fiber #",self.iFiber," was restored.")
            if (self.RestoreRegion!='none'):
                print("  Fiber variation for region ",self.RestoreRegion," was restored.")
            if (self.RestoreLayer!='0'):
                print("  Fiber variation for Layer ",self.RestoreLayer," was restored.")
                
        else:
            if (self.iFiber!=-1):
                print("  Fiber variation for fiber #",self.iFiber," was saved.")
            if (self.RestoreRegion!='none'):
                print("  Fiber variation for region ",self.RestoreRegion," was saved.")
            if (self.RestoreLayer!='0'):
                print("  Fiber variation for Layer ",self.RestoreLayer," was saved.")


