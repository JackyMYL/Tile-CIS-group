#!/usr/bin/env python
# Author : Sam Meehan
#  April 2012
#
# python macros/CombinedCalibFromNTuple.py --date 2011-01-15 --enddate 2012-05-01 --region LBA_m33_c10 --cis --laser --cesium

import argparse
import os.path
import time
import sys
from DataSets import getContents

import array
import ROOT
from ROOT import TCanvas, TPad, TFile, gDirectory, TGraph, TGraphErrors, TLegend



################# Global Arguments #####################################################

# FIX MEEEEEEEE!!!!  This should not be pointing to a local directory but to a more general directory

NTupleDirectory = '/afs/cern.ch/user/t/tilecali/w0/ntuples/common/'

################## Global Functions ###################################################
NPart=4
NMod=64
NChan=48
NGain=2
ravelshape = [NPart,NMod,NChan,NGain]

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
    
def ParseRegion(region):
    print "regionlength ",region
    splitregion = region.split('_')
    print splitregion
    
    # partition
    part=0
    if splitregion[0]=='LBA': part=0
    if splitregion[0]=='LBC': part=1
    if splitregion[0]=='EBA': part=2
    if splitregion[0]=='EBC': part=3
    
    # module
    module = 0
    module = int(splitregion[1].replace('m',''))

    # channel
    channel = 0
    channel = int(splitregion[2].replace('c',''))
    
    # gain
    gain = 0
    
    return part,module,channel
    
def GetDate(epochtime):

    t = time.gmtime(epochtime)

    print "Getting time: ",t[0]-2008,t[1],t[2],t[3]

    outputtime = t[0] + t[1]/12.0 + t[2]/365.0 + t[3]/8760.0  # years*12 + months + days/30

    print 'Time of Run: ',outputtime

    return outputtime

def GetLowBoundDate(datestring):
    year  = int(datestring.split('-')[0])
    month = int(datestring.split('-')[1])
    day   = int(datestring.split('-')[2])

    outputtime = year + month/12 - 0.1  # years*12 + months + days/30

    print 'StartDate: ',outputtime
    return outputtime
    
def GetHighBoundDate(datestring):
    year  = int(datestring.split('-')[0])
    month = int(datestring.split('-')[1])
    day   = int(datestring.split('-')[2])

    outputtime = year + month/12 + 0.1  # years*12 + months + days/30

    print 'EndDate: ',outputtime
    return outputtime
    
################# Plotting Tools #####################################################
class CombinedPlot():
    "Combined plotting class"

    def __init__(self, outputname='defaultname', cis=False, laser=False, cesium=False):
        self.name       =  outputname
        self.plotcis    =  cis
        self.plotlaser  =  laser
        self.plotcesium =  cesium
               
    def Print(self):
        print "=========="
        print "Variables:"
        print self.name
        print self.plotcis
        print self.plotlaser
        print self.plotcesium
        print "=========="
        
    def MakeGraph(self, type='default', region='LBA_m01_c01', gainvar=0):
        path='.'
        
        if type=='CIS':
            path = NTupleDirectory+'CIS'
        elif type=='Las':
            path = NTupleDirectory+'Las'
        elif type=='cesium':
            path = NTupleDirectory+'cesium'
        else:
            print 'You may not have correctly specified the system to process ...'
          
        # make list of all root files in the systems directory
        # NEED FIX HERE --- use this step to limit dates of run numbers loaded
        files = getContents(path)
        goodfiles = []
        for file in files:
            print file
            splitfile = file.split('.')
            # check that we only try to access root files
            if splitfile[ len(splitfile)-1 ]=='root':
                goodfiles.append(file)
                
        [part,module,channel] = ParseRegion(region)
        gain=gainvar

        global_channel = Region_to_GlobalRegion( [part,module,channel,gain] , ravelshape )
        print 'Region: ',part,module,channel,gain,global_channel
        
        # loop through files
        # open file
        # read run=x, calibration=y
        # ex=0,ey=0
        # count number of points

        count=0
        nruns = len(goodfiles)   
        
        xx = [0 for runs in range(nruns)]
        yy = [0 for runs in range(nruns)]
        
        x = array.array('f', xx)
        y = array.array('f', yy)
        
        for file in sorted(goodfiles):
            print file
            
            # open the file
            myfile = TFile( file )

            # retrieve the ntuple of interest
            mychain = myfile.Get('tree')
            entries = mychain.GetEntriesFast()
            if entries>1:
                print entries
                print 'This run has more events than one'
                sys.exit(0)
                
            ientry = mychain.GetEntry( 0 )
            
