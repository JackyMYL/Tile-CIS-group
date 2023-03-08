# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# March 04, 2009
#

import os
from ROOT import TFile
from src.GenericWorker import *

class ReadGenericCalibration(GenericWorker):
    "The Generic Calibration Template"

    tfile_cache = {}
    processingDir = 'tmp'
    
    def getFileTree(self, fileName, treeName):
        f, t = [None, None]

        if self.processingDir+fileName in self.tfile_cache:
            f, t = self.tfile_cache[self.processingDir+fileName]
  #      elif self.tfile_cache.has_key(self.processingDir+fileName) and not f.IsOpen():
  #          if os.path.exists(os.path.join(self.processingDir, fileName)) or 'rfio:/' == self.processingDir[0:6]:
  #              f = TFile.Open(os.path.join(self.processingDir, fileName), "read")

  #          if not f:
  #              return [None, None]

  #          t = f.Get(treeName)
  #          if not t:
  #              print "Tree failed to be grabbed: " + fileName
  #          print 'found tree %s' % treeName
  #          f.GetListOfKeys().Print('all')
        else:
            if os.path.exists(os.path.join(self.processingDir, fileName)) or 'rfio:/' == self.processingDir[0:6]:
                f = TFile.Open(os.path.join(self.processingDir, fileName), "read")

            if not f:
                return [None, None]
            
            t = f.Get(treeName)
            if not t:
                print(("Tree failed to be grabbed: " + fileName))
                return [None, None]

            self.tfile_cache[self.processingDir+fileName] = [f, t]
            # print 'found tree %s' % treeName
            # f.GetListOfKeys().Print('all')
        return [f, t]
