#!/usr/bin/env python
import ROOT
import os,sys,pdb,math
import argparse
from  array import array

ROOT.gROOT.SetBatch()

#for DB
#from TileCalibBlobPython import TileCalibTools, TileBchTools
#from TileCalibBlobObjs.Classes import *
#from CaloCOndblobalgs Import Calocondtools, Calocondlogger
from TileCalibBlobPython import TileCellTools

#Create Histogram. X = 64 (Module number), Y = 16 (Channel number)
#map_diff_hist = TH2D("Diff", "Diff",0,800, 64, 0, 400, 16)
#map_diff_hist.SetXTitle("Module")
#map_diff_hist.SetYTitle("Cell")

#map_diff_hist.Draw()

class CellHelper:
  def __init__(self, run_number,folderTag):
    self.dbConn='CONDBR2'
    self.run=run_number
    self.folderTag=folderTag
    self.chan=48
    #if cell_number > -1:
      #get cell name (module, cell name)


    #open DB
    #self.db =  TileCalibTools.openDb('ORACLE', self.dbConn, 'READONLY', schema='COOLOFL_TILE')
    #if not self.db:
    #  print("plot_cellNoise_diff: Failed to open oracle database.")
    #=== get the blob for a given tag and iov
    #iov = CaloCondTools.iovFromRunLumi( self.run, self.lumi )

    #obj = folder.findObject( iov, self.chan, self.folderTag )
    #=== create CaloCondBlobFlt
    #self.blobFlt = PyCintex.gbl.CaloCondBlobFlt.getInstance(blob)
    #self.ncell=blobFlt.getNChans()
    #self.ngain=blobFlt.getNGains()
    #selfnval=blobFlt.getObjSizeUint32()
    self.hashMgr=TileCellTools.TileCellHashMgr()
    self.cellMax=5183
    
   
  def get_name(self, cell_number):
    if cell_number <0 or cell_number>self.cellMax:
      print("Error: Invalid Cell Number.")
      return
      
    partition, cellID = self.hashMgr.getNames(cell_number)
    return [ partition[:3], int(partition[3:]), cellID ]
  

#Create 2D histograms to store diff. X- is module number, Y- is cell ID.


