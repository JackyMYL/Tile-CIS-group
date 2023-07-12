from src.ReadGenericCalibration import ReadGenericCalibration
from workers.noise.NoiseWorker import NoiseWorker

class ReadPedestalFile(ReadGenericCalibration, NoiseWorker):
    """
    Read pedestal values from a set of pedestal runs
    Parameters:
    - output Object of type _NoiseCommon.NoiseOutput
    - minEvents Minimum of events in original run
    - removeEvents If runs with insufficient number of events should not be processed by further workers
    """
    def __init__(self, output, minEvents=0, removeEvents=True):
        self.m_output = output
        self.m_treesByRun = {}
        self.processingDir = ReadPedestalFile.NTupleDirectory
        self.m_minEvents = minEvents
        self.m_removeEvents = removeEvents
    
    # **** Constants unlikely to change ****

    NTupleDirectory = '/afs/cern.ch/user/t/tilecali/w0/ntuples/ped'

    TreeName = 'Digi_NoiseCalib'

    # **** Implementation of Worker ****

    def ProcessStart(self):
        pass
        
    def ProcessStop(self):
        pass
        
    def ProcessRegion(self, region):
        # we only care about ADCs
        if not self._IsADC(region):
            return

        events_to_remove = []
        for event in region.GetEvents():
            runNumber = event.run.runNumber
            tree = self._OpenTree(runNumber)
            if tree:
                index = self._GetIndex(region)
                event.data['ped'] = tree.ped[index]
                event.data['hfn'] = tree.hfn[index]
                event.data['lfn'] = tree.lfn[index]
            elif self.m_removeEvents:
                events_to_remove.append(event)
        for event in events_to_remove:
            region.GetEvents().remove(event)
    
    # **** Protected methods ****

    def _IsADC(self, region):
        return 'gain' in region.GetHash()

    def _GetIndex(self, region):
        [part, mod, chan, gain] = region.GetNumber()
        index = self.get_index(region.GetType(),part, mod - 1, chan, gain)
        return index

    def _OpenTree(self, runNumber):
        # do we have the file cached?
        if runNumber in self.m_treesByRun:
            file, tree = self.m_treesByRun[runNumber]
            return tree
        
        # determine file name
        fileName = 'Digi_NoiseCalib_1_%s_Ped.root' % (runNumber)
        file, tree = self.getFileTree(fileName, ReadPedestalFile.TreeName)

        # store refs to file and tree
        self.m_treesByRun[runNumber] = [file, tree]
        
        if not file or not tree:
            self.m_output.print_log("ERROR unable to get file (%s) or tree (%s)" % (fileName, ReadPedestalFile.TreeName))
            return None

        # get data from tree
        tree.SetBranchStatus("*",0)
        tree.SetBranchStatus("ped",1)
        tree.SetBranchStatus("hfn",1)
        tree.SetBranchStatus("lfn",1)
        tree.SetBranchStatus("nEvt",1)
        tree.GetEntry(0)

        self.m_output.print_log("ReadPedestalFile opened file %s with %d events" % (fileName, tree.nEvt))
        if tree.nEvt > self.m_minEvents:
            return tree
        else:
            # Clear ref to tree
            self.m_output.print_log("ReadPedestalFile ignoring file %s with %d events, min %d events" % (fileName, tree.nEvt, self.m_minEvents))
            self.m_treesByRun[runNumber] = [file, None]
            return None


