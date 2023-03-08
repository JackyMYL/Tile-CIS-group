# Author: Mikhail Makouski <makouski@mail.cern.ch>
#
# Cesium quality checker. Prints error messages and prepares data for writing
#
# July 25, 2009
#
# Andrey Kamenshchikov, 23-10-2013 (akamensh@cern.ch)
################################################################

from src.GenericWorker import *
from src.region import *
import os

class CsQC(GenericWorker):
    "Checks if cesium data is OK"

    def __init__(self, qcthreshold=0.05, gapthreshold=-1.0, updthreshold=0.0005, rerunlist=False):
        self.runType = 'cesium'
        self.thre=qcthreshold
        if gapthreshold<0:
            self.gapthre=qcthreshold
            print("WARNING: GAP threshold is not set, using threshold for normal cells")
        else:
            self.gapthre=gapthreshold
        self.updthre=updthreshold
        self.rerunlist=rerunlist
        self.deadpmtsign='Ignore Cesium'
        self.unstablepmtsign='Unstable Cesium'
        self.emergencypmtsign='Emergency'
        
    def ProcessStart(self):
        pass
        
    def ProcessStop(self):
        pass
    
    def ProcessRegion(self, region):
        num=region.GetNumber(1)
        if len(num)!=2:
            return
        # this region is module
        par=region.GetParent().GetName()
        ros=int(num[0])
        mod=int(num[1])
        calibration = False
        iov=[]
        for event in region.GetEvents():
            if 'PMT' in event.data:
                if event.data['PMT']:
                    # this module has some channels calibrated 
                    calibration=True
                    if event.data['csRun'] not in iov:
                        iov.append(event.data['csRun'])
        
        if calibration:
            print('module',par,"%02i"%mod,'was calibrated in run',iov)
            #pass
        else:
            # this module is not calibrated
            # message will be printed only if there was at least one run during
            # requested period
            if self.rerunlist and par in self.rerunlist and mod in self.rerunlist[par]:
                print('module',par,"%02i"%mod,'was not calibrated but it is in rerun list')
            else:
                if region.GetEvents():
                    print('module',par,"%02i"%mod,'was not calibrated')
                return

        for physchan in region.GetChildren('readout'):
            num=physchan.GetNumber()
            chan=num[2]
            num=physchan.GetNumber(1)
            pmt=num[2]
            rerunpmt = (not self.rerunlist or (par in self.rerunlist and mod in self.rerunlist[par] and pmt in self.rerunlist[par][mod]))
            specD4   = ( (par=='EBA' and mod==15) or (par=='EBC' and mod==18) )
            specC10  = ( (par=='EBA' or par=='EBC') and ((mod>=39 and mod<=42) or (mod>=55 and mod<=58)) )
            gapCrack = ( not specD4 and (par=='EBA' or par=='EBC') and (pmt==1 or pmt==2 or pmt==13 or pmt==14) ) or \
                       ( specD4 and (pmt==13 or pmt==14 or pmt==19 or pmt==20) )
            specD4   = ( specD4  and (pmt==3 or pmt==4) )
            specC10  = ( specC10 and (pmt==5 or pmt==6) )
            normC10  = ( not specC10 and (par=='EBA' or par=='EBC') and (pmt==5 or pmt==6) )
            cesium=0
            HV = 499.0
            temp = 0.0
            runN=0
            ATLASrun=0
            calibration=False
            goodCalibration=0.0
            Time=None
            mydata={}
            mydata['update_needed']=False
            for event in physchan.GetEvents():
                deadpmt=False
                unstablepmt=False
                emergencypmt=False
                if 'problems' in event.data:
                    if self.deadpmtsign in event.data['problems']:
                        deadpmt=True
                    if self.unstablepmtsign in event.data['problems']:
                        unstablepmt=True
                    if self.emergencypmtsign in event.data['problems']:
                        emergencypmt=True
                if event.run.runType == self.runType:
                    if 'calibration_db' in event.data:
                        mydata['calibration_db']=event.data['calibration_db']

                    if 'calibration' in event.data and event.data['calibration']:
                        if event.data['csRun']>runN:
                            calibration = event.data['calibration']
                            if event.data['integrator']:
                                if abs(event.data['integrator']-1.0) > 0.1:
                                    print('integrator value out of range: %f'%event.data['integrator']," ignoring it ",par,"%02i"%mod,"%02i"%pmt)
                                elif calibration>0.0:
                                    calibration = event.data['calibration']/event.data['integrator']
                            if HV>499.01 and event.data['HV']>499.01:
                                if abs(HV-event.data['HV'])>0.5:
                                    print("HV was changed",par,mod,"pmt",pmt,"in run",event.data['csRun'],"from",HV,"to",event.data['HV'],"delta",event.data['HV']-HV)

                            if rerunpmt:
                                if calibration<0:
                                    if calibration<-400.01:
                                        print('special update for ',par,"%02i"%mod,"%02i"%pmt,\
                                              'keep old value',event.data['calibration_db'],'set new HV',-calibration,'   csrun',event.data['csRun'])
                                    elif calibration<-0.1:
                                        if 'HV' in event.data:
                                            print('special update for ',par,"%02i"%mod,"%02i"%pmt,\
                                                  'keep old value',event.data['calibration_db'],'set new HV',event.data['HV'],'   csrun',event.data['csRun'])
                                        else:
                                            print('special update for ',par,"%02i"%mod,"%02i"%pmt,\
                                                  'keep old value',event.data['calibration_db'],'trying to set new HV   csrun',event.data['csRun'])
                                    else:
                                        if 'temp' in event.data:
                                            print('special update for ',par,"%02i"%mod,"%02i"%pmt,\
                                                  'keep old value',event.data['calibration_db'],'set new Temp',event.data['temp'],'   csrun',event.data['csRun'])
                                        else:
                                            print('special update for ',par,"%02i"%mod,"%02i"%pmt,\
                                                  'keep old value',event.data['calibration_db'],'trying to set new Temp   csrun',event.data['csRun'])
                                    mydata['update_needed']=True
                                elif 'calibration_db' in event.data:
                                    #compare these values with DB
                                    if specC10:
                                        # this channel is not calibrated by Cs - we'll use default or value from input file
                                        calibration = event.data['calibration'] # don't apply integrator calibration
                                        if abs(calibration - event.data['calibration_db'])>self.gapthre:
                                            if mydata['update_needed']:
                                                print('special C10 deviation more than',self.gapthre,'from DB ',par,"%02i"%mod,"%02i"%pmt,\
                                                      "run",event.data['csRun'],calibration,'use value found in another run',goodCalibration)
                                                calibration=goodCalibration
                                            else:
                                                print('special C10 deviation more than',self.gapthre,'from DB ',par,"%02i"%mod,"%02i"%pmt,\
                                                      "run",event.data['csRun'],calibration,'keep old value',event.data['calibration_db'])
                                        elif abs(calibration/event.data['calibration_db']-1.0)>self.updthre:
                                            mydata['update_needed']=True
                                            print('special C10 pmt',par,"%02i"%mod,"%02i"%pmt,'calibration',calibration,\
                                                  'update old value',event.data['calibration_db'],'   csrun',event.data['csRun'])
                                        else:
                                            mydata['update_needed']=False
                                            print('special C10 pmt',par,"%02i"%mod,"%02i"%pmt,'calibration',calibration,\
                                                  'keep old value',event.data['calibration_db'])
                                            continue
                                    elif specD4 or gapCrack:
                                        # this channel is not calibrated by Cs - we'll use default or value from input file
                                        calibration = event.data['calibration'] # don't apply integrator calibration
                                        if abs(calibration - event.data['calibration_db'])>self.gapthre:
                                            if mydata['update_needed']:
                                                print('gap/crack/mbts deviation more than',self.gapthre,'from DB ',par,"%02i"%mod,"%02i"%pmt,\
                                                      "run",event.data['csRun'],calibration,'use value found in another run',goodCalibration)
                                                calibration=goodCalibration
                                            else:
                                                print('gap/crack/mbts deviation more than',self.gapthre,'from DB ',par,"%02i"%mod,"%02i"%pmt,\
                                                      "run",event.data['csRun'],calibration,'keep old value',event.data['calibration_db'])
                                        elif abs(calibration/event.data['calibration_db']-1.0)>self.updthre:
                                            mydata['update_needed']=True
                                            print('gap/crack/mbts pmt',par,"%02i"%mod,"%02i"%pmt,'calibration',calibration,\
                                                  'update old value',event.data['calibration_db'],'   csrun',event.data['csRun'])
                                        else:
                                            mydata['update_needed']=False
                                            print('gap/crack/mbts pmt',par,"%02i"%mod,"%02i"%pmt,'calibration',calibration,\
                                                  'keep old value',event.data['calibration_db'])
                                            continue
                                    elif deadpmt:
                                        # this channel is dead in Cs - we'll use default from DB
                                        print('dead pmt',par,"%02i"%mod,"%02i"%pmt,'calibration',calibration,\
                                              'keep old value',event.data['calibration_db'])
                                        mydata['update_needed']=False
                                        continue
                                    elif not (unstablepmt or emergencypmt) and abs(calibration - event.data['calibration_db'])>self.thre: ##akamensh 'and not wrongpmt'
                                        # deviation is too big, probably problem in reco - ignore it
                                        if mydata['update_needed']:
                                            print('deviation more than',self.thre,'from DB ',par,"%02i"%mod,"%02i"%pmt,\
                                                  "run",event.data['csRun'],calibration,'use value found in another run',goodCalibration)
                                            calibration=goodCalibration
                                        else:
                                            print('deviation more than',self.thre,'from DB ',par,"%02i"%mod,"%02i"%pmt,\
                                                  "run",event.data['csRun'],calibration,'keep old value',event.data['calibration_db'])
                                        # next line is commented out - it can be that deviation is not so big in other run whcih was checked already
                                        #mydata['update_needed']=False 
                                        continue
                                    else:
                                        if abs(calibration/event.data['calibration_db']-1.0)>self.updthre:
                                            mydata['update_needed']=True
                                            if (unstablepmt or emergencypmt):
                                                print('known unstable pmt',par,"%02i"%mod,"%02i"%pmt,'calibration',calibration,\
                                                      'update old value',event.data['calibration_db'],'   csrun',event.data['csRun'])