def DrawHist(partition='LBA',gain=3, data=None, run=329588, out_dir='./', doRatio=False, tag='UPD4-22'):
  partitions = {}
  partitions['LBC']=['A-%s'%i for i in range(1,11)] + ['B-%s'%i for i in range(1,10)] + ['D-%s'%i for i in range(1,4)]
  partitions['LBA']=['A+%s'%i for i in range(1,11)] + ['B+%s'%i for i in range(1,10)] + ['D+%s'%i for i in range(1,4)]+['D*0']
  partitions['EBC']=['A-%s'%i for i in range(12,17)]+['B-%s'%i for i in range(11,16)] +['C-10']+ ['D-%s'%i for i in range(4,7)]+['E-%s'%i for i in range(1,5)]+['e4E-1', 'spC-10', 'spD-4', 'spD-40', 'spE-1', 'mbE-1']
  partitions['EBA']=['A+%s'%i for i in range(12,17)]+['B+%s'%i for i in range(11,16)] +['C+10']+ ['D+%s'%i for i in range(4,7)]+['E+%s'%i for i in range(1,5)]+['e4E+1', 'spC+10', 'spD+4', 'spD+40', 'spE+1', 'mbE+1']

  nBinX = 64
  nBinY = len(partitions[partition])
  if nBinY>30:
    nBinY = 30
  gain_names = ['LGLG', 'LGHG', 'HGLG', 'HGHG']
  map_diff_hist = ROOT.TH2F("Cell_Noise_diff_relative_%s"%partition, "%s, gain %s, RMS"%(partition, gain_names[gain]), nBinX,0,nBinX,  nBinY, 0, nBinY)
  map_diff_hist.SetXTitle("Module")
  map_diff_hist.SetYTitle("Cell")
  map_diff_hist.GetYaxis().SetTitleOffset(1.5)
  map_diff_hist.GetXaxis().SetTitleOffset(1.2)
  map_diff_hist.SetStats(0)
  
  #for i in range(64):
  #  map_diff_hist.GetXaxis().SetBinLabel(i, i+1)
  for i in range(len(partitions[partition])):
    map_diff_hist.GetYaxis().SetBinLabel(i+1, partitions[partition][i])
    #for j in range(64):
    #  map_diff_hist.Fill(j,i, ROOT.gRandom.Gaus(30.,8.))
  cell = CellHelper(run,tag)
  for iCell in data:
    cellN = iCell[0]
    cellName=cell.get_name(cellN)
    if iCell[1] != gain: continue
    if cellName[0] not in partition: continue 
    if cellName[2] not in partitions[partition]: print ("This cell is not in plot ==> %s"%cellName)
    if iCell[2] < 0.5 or iCell[2] > 1.5: print ("This cell is off the grid ==> %s, value: %s"%(cellName,iCell[2]))
    #if 'LBA' == cellName[0] and 29 == cellName[1]: print ("This cell is cool ==> %s, with value: %s, ... %s" % (cellName,iCell[2],cellName[1]-0.1))
    #if 'E-1' in cellName[2]: print ("This cell is cool ==> %s, with value: %s, ... %s" % (cellName,iCell[2],cellName[1]-0.1))    #if cellName[0] == 'EBC' and cellName[1]==18: print ("This cell is cool ==> %s, with value: %s, ... %s" % (cellName,iCell[2],cellName[1]-0.1))
    map_diff_hist.Fill(cellName[1]-0.1, cellName[2], iCell[2])

  canvas=ROOT.TCanvas('can','', 900, 800)
  ROOT.SetOwnership(canvas, False)
  canvas.cd()
  #nb=21;
  #palette = array('i', [0, ROOT.kBlue-10, ROOT.kBlue-7, ROOT.kBlue-4, ROOT.kBlue, ROOT.kGreen-6, ROOT.kGreen-3, ROOT.kGreen, ROOT.kGreen+3, ROOT.kCyan-7, ROOT.kCyan-3, ROOT.kCyan+2, ROOT.kMagenta-7, ROOT.kMagenta-4, ROOT.kMagenta, ROOT.kMagenta+1, ROOT.kYellow-7, ROOT.kYellow+1, ROOT.kRed-4, ROOT.kRed])
  if doRatio:
    #level = array('d', [i*.001 for i in range(475,1525,50)])
    #level.append(0)
    #level.append(2)
    #level.sort()
    #pdb.set_trace()
    map_diff_hist.SetMaximum(1.5)
    map_diff_hist.SetMinimum(0.5)
    #palette = array('i', [ROOT.kBlue+4, ROOT.kBlue+2,ROOT.kBlue, ROOT.kBlue-4, ROOT.kBlue-7, ROOT.kBlue-9, ROOT.kBlue-10, ROOT.kYellow-9, ROOT.kYellow-4, ROOT.kGreen, ROOT.kGreen+1, ROOT.kGreen+2, ROOT.kYellow+1, ROOT.kOrange, ROOT.kOrange-3, ROOT.kOrange+2, ROOT.kRed-3, ROOT.kRed+1, ROOT.kRed+3, ROOT.kRed+4, ROOT.kBlack,])
    #print(len(level), len(palette))
    #ROOT.gStyle.SetPalette(21, palette)
  else:
    #level = array('d', [i for i in range(0, 110,10)])
    map_diff_hist.SetMaximum(200)
    #palette = array('i', [0, ROOT.kBlue-10, ROOT.kBlue-9, ROOT.kBlue-7, ROOT.kBlue-4, ROOT.kBlue, ROOT.kYellow-9, ROOT.kYellow-7, ROOT.kYellow, ROOT.kYellow+1, ROOT.kRed-10, ROOT.kRed-9, ROOT.kRed-6, ROOT.kRed-7, ROOT.kRed-4, ROOT.kRed-3, ROOT.kRed-1, ROOT.kRed+1, ROOT.kRed+3, ROOT.kRed+4])
    #ROOT.gStyle.SetPalette(20, palette)
  #NRGBs = 6
  #NCont = 999
  #stops = array('d', [0.00, 0.1, 0.34, 0.61, 0.84, 1.00 ])
  #Red = array('d',[0.99, 0.0, 0.00, 0.87, 1.00, 0.51 ])
  #Green = array('d', [0.00, 0.0, 0.81, 1.00, 0.20, 0.00])
  #Blue = array('d', [0.99, 0.0, 1.00, 0.12, 0.00, 0.00])
  #ROOT.TColor.CreateGradientColorTable(NRGBs, stops, Red, Green, Blue, NCont)
  #ROOT.gStyle.SetNumberContours(NCont)
  canvas.SetMargin(0.12,0.13,0.1,0.1)
  save_name=map_diff_hist.GetName()
  #map_diff_hist.SetContour(21,level)
  #map_diff_hist.SetMinimum(10)
  map_diff_hist.Draw('COLZ')
  canvas.Print('%s/%s_gain%s_%i.pdf'%(out_dir,save_name, gain, run))
  #pdb.set_trace()
  del (canvas)