#            run       = int( file.split('/')[13].split('_')[2].split('.')[0] )   # <<<<<<< FIX ME, read this from the ntuple
            run       = mychain.date
            calib     = mychain.calibration[global_channel]
            months    = GetDate(run)            
            print "Checking Vars: ",run,calib
            
            x[count] = months
            y[count] = calib

            count = count+1
            
        print 'Loading into TGraph:'
        print count
        print x
        print y
        
        graph = ROOT.TGraphErrors(count,x,y)
        
            
        return graph
        
    def StyleGraph(self, graph='nograph', msize=1, mtype=1, mcolor=1, xtitle='xaxis', ytitle='yaxis', title='Title', minx=0, maxx=100):
    
        graph.SetMarkerSize(msize)
        graph.SetMarkerStyle(mtype)
        graph.SetMarkerColor(mcolor)
        graph.GetXaxis().SetTitle(xtitle)
        graph.GetYaxis().SetTitle(ytitle)
        graph.SetTitle(title)
        graph.SetMaximum(1.05)
        graph.SetMinimum(0.95)
        graph.GetXaxis().SetNdivisions(5);
        graph.GetXaxis().SetLimits(minx,maxx);
        print 'PlotBounds: ',minx,maxx
        

        
        return graph
        
        
        
######################################################################


parser = argparse.ArgumentParser(description='Plots channel response as measured \
                    by Laser, High Voltage, Cesium, and Charge Injection combined')

parser.add_argument('--date', action='store', nargs=1, type=str, default='2012-01-01',
                    required=True, help='Select runs to use. Preferred formats: \
                    1) list of integers: [194834, 194733] \
                    2) starting date as a string (takes from there to present):\
                       \'YYYY-MM-DD\' \
                    3) runs X days, or X months in the past as string: \
                       \'-28 days\' or \'-2 months\' \
                    EX: --date 2011-10-01 or --date \'-28 days\' ')
                    
parser.add_argument('--enddate', action='store', nargs=1, type=str, default='',
                    help='Select the enddate for the runs you wish to use if you \
                    want to specify an interval in the past. Accepted format is \
                    \'YYYY-MM-DD\' EX: --enddate 2012-02-01')

parser.add_argument('--region', action='store', nargs='+', type=str, default=None,
                    required=True, help='Select the region you wish to plot.  Currently \
                    this only takes a full specification such as LBA_m33_c10 and will \
                    default to high gain, gain==0')

parser.add_argument('--debug', action='store_true', default=False,
                    help='This is a switch that speeds computation time by only retrieving \
                    N-Tuple and Database information from the regions specified. \
                    NOTE: The plots produced when this option is selected will NOT \
                    HAVE the correct LASER corrections (which require the entire \
                    TileCal to be used).')
                    
parser.add_argument('--cis', action='store_true', default=False,
                    help='Set this if you want to show cis calibrations')
                    
parser.add_argument('--laser', action='store_true', default=False,
                    help='Set this if you want to show laser calibrations')
                    
parser.add_argument('--cesium', action='store_true', default=False,
                    help='Set this if you want to show cesium calibrations')



args=parser.parse_args()

plot_regions  = args.region[0]
date          = args.date[0]
if isinstance(args.enddate, list):
    enddate   = args.enddate[0] 
else:
    enddate   = args.enddate

if args.debug:
    region    = args.region
    
if enddate:
    twoinput  = True
else:
    twoinput  = False
    
flag_plotcis    = args.cis
flag_plotlaser  = args.laser
flag_plotcesium = args.cesium

# Check to ensure you are running on dedicated pcata023 machine
if False:
    machinename = os.uname()[1]
    print 'your machine is ',machinename
    if machinename != 'pcata023':
        print '------------------------------------------------------------------------'
        print 'THIS PROGRAM MUST BE RUN ON pcata023. This is the dedicated TUCS machine. '
        print 'If you do not have access, email samuel.meehan@cern.ch.'
        print '<<<<<< Exiting >>>>>>'
        print '------------------------------------------------------------------------'
        sys.exit(0)
    # make output directory if not already present
    user = os.getusername()
    outputdir = '/tucs/CommonNTupleOutput/plots/'+user
    cmd = 'mkdir -p '+str(outputdir)
    os.system(cmd)
    
    
    