##                                            elif wrongpmt:
##                                                print 'known wrong pmt',par,"%02i"%mod,"%02i"%pmt,'calibration',calibration,\
##                                                      'update old value',event.data['calibration_db'],'   csrun',event.data['csRun']
                                            else:
                                                print('new/old-1 difference is above threshold - use it ',par,"%02i"%mod,"%02i"%pmt,calibration,calibration/event.data['calibration_db']-1.0,'   csrun',event.data['csRun'])
                                        else:
                                            mydata['update_needed']=False
                                            print('new/old-1 difference is too small - no update ',par,"%02i"%mod,"%02i"%pmt,calibration,calibration/event.data['calibration_db']-1.0)
                                else:
                                    if deadpmt:
                                        mydata['update_needed']=False
                                    else:
                                        mydata['update_needed']=True
        
                                runN=event.data['csRun']
                                if (event.data['HV']>499.01 and calibration>=0.0) or calibration<-0.1:  ##or wrongpmt:
                                    if calibration<-400.01:
                                        HV=-calibration
                                    else:
                                        HV=event.data['HV']
                                    temp=self.FindTemp(region,runN)
                                elif calibration<0.0:
                                    HV=event.data['HV_db']
                                    runN=self.FindRun(physchan,HV)
                                    temp=self.FindTemp(region,runN)
                                cesium=event.data['calibration']
                                ATLASrun=event.run.runNumber
                                Time=event.run.time
                                goodCalibration=calibration
                            
            #creating an event with final constants, suitable for WriteDB
            for gainchan in physchan.GetChildren('readout'):
                x,y,z,w=gainchan.GetNumber()
                if w==0:
                    if calibration:
                        #gain 0
                        mydata['calibration']=calibration
                        mydata['HV']=HV
                        mydata['temp']=temp
                        print('Final value for',par,"%02i"%mod,"%02i"%pmt,'calibaration',calibration,'HV',HV,'T',temp,'from csrun',runN,'ATLASrun',ATLASrun) 
                        gainchan.AddEvent(Event(Run(ATLASrun,'cesium',Time,None),mydata))   #akamensh
                    else:
                        if gapCrack or specD4:
                            print('pmt', par,"%02i"%mod,"%02i"%pmt,'gap/crack/mbts scintillator was not calibrated')
                        elif specC10:
                            print('pmt', par,"%02i"%mod,"%02i"%pmt,'special C10 was not calibrated')
                        elif normC10:
                            print('pmt', par,"%02i"%mod,"%02i"%pmt,'normal C10 was not calibrated')
                        else:
                            print('pmt', par,"%02i"%mod,"%02i"%pmt,'was not calibrated')
                        mydata['default']=1
                        gainchan.AddEvent(Event(Run(0,'cesium',0,None),mydata)) #akamensh
                    break
                                              
                #print "writing ",par,mod,chan,calibration,HV,temp
                #modBlob.setData(chan, 0, 0, float(calibration))
                #modBlob.setData(chan, 0, 2, float(HV))
                #modBlob.setData(chan, 0, 3, float(temp))

            
    def FindTemp(self,module,csrun):
        temp=11.11
        for evt in module.GetEvents():
            if 'csRun' in evt.data and 'temp' in evt.data:
                if csrun==evt.data['csRun']:
                    temp=evt.data['temp']
        if temp<11.12:
            run=0
            for evt in module.GetEvents():
                if 'csRun' in evt.data and 'temp' in evt.data:
                    if run<evt.data['csRun']:
                        run=evt.data['csRun']
                        temp=evt.data['temp']
            if run>0:
                print('Temp taken from last csrun',run)

        return temp

    def FindRun(self,physchan,HV):
        run=0
        newr=0
        newt=0.0
        newd=1000.0
        for evt in physchan.GetEvents():
            if 'csRun' in evt.data and 'HV' in evt.data:
                delta=evt.data['HV']-HV
                if abs(delta)<abs(newd):
                    newd=delta
                    newr=evt.data['csRun']
                if abs(delta)<0.05 and run<evt.data['csRun']:
                    run=evt.data['csRun']
        if run<1 and abs(newd)<1.0:
            run=newr
            print('Temp taken from csrun',run,'delta HV',newd)
        if run<1:
            run=0
            delta=1000.0
            for evt in physchan.GetEvents():
                if 'csRun' in evt.data:
                    if run<evt.data['csRun']:
                        run=evt.data['csRun']
                        if 'HV' in evt.data:
                            delta=evt.data['HV']-HV
            if run>0:
                print('Temp taken from last csrun',run,'delta HV',delta)

        return run

