#!/usr/bin/env python
# Based on ReadFloatFromCaloCool.py by Carlos.Solans <Carlos.Solans@cern.ch>
# Each Tile cell has 5 values stored in COOL.
# The first two values are the RMS of a sigle gaussian model of the electronic noise
# and the pile-up noise normalized at 10^33cm-2s-1, (backwards compatibility)
# The next three values are used for a two gaussian model. 
# These are: ratio between first and second gaussian, RMS of the first gaussian, and RMS of the second gaussian

import getopt,string
from TileCalibBlobPython import TileCalibTools
from TileCalibBlobObjs.Classes import *
from src.oscalls import *
import cell_index_cool
import pdb

runnumbers = [220000]#[199825, 200561, 201324, 202656, 205495, 206701, 208079, 208818, 210167, 210232, 211208, 212375]
#run    = 210167
lumi   = 0
idx    = 0

folderPath1='/TILE/OFL02/NOISE/CELL'
folderPath2='/TILE/OFL02/NOISE/CELL'
folderTag1='TileOfl02NoiseCell-PileUp-Dt75-OFC0-HVCorr-02'
folderTag2='TileOfl02NoiseCell-PileUp-Dt75-OFC0-HVCorr-02'
from src.oscalls import *

import os,sys
try:
   # ROOT5
   import PyCintex
except:
   # ROOT6
   import cppyy as PyCintex
   sys.modules['PyCintex'] = PyCintex
from PyCool import cool
from CaloCondBlobAlgs import CaloCondTools, CaloCondLogger

#=== get a logger
log = CaloCondLogger.getLogger("ReadCellNoise")

#=== Read from COOL server:
string1 = 'sqlite://;schema=%s;dbname=OFLP200' % os.path.join(getResultDirectory(),"caloSqlite_data2p76TeV.db")
db1 = CaloCondTools.openDbConn(string1)
log.info("Initializing folder %s with tag %s" % (folderPath1, folderTag1))
folder1 = db1.getFolder(folderPath1)

string2 = 'sqlite://;schema=%s;dbname=OFLP200' % os.path.join(getResultDirectory(),"caloSqlite_MC_28Feb2013.db")
db2 = CaloCondTools.openDbConn(string2)
log.info("Initializing folder %s with tag %s" % (folderPath2, folderTag2))
folder2 = db2.getFolder(folderPath2)

#=== get reader
#reader=TileCalibTools.TileBlobReader(db1,folderPath1,folderTag1)

#=== get the blob for a given tag and iov
for run in runnumbers:
    iov = CaloCondTools.iovFromRunLumi( run, lumi )

    coolchannel = 48 # represents Tile
    obj1 = folder1.findObject( iov, coolchannel, folderTag1 )
    blob1 = obj1.payload()[0]
    obj2 = folder2.findObject( iov, coolchannel, folderTag2 )
    blob2 = obj2.payload()[0]

#=== create CaloCondBlobFlt
    blobFlt1 = PyCintex.gbl.CaloCondBlobFlt.getInstance(blob1)
    blobFlt2 = PyCintex.gbl.CaloCondBlobFlt.getInstance(blob2)

#=== retrieve data from the blob
#hash  = 0 # 0..5183 - Tile hash
#iGain = 0 # 0..3    - four Tile cell gains: -11, -12, -15, -16
#idx   = 0 # 0..4    - electronic or pile-up noise or 2-G noise parameters

    nofbad = 0
    goodnumber = 0
    badlist = []
    the_cell=-1
    for cell in range(5184):
#        for adc in range(4):
            adc = 2
            noise1 = blobFlt1.getData(cell, adc, 0)
            noise2 = blobFlt2.getData(cell, adc, 0)
            if noise1 != 0:
                noisechange = (noise2-noise1)/noise1
            else:
                noisechange = 0
            #    noisechange = noise2-noise1 #CHANGE
#                if noisechange > 0.001:
#                    print "noise1 = 0, noisechange = ", noisechange
#            if noise2==0: 
            if noise2>0 and noise1>0 and abs(noisechange)>0.2: #or pilechange > 0.001:
                prev_cell = the_cell
                the_cell = cell
                if prev_cell != the_cell:
                    nofbad = nofbad+1
                    badlist.append(cell)
                    log.info( "Noise cell %d gain %d\t" % ( cell, adc) +
                    "RMS-1 %f\t" % blobFlt1.getData(cell, adc, 0)+
                    #"pile-up-1%f\t" % blobFlt1.getData(cell, adc, 1) +
                    "RMS-2 %f\t" % blobFlt2.getData(cell, adc, 0))
                   #"pileup-2 %f\t" % blobFlt2.getData(cell, adc, 1) +
                  #"NoiseChange %f\t" % noisechange )
    print "run = ", run, "number of bad cells = ", nofbad

    IDlist=[]
    Alist = []
    BClist = []
    Dlist = []
    Elist = []
    for badind in range(len(badlist)):
        badel = badlist[badind]
        myID = cell_index_cool.cellToHwid((badel,0))
        cellLetter = cell_index_cool.channelToCelltype(myID)
        IDlist.append(myID)
        print "myID=", myID
        if cellLetter=='A':
                Alist.append(myID)
        elif cellLetter=='BC':
                BClist.append(myID)
        elif cellLetter=='D':
                Dlist.append(myID)
        elif cellLetter=='E':
                Elist.append(myID)
                

print "nofbad = ", nofbad
print "Alist length: ", len(Alist)
print "BClist length: ", len(BClist)
print "Dlist length: ", len(Dlist)
print "Elist length: ", len(Elist)
#print "badlist = ", badlist
#myID = cell_index_cool.cellToHwid((badlist[2],0))
#print "myID =", myID

##=== close DB
db1.closeDatabase()
db2.closeDatabase()
