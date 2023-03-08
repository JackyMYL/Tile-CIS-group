############################################################
#
# ReadTimeFromCool.py
#
############################################################
#
# Author: Henric
#
# February, 2012
#
# Goal: Get time info from COOL
# 
#

from src.ReadGenericCalibration import *
from src.region import *
from src.oscalls import *

# For reading from DB
from TileCalibBlobPython import TileCalibTools
from TileCalibBlobObjs.Classes import *

# For turning off annoying logging
import logging
from TileCalibBlobPython.TileCalibLogger import TileCalibLogger, getLogger
#getLogger("ReadCalFromCool").setLevel(logging.DEBUG)

class ReadTimeFromCool(ReadGenericCalibration):
    "Read database timing constants from COOL"

    ## the default value of this tag is left hardcoded for now so this upgrade
    ## does not break for other systems who haven't implemented the leaf tag code
    ## however this is temporary, and non-CIS systems should update the code to implement
    ## the leaf tagging. See the CIS parts of this code for examples.
    
    def __init__(self, schema='COOLOFL_TILE/CONDBR2', folder='/TILE/OFL02/TIME/CHANNELOFFSET/PHY', tag = 'UPD4', runNumber=1000000000, verbose=False):
        self.schema    = schema
        self.folder    = folder
        self.tag       = tag
        self.runNumber = runNumber
        self.verbose = verbose
        
        if "sqlite" in schema:
            splitname=schema.split("=")
            if not "/" in splitname[1]: 
                splitname[1]=os.path.join(getResultDirectory(), splitname[1])
                self.schema="=".join(splitname)


    def ProcessStart(self):

        # Turn off the damn TileCalibTools startup prompt. grr.
        #getLogger("TileCalibTools").setLevel(logging.ERROR)

        ######
        ### Open up a DB connection
        ######
        

        self.dbConstants = TileCalibTools.openDbConn(self.schema, 'READONLY')
        
        if not self.dbConstants:
            raise IOError("ReadCalFromCOOL: Failed to open a database connection, this can be an AFS token issue"            )

        tag = TileCalibTools.getFolderTag(self.dbConstants, self.folder, self.tag)
        
        print(("Creating Blob reader for\n foler: %s\n tag:  %s\n" % (self.folder, tag)))  
        self.blobReader = TileCalibTools.TileBlobReader(self.dbConstants, self.folder, tag)


    def ProcessStop(self):

        if self.dbConstants:
            self.dbConstants.closeDatabase()

    def ProcessRegion(self, region):
        if len(region.GetNumber())!= 4:
            return
        
        [ros, module, channel, gain] = region.GetNumber()
        drawer = module-1
        
        
        for event in region.GetEvents():            
            if self.runNumber == 1000000000:
                runNumber = event.run.runNumber
            else:
                runNumber = self.runNumber
            
            flt = self.blobReader.getDrawer(ros, drawer, (runNumber, 0))  # DB module numbers start from 0
            if not flt: # Sanity check
                print(('No DB info !!! for run ', runNumber))
                continue

            event.data['TimeOffset'] = flt.getData(channel, gain, 0)
            #print event.data['TimeOffset']
