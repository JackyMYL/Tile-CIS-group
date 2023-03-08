# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# March 04, 2009
#

from src.ReadGenericCalibration import *
from src.region import *
from src.oscalls import *
import logging, getopt
from TileCalibBlobPython import TileCalibTools, TileBchTools
from TileCalibBlobPython.TileCalibTools import MINRUN, MINLBK, MAXRUN, MAXLBK
from TileCalibBlobObjs.Classes import *

class ReadChanStat(ReadGenericCalibration):
    "The ChanStat Reader"

    use_oracle = True
    db = None
    mgr = None
    noisePrbs = [TileBchPrbs.LargeLfNoise,TileBchPrbs.LargeHfNoise,TileBchPrbs.VeryLargeHfNoise,TileBchPrbs.CorrelatedNoise]
    def __init__(self,type='physical',schema='COOLOFL_TILE/CONDBR2',folder='/TILE/OFL02/STATUS/ADC'):
        self.type = type
        self.schema = schema
        self.folder = folder
    
        if "sqlite" in schema:
            splitname=schema.split("=")
            if not "/" in splitname[1]: 
                splitname[1]=os.path.join(getResultDirectory(), splitname[1])
                self.schema="=".join(splitname)


    def ProcessStart(self):
        logger = getLogger("TileCalibTools")
#        logger.setLevel(logging.ERROR)

        self.mgr = {}
        
        self.db = TileCalibTools.openDbConn(self.schema, 'READONLY')

        global run_list
        
        if not self.db:
            print(self.__class__.__name__+": Failed to open a connection to the COOL ORACLE database")
        else:
            self.folderTag = TileCalibTools.getFolderTag(self.db, self.folder, 'CURRENT')
            # Setup manager for each run that will be read
            logger = getLogger("TileBchMgr")
            logger.setLevel(logging.ERROR)        
            for run in sorted(run_list):
                self.mgr[run.runNumber] = TileBchTools.TileBchMgr()
                print("Intializing DB for run: ",run)
                self.mgr[run.runNumber].initialize(self.db, self.folder, self.folderTag,(run.runNumber,0))

        if not self.mgr:
            print(self.__class__.__name__+": Failed to create a Bad Channel manager from the DB")
            
    def ProcessStop(self):
        if self.db:
            self.db.closeDatabase()

    def ProcessRegion(self, region):
        if not self.db or not self.mgr:
            print("DB not setup, exiting...")
            return

        newEvents = set()
        for event in region.GetEvents():

            if '_t' in region.GetHash():

                fracMasked = self.GetCellStatus(region,event)
                event.data['fracMasked'] = fracMasked

#                    if abs(fracMasked - 1.0) < 10e-4:
#                        event.data['isBad'] = True
#                    else:
#                        event.data['isBad'] = False
                event.data['isBad'] = fracMasked
                if abs(fracMasked - 1.0) < 10e-4:
                    event.data['isMasked'] = True
                else:
                    event.data['isMasked'] = False




                    
                fracNoisy = self.IsCellNoisy(region,event)
                event.data['isNoisy'] = fracNoisy

            elif 'gain' in region.GetHash():
                # Access mgr specific to run number (cached at start of job)
                status   = self.GetAdcStatus(region,event)
                problems = self.GetAdcProblems(region,event)

                isNoisyDetail = False
                if len(problems) != 0:
                    for prbCode in sorted(problems.keys()):
                        if prbCode in self.noisePrbs and not status.isNoisy():
                            print("Disagreement for Noise Flag: ", problems[prbCode])
                            isNoisyDetail = True
                            
                event.data['isBad']   = status.isBad()
                event.data['isNoisy'] = status.isNoisy() or isNoisyDetail
                event.data['problems']= problems
        	


    def GetCellStatus(self,cell,event):
        '''Determines Cell status from status of children.  Returns fraction of cell (of 4 ADCs) that is bad.'''
        nAdc = 0.0
        cellStatus = 0.0
        for ch in cell.GetChildren('readout'):
            cellStatus += self.GetChStatus(ch,event)
            nAdc += 2
            
        return float(cellStatus/nAdc)

    def GetChStatus(self,ch,event):
        '''Determines Ch status from status of children.  Returns fraction of chan (of 2 ADCs) that is bad.'''
        chStatus = 0
        for adc in ch.GetChildren('readout'):
            if self.GetAdcStatus(adc,event).isBad(): chStatus += 1
        return chStatus

    def GetAdcStatus(self,adc,event):
        '''Determines Adc status from reading Db'''
        [part, mod, ch, gain] = adc.GetNumber()
        # Access mgr specific to run number (cached at start of job)



        return self.mgr[event.run.runNumber].getAdcStatus(part, mod-1, ch, gain)

    def IsCellNoisy(self,cell,event):
        '''Determines Cell isNoisy status from children.  Returns fraction of cell (of 4 ADCs) that is noisy.'''
        nAdc = 0.0
        cellNoisy = 0.0
        for ch in cell.GetChildren('readout'):
            cellNoisy += self.IsChNoisy(ch,event)
            nAdc += 2
            
        return float(cellNoisy/nAdc)

    def IsChNoisy(self,ch,event):
        '''Determines Ch isNoisy status from children.  Returns fraction of chan (of 2 ADCs) that is noisy.'''
        chNoisy = 0
        for adc in ch.GetChildren('readout'):
            if self.GetAdcStatus(adc,event).isNoisy(): chNoisy += 1
        return chNoisy

    def GetAdcProblems(self,adc,event):
        '''Returns Adc problems from Db'''
        [part, mod, ch, gain] = adc.GetNumber()
        # Access mgr specific to run number (cached at start of job)
        return self.mgr[event.run.runNumber].getAdcProblems(part, mod-1, ch, gain)
