# Author: Mikhail Makouski <Mikhail.Makouski@cern.ch>
# March 04, 2009
#
# Edited: Marco van Woerden <mwoerden@gmail.com>
# January 2011
#
# Andrey Kamenshchikov, 06-10-2013 (akamensh@cern.ch)
################################################################

EBcell = ["E3", "E4","D4", "D4", "C10","C10","A12","A12","B11","B11","A13","A13",
          "E1", "E2","B12","B12","D5", "D5",             "A14","A14","B13","B13",
                                "A15","A15",             "B14","B14",
          "D6","D6",            "A16","A16","B15","B15",
          "xx","xx","xx","xx","xx","xx","xx","xx",
          "xx","xx","xx","xx","xx","xx","xx","xx"]

EBpmt = [ 1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,
          13,14,15,16,17,18,      21,22,23,24,
                      29,30,      33,34,
          37,38,      41,42,43,44,
          0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

LBcell = ["D0","A1","B1","B1","A1","A2","B2","B2","A2","A3","A3","B3",
          "B3","D1","D1","A4","B4","B4","A4","A5","A5","B5","B5","A6",
          "A6","D2","D2","A7","B6","B6","A7",          "A8","B7","B7",
          "A8","A9","A9","D3","B8","B8","D3",     "B9","B9","A10","A10",
          "xx","xx","xx"]

LBpmt = [1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12,
         13,14,15,16,17,18,19,20,21,22,23,24,
         25,26,27,28,29,30,31,      34,35,36,
         37,38,39,40,41,42,43,   45,46,47,48,
         0,0,0]

chanlb = [[], 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
          21, 22, 23, 26, 25, 24, 29, 28, 27, 32, [], [], 35, 34, 33, 38, 37, 36, 41,
          40, 39, 44, [], 42, 47, 46, 45, []]

chaneb = [[], 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, [], [], 20,
          21, 22, 23, [], [], [], [], 31, 32, [], [], 30, 35, [], [], 38, 37, [], [], 41,
          40, 39, 36, [], [], [], [], []]

partname = ["LBA","LBC","EBA","EBC"]

# module number for modules with MBTS
eba_mbts_inner = [ 4,13,24,31,36,44,53,61] #E6
eba_mbts_outer = [ 3,12,23,30,35,45,54,60] #E5
ebc_mbts_inner = [ 5,13,20,28,37,45,55,62] #E6
ebc_mbts_outer = [ 4,12,19,27,36,44,54,61] #E5

def is_mbts(par,mod,pmt):
    mbtsA = ( par=='EBA' and pmt==1 and (mod in eba_mbts_inner or mod in eba_mbts_outer) )
    mbtsC = ( par=='EBC' and pmt==1 and (mod in ebc_mbts_inner or mod in ebc_mbts_outer) )
    return (mbtsA or mbtsC)

def chan2hole(partition,chan):
    if partition[0]=='L':
        if chan in chanlb:
            return chanlb.index(chan)
        else: return 0
    else:
        if chan in chaneb:
            return chaneb.index(chan)
        else: return 0

def pmt2cell(partition,pmt):
    if partition[0]=='L':
        pmtl=LBpmt
        cell=LBcell
    else:
        pmtl=EBpmt
        cell=EBcell
    return cell[pmtl.index(pmt)]

def blanktbl():
    tbl={}
    for par in ['LBA','LBC','EBA','EBC']:
        for mod in range(1,65):
            for pmt in range(1,49):
                tbl[(par,mod,pmt)] = {}
    return tbl

from src.oscalls import *
import datetime,math
# values after intercalibration, TB 2002 is a reference
#sourcereference = {'4089RP':(1810*1.219,datetime.datetime(2002,06,15)),#EBC 4089RP
#                   '4090RP':(1810*1.160,datetime.datetime(2002,06,15)),#EBA 4090RP
#                   '4091RP':(1810*1.186,datetime.datetime(2002,06,15))}#LB  4091RP

# values after intercalibration, TB 2001 is a reference
sourcereference = {'4089RP':(1845*1.219,datetime.datetime(2001, 6, 15)),#EBC 4089RP
                   '4090RP':(1845*1.160,datetime.datetime(2001, 6, 15)),#EBA 4090RP
                   '4091RP':(1845*1.186,datetime.datetime(2001, 6, 15))}#LB  4091RP

# values before intercalibration in Apr 2009
#sourcereference = {'4089RP':(2270,datetime.datetime(2008,07,15)),#EBC 4089RP
#                   '4090RP':(2187,datetime.datetime(2008,07,15)),#EBA 4090RP
#                   '4091RP':(2238,datetime.datetime(2008,07,15))}#LB  4091RP
halflife=10987 #half-life of Cs137 in days

def intnorm(source,time):
    (refval,reftime)=sourcereference[source]
    return refval*math.exp(-0.69314718056*(time-reftime).days/halflife)


import ROOT
#ROOT.gROOT.ProcessLine("float* mydata = new float[65*48*13];")
#from ROOT import mydata

from array import array 
mydata = array('f', (65*48*13)*[0.])

    
spcpath=getResultDirectory()
specfile=os.path.join(getResultDirectory(),'specialcells.txt')
rawfiles={}
intfiles={}
spcfiles={}
spcCoeff={}

def readhv(run,par,mod,rawpath):
    """readhv(run,par,mod) returns list of HV for given Cs run, partition and module"""
    run1=run+partname.index(par)*10000000
    if not run1 in rawfiles:
        rawfiles[run1] = ROOT.TFile(rawpath+"/cs%05i.root"%run,"READ")
        if rawfiles[run1].IsZombie():
            print(("CAN'T OPEN %s"%(rawpath+"/cs%05i.root"%run)))
            return None

    rawfiles[run1].cd("RawData")
    HVtree = ROOT.gDirectory.Get("DCS.HV.%s%02i"%(par,mod))
    if not HVtree:
        print(("can't get tree %s for run %i" % ("DCS.HV.%s%02i"%(par,mod),run)))
        retlist=[-1]
        for pmt in range(1,49):
            retlist.append(0.)
        return (retlist,24.)
        #return None
    ne = HVtree.GetEntries()
    HVtree.GetEntry(ne-1)
    retlist=[-1]
    for pmt in range(1,49):
        retlist.append(HVtree.pmt[pmt-1])
    return (retlist,HVtree.temp[5])
    
def readces(run,par,mod, intpath):
    """readsec(run,par,mod) returns list of Cs constants for given run, partition and module"""
    run1=run+partname.index(par)*10000000
    if not run1 in intfiles:
        intfiles[run1] = ROOT.TFile(intpath+"/integrals_%05i.root"%run,"READ")
        if intfiles[run1].IsZombie():
            print(("CAN'T OPEN %s" % (intpath+"..._%05i.root"%run)))
            return None
    intfiles[run1].cd("")
    inttree = ROOT.gDirectory.Get("integrals")
    br = inttree.FindBranch(par)
    if br==None:
        print(('no such %s partition in run %i'%(par,run)))
        return None
    br.SetAddress(mydata)
    if inttree.GetEntries()!=1:
        print(("Corrupted tree: ",intpath+"/cs%05i/integrals_%05i.root"%(run,run)," branch: ", par))
        #print "Corrupted tree, warning 1: ",intpath1+"/cs%05i/integrals_%05i.root"%(run,run)," branch: ",par
        #print "Corrupted tree, warning 2: ",intpath2+"/cs%05i/integrals_%05i.root"%(run,run)," branch: ",par
        #print "Corrupted tree, warning 3: ",intpath3+"/cs%05i/integrals_%05i.root"%(run,run)," branch: ",par
        return None
    inttree.GetEntry(0)
    retlist=[-1]
    for pmt in range(1,49):
        retlist.append(mydata[12+(pmt-1)*13+(mod-1)*13*48])
    return retlist

def readspecialces(run,par,mod,pmt):
    """
       readsec(run,par,mod,pmt) returns special Cs constants for given partition and module and pmt
       all constats are taken from input file - specialcells.txt
       If constant is not found in input ascii file value -1 is returned
    """
    global spcCoeff
    retval=-999.9
    run=0 # run is not needed for the moment
    if not run in spcfiles:
        spcfiles[run] = specfile
        print(("csdb.specfile is ",spcfiles[run]))
        try:
            lines = open(spcfiles[run],"r").readlines()
        except Exception as e:
            print(("can't open file %s" % spcfiles[run]))
            return retval
        for line in lines:
            fields = line.strip().split()
            #=== ignore empty and comment lines
            if not len(fields)          : continue
            if fields[0].startswith("#"): continue

            #=== read in fields
            frag = fields[0]
            chan = fields[1]
            gain = fields[2]
            data = fields[3]

            #=== decode fragment
            if not ( frag.startswith('0x') or frag.startswith('LB') or frag.startswith('EB')):
                print(("Misformated fragment %s" % frag + " in file %s" % spcfiles[run]))
                continue
            if frag.startswith('0x'):
                ros = int(frag[2])
                prt = partname[ros-1]
                mdn = int(frag[3:],16)+1
                chn = int(chan)
                pmn = chan2hole(prt,chn)
                if ( ( (prt=='EBA' and mdn==15) or (prt=='EBC' and mdn==18) ) and (chn==18 or chn==19) ):
                    pmn = chn+1
            elif frag.startswith('x'):
                prt = frag[1:4]
                mdn = int(frag[4:])
                chn = int(chan)
                pmn = chan2hole(prt,chn)
                if ( ( (prt=='EBA' and mdn==15) or (prt=='EBC' and mdn==18) ) and (chn==18 or chn==19) ):
                    pmn = chn+1
            elif chan.startswith('c'):
                prt = frag[0:3]
                mdn = int(frag[3:])
                chn = int(gain)
                pmn = chan2hole(prt,chn)
                if ( ( (prt=='EBA' and mdn==15) or (prt=='EBC' and mdn==18) ) and (chn==18 or chn==19) ):
                    pmn = chn+1
                if chan.startswith('ch1'):
                    pmn = chn+1
            else:
                prt = frag[0:3]
                mdn = int(frag[3:])
                pmn = int(chan)
            if int(gain)<0 or mdn>64:
                mdn=-1
            #=== fill array
            key = (prt,mdn,pmn)
            spcCoeff[key] = float(data)
            print(('module',prt,"%02i"%mdn,"  %02i"%pmn, ' coeff %f'%spcCoeff[key]))
        for pmn in range(1,49):
            for prt in ['LBA','LBC','EBA','EBC']:
                for mdn in range(1,65):
                    key0 = (prt,-1,pmn)
                    key  = (prt,mdn,pmn)
                    if key0 in spcCoeff:
                        if key in spcCoeff:
                            newval=spcCoeff[key]*spcCoeff[key0]
                            print(('module',prt,"%02i"%mdn,"  %02i"%pmn, ' coeff %f'%spcCoeff[key],' rescaled by %f'%spcCoeff[key0],' to %f'%newval))
                            spcCoeff[key] = newval
                        else:
                            print(('module',prt,"%02i"%mdn,"  %02i"%pmn, ' coeff set to %f'%spcCoeff[key0]))
                            spcCoeff[key] = spcCoeff[key0]

    key = (par,mod,pmt)
    if key in spcCoeff:
        return spcCoeff[key]
    else:
        return retval

def closeall():
    global rawfiles
    global intfiles
    global spcfiles
    for run in rawfiles:
        rawfiles[run].Close()
    for run in intfiles:
        intfiles[run].Close()
    rawfiles={}
    intfiles={}
    spcfiles={}
#    ROOT.gROOT.ProcessLine("delete[] mydata;")

