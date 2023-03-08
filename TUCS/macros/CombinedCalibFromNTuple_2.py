#!/usr/bin/env python

#############################################
# Author : Sam Meehan
#  April 2012
#
#  EXAMPLE COMMAND:
#  python macros/CombinedCalibFromNTuple_2.py --date 2011-01-15 --enddate 2012-05-01 --region LBA_m33_c10 --cis --laser --hv --cesium --d6norm
#
#
#############################################

import argparse
import os.path
import os
import time
import sys
from DataSets import getContents

import array
import ROOT
from ROOT import TCanvas, TPad, TFile, gDirectory, TGraph, TGraphErrors, TLegend, TDatime, gStyle


################# Global Arguments #####################################################

# FIX MEEEEEEEE!!!!  This should not be pointing to a local directory but to a more general directory

NTupleDirectory = '/afs/cern.ch/user/t/tilecali/w0/ntuples/common/'
#NTupleDirectory = '/tucs/CommonNTuples/'

################## Global Functions ###################################################
NPart=4
NMod=64
NChan=48
NGain=2
ravelshape = [NPart,NMod,NChan,NGain]
MaxValY = 1.08
MinValY = 0.92


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

    outputtime = t[0] + t[1]/12.0 + t[2]/365.0 + t[3]/8760.0  # years*12 + months + days/30

    print 'Time of Run: ',t[0],t[1],t[2],t[3],' ---- ',outputtime

    return outputtime
    
    
def GetFromEpochTime(epochtime, type=1):
    t = time.gmtime(epochtime)
    if type==0:
        outputtime = t[0] 
    if type==1:
        outputtime = t[1] 
    if type==2:
        outputtime = t[2] 
    if type==3:
        outputtime = t[3] 
    
    return outputtime

def GetLowBoundDate(datestring):
    year  = int(datestring.split('-')[0])
    month = int(datestring.split('-')[1])
    day   = int(datestring.split('-')[2])
    
    print 'START OF PLOT:  ',year,month,day

    outputtime = year + month/12.0 - 0.1  # years*12 + months + days/30

    print 'StartDate: ',outputtime
    return outputtime
    
def GetHighBoundDate(datestring):
    year  = int(datestring.split('-')[0])
    month = int(datestring.split('-')[1])
    day   = int(datestring.split('-')[2])

    print 'END OF PLOT:  ',year,month,day

    outputtime = year + month/12.0 + 0.1  # years*12 + months + days/30

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
        
    def MakeGraph(self, type='default', normtoD6='0', region='LBA_m01_c01', gainvar=0 , minx=1200000000):
        path='.'
        
        if type=='CIS':
            path = NTupleDirectory+'CIS'
        elif type=='Las':
            path = NTupleDirectory+'Las'
        elif type=='cesium':
            path = NTupleDirectory+'cesium'
        elif type=='HV':
            path = NTupleDirectory+'HV'    
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
            print '\n======================'
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
            
            # Get relevant information
            run       = mychain.date 
            calib     = mychain.calibration[global_channel]
            months    = GetDate(run)            
            RunYear   = GetFromEpochTime(run,0)            
            RunMonth  = GetFromEpochTime(run,1)             
            RunDay    = GetFromEpochTime(run,2)     
            RunHour   = GetFromEpochTime(run,3)     
            #print "Checking Vars: ",run,months,RunYear,RunMonth,RunDay,RunHour
            
            timestring = str(RunYear)+'-'+str(RunMonth)+'-'+str(RunDay)+' '+str(RunHour)+':00:00'
            axistime = TDatime(timestring).Convert()
            
            #print 'AxisTime: ',timestring,axistime
            
            x[count] = axistime
            y[count] = calib
            
            # normalize to D6 cell if flag is specified
            CalibD6L = 1
            CalibD6R = 1
            CalibD6 = 1
            if normtoD6=='1':
                ChanD6L   = 37
                GlobalD6L = Region_to_GlobalRegion( [part,module,ChanD6L,gain] , ravelshape )
                CalibD6L  = mychain.calibration[GlobalD6L]
                
                ChanD6R   = 37
                GlobalD6R = Region_to_GlobalRegion( [part,module,ChanD6L,gain] , ravelshape )
                CalibD6R  = mychain.calibration[GlobalD6R]
                
                CalibD6 = (CalibD6L + CalibD6R)/2.0
                
                y[count] = y[count]/CalibD6
                
            # special value calculated if using HV ntuple
            if type=='HV':
                HVMarker    = Region_to_GlobalRegion( [part,module,channel,0] , ravelshape )
                HVVal       = mychain.calibration[HVMarker]
                HVSetMarker = Region_to_GlobalRegion( [part,module,channel,1] , ravelshape )
                HVSetVal    = mychain.calibration[HVSetMarker]
                
                print 'HVpoint ',HVVal,HVSetVal
                
                if HVSetVal!=0:
                    calibval = 1+6.9*(HVVal-HVSetVal)/HVSetVal
                else:
                    calibval = 666
                    
                y[count] = calibval
                
                    
            print 'CHECK --- ',type,count,y[count]
    
            # If calibration value is outside of graph bounds, stick it to top or bottom
            if y[count] > MaxValY:
                y[count] = MaxValY-0.001
            if y[count] < MinValY:
                if y[count] != -666:
                    y[count] = MinValY+0.001
                            
            count = count+1
            
        print 'Loading into TGraph:'
        print count
        print x
        print y
        
        graph = ROOT.TGraphErrors(count,x,y)
        
            
        return graph
        
    def StyleGraph(self, graph='nograph', msize=1, mtype=1, mcolor=1, xtitle='xaxis', ytitle='yaxis', title='Title', minx=0, maxx=100):
    
        print minx,maxx
        
        ROOT.gStyle.SetOptTitle(1)
        ROOT.gStyle.SetTitleX(0.65)
        ROOT.gStyle.SetTitleW(0.2)
        ROOT.gStyle.SetTitleY(0.92)
        ROOT.gStyle.SetTitleBorderSize(0)                                          
        ROOT.gStyle.SetTitleFontSize(0.1)
        ROOT.gStyle.SetTitleFillColor(0)
        ROOT.gStyle.SetEndErrorSize(0.)
    
        graph.SetMarkerSize(msize)
        graph.SetMarkerStyle(mtype)
        graph.SetMarkerColor(mcolor)
        graph.GetXaxis().SetTitle(xtitle)
        graph.GetYaxis().SetTitle(ytitle)
        graph.SetTitle(title)
        graph.SetMaximum(MaxValY)
        graph.SetMinimum(MinValY)
        graph.GetXaxis().SetNdivisions(8);
        graph.GetXaxis().CenterTitle(1);
        graph.GetXaxis().SetTimeDisplay(1); 
        graph.GetXaxis().SetTimeFormat("%d-%b-%y %F1970-01-01 00:00:01"); # NOTE:Offset neccessary to specify start as that from Epoch time
        
        graph.GetXaxis().SetLimits(minx,maxx);
        
        
        print 'PlotBounds: ',minx,maxx
        print 'Flags: ',flag_plotcis,flag_plotlaser,flag_plotcesium
        

        
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
                    
