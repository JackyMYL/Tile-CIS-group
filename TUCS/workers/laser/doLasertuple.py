from src.GenericWorker import *
from src.oscalls import *
from src.region import *
from src.ReadGenericCalibration import *

#from ROOT import *
import ROOT

import time

#class doLasertuple(GenericWorker):
class doLasertuple(ReadGenericCalibration):
    " This worker does a rootuple of laser data for one run "    
        
    def __init__(self, runNumber):
        self.runNumber = runNumber

        #self.fo = TFile.Open("output_%d.root"%(self.runNumber),"recreate")
        #self.to = ("ZeTree", "ZeTree")

        #self.fo, self.to = self.createFileTree("output_%d.root"%(self.runNumber), "Laser_rootuple")
        self.fo, self.to = self.createFileTree(os.path.join(getResultDirectory(),"output.root"), "ZeTree")

        self.timestamp = array('i',[ 0 ])
        self.f_laser   = array('d',[ 0 ])
        self.partition = array('i',[ 0 ])
        self.module    = array('i',[ 0 ])
        self.channel   = array('i',[ 0 ])
        self.filter    = array('i',[ 0 ])
        self.HV        = array('i',[ 0 ])
        self.Status    = array('i',[ 0 ])
        self.isBad     = array('i',[ 0 ])
        self.f_fiber   = array('d',[ 0 ])

        self.PMTool   = LaserTools()

        self.to.Branch('Date',self.timestamp,'Date/I')
        self.to.Branch('Measure',self.f_laser,'Measure/D')
        self.to.Branch('Partition',self.partition,'Partition/I')
        self.to.Branch('Module',self.module,'Module/I')
        self.to.Branch('Canal',self.channel,'Canal/I')
        self.to.Branch('MeasureType',self.filter,'MeasureType/I')
        self.to.Branch('HV',self.HV,'HV/I')
        self.to.Branch('Status',self.Status,'Status/I')
        self.to.Branch('f_fiber',self.f_fiber,'f_fiber/D')

    def ProcessRegion(self, region):

        count_lba = 0
        count_lbc = 0
        count_eba = 0
        count_ebc = 0

        for event in region.GetEvents():

            #print 'region',event.data['region']

           ##  if event.data['region'].find('LBA')!=-1:
##                 count_lba+=1
##             elif event.data['region'].find('LBC')!=-1:
##                 count_lbc+=1
##             elif event.data['region'].find('EBA')!=-1:
##                 count_eba+=1
##             elif event.data['region'].find('EBC')!=-1:
##                 count_ebc+=1
##             else:
##                 print 'problem, region :', event.data['region']
            

            self.timestamp[0] = event.run.time_in_seconds 
            #self.f_laser[0]   = event.data['deviation']
            if 'f_laser' in event.data:
                self.f_laser[0]   = (1/event.data['f_laser']-1)*100.
            # [self.partition[0], self.module[0], self.channel[0], w] = self.PMTool.GetNumber(event.data['region'])
            [self.partition[0], self.module[0], self.channel[0], w] = event.region.GetNumber()

            self.partition[0] = self.partition[0]-1
            self.module[0] = self.module[0]-1
            self.filter[0] = event.run.data['wheelpos']
            self.HV[0] = event.data['HV']
            self.Status[0] = event.data['status']

            if event.data['status']:
                self.Status[0] = 1
            else:
                self.Status[0] = 0
            
            #self.isBad[0] = event.data['isBad']
            #if self.f_laser[0]>100 or self.f_laser[0]<-100:
            print('deviation :',self.f_laser[0],'status :',self.Status[0],'region :', event.region.GetNumber())

            if 'fiber_var' in event.data:
                self.f_fiber[0] = event.data['fiber_var']
            self.to.Fill()

        #print 'LBA :',count_lba,'LBC :',count_lbc,'EBA :',count_eba,'EBC :',count_ebc

    def ProcessStop(self):

        #self.to.Fill();
        self.fo.Write()
        self.fo.Close()