def get_rms_effective(ratio, sigma1, sigma2):
  rms_eff = math.sqrt((1-ratio) * sigma1**2 + ratio * sigma2**2)
  return rms_eff

def get_relative_diff_from_file(fileName, doRatio, doRMSeff, tag, run):
  lines=[]
  #Read data from a file. The file contains cell_number, gain, cell noise value, and difference. 
  with open(fileName) as f:
    lines1 = f.readlines()
    print(lines1[0])
  for line in lines1:
    lines.append([line[0:4],line[5],line[12:13],line[14:22],line[23:25],line[26:34],line[35:39],line[40:48],line[49:60],line[61:-1]])
  #lines = [line.lstrip(' ').rstrip(' \n').replace('\t','').split(' ') for line in lines]
  #print lines[483:]
  #lines = [filter(None, line) for line in lines]
  print(lines[0])
  #Data is in [cell_number, gain, relative_difference]
  #print lines
  #print(len(lines))
  #print(lines)
  if doRatio:
    diff_re = [[int(iLine[0]), int(iLine[1]), float(iLine[6])/float(iLine[4])] for iLine in lines]
    #for iLine in lines:
     # diff_re = []
      #try:
       # diff_re.append([int(iLine[0]), int(iLine[1]), float(iLine[9])/float(iLine[3])])
      #except ZeroDivisionError:
       # diff_re.append([int(iLine[0]), int(iLine[1]), float(9999)])
  elif doRMSeff:
    print("diff_re = [[int(iLine[0]), int(iLine[1]), get_rms_effective(ratio=float(iLine[29]),sigma1=float(iLine[13]),sigma2=float(iLine[21]))/float(iLine[5])] for iLine in lines]")
    cell = CellHelper(run,tag)
    diff_re = []
    for iLine in lines:
      try:
        diff_re.append([int(iLine[0]), int(iLine[1]), get_rms_effective(ratio=float(iLine[29]),sigma1=float(iLine[13]),sigma2=float(iLine[21]))/float(iLine[5])])
      except IndexError:
        diff_re.append([int(iLine[0]), int(iLine[1]), 3.])
        print("IndexError:", cell.get_name(int(iLine[0])), iLine[1])
        #print "IndexError+1:", cell.get_name(iLine[0]+1), iLine[1]
      except ZeroDivisionError:
        diff_re.append([int(iLine[0]), int(iLine[1]), 0.])
        print("ZeroDivisionError+1:", cell.get_name(int(iLine[0])), iLine[1])
  else:
    diff_re = [[int(iLine[0]), int(iLine[1]), float(iLine[7])] for iLine in lines]