parser.add_argument('--hv', action='store_true', default=False,
                    help='Set this if you want to show high voltage calibrations')
                    
parser.add_argument('--d6norm', action='store_true', default=False,
                    help='Set this if you want to show laser/cesium calibrations \
                    also normalized to the D6 cell')                    



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
flag_plothv     = args.hv
flag_plotcesium = args.cesium

flag_d6norm     = args.d6norm

print flag_plotcis,flag_plotlaser,flag_plothv,flag_plotcesium,flag_d6norm

# Check to ensure you are running on dedicated pcata023 machine
if True:
#     machinename = os.uname()[1]
#     print 'your machine is ',machinename
#     if machinename != 'pcata023':
#         print '------------------------------------------------------------------------'
#         print 'THIS PROGRAM MUST BE RUN ON pcata023. This is the dedicated TUCS machine. '
#         print 'If you do not have access, email samuel.meehan@cern.ch.'
#         print '<<<<<< Exiting >>>>>>'
#         print '------------------------------------------------------------------------'
#         sys.exit(0)
    # make output directory if not already present
#    user = os.getusername()
    outputdir = 'CommonNTupleOutput/plots/'
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
#xmin = GetLowBoundDate(date)
#xmax = GetHighBoundDate(enddate)

xminstring = date+' 00:00:00'
xmin = TDatime(xminstring).Convert()
xmaxstring = enddate+' 00:00:00'
xmax = TDatime(xmaxstring).Convert()

print '======================='
print 'XRANGES: ',xmin,xmax
print '======================='

# array of plots to output
plotarray = []
plotnamearray = []

# CIS Plot
if flag_plotcis:
    cis_lg_plot = ROOT.TGraphErrors()
    cis_lg_plot = plotter.MakeGraph( type='CIS', normtoD6='0', region=plot_regions, gainvar=0 , minx=xmin)
    cis_lg_plot = plotter.StyleGraph(graph=cis_lg_plot, msize=0.8, mtype=8, mcolor=3, xtitle=xaxistitle, ytitle=yaxistitle, title=headtitle, minx=xmin, maxx=xmax)
    plotarray.append(cis_lg_plot)
    plotnamearray.append('CIS Low Gain')

    cis_hg_plot = ROOT.TGraphErrors()
    cis_hg_plot = plotter.MakeGraph( type='CIS', normtoD6='0', region=plot_regions, gainvar=1 , minx=xmin)
    cis_hg_plot = plotter.StyleGraph(graph=cis_hg_plot, msize=0.8, mtype=8, mcolor=2, xtitle=xaxistitle, ytitle=yaxistitle, title=headtitle, minx=xmin, maxx=xmax)
    plotarray.append(cis_hg_plot)
    plotnamearray.append('CIS High Gain')
    
    
