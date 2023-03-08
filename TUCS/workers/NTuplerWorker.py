############################################################
#
# LasCsCIS_plots.py
#
############################################################
#
# Author: Samuel Meehan
# Date  : April 20, 2012
#
# Notes: Default CIS HG: 81.3669967651
#        Default CIS LG: 1.29400002956
#


from src.GenericWorker import *
from src.oscalls import *
import src.MakeCanvas
import time
import math
import ROOT
from ROOT import TCanvas, TPad, TPaveText
import numpy
unravel = numpy.unravel_index
from src.TreeMaker import TreeMaker      #### Import TreeMaker here

NPart=4
NMod=64
NChan=48
NGain=2


def GetGlobalChannel(part,module,channel,gain):
    globalchannel = NMod*NChan*NGain*part + NChan*NGain*module + NGain*channel + gain
    return globalchannel
    
# This function takes a list of sub-indices and returns a global index

def Region_to_GlobalRegion(pos, shape):
    res = 0
    acc = 1
    for pi, si in zip(reversed(pos), reversed(shape)):
        res += pi * acc
        acc *= si
    return res
    
def GlobalRegion_to_Region(gchan, shape):
    part = 0
    module = 0
    channel = 0
    gain = 0
    region = unravel(gchan,shape)

    return region[0],region[1],region[2],region[3]

class NTuplerWorker(GenericWorker):
    "This worker generates fractional response plots with combined TileCal calibration systems."

    def __init__(self, DebugFlag=False, OutputPath=None, RunType='NOTYPE' ):
        self.Debug          = DebugFlag

        if RunType=='CIS':
            self.Type           = 1
        elif RunType=='Las':
            self.Type           = 2
        elif RunType=='cesium':
            self.Type           = 3
        elif RunType=='MinBias':
            self.Type           = 4
        elif RunType=='HV':
            self.Type           = 5
        else:
            print('Not a valid run choice - does this file/run combination exist?')

        self.OutputFileName = os.path.join(getPlotDirectory(),OutputPath)
        self.OutputTreeName = 'tree'
        
        print((self.OutputFileName))
            
        
    def ProcessStart(self):
        
        print("--PROCESS START--")
        
        if self.Debug==1 : print(' >>>>>> INITIALIZING OUTPUT COMMON NTUPLE >>>>>>')
            
        self.tree = TreeMaker('tree', 'tree', compression=1)

        self.var_runnumber   = ('runnumber', 'i')
        self.var_date        = ('date', 'F')
        self.var_runtype     = ('runtype', 'i')
        self.var_nchan       = ('nchan','i')
        self.var_quality     = ('quality', 'F','nchan')
        self.var_calibration = ('calibration', 'F','nchan')

        self.tree.addLeaf(*(self.var_runtype))
        self.tree.addLeaf(*(self.var_runnumber))
        self.tree.addLeaf(*(self.var_date))
        self.tree.addLeaf(*(self.var_nchan))
        self.tree.addLeaf(*(self.var_quality))
        self.tree.addLeaf(*(self.var_calibration))

        self.mytree = self.tree.create()

        print('Set up some variables')
        self.npart    = NPart
        self.nmodule  = NMod
        self.nchannel = NChan
        self.ngain    = NGain
        self.array_shape = [self.npart,self.nmodule,self.nchannel,self.ngain]
        self.dbproblems  = [] 

        print('Initialize values')
        self.tree.runtype     = 666
        self.tree.runnumber   = 666
        self.tree.date        = 666
        self.tree.nchan       = self.npart * self.nmodule * self.nchannel * self.ngain
        
        # expand array to necessary size before intialization
        checkravel={}
        checkglob={}        
        
        for i in range(self.npart):
            for j in range(self.nmodule):
                for k in range(self.nchannel):
                    for l in range(self.ngain):
                        rav = Region_to_GlobalRegion( [i,j,k,l] , self.array_shape )
                        glob = GetGlobalChannel(i,j,k,l)
                        
                        if rav not in list(checkravel.keys()):
                            checkravel[rav]=66666666
                        else:
                            print('ITS HERE in rav ************************************************')
                            check = eval(input())
                        
                        if glob not in list(checkglob.keys()):
                            checkglob[rav]=66666666
                        else:
                            print('ITS HERE in glob************************************************')
                            check=eval(input())
                        
                        #if self.Debug:
#                             print 'original;   ',i,j,k,l
#                             print 'ravel=      ',Region_to_GlobalRegion( [i,j,k,l] , self.array_shape )
#                             print 'getglob=    ',GetGlobalChannel(i,j,k,l)
#                             print 'unravelled=  ',GlobalRegion_to_Region(rav, self.array_shape)
                        self.tree.quality.append(-20)
                        self.tree.calibration.append(-20)
                        
        print(('size of array ', len(self.tree.calibration)))

        # fill initial values into array
        for i in range(self.npart):
            for j in range(self.nmodule):
                for k in range(self.nchannel):
                    for l in range(self.ngain):
                        self.gchan = Region_to_GlobalRegion( [i,j,k,l] , self.array_shape )
                        self.tree.quality[self.gchan]=-666.0
                        self.tree.calibration[self.gchan]=-666.0
                

    def ProcessRegion(self, region):
    
        # Initialize values
        part_val    = -666
        module_val  = -666
        channel_val = -666
        gain_val    = -666
        qual_val    = -666
        cal_val     = -666
#       self.var_runnumber = 666
#       self.var_runtype   = 666
#       self.var_date      = 666
    
        numbers = region.GetNumber()
        if len(numbers)==4:
            [part, module, channel, gain] = numbers
        elif len(numbers)==3:
            [part, module, channel] = numbers
            gain = 0  
        else:
            return
            
        for event in region.GetEvents():
    
            # FILL VARIABLES THAT WILL BE WRITTEN TO TREE HERE     
            self.tree.runnumber   = int(event.run.runNumber)
            self.tree.runtype     = self.Type
            self.tree.date        = event.run.time_in_seconds

            if self.Debug:                  
                print(("Date in seconds:  ", self.var_date))
                
    
            #===========================================
            #
            # CIS
            #
            #===========================================
            if event.run.runType == 'CIS' and self.Type==1:   
            
                # Tranform indices from original detector object to ntuple object
                part_val    = part-1
                module_val  = module-1 
                channel_val = channel
                gain_val    = gain
                self.gchan = Region_to_GlobalRegion( [part_val,module_val,channel_val,gain_val] , self.array_shape )
            
                # Check data present in event and fill calibration value
                if 'gain' not in region.GetHash():
                    print(('Run {0}: Warning: CIS event with no gain tag! region: {1}'.format(event.run.runNumber, region.GetHash())))
                    continue
                if 'calibration' not in event.data:
                    print(('Run {0}: Event Data Dictionary missing calibration key: {1}'.format(event.run.runNumber, region.GetHash())))    
                    continue
                    
                if gain:                # high gain
                    cal_val   = (event.data['calibration']/81.3669967651)
                else:                   # low gain
                    cal_val   = (event.data['calibration']/1.29400002956)

                # Check quality of region calibration and fill quality bitmask
                qual_val     = 1111111

                if self.Debug: 
                    print(('EventCIS:',part_val,module_val,channel_val,gain_val,self.gchan,cal_val))
                                    
                self.tree.quality[self.gchan]     = qual_val
                self.tree.calibration[self.gchan] = cal_val
            
            
            #===========================================
            #
            # Laser
            #
            #===========================================
            if event.run.runType == 'Las' and self.Type==2: 
            
                # Tranform indices from original detector object to ntuple object
                part_val    = part-1
                module_val  = module-1 
                channel_val = channel
                gain_val    = gain
                self.gchan = Region_to_GlobalRegion( [part_val,module_val,channel_val,gain_val] , self.array_shape )
                    
                # Check data present in event and fill calibration value
                if 'deviation' not in event.data:
                    print(('Run {0}:  Las has no deviation info for {1}'.format(event.run.runNumber, region.GetHash())))
                    continue
                
                if gain:                # high gain         
                    cal_val   = 1.+event.data['deviation']/100.
                else:                   # low gain
                    cal_val   = 1.+event.data['deviation']/100.
            
                # Check quality of region calibration and fill quality bitmask
                qual_val     = 111111

                if self.Debug: 
                    print(('EventLaser:',part_val,module_val,channel_val,gain_val,self.gchan,cal_val))
                    
                self.tree.quality[self.gchan]     = qual_val
                self.tree.calibration[self.gchan] = cal_val
                
                
            #===========================================
            #
            # High Voltage
            #
            #===========================================
            if event.run.runType == 'Las' and self.Type==5: 
                ## NOW REMEMBER -- EACH LASER RUN HAS ONLY HIGHGAIN OR LOWGAIN ##
                ## However, we read store the hvset and hv values in high and lowgain
                ## in the actual NTuples.... so here we have to write them simultaneously
                ## because otherwise none of either high or lowgain info will be written
                ## in this NTuple. IE: Only every other NTuple will contain HVset
                ## and likewise with HV
                
                            
                # Tranform indices from original detector object to ntuple object
                part_val           = part-1
                module_val         = module-1 
                channel_val        = channel
                gain_val           = gain
                self.gchanHIGH_SET = Region_to_GlobalRegion( [part_val,module_val,channel_val,1] , self.array_shape )
                self.gchanLOW      = Region_to_GlobalRegion( [part_val,module_val,channel_val,0] , self.array_shape )