#print diff_re
  return diff_re

def main():
  descrip = "python $TUCS/macros/noise/MakeCellNoiseUpdate.py --run=<run mumber> --db_use_oracle --db_output_file=tile_cell_noise_<run number>.sqlite \n"+\
  "\n and\n" + \
  "ReadCellNoiseFromCoolCompare.py --folder=/TILE/OFL02/NOISE/CELL --schema=OFL2 --schema2=\"sqlite://;schema=tile_cell_noise_<run number>.sqlite;dbname=CONDBR2\" --tag2=UPD4 --tag=UPD4 --run2=<run number> --run=99999999 --maxdiffpercent=10 --maxdiff=0 --brief --index=0 |grep v1 |& tee ReadCellNoiseFromCoolCompare_summary_<run number>.txt"
  
  print("\n########## instruction ########")
  print("Run this two command if you haven't yet run them:")
  print("%s\n"%descrip)

  parser = argparse.ArgumentParser(description="plot cell noise difference!", prog='plot_cellNoise_diff.py', usage='%(prog)s [options]')
  parser.add_argument('--inFile', default='ReadCellNoiseFromCoolCompare_summary_329364_brief.txt' ,dest='inFile', help='Log file from ReadCellNoiseFromCoolCompare.py')
  parser.add_argument('--output_dir', default='./', dest='output_dir', help='Redirect output directory.')
  parser.add_argument('--partitions', default=['LBA', 'LBC', 'EBA', 'EBC'], nargs='*', help='Partitions: LBA,LBC,EBA,EBC')
  parser.add_argument('--gains', default=[0, 1, 2, 3], nargs='*', help='Combination of gains: 0,1,2,3')
  #parser.add_argument('--index', default=[0], nargs='*', help='Parameter indices: 0,1,2,3,4')
  parser.add_argument('--run', default=999999, type=int, dest='run', help='Run number')
  parser.add_argument('--doRatio', action='store_true', default=False, dest='doRatio', help='Plot Ratio instead of relative difference')
  parser.add_argument('--tag', default='RUN2-UPD4-22', type=str, dest='tag', help='end of tag, RUN2-UPD4-22 e.g.')
  parser.add_argument('--exclude_bad_channels', action='store_true', default=False, help='Exclude bad channels', dest='excludeBadChannels')
  parser.add_argument('--bad_channel_list', required=False, help='ReadBchFromCool.py |grep BAD cut')
  parser.add_argument('--doRMSeff', action='store_true', default=False, dest='doRMSeff', help='Plot RMS_eff/RMS')
  #Patch_bad_grp.add_argument('--do_not_patch_bad_values', action='store_false',
  #                         help='Do not apply patch to bad values from data', dest='patchBadValues')
  #argparser.set_defaults(patchBadValues=False)
  args = parser.parse_args()
  tag = 'TileOfl02NoiseCell-'+ args.tag
  try:
    if args.help:
      print(main.__doc__)
  except AttributeError:
    True
  #Use log file from ReadCellNoiseFromCoolCompare.py script.
  #tmpFileName='ReadCellNoiseFromCoolCompare_summary_329364_brief.txt'

  if args.excludeBadChannels:
    output.print_log("Use bad channel schema %s with tag %s." % (args.badChannelSchema, args.badChannelTag))
    processList.append(ReadBadChFromCool(schema=args.badChannelSchema, tag=args.badChannelTag, Fast=False, storeADCinfo=False))


  #Data is in [cell_number, gain, relative_difference]
  data_diff_re = get_relative_diff_from_file(args.inFile, args.doRatio, args.doRMSeff, tag=tag, run=args.run)
  
  ratioPlot = False
  if args.doRatio or args.doRMSeff:
    ratioPlot = True
  
  #Plot for each partition and gain.
  for partition in args.partitions:
    for gain in args.gains:
      DrawHist(partition, gain, data_diff_re, args.run, args.output_dir, ratioPlot, tag=tag)


if __name__== '__main__':
  main()