##############################################
#
#
# Start main program here
#
#
###############################################

# Initialize Plotter and Global Variables
plotter = CombinedPlot(outputname='testname', cis=flag_plotcis, laser=flag_plotlaser, cesium=flag_plotcesium)
plotter.Print()

xaxistitle = 'Year'
yaxistitle = 'Relative Calibration'
headtitle  = plot_regions
xmin = GetLowBoundDate(date)
xmax = GetHighBoundDate(enddate)



# array of plots to output
plotarray = []
plotnamearray = []

# CIS Plot
if flag_plotcis:
    cis_lg_plot = ROOT.TGraphErrors()
    cis_lg_plot = plotter.MakeGraph( type='CIS', region=plot_regions, gainvar=0 )
    cis_lg_plot = plotter.StyleGraph(graph=cis_lg_plot, msize=0.8, mtype=8, mcolor=3, xtitle=xaxistitle, ytitle=yaxistitle, title=headtitle, minx=xmin, maxx=xmax)
    plotarray.append(cis_lg_plot)
    plotnamearray.append('CIS Low Gain')

    cis_hg_plot = ROOT.TGraphErrors()
    cis_hg_plot = plotter.MakeGraph( type='CIS', region=plot_regions, gainvar=1 )
    cis_hg_plot = plotter.StyleGraph(graph=cis_hg_plot, msize=0.8, mtype=8, mcolor=2, xtitle=xaxistitle, ytitle=yaxistitle, title=headtitle, minx=xmin, maxx=xmax)
    plotarray.append(cis_hg_plot)
    plotnamearray.append('CIS High Gain')
    
# Laser Plot
if flag_plotcis:
    las_lg_plot = ROOT.TGraphErrors()
    las_lg_plot = plotter.MakeGraph( type='Las', region=plot_regions, gainvar=0 )
    las_lg_plot = plotter.StyleGraph(graph=las_lg_plot, msize=0.8, mtype=23, mcolor=4, xtitle=xaxistitle, ytitle=yaxistitle, title=headtitle, minx=xmin, maxx=xmax)
    plotarray.append(las_lg_plot)
    plotnamearray.append('Laser Low Gain')
    
    las_hg_plot = ROOT.TGraphErrors()
    las_hg_plot = plotter.MakeGraph( type='Las', region=plot_regions, gainvar=1 )
    las_hg_plot = plotter.StyleGraph(graph=las_hg_plot, msize=0.8, mtype=22, mcolor=9, xtitle=xaxistitle, ytitle=yaxistitle, title=headtitle, minx=xmin, maxx=xmax)
    plotarray.append(las_hg_plot)
    plotnamearray.append('Laser High Gain')
    

    
# cesium Plot
if flag_plotcis:
    cesium_plot = ROOT.TGraphErrors()
    cesium_plot = plotter.MakeGraph( type='cesium', region=plot_regions, gainvar=0 )
    cesium_plot = plotter.StyleGraph(graph=cesium_plot, msize=0.8, mtype=28, mcolor=1, xtitle=xaxistitle, ytitle=yaxistitle, title=headtitle, minx=xmin, maxx=xmax)
    plotarray.append(cesium_plot)
    plotnamearray.append('Cesium')


# Canvas 
canvas = ROOT.TCanvas()
canvas.SetWindowSize(1200,600)
canvas.SetFillColor(0)
canvas.SetGrid(1)
canvas.SetRightMargin(0.4)

canvas.cd()

# Legend
legend = ROOT.TLegend(0.63,0.6,0.95,0.9)
legend.SetTextSize(0.03)
legend.SetFillColor(0)
legend.SetBorderSize(0)

for i in range(len(plotarray)):
    if i==0:
        plotarray[i].Draw("ap")
    else:
        plotarray[i].Draw("Same p")
    legend.AddEntry(plotarray[i],plotnamearray[i],"p")

legend.Draw()


problembox=ROOT.TPaveText(0.63,0.1,0.9,0.5,"brNDC")
problembox.SetBorderSize(0)
problembox.SetFillColor(0)
problembox.SetTextSize(0.08)
problembox.SetTextFont(42)
problembox.AddText("Problem Box")
problembox.AddText("In Progress")
problembox.Draw()

# Save canvas as output
#outputpath = outputdir+'/'+region+'.'+date+'.'+enddate+'.pdf'
canvas.SaveAs("testcan.pdf")

print 'Enter anything and hit enter to exit:'
exitvar = input()

