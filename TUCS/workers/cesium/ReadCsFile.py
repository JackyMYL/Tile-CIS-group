# Author: Mikhail Makouski <Mikhail.Makouski@cern.ch>
#
# March 04, 2009
#
# Andrey Kamenshchikov, 05-10-2013 (akamensh@cern.ch)
################################################################

from src.GenericWorker import *
from src.region import *
from src.cesium import csdb
#^my functions to read Cs files
from datetime import datetime
#import MySQLdb


class ReadCsFile(GenericWorker):
    "the second approximation to Cs cailbration reader"
    def __init__(self, processingDir='/afs/cern.ch/user/t/tilecali/w0/ntuples/cs',
                 normalize=True,
                 skipITC = False,
                 verbose=True):
        # directory where ROOT ntuples are
        self.processingDir=processingDir
        # keep ADC counts or divide by reference value
        self.normalize=normalize
        self.skipITC = skipITC
        self.verbose = verbose

    def ProcessStart(self):
        print(self.processingDir)
        pass

    def ProcessStop(self):
        csdb.closeall()
    
    def ProcessRegion(self, region):
        num=region.GetNumber(1)
        if len(num)!=2:
            return
        # this region is module
        par=region.GetParent().GetName()
        mod=int(num[1])
        tmpval=99.9
        for evt in region.GetEvents():
            #cycle over events -- runs for this module
            if evt.run.runType!='cesium':
                continue
            if 'csRun' not in evt.data:
                continue
            if evt.run.time==None:
                continue
                
            csrun=evt.data['csRun']
            if tmpval>99.0: # just to read all special cells at the beginning
                tmpval = csdb.readspecialces(csrun,par,0,0)

            csdb.rawpath=self.processingDir+'/'+str(datetime.datetime.strptime(evt.run.time, '%Y-%m-%d %H:%M:%S').year)+'/data'
            csdb.intpath=self.processingDir+'/'+str(datetime.datetime.strptime(evt.run.time, '%Y-%m-%d %H:%M:%S').year)+'/summary'
            try:    
                csconsts=csdb.readces(csrun,par,mod,csdb.intpath)
                hvtemp=csdb.readhv(csrun,par,mod,csdb.rawpath)
            except AttributeError:
                print('Problems with files for Cs Run', csrun)
                continue
            
            if not hvtemp:
                print('no hvtemp!')
                hv=-1
                temp=-1
                continue
            
            hv,temp=hvtemp
            norm=1.0
            if self.normalize:
                norm=csdb.intnorm(evt.data['source'],datetime.datetime.strptime(evt.run.time, '%Y-%m-%d %H:%M:%S'))
            # we have read calibration constants from files
            # distribute them over 'children'

            UNIXtime = evt.run.time_in_seconds
            
            for chan_region in region.GetChildren('readout'):
                chnum=chan_region.GetNumber(1)
                pmt=chnum[2]
                mbts = csdb.is_mbts(par,mod,pmt)
                specD4mod   = ( (par=='EBA' and mod==15) or (par=='EBC' and mod==18) )
                specC10mod  = ( (par=='EBA' or par=='EBC') and ((mod>=39 and mod<=42) or (mod>=55 and mod<=58)) )
                gapCrack = ( (par=='EBA' or par=='EBC') and (pmt==1 or pmt==2 or pmt==13 or pmt==14) ) or \
                           ( specD4mod and (pmt==19 or pmt==20) )
                specD4   = ( specD4mod  and (pmt==3 or pmt==4) )
                specC10  = ( specC10mod and (pmt==5 or pmt==6) )
                gapCrack = ( gapCrack and not mbts )

                specval = csdb.readspecialces(csrun,par,mod,pmt)

                if self.skipITC and (par=='EBA' or par=='EBC'):
                    if gapCrack or mbts:
                        continue
                    if (pmt==5 or pmt==6): #C10
                        continue

                for ch_ev in chan_region.GetEvents():

                    if ch_ev.run.runType!='cesium': 
                        print('this is still not a cesium event')
                        print(ch_ev.run.runType)
                        continue
                    
                    if 'csRun' not in ch_ev.data:
                        print('something funky is going on here with this event data')
                        continue
                    
                    if ch_ev.data['csRun']==evt.data['csRun']:
                        if specD4:
                            if specval>-999.0 and specval!=0.0:
                                ch_ev.data['calibration']=specval
                            else:
                                ch_ev.data['calibration']=1.2
                            if self.verbose:
                                print("sD4  csconst ",csrun,par,"%02i"%mod,"%02i"%pmt,ch_ev.data['calibration'])
                        elif specC10:
                            if specval>-999.0 and specval!=0.0:
                                ch_ev.data['calibration']=specval
                            else:
                                ch_ev.data['calibration']=2.4 # twice bigger than needed (because of masking)
                            if self.verbose: 
                                print("sC10 csconst ",csrun,par,"%02i"%mod,"%02i"%pmt,ch_ev.data['calibration'])
                        elif mbts:
                            if specval>-999.0 and specval!=0.0:
                                ch_ev.data['calibration']=specval
                            else:
                                ch_ev.data['calibration']=1.0/1.05
                                # putting crazy value - to keep old constant in DB
                                #ch_ev.data['calibration']=99.
                            if self.verbose: 
                                print("mbts csconst ",csrun,par,"%02i"%mod,"%02i"%pmt,ch_ev.data['calibration'])
                        elif gapCrack:
                            if specval>-999.0 and specval!=0.0:
                                ch_ev.data['calibration']=specval
                            else:
                                ch_ev.data['calibration']=1.5
                            if self.verbose: 
                                print("gap  csconst ",csrun,par,"%02i"%mod,"%02i"%pmt,ch_ev.data['calibration'])
                        elif csconsts[pmt]>2500 or csconsts[pmt]<100:
                            if specval>-999.0 and specval!=0.0:
                                if self.verbose: 
                                    print("bad csconst! ",csrun,par,"%02i"%mod,"%02i"%pmt,csconsts[pmt],norm,csconsts[pmt]/norm," ==> overriding it by ",specval)
                                ch_ev.data['calibration']=specval
                            else:
                                if self.verbose: 
                                    print("bad csconst! ",csrun,par,"%02i"%mod,"%02i"%pmt,csconsts[pmt],norm,csconsts[pmt]/norm)
                                if csconsts[pmt]>100 and csconsts[pmt]<4500 : # keep reasonable overflow values only
                                    ch_ev.data['calibration']=csconsts[pmt]/norm
                        else:
                            if specval>-999.0 and specval!=0.0:
                                if self.verbose: 
                                    print("good csconst ",csrun,par,"%02i"%mod,"%02i"%pmt,csconsts[pmt],norm,csconsts[pmt]/norm," ==> overriding it by ",specval)
                                ch_ev.data['calibration']=specval
                            else:
                                if self.verbose: 
                                    print("good csconst ",csrun,par,"%02i"%mod,"%02i"%pmt,csconsts[pmt],norm,csconsts[pmt]/norm)
                                ch_ev.data['calibration']=csconsts[pmt]/norm
                        ch_ev.data['HV']=hv[pmt]
                        ch_ev.data['time']= UNIXtime
                        
            # temperature is measured for a whole module
            evt.data['temp']=temp
                                
