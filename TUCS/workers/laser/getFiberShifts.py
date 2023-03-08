############################################################
#
# getFiberShifts.py
#
############################################################
#
# Author: S. Viret
# Modifications :
#        Novembre 2011 : D. Boumediene, E. Dubreuil
#                        Use stable cells only for fiber var
#        January  2012 : E. Dubreuil, D. Boumediene
#                        Skip PMTs with no reference
#                        Flag UseStableCells added
#                        (commited)
#
# Goal:
# Get the overall relative gain variation per patch panel fiber
# using stable PMTs as reference
#
# Input parameters are:
#
# -> n_iter: the number of iterations necessary to get the offset value
#
# -> n_sig: the number of st.dev. considered for outlier rejection (for iterations)
#
# -> UseStableCells: Use a set of stable cells to compute the fiber var.
#    If set to False, all the PMTs are used. The definition of a stable Cell
#    is in toolbox.
#
# For more info on the LASER system : http://atlas-tile-laser.web.cern.ch
#
#############################################################


from src.GenericWorker import *
from src.region import *
from array import *
import math
from src.laser.toolbox import *


class getFiberShifts(GenericWorker):
    " This worker computes the PP fiber variation"


    # make this runs eventually
    def __init__(self, n_sig=2, n_iter=5, verbose=False, UseStableCells=True, SkipEmergency=False):
        self.n_sig     = n_sig
        self.SkipEmergency = SkipEmergency
        self.n_iter    = n_iter
        self.verbose    = verbose
        self.UseStableCells = UseStableCells
        self.events   = set()
        self.allevents = set()
        self.run_list = []
        self.PMTool   = LaserTools()


    def ProcessRegion(self, region):
        # exclude problematic channels (isBad+Status) + emergency (HV<10)
        for event in region.GetEvents():
            self.allevents.add(event)
            if 'deviation' in event.data:
                pmt_region = str(event.region)
                                        
                if 'is_OK' in event.data:
                    if (not event.data['is_OK']):
                        continue

                #### based on getFiberShiftsHenric.py ADD IgnoreStatus
                if 'status' in event.data:
                    if (event.data['status']&0x4) or (event.data['status']&0x10):
                        continue

                if ((event.data['HV']>5) and abs(event.data['HV']-event.data['hv_db'])>5):      # bad HV, will bias fiber correction
                    continue
                    
        # This is the DQ status list that affect laser data
                DQstatus_list = ['No HV','Wrong HV','ADC masked (unspecified)','ADC dead','Data corruption','Severe data corruption','Severe stuck bit','Large LF noise','Very large LF noise','Channel masked (unspecified)','Bad timing']

                if 'problems' in event.data:
                    for problem in event.data['problems']:
                        if (problem in DQstatus_list):
                            continue

#                if (pmt_region.find('LBC_m48')!=-1 and self.SkipEmergency==True):## emergency + HV not properly stored
#                    print event.run.runNumber,' ', pmt_region,' hv=',event.data['HV'],' deviation=',event.data['deviation'],'%'
#                    continue