# Check data present in event and fill calibration value
#                 if not event.data.has_key('deviation'):
#                     print 'Run {0}:  Las has no deviation info for {1}'.format(event.run.runNumber, region.GetHash())
#                     continue
                    
                # FILL HIGH VOLTAGE 
                hv_val = -666
                if 'HV' in event.data:       
                    hv_val   = event.data['HV']
                else:
                    if self.Debug:
                        print(('Run {0}: Laser event data missing HV info for {1}'.format(event.run.runNumber, region.GetHash())))
                        print('Filling with HV=-666')
                        hv_val  = -666
                        
                # FILL HIGH VOLTAGE SET
                hvs_val = -666
                if 'HVSet' in event.data:       
                    hvs_val  = event.data['HVSet']
                else:
                    if self.Debug:
                        print(('Run {0}: Laser event data missing HV info for {1}'.format(event.run.runNumber, region.GetHash())))
                        print('Filling with HVset=-444')
                        hvs_val = -444
            
                # Check quality of region calibration and fill quality bitmask
                qual_val     = 111111

                if self.Debug: 
                    print(('EventHV:',part_val,module_val,channel_val,gain_val,self.gchanHIGH_SET,hvs_val,self.gchanLOW, hv_val))

                self.tree.quality[self.gchanLOW]          = qual_val
                self.tree.quality[self.gchanHIGH_SET]     = qual_val
                self.tree.calibration[self.gchanLOW]      = hv_val
                self.tree.calibration[self.gchanHIGH_SET] = hvs_val
            
            #===========================================
            #
            # Cesium
            #
            #===========================================
            if event.run.runType == 'cesium' and self.Type==3: 
            
                # Tranform indices from original detector object to ntuple object
                part_val    = part-1
                module_val  = module-1 
                channel_val = channel
                gain_val    = gain
                self.gchan = Region_to_GlobalRegion( [part_val,module_val,channel_val,gain_val] , self.array_shape )
                    
                # Check data present in event and fill calibration value
                if 'calibration' not in event.data:
                    if self.Debug: 
                        print(('Run {0}: no Cs calibration data filled for {1}'.format(event.run.runNumber, region.GetHash())))
                    continue
                if not event.data['calibration']:
                    if self.Debug: 
                        print(('Run {0}: None Type Cs calibration data filled for {1}'.format(event.run.runNumber, region.GetHash())))
                    continue
                    
                cal_val   = event.data['calibration']/event.data['f_integrator_db']
            
                # Check quality of region calibration and fill quality bitmask
                qual_val     = 111111

                if self.Debug:
                    print(('EventCesium:',part_val,module_val,channel_val,gain_val,self.gchan,cal_val))
                    print(('Time/Run/Partition:', event.run.time_in_seconds, event.run.runNumber, region.GetHash()))

                self.tree.quality[self.gchan]     = qual_val
                self.tree.calibration[self.gchan] = cal_val


 
    def ProcessStop(self):            
        print("--PROCESS STOP--")
        
        self.tree.fill()
        
        print((self.dbproblems))
        # Format DB problems as TPaveText and save to TFile to be retrieved
        # as the title of the TPaveText to print in Problem Box of graph
#        dbproblems_set = set(self.dbproblems)
#        lineproblems = 'DBProblems='
#        for prob in dbproblems_set:
#            lineproblems=lineproblems+str(prob)+'|'
        
#        print lineproblems
#        problems = ROOT.TPaveText(.05,.1,.95,.8)
#        problems.AddText(lineproblems)
        
        self.outFile = ROOT.TFile.Open(str(self.OutputFileName),"RECREATE")
        
        self.mytree.Write()
#        problems.Write("DBProblems")
        self.outFile.Close()
        return
