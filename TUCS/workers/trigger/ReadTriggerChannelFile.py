# ReadTriggerChannelFile.py
# Class for reading Trigger channels from ntuple
# Author: Bernardo Peralva (bernardo@cern.ch)
# Editor: Peter Thomas Camporeale (peter.thomas.camporeale@cern.ch)
from __future__ import print_function
from src.ReadGenericCalibration import *
from src.region import *
import random
import time

class ReadTriggerChannelFile(ReadGenericCalibration):
    '''Class to read trigger channels from calibration ntuple'''

    def __init__(self,processingDir='/afs/cern.ch/user/t/tilecali/w0/ntuples/l1calo',load_autocr=True):
        self.processingDir = processingDir
        self.ftDict = {} # Each element is a [TTree, TFile]
        self.load_autocr = load_autocr
        self.samples     = set()
        self.run_list    = set()


    def get_index(self, ros, mod, chan):
        return ros  *64*48\
            + mod      *48\
            + chan

    def ProcessStart(self):
        pass
        
    def ProcessStop(self):
        pass
        
    def ProcessRegion(self,region):
        if region.GetEvents() == 0:
            return
        newevents = set()
        if 'gain' not in region.GetHash():
            for event in region.GetEvents():
                if event.run.runType != 'staging':
                    newevents.add(event)
            region.SetEvents(newevents)
            return

        for event in region.GetEvents():
            f, t = self.getFileTree('tileCalibL1Calo_%s_%s.%s.root' % (event.run.runNumber,'L1Calo',0), 'h3000')
            if [f, t] == [None, None]:
                f, t = self.getFileTree('tileCalibL1Calo_%s_%s.%s.root' % (event.run.runNumber,'L1Calo','calibration_L1CaloPmtScan'), 'h3000')
            if [f, t] != [None, None]:
                self.run_list.add(event.run)
                self.samples.add(event)

            if [f, t] == [None, None]:
                print('File missing for run: ',event.run.runNumber)
                return False
            else:
                self.ftDict[event.run.runNumber] = [f, t]
                #print f, t

        # Either lowgain or highgain should work
        #if 'lowgain' in region.GetHash():
                # Setup header for file (by run number)

        for run in self.run_list:
            run_number = run.runNumber
            file_string = 'events'+str(run_number)+'.txt'
            #print(f'file_string = {file_string}')
            #print(type(file_string))
            with open(file_string, 'w') as f:
                f.write('#  ')
                f.write('meanTile   ')
                f.write('rmsTile    ')
                f.write('ietaTile   ')
                f.write('ipmtTile   ')
                f.write('nEvtTile   ')
                f.write('meanL1Calo ')
                f.write('rmsL1Calo  ')
                f.write('ietaL1Calo ')
                f.write('iphiL1Calo ')
                f.write('ipmtL1calo ')
                f.write('nEvtL1Calo ')
                f.write('\n')

            for event in region.GetEvents():

                # Get data from noise tree
                [f, t] = self.ftDict[run.runNumber]
                t.GetEntry(0)

                # Get indices
                [part, mod, chan, gain] = region.GetNumber()
            
                index = self.get_index(part, mod - 1, chan)
                #print index
            
                event.data['meanTile']     =  t.meanTile[index]
                event.data['rmsTile']      =  t.rmsTile[index]
                event.data['ietaTile']     =  t.ietaTile[index]
                event.data['iphiTile']     =  t.iphiTile[index]
                event.data['ipmtTile']     =  t.ipmtTile[index]
                event.data['nEvtTile']     =  t.nEvtTile[index]
                event.data['meanL1Calo']   =  t.meanL1Calo[index]
                event.data['rmsL1Calo']    =  t.rmsL1Calo[index]
                event.data['ietaL1Calo']   =  t.ietaL1Calo[index]
                event.data['iphiL1Calo']   =  t.iphiL1Calo[index]
                event.data['ipmtL1Calo']   =  t.ipmtL1Calo[index]
                event.data['nEvtL1Calo']   =  t.nEvtL1Calo[index]

                event.data['DACvalue']     =  t.DACvalue
        
                newevents.add(Event(run,event.data))
                # Write each event to the text file corresponding to the run
                with open(file_string, 'w') as f:
                    f.write(str(event.data))
                    f.write('\n')
            

            region.SetEvents(newevents)