# Laser Plot
if flag_plotlaser:
    las_lg_plot = ROOT.TGraphErrors()
    las_lg_plot = plotter.MakeGraph( type='Las', normtoD6='0', region=plot_regions, gainvar=0 , minx=xmin)
    las_lg_plot = plotter.StyleGraph(graph=las_lg_plot, msize=0.8, mtype=23, mcolor=4, xtitle=xaxistitle, ytitle=yaxistitle, title=headtitle, minx=xmin, maxx=xmax)
    plotarray.append(las_lg_plot)
    plotnamearray.append('Laser Low Gain')
    
    las_hg_plot = ROOT.TGraphErrors()
    las_hg_plot = plotter.MakeGraph( type='Las', normtoD6='0', region=plot_regions, gainvar=1 , minx=xmin )
    las_hg_plot = plotter.StyleGraph(graph=las_hg_plot, msize=0.8, mtype=22, mcolor=9, xtitle=xaxistitle, ytitle=yaxistitle, title=headtitle, minx=xmin, maxx=xmax)
    plotarray.append(las_hg_plot)
    plotnamearray.append('Laser High Gain')
 
    if flag_d6norm:
        las_lg_plot_d6 = ROOT.TGraphErrors()
        las_lg_plot_d6 = plotter.MakeGraph( type='Las', normtoD6='1', region=plot_regions, gainvar=0 , minx=xmin)
        las_lg_plot_d6 = plotter.StyleGraph(graph=las_lg_plot_d6, msize=0.8, mtype=29, mcolor=4, xtitle=xaxistitle, ytitle=yaxistitle, title=headtitle, minx=xmin, maxx=xmax)
        plotarray.append(las_lg_plot_d6)
        plotnamearray.append('Laser Low Gain (D6 Norm)')
        
        las_hg_plot_d6 = ROOT.TGraphErrors()
        las_hg_plot_d6 = plotter.MakeGraph( type='Las', normtoD6='1', region=plot_regions, gainvar=1 , minx=xmin)
        las_hg_plot_d6 = plotter.StyleGraph(graph=las_hg_plot_d6, msize=0.8, mtype=30, mcolor=9, xtitle=xaxistitle, ytitle=yaxistitle, title=headtitle, minx=xmin, maxx=xmax)
        plotarray.append(las_hg_plot_d6)
        plotnamearray.append('Laser High Gain (D6 Norm)')
    
    
# cesium Plot
if flag_plotcesium:
    cesium_plot = ROOT.TGraphErrors()
    cesium_plot = plotter.MakeGraph( type='cesium', normtoD6='0', region=plot_regions, gainvar=0 , minx=xmin)
    cesium_plot = plotter.StyleGraph(graph=cesium_plot, msize=0.8, mtype=28, mcolor=1, xtitle=xaxistitle, ytitle=yaxistitle, title=headtitle, minx=xmin, maxx=xmax)
    plotarray.append(cesium_plot)
    plotnamearray.append('Cesium')
    
    if flag_d6norm:
        cesium_plot_d6 = ROOT.TGraphErrors()
        cesium_plot_d6 = plotter.MakeGraph( type='cesium', normtoD6='1', region=plot_regions, gainvar=0 , minx=xmin)
        cesium_plot_d6 = plotter.StyleGraph(graph=cesium_plot_d6, msize=0.8, mtype=34, mcolor=1, xtitle=xaxistitle, ytitle=yaxistitle, title=headtitle, minx=xmin, maxx=xmax)
        plotarray.append(cesium_plot_d6)
        plotnamearray.append('Cesium (D6 Norm)')


# HV Plot
if flag_plothv:
    hv_plot = ROOT.TGraphErrors()
    hv_plot = plotter.MakeGraph( type='HV', normtoD6='0', region=plot_regions, gainvar=0 , minx=xmin)
    hv_plot = plotter.StyleGraph(graph=hv_plot, msize=0.8, mtype=25, mcolor=12, xtitle=xaxistitle, ytitle=yaxistitle, title=headtitle, minx=xmin, maxx=xmax)
    plotarray.append(hv_plot)
    plotnamearray.append('High Voltage')
    
    

# Canvas 
canvas = ROOT.TCanvas()
canvas.SetWindowSize(1200,600)
canvas.SetFillColor(0)
canvas.SetGrid(1)
canvas.SetRightMargin(0.4)

canvas.cd()

# Legend
legend = ROOT.TLegend(0.63,0.5,0.95,0.8)
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


problembox=ROOT.TPaveText(0.63,0.1,0.9,0.45,"brNDC")
problembox.SetBorderSize(0)
problembox.SetFillColor(0)
problembox.SetTextSize(0.08)
problembox.SetTextFont(42)
problembox.AddText("Problem Box")
problembox.AddText("In Progress")
problembox.Draw()

# Save canvas as output
outputpath = outputdir+plot_regions+'.'+date+'.'+enddate+'.pdf'
canvas.SaveAs(outputpath)
outputpath = outputdir+plot_regions+'.'+date+'.'+enddate+'.eps'
canvas.SaveAs(outputpath)

print 'Enter anything and hit enter to exit:'
exitvar = input()