#                if (pmt_region.find('LBA_m61')!=-1):## special case
#                    continue

                if ('deviation' in event.data):
                    if (event.data['deviation']==0 or event.data['deviation']<-25.0): #dead or big drops (eg. emergency)
                        continue

                if (event.data['calibration']<=0. or event.data['lasref_db']<=0):
                    continue

                if (self.SkipEmergency==True and event.data['HV']<5): # or pmt_region.find('LBA_m54')!=-1: # or pmt_region.find('LBA_m13')!=-1) :
                    continue
                else:
                    self.events.add(event)

                    if event.run.runNumber not in self.run_list:
                        event.run.data['fiber_var'] = dict()
                        self.run_list.append(event.run.runNumber)

        return


    def ProcessStop(self):

        self.max_val    = 1000.0 # Can handle a 1000% variation!!!
        self.nbins      = 8000
        self.bin_width  = 2.*self.max_val/self.nbins
        Nb_PMT          = [0 for x in range(384)]

        for run in self.run_list:
            # Initialize patch panel fibers arrays

            e_FIB_n   = [0 for x in range(384)]
            sig_FIB_n = [100000 for x in range(384)]

            # Special array needed to improve robustness

            bin_FIB_n = [0 for x in range(384*self.nbins)]


            # Then compute the corrections iteratively

            for iter in range(self.n_iter):

                n_FIB     = [0 for x in range(384)]
                e_FIB     = [0 for x in range(384)]
                sig_FIB   = [0 for x in range(384)]

                for event in self.events:

                    if run != event.run.runNumber:
                        continue

                    # BDE
                    # if long barrel and PMT is not a D cell PMT : skip
                    # used to used stable outside layers only

                                     
                    [part_num, module, pmt, gain] = event.region.GetNumber(1)
                    part_num -= 1
                    indice = self.PMTool.get_fiber_index(part_num,module-1,pmt)

                    iCell = self.PMTool.get_stable_cells(part_num,pmt) #Get cell name a PMT number starting from 1

                    if self.UseStableCells:
                        if (iCell != 3):
                            continue
                    else:
                        print('WARNING : You use the old definition of the fiber correction')

                    p_var = 0
                    if 'part_var' in event.data:
                        p_var = event.data['part_var']

                    var = event.data['deviation'] - p_var - e_FIB_n[indice]


                    # Outlier removal
                    if math.fabs(var) < self.n_sig*sig_FIB_n[indice]:
                        n_FIB[indice] += 1
                        Nb_PMT[indice] = n_FIB[indice]
                        e_FIB[indice] += var

                    # Special process for better outlier removal
                    if iter==0 and  math.fabs(var) < self.max_val:
                        bin = int(float((var+self.max_val)/self.bin_width))
                        bin_FIB_n[int(self.nbins*indice+bin)] += 1


                if iter == 0:

                    for fibre in range(384):

                        iMAX = 0
                        vMAX = 0
                        nval = int(self.nbins)

                        for k in range(nval):

                            if bin_FIB_n[nval*fibre+k]>vMAX:
                                iMAX=k
                                vMAX=bin_FIB_n[nval*fibre+k]

                        if iMAX==0 or iMAX==nval-1: # Bad case
                            if n_FIB[fibre] != 0:
                                e_FIB[fibre] /= n_FIB[fibre]
                                n_FIB[fibre] = 0
                        else:
                            v0 = self.bin_width*(iMAX-1+0.5)-self.max_val
                            v1 = self.bin_width*(iMAX+0.5)-self.max_val
                            v2 = self.bin_width*(iMAX+1+0.5)-self.max_val

                            n0 = bin_FIB_n[nval*fibre+iMAX-1]
                            n1 = bin_FIB_n[nval*fibre+iMAX]
                            n2 = bin_FIB_n[nval*fibre+iMAX+1]

                            barycenter = float(n0*v0+n1*v1+n2*v2)/float(n0+n1+n2)

                            e_FIB_n[fibre]=barycenter
                            e_FIB[fibre]=0.
                            sig_FIB_n[fibre] = self.bin_width

                else:
                    for fibre in range(384):
                        if n_FIB[fibre] != 0:
                            e_FIB[fibre] /= n_FIB[fibre]
                            n_FIB[fibre] = 0

                for event in self.events:

                    if run != event.run.runNumber:
                        continue

                    if 'problems' in event.data:
                        continue

                        
                    [part_num, module, pmt, gain] = event.region.GetNumber(1)
                    part_num -= 1
                    drawer = module-1
                    indice = self.PMTool.get_fiber_index(part_num,drawer,pmt)
                    p_var = 0

                    if 'part_var' in event.data:
                        p_var = event.data['part_var']

                    var = event.data['deviation'] - p_var - e_FIB[indice] - e_FIB_n[indice]

                    if math.fabs(var) < self.n_sig*sig_FIB_n[indice]:
                        sig_FIB[indice] += var*var
                        n_FIB[indice] += 1

                for fibre in range(384):
                    if n_FIB[fibre] > 1:
                        sig_FIB_n[fibre] = math.sqrt(sig_FIB[fibre]/(n_FIB[fibre]-1))
                        e_FIB_n[fibre]  += e_FIB[fibre]


            #
            # Here we compute the partition variation, using the fiber ones
            #
            # Getting the correction this way, we avoid any biasing problem
            # on the pmt variation calculation
            #

            self.barrel_var = 0.
            self.endcap_var = 0.

            self.n_barrel = 0
            self.n_endcap = 0

            for i in range(128):
                if e_FIB_n[i] != 0.: # Barrel
                    self.barrel_var += e_FIB_n[i]
                    self.n_barrel   += 1

                if e_FIB_n[128+i] != 0.: # EBA
                    self.endcap_var += e_FIB_n[128+i]
                    self.n_endcap   += 1

                if e_FIB_n[256+i] != 0.: # EBC
                    self.endcap_var += e_FIB_n[256+i]
                    self.n_endcap   += 1

            if self.n_barrel != 0:
                self.barrel_var /= self.n_barrel

            if self.n_endcap != 0:
                self.endcap_var /= self.n_endcap

            for event in self.allevents:

                if run != event.run.runNumber:
                    continue


                [part_num, module, pmt, gain] = event.region.GetNumber(1)

                part_num -= 1
                indice = self.PMTool.get_fiber_index(part_num,module-1,pmt)

                if indice < 128:
                    event.run.data['fiber_var'][indice] = e_FIB_n[indice] - self.barrel_var
                    event.data['fiber_var'] = e_FIB_n[indice] - self.barrel_var

                    if ('part_var' not in event.data):
                        event.data['part_var']  = self.barrel_var
                    event.run.data['part_var_lb'] = self.barrel_var
                    
                else:
                    event.run.data['fiber_var'][indice] = e_FIB_n[indice] - self.endcap_var
                    event.data['fiber_var'] = e_FIB_n[indice] - self.endcap_var
                    if ('part_var' not in event.data):
                        event.data['part_var'] = self.endcap_var
                    event.run.data['part_var'] = self.endcap_var

                
            if self.verbose: # some printouts
                for fibre in range(384):
                    if fibre<128:
                        part_var = self.barrel_var
                    else:
                        part_var = self.endcap_var

                    print('Run %7d: Mixing is introducing a global %5.2f & fibre %5.2f+/-%4.2f %% shift in fiber %s Nb de PMT : %2d' % ( run,part_var ,e_FIB_n[fibre], sig_FIB_n[fibre], self.PMTool.get_fiber_name(fibre),Nb_PMT[fibre]))

    
                print(' Mean variation in LB ',self.barrel_var,' %')
                print(' Mean variation in EB ',self.endcap_var,' %')
