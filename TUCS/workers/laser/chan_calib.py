# Worker to be used to add runs to be used mainly for getLaserFlags
############################################################
#
# chan_calib.py
#
############################################################
#
# Author: Arthur Chomont (arthur.chomont@cern.ch)
#
# July 2015
#
# Goal:
# ->  For a given Laser run, separate the channels in different categories
#       Channels which can be calibrated
#       Channels which need to be calibrated but whose deviation origin is unknown
#       Channels which don't need to be calibrated
#
# Input parameters are:
# -> Global variable from workers: runNumber which is looked at, What is stored in the txt file in output
# 
# Ouput
# -> txt file with for each channels a flag corresponding to the category of the channel (possibility to have all the channels or only the channels which need calibration)
#
#############################################################

from src.GenericWorker import *
from src.region import *

from src.laser.toolbox import *

class chan_calib(GenericWorker):
    " This worker Enounces the channel for which the laser constant is different from 1"

    def __init__(self,run,PrintAll=False,status = True,forceModule='LBA_m99'):

        self.run_list      = []
        self.low_gain=int(run)
        self.Event_time=timedelta(days=1)
        self.printall=PrintAll
        self.status=status
        self.forceModule=forceModule
    
    def ProcessStart(self):

        
        self.nb=0
        global LgRun                       
        global HgRun
        LgRun={}                                              #Store the runs with wheelpos=6 (low gain run)
        HgRun={}                                              #Store the runs with wheelpos=8 (high gain run)
        global Chan_flag
        Chan_flag={}
        global Chan_DQ
        Chan_DQ={}

        global run_list
        for run in run_list.getRunsOfType('Las'):
            self.run_list.append(run)

        run_dis=self.run_list[0]
        test=1
        while test!=0:                                        #To store the runs in a good order (here the run in input of the macros is the first one, need to be put at the end)
            if self.run_list[test].runNumber<run_dis.runNumber:
                if test==len(self.run_list)-1:
                    self.run_list.insert(test,self.run_list.pop(0))
                    test=0
                else:
                    test+=1
            else:
                self.run_list.insert(test-1,self.run_list.pop(0))
                test=0

        for x in self.run_list:
            #print x.runNumber
            if x.runNumber==self.low_gain:
                self.Event_time=datetime.datetime.strptime(x.time,"%Y-%m-%d %H:%M:%S")
                self.Highgain_time=self.Event_time

        self.highgain=0
        global flas_ratio                                       #Store the ratio f_las over f_HV for small value of the deviation (<5%) (only to do plot for definition of threshold)
        flas_ratio=[]
        self.ratio=0
        global flas_ratio_MD                                    #Store the ratio f_las over f_HV for medium value of the deviation (>5% and <15%)
        flas_ratio_MD=[]
        self.ratio_MD=0
        global flas_ratio_HD                                    #Store the ratio f_las over f_HV for big value of the deviation (>15%)
        flas_ratio_HD=[]
        self.ratio_HD=0
        self.file=os.path.join(getResultDirectory(),"Channels.txt")
        self.opfile=open(self.file,"w")

        global Dev_diffA                                        #Store the value of the laser deviation for channels of part A to define a mean value of deviation of the channels of this type
        Dev_diffA=[]
        global FlasA                                            #Store the value of the laser constant for channels of part A
        FlasA=[]
        global Dev_diffBC                                       #Store the value of the laser deviation for channels of part BC to define a mean value of deviation of the channels of this type
        Dev_diffBC=[]
        global Dev_diffD                                        #Store the value of the laser deviation for channels of part D to define a mean value of deviation of the channels of this type
        Dev_diffD=[]
        global Dev_diffE1                                        #Store the value of the laser deviation for channels of part E1 to define a mean value of deviation of the channels of this type
        Dev_diffE1=[]
        global Dev_diffE2                                        #Store the value of the laser deviation for channels of part E2 to define a mean value of deviation of the channels of this type
        Dev_diffE2=[]
        global Dev_diffE3                                        #Store the value of the laser deviation for channels of part E3 to define a mean value of deviation of the channels of this type
        Dev_diffE3=[]
        global Dev_diffE4                                        #Store the value of the laser deviation for channels of part E4 to define a mean value of deviation of the channels of this type
        Dev_diffE4=[]
        global Dev_diffTot                                      #Store the value of the laser deviation for all channels to define a mean value of deviation of the channels of this type
        Dev_diffTot=[]
        self.HV={}                                              #Store the value of HV value for a given channel
        self.HVref={}                                           #Store the value of HVref for a given channel
        self.layer={}                                           #Store the value of layer for a channel in order to compute deviation from mean cell deviation

        self.timediff_HG=timedelta(days=5)                   #Will be used to separate the High gain run nearer to the low gain laser run that interest us

        self.fiber={}                                        #Will be used to test fiber flag : for each module all the channels deviation are stocked then a comparison is done between all odd and even channels
        self.fiber['TILECAL_LBA_m65_c00_lowgain']=0

        self.meaneven=0 
        self.meanodd=0       

        self.beta={}                                         # beta for computation of deviation using H
        
    def ProcessRegion(self, region):
    
        for event in region.GetEvents():

            layer =  region.GetLayerName()                       #Use of functions to get name of layer and region for 
            cell  =  region.GetCellName()

            if event.run.runNumber==self.low_gain:
                if 'beta' in region.GetParent().data:       #Definition of the beta which will be used to compute the deviation from HV
                    if region.GetParent().data['beta']>5:
                        self.beta[str(event.region)] = region.GetParent().data['beta']
                    else:
                        self.beta[str(event.region)] = 6.9
                else:
                    self.beta[str(event.region)] = 6.9
                    
            self.bool=0                                          #Will be used to choose to look only at events from the last lowgain run

            self.timediff=timedelta(days=1)                      #Will be used to separate the HV run nearer to the laser run that interest us
            self.HV_index=0                                      #Will be used to store the HV run nearer to the laser run that interest us

#The following lines are needed since the name of channels for getLaserFlags and HV_value worker are in a different shape that the one of event.region                                  
            pmt_region = str(event.region)
            pmt_channel=''
            pmt_region_hl=''
            pmt_region_flag=''
            module_fiber=''                               #Just present to do test about fiber default
            pmt_region_flaghg=''
            pmt_region_flaglg=''
            for i in range(20):
                pmt_region_hl+=pmt_region[i]
            for x in range(8,11):
                pmt_region_flag+=pmt_region[x]
                pmt_region_flaghg+=pmt_region[x]
                pmt_region_flaglg+=pmt_region[x]
            for x in range(13,19):
                pmt_region_flag+=pmt_region[x]
                pmt_region_flaglg+=pmt_region[x]
                pmt_region_flaghg+=pmt_region[x]
            for x in range(17,19):
                pmt_channel+=pmt_region[x]
            for x in range(8,15):
                module_fiber+=pmt_region[x]
            pmt_region_flaghg+=' high gain'
            pmt_region_flaglg+=' low gain'

            self.layer[pmt_region]=layer

            if  pmt_region.find('lowgain')!=-1:

#If the run number is superior to the one store, we conserve the new one (the aim is to only keep the last lowgain laser run)
                if event.run.runNumber==self.low_gain:
                    self.nb+=1
                    self.bool=1
                    if (pmt_region in LgRun):
                        del self.HV[pmt_region]
                        del self.HVref[pmt_region]
                        del LgRun[pmt_region]
                        self.HV[pmt_region]=event.data['HV']
                        self.HVref[pmt_region]=event.data['hv_db']
                        LgRun[pmt_region]=event                          
                    else:
                        LgRun[pmt_region]=event
                        self.HV[pmt_region]=event.data['HV']
                        self.HVref[pmt_region]=event.data['hv_db']



#In the following we stores diverse values to produce plots used after to define threshold to the definition of the categories (we take here all the runs lowgain and not only the last one) 
                if 'f_laser' in event.data:

 # This is the DQ status list that affect laser data
#                            DQstatus_list = ['No HV','Wrong HV','ADC masked (unspecified)','ADC dead','Data corruption','Severe data corruption','Severe stuck bit','Large LF noise','Very large LF noise','Channel masked (unspecified)','Bad timing']
                    DQstatus_list = ['No HV','ADC masked (unspecified)','ADC dead','Severe data corruption','Severe stuck bit','Very large LF noise','Channel masked (unspecified)']

                    if 'problems' in event.data:
                        newtest=0
                        for problem in event.data['problems']:
                            if (problem in DQstatus_list):
                                newtest=1
                        if newtest==1:
                            continue
                                        
                    if 'is_OK' in event.data:
                        if (not event.data['is_OK']):
                            continue

                    if (self.status):
                        if (event.data['status']&0x10 or event.data['status']&0x4):
                            continue




                    #We store here the value used to define threshold with the mean value of the deviation of cells of the same type
                    if (self.bool==1 and layer=='A'):               
                        if (event.data['f_laser']==1):
                            Dev_diffA.append(0)
                            Dev_diffTot.append(0)
                            FlasA.append(1)
                        else:
                            Dev_diffA.append(event.data['deviation'])   
                            FlasA.append(event.data['f_laser']) 
                            Dev_diffTot.append(event.data['deviation'])
                    elif (self.bool==1 and (layer=='B' or layer=='C')):           
                        if (event.data['f_laser']==1):
                            Dev_diffBC.append(0)  
                            Dev_diffTot.append(0)
                        else:
                            Dev_diffBC.append(event.data['deviation']) 
                            Dev_diffTot.append(event.data['deviation'])
                    elif (self.bool==1 and layer=='D'):
                        if (event.data['f_laser']==1):
                            Dev_diffD.append(0)  
                            Dev_diffTot.append(0)
                        else:
                            Dev_diffD.append(event.data['deviation'])  
                            Dev_diffTot.append(event.data['deviation'])
                    elif (self.bool==1 and layer in ['E1']):
                        if (event.data['f_laser']==1):
                            Dev_diffE1.append(0)  
                            Dev_diffTot.append(0)
                        else:
                            Dev_diffE1.append(event.data['deviation'])
                            Dev_diffTot.append(event.data['deviation'])
                    elif (self.bool==1 and layer in ['E2']):
                        if (event.data['f_laser']==1):
                            Dev_diffE2.append(0)  
                            Dev_diffTot.append(0)
                        else:
                            Dev_diffE2.append(event.data['deviation'])
                            Dev_diffTot.append(event.data['deviation'])
                    elif (self.bool==1 and layer in ['E3']):
                        if (event.data['f_laser']==1):
                            Dev_diffE3.append(0)  
                            Dev_diffTot.append(0)
                        else:
                            Dev_diffE3.append(event.data['deviation'])
                            Dev_diffTot.append(event.data['deviation'])
                    elif (self.bool==1 and layer in ['E4']):
                        if (event.data['f_laser']==1):
                            Dev_diffE4.append(0)  
                            Dev_diffTot.append(0)
                        else:
                            Dev_diffE4.append(event.data['deviation'])
                            Dev_diffTot.append(event.data['deviation'])
                    #We store here ratio f_las over f_HV to define threshold for which HV and laser are compatible or not
                    if (event.data['f_laser']!=1):

#Just a small block of code to test if anomaly on the fiber : a majority of odd/even channels of a same modules drift in the same way (threshold of 1.5% chosen arbitrarily)
                        if (self.bool==1 and event.run.runNumber==self.low_gain):   

                                              
                            if (module_fiber in str(self.fiber)):
                                self.fiber[pmt_region]=event.data['deviation']
                            else:
                                nodd=0
                                neven=0                                
                                self.meanodd=0.0
                                self.meaneven=0.0
                                for x in self.fiber:
                                    if int(x[18])%2==0 and math.fabs(self.fiber[x])>0 and math.fabs(self.fiber[x])<10:
                                        neven+=1
                                        self.meaneven+=self.fiber[x]
                                    elif int(x[18])%2==1 and math.fabs(self.fiber[x])>0 and math.fabs(self.fiber[x])<10:
                                        nodd+=1
                                        self.meanodd+=self.fiber[x]
                                if (nodd>0):
                                    self.meanodd=self.meanodd/nodd
                                if (neven>0):
                                    self.meaneven=self.meaneven/neven

                                flag_fiber=''
                                module_fiber=''
                                for r in self.fiber:
                                    flag_fiber=''
                                    module_fiber=''
                                    for x in range(8,11):
                                        flag_fiber+=r[x]
                                        module_fiber+=r[x]
                                    for x in range(13,15):
                                        module_fiber+=r[x]
                                    for x in range(13,17):
                                        flag_fiber+=r[x]

                                if ('LBA_m61' in str(self.fiber) ):
                                    print(" fibre = ",str(self.fiber)," diff=",math.fabs(self.meaneven-self.meanodd),"% odd=",self.meanodd," even=",self.meaneven,"%")


                                if ('LB' in str(self.fiber) and math.fabs(self.meaneven-self.meanodd)>0.5 and self.meaneven!=0 and self.meanodd!=0):  #To test if for a given module we have sum of odd/even in A and even/odd in B greater than a threshold.                                    
                                    Flag_Chan[module_fiber]=[str(neven),"0"]
                                    Flag_Chan[module_fiber]=[str(nodd),"1"]

                                elif ('EB' in str(self.fiber) and math.fabs(self.meaneven-self.meanodd)>0.5 and self.meaneven!=0 and self.meanodd!=0 ):  #half the number of channels in an extended barrel module #TMP TMP BDE 8 was 10
                                    Flag_Chan[module_fiber]=[str(neven),"0"]
                                    Flag_Chan[module_fiber]=[str(nodd),"1"]

                                self.fiber.clear()
                                self.fiber[pmt_region]=event.data['deviation']
                                        

                        if (math.fabs(event.data['deviation'])<5):
                            if event.data['hv_db']>0 and event.data['HV']>0.:
                                if event.run.runNumber==self.low_gain:
                                    HVG=(pow(event.data['HV']/event.data['hv_db'],self.beta[pmt_region])-1)*100
                                else:
                                    HVG=(pow(event.data['HV']/event.data['hv_db'],6.9)-1)*100
                            else:
                                HVG=0;

                            if (math.fabs(event.data['deviation']-HVG)<=5):                               
                                self.ratio=(1+HVG/100)*event.data['f_laser']
                                flas_ratio.append(self.ratio)                                                                                           
                        else:
                            if event.data['hv_db']>0 and event.data['HV']>0.:
                                if event.run.runNumber==self.low_gain:
                                    HVG=(pow(event.data['HV']/event.data['hv_db'],self.beta[pmt_region])-1)*100
                                else:
                                    HVG=(pow(event.data['HV']/event.data['hv_db'],6.9)-1)*100
                            else:
                                HVG=0;
                            if (math.fabs(event.data['deviation']-HVG)<=8.5 and HVG!=-100.0):#4.5
                               
                                self.ratio_HD=(1+HVG/100)*event.data['f_laser']
                                flas_ratio_HD.append(self.ratio_HD)

#High gain events from the latest high gain laser run to be kept
            elif pmt_region.find('highgain')!=-1:
                
                self.Highgain_time=datetime.datetime.strptime(event.run.time,"%Y-%m-%d %H:%M:%S")
                if abs(self.Highgain_time-self.Event_time)<=self.timediff_HG:
                    self.timediff_HG=abs(self.Highgain_time-self.Event_time)
                    self.highgain=event.run.runNumber
                    if (pmt_region in HgRun):
                        del HgRun[pmt_region]
                        HgRun[pmt_region]=event
                    else:
                        HgRun[pmt_region]=event

    def ProcessStop(self):


        nodd=0
        neven=0
        for x in self.fiber:                                              #Flag fiber attribution for the last modules looked at (for the others, already done in ProcessRegion)
            if (int(x[18])%2==0 and math.fabs(self.fiber[x])>1.5):
                neven+=1
            elif (int(x[18])%2==1 and math.fabs(self.fiber[x])>1.5):
                nodd+=1
            test=x
        flag_fiber=''
        module_fiber=''
        for x in range(8,11):
            flag_fiber+=test[x]
            module_fiber+=test[x]
        for x in range(13,15):
            module_fiber+=test[x]
        for x in range(13,17):
            flag_fiber+=test[x]

        if ('LB' in str(self.fiber) and math.fabs(self.meaneven-self.meanodd)>1.0 and self.meaneven!=0 and self.meanodd!=0):  #To test if for a given module we have sum of odd/even in A and even/odd in B greater than a threshold.                                    
                Flag_Chan[module_fiber]=[str(neven),"0"]
                Flag_Chan[module_fiber]=[str(nodd),"1"]
                
        elif ('EB' in str(self.fiber) and math.fabs(self.meaneven-self.meanodd)>2.0 and self.meaneven!=0 and self.meanodd!=0 ):  #half the number of channels in an extended barrel module #TMP TMP BDE 8 was 10
            Flag_Chan[module_fiber]=[str(neven),"0"]
            Flag_Chan[module_fiber]=[str(nodd),"1"]


#In the next lines we append the flag fiber to the channels defined above
        test={}
        for x in Flag_Chan:
            test[x]=Flag_Chan[x]
        for x in test:
            if '_c' not in x:
                flag_module_C=''
                flag_fiber_A=''
                flag_fiber_C=''
                for t in range(2):
                    flag_fiber_A+=x[t]
                    flag_fiber_C+=x[t]
                    flag_module_C+=x[t]
                flag_fiber_A+='A'
                flag_fiber_C+='C'
                flag_module_C+='C'
                for t in range(3,5):
                    flag_fiber_A+=x[t]
                    flag_fiber_C+=x[t]
                    flag_module_C+=x[t]
                flag_fiber_A+='_c'
                flag_fiber_C+='_c'
                if 'LBA' in x:
                    if int(Flag_Chan[x][1])%2==0 or int(Flag_Chan[x][1])%2==1: #and flag_module_C in Flag_Chan:
                        #if (int(Flag_Chan[x][0])+int(Flag_Chan[flag_module_C][0])>30 or int(Flag_Chan[x][0])>20 or int(Flag_Chan[flag_module_C][0])>20) and int(Flag_Chan[flag_module_C][1])%2==1:
                            #for t in xrange(24):
                            #    if (2*t+1<10):
                            #        flag_fiber_A+='0'+str(2*t)
                            #        flag_fiber_C+='0'+str(2*t+1)
                            #    else:
                            #        flag_fiber_A+=str(2*t)
                            #        flag_fiber_C+=str(2*t+1)
                            #    if flag_fiber_A in Flag_Chan:
                            #        if (Flag_Chan[flag_fiber_A]!='Fiber'):
                            #            Flag_Chan[flag_fiber_A].append('Fiber')
                            #        flag_fiber_A=flag_fiber_A[:-2]
                            #    else:
                            #        Flag_Chan[flag_fiber_A]='Fiber'
                            #        flag_fiber_A=flag_fiber_A[:-2]
                            #    if flag_fiber_C in Flag_Chan:
                            #        if (Flag_Chan[flag_fiber_C]!='Fiber'):
                            #            Flag_Chan[flag_fiber_C].append('Fiber')
                            #        flag_fiber_C=flag_fiber_C[:-2]
                            #    else:
                            #        Flag_Chan[flag_fiber_C]='Fiber'
                            #        flag_fiber_C=flag_fiber_C[:-2]
                            for t in range(48):
                                if (t<10):
                                    flag_fiber_A+='0'+str(t)
                                    flag_fiber_C+='0'+str(t)
                                else:
                                    flag_fiber_A+=str(t)
                                    flag_fiber_C+=str(t)
                                if flag_fiber_A in Flag_Chan:
                                    if (Flag_Chan[flag_fiber_A]!='Fiber'):
                                        Flag_Chan[flag_fiber_A].append('Fiber')
                                    flag_fiber_A=flag_fiber_A[:-2]
                                else:
                                    Flag_Chan[flag_fiber_A]='Fiber'
                                    flag_fiber_A=flag_fiber_A[:-2]
                                if flag_fiber_C in Flag_Chan:
                                    if (Flag_Chan[flag_fiber_C]!='Fiber'):
                                        Flag_Chan[flag_fiber_C].append('Fiber')
                                    flag_fiber_C=flag_fiber_C[:-2]
                                else:
                                    Flag_Chan[flag_fiber_C]='Fiber'
                                    flag_fiber_C=flag_fiber_C[:-2]

                    #if int(Flag_Chan[x][1])%2==1: #and flag_module_C in Flag_Chan:
                    #    #if (int(Flag_Chan[x][0])+int(Flag_Chan[flag_module_C][0])>30 or int(Flag_Chan[x][0])>20 or int(Flag_Chan[flag_module_C][0])>20) and int(Flag_Chan[flag_module_C][1])%2==0:
                    #        for t in xrange(24):
                    #            if (2*t+1<10):
                    #                flag_fiber_A+='0'+str(2*t+1)
                    #                flag_fiber_C+='0'+str(2*t)
                    #            else:
                    #                flag_fiber_A+=str(2*t+1)
                    #                flag_fiber_C+=str(2*t)
                    #            if flag_fiber_A in Flag_Chan:
                    #                if (Flag_Chan[flag_fiber_A]!='Fiber'):
                    #                    Flag_Chan[flag_fiber_A].append('Fiber')
                    #                flag_fiber_A=flag_fiber_A[:-2]
                    #            else:
                    #                Flag_Chan[flag_fiber_A]='Fiber'
                    #                flag_fiber_A=flag_fiber_A[:-2]
                    #            if flag_fiber_C in Flag_Chan:
                    #                if (Flag_Chan[flag_fiber_C]!='Fiber'):
                    #                    Flag_Chan[flag_fiber_C].append('Fiber')
                    #                flag_fiber_C=flag_fiber_C[:-2]
                    #            else:
                    #                Flag_Chan[flag_fiber_C]='Fiber' 
                    #                flag_fiber_C=flag_fiber_C[:-2]
                elif 'LBC' in x:
                    if int(Flag_Chan[x][1])%2==0 or int(Flag_Chan[x][1])%2==1: #and flag_module_C in Flag_Chan:
                        #if (int(Flag_Chan[x][0])+int(Flag_Chan[flag_module_C][0])>30 or int(Flag_Chan[x][0])>20 or int(Flag_Chan[flag_module_C][0])>20) and int(Flag_Chan[flag_module_C][1])%2==1:
                        for t in range(48):
                                if (t<10):
                                    flag_fiber_A+='0'+str(t)
                                    flag_fiber_C+='0'+str(t)
                                else:
                                    flag_fiber_A+=str(t)
                                    flag_fiber_C+=str(t)
                                if flag_fiber_A in Flag_Chan:
                                    if (Flag_Chan[flag_fiber_A]!='Fiber'):
                                        Flag_Chan[flag_fiber_A].append('Fiber')
                                    flag_fiber_A=flag_fiber_A[:-2]
                                else:
                                    Flag_Chan[flag_fiber_A]='Fiber'
                                    flag_fiber_A=flag_fiber_A[:-2]
                                if flag_fiber_C in Flag_Chan:
                                    if (Flag_Chan[flag_fiber_C]!='Fiber'):
                                        Flag_Chan[flag_fiber_C].append('Fiber')
                                    flag_fiber_C=flag_fiber_C[:-2]
                                else:
                                    Flag_Chan[flag_fiber_C]='Fiber'
                                    flag_fiber_C=flag_fiber_C[:-2]
                            # for t in xrange(24):
                    #             if (2*t+1<10):
                    #                 flag_fiber_C+='0'+str(2*t)
                    #                 flag_fiber_A+='0'+str(2*t+1)
                    #             else:
                    #                 flag_fiber_C+=str(2*t)
                    #                 flag_fiber_A+=str(2*t+1)
                    #             if flag_fiber_A in Flag_Chan:
                    #                 if (Flag_Chan[flag_fiber_A]!='Fiber'):
                    #                     Flag_Chan[flag_fiber_A].append('Fiber')
                    #                 flag_fiber_A=flag_fiber_A[:-2]
                    #             else:
                    #                 Flag_Chan[flag_fiber_A]='Fiber'
                    #                 flag_fiber_A=flag_fiber_A[:-2]
                    #             if flag_fiber_C in Flag_Chan:
                    #                 if (Flag_Chan[flag_fiber_C]!='Fiber'):
                    #                     Flag_Chan[flag_fiber_C].append('Fiber')
                    #                 flag_fiber_C=flag_fiber_C[:-2]
                    #             else:
                    #                 Flag_Chan[flag_fiber_C]='Fiber'
                    #                 flag_fiber_C=flag_fiber_C[:-2]
                    # if int(Flag_Chan[x][1])%2==1: #and flag_module_C in Flag_Chan:
                    #     #if (int(Flag_Chan[x][0])+int(Flag_Chan[flag_module_C][0])>30 or int(Flag_Chan[x][0])>20 or int(Flag_Chan[flag_module_C][0])>20) and int(Flag_Chan[flag_module_C][1])%2==0:
                    #         for t in xrange(24):
                    #             if (2*t+1<10):
                    #                 flag_fiber_C+='0'+str(2*t+1)
                    #                 flag_fiber_A+='0'+str(2*t)
                    #             else:
                    #                 flag_fiber_C+=str(2*t+1)
                    #                 flag_fiber_A+=str(2*t)
                    #             if flag_fiber_A in Flag_Chan:
                    #                 if (Flag_Chan[flag_fiber_A]!='Fiber'):
                    #                     Flag_Chan[flag_fiber_A].append('Fiber')
                    #                 flag_fiber_A=flag_fiber_A[:-2]
                    #             else:
                    #                 Flag_Chan[flag_fiber_A]='Fiber'
                    #                 flag_fiber_A=flag_fiber_A[:-2]
                    #             if flag_fiber_C in Flag_Chan:
                    #                 if (Flag_Chan[flag_fiber_C]!='Fiber'):
                    #                     Flag_Chan[flag_fiber_C].append('Fiber')
                    #                 flag_fiber_C=flag_fiber_C[:-2]
                    #             else:
                    #                 Flag_Chan[flag_fiber_C]='Fiber' 
                    #                 flag_fiber_C=flag_fiber_C[:-2]
                else:
                    if int(Flag_Chan[x][1])%2==0:
                        for t in range(24):
                            if (2*t<10):
                                flag_fiber+='0'+str(2*t)
                            else:
                                flag_fiber+=str(2*t)
                                if flag_fiber in Flag_Chan:
                                    Flag_Chan[flag_fiber].append('Fiber')
                                    flag_fiber=flag_fiber[:-2]
                                else:
                                    Flag_Chan[flag_fiber]=['Fiber']
                                    flag_fiber=flag_fiber[:-2]
                    if int(Flag_Chan[x][1])%2==1:
                        for t in range(24):
                            if (2*t+1<10):
                                flag_fiber+='0'+str(2*t+1)
                            else:
                                flag_fiber+=str(2*t+1)
                                if flag_fiber in Flag_Chan:
                                    Flag_Chan[flag_fiber].append('Fiber')
                                    flag_fiber=flag_fiber[:-2]
                                else:
                                    Flag_Chan[flag_fiber]=['Fiber']   
                                    flag_fiber=flag_fiber[:-2]



#The next block of lines correspond to different plots used to define threshold
        self.c1 = src.MakeCanvas.MakeCanvas()
        self.plot_name = os.path.join(getResultDirectory(),"Diff_HVLas_LD")
        self.c1.SetFrameFillColor(0)
        self.c1.SetFillColor(0);
        self.c1.SetBorderMode(0); 
        self.c1.SetGridx(1);
        self.c1.SetGridy(1);
        self.c1.cd()
        self.Ratio = ROOT.TH1F('testld','Ratio Laser constant/HV constant;f_{las}/f_{HV};N_{chan}',21,0.955,1.055)
        for x in flas_ratio:
            self.Ratio.Fill(x)
        self.Ratio.Draw()
        self.c1.Modified()
        #self.c1.Print("%s.eps" % (self.plot_name))
        #self.c1.Print("%s.png" % (self.plot_name))
        #self.c1.Print("%s.C" % (self.plot_name))

        self.c6 = src.MakeCanvas.MakeCanvas()
        self.plot_name6 = os.path.join(getResultDirectory(),"Diff_HVLas_HD")
        self.c6.SetFrameFillColor(0)
        self.c6.SetFillColor(0);
        self.c6.SetBorderMode(0); 
        self.c6.SetGridx(1);
        self.c6.SetGridy(1);
        self.c6.cd()
        self.RatioHD = ROOT.TH1F('testhd','Ratio HD Laser constant/HV constant;f_{las}/f_{HV};N_{chan}',21,0.955,1.055)
        for x in flas_ratio_HD:
            self.RatioHD.Fill(x)
        self.RatioHD.Draw()
        self.c6.Modified()
        #self.c6.Print("%s.eps" % (self.plot_name6))
        #self.c6.Print("%s.png" % (self.plot_name6))
        #self.c6.Print("%s.C" % (self.plot_name6))

        self.c2 = src.MakeCanvas.MakeCanvas()
        self.plot_name2 = os.path.join(getResultDirectory(),"DevAM")
        self.c2.SetFrameFillColor(0)
        self.c2.SetFillColor(0);
        self.c2.SetBorderMode(0); 
        self.c2.SetGridx(1);
        self.c2.SetGridy(1);
        self.c2.cd()
        self.DiffA = ROOT.TH1F('DevA','Deviation for A cells;Deviation;N_{chan}',101,-5.05,5.05)
        for x in Dev_diffA:
            self.DiffA.Fill(x)
        self.DiffA.Draw()
        #print self.DiffA.GetMean()
        self.c2.Modified()
        #self.c2.Print("%s.eps" % (self.plot_name2))
        #self.c2.Print("%s.png" % (self.plot_name2))
        #self.c2.Print("%s.C" % (self.plot_name2))

        self.c2bis = src.MakeCanvas.MakeCanvas()
        self.plot_name2bis = os.path.join(getResultDirectory(),"flasA")
        self.c2bis.SetFrameFillColor(0)
        self.c2bis.SetFillColor(0);
        self.c2bis.SetBorderMode(0); 
        self.c2bis.SetGridx(1);
        self.c2bis.SetGridy(1);
        self.c2bis.cd()
        self.flasA = ROOT.TH1F('flasA','Constant for A cells;Laser Constant;N_{chan}',45,0.945,1.055)
        for x in FlasA:
            self.flasA.Fill(x)
        self.flasA.Draw()
        #print self.DiffA.GetMean()
        self.c2bis.Modified()
        #self.c2bis.Print("%s.eps" % (self.plot_name2bis))
        #self.c2bis.Print("%s.png" % (self.plot_name2bis))
        #self.c2bis.Print("%s.C" % (self.plot_name2bis))

        self.c3 = src.MakeCanvas.MakeCanvas()
        self.plot_name3 = os.path.join(getResultDirectory(),"DevBCM")
        self.c3.SetFrameFillColor(0)
        self.c3.SetFillColor(0);
        self.c3.SetBorderMode(0); 
        self.c3.SetGridx(1);
        self.c3.SetGridy(1);
        self.c3.cd()
        self.DiffBC = ROOT.TH1F('DevBC','Deviation for BC cells;Deviation;N_{chan}',101,-5.05,5.05)
        for x in Dev_diffBC:
            self.DiffBC.Fill(x)
        self.DiffBC.Draw()
        self.c3.Modified()
        #self.c3.Print("%s.eps" % (self.plot_name3))
        #self.c3.Print("%s.png" % (self.plot_name3))
        #self.c3.Print("%s.C" % (self.plot_name3))


        self.c4 = src.MakeCanvas.MakeCanvas()
        self.plot_name4 = os.path.join(getResultDirectory(),"DevDM")
        self.c4.SetFrameFillColor(0)
        self.c4.SetFillColor(0);
        self.c4.SetBorderMode(0); 
        self.c4.SetGridx(1);
        self.c4.SetGridy(1);
        self.c4.cd()
        self.DiffD = ROOT.TH1F('DevD','Deviation for D cells;Deviation;N_{chan}',101,-5.05,5.05)
        for x in Dev_diffD:
            self.DiffD.Fill(x)
        self.DiffD.Draw()
        self.c4.Modified()
        #self.c4.Print("%s.eps" % (self.plot_name4))
        #self.c4.Print("%s.png" % (self.plot_name4))
        #self.c4.Print("%s.C" % (self.plot_name4))

        
        self.c5A = src.MakeCanvas.MakeCanvas()
        self.plot_name5A = os.path.join(getResultDirectory(),"DevEM1")
        self.c5A.SetFrameFillColor(0)
        self.c5A.SetFillColor(0);
        self.c5A.SetBorderMode(0); 
        self.c5A.SetGridx(1);
        self.c5A.SetGridy(1);
        self.c5A.cd()
        self.DiffE1 = ROOT.TH1F('DevE1','Deviation for E1 cells;Deviation;N_{chan}',201,-20.05,10.05)
        for x in Dev_diffE1:
            self.DiffE1.Fill(x)
        self.DiffE1.Draw()
        self.c5A.Modified()
        #self.c5A.Print("%s.eps" % (self.plot_name5A))
        #self.c5A.Print("%s.png" % (self.plot_name5A))
        #self.c5A.Print("%s.C" % (self.plot_name5A))

        self.c5B = src.MakeCanvas.MakeCanvas()
        self.plot_name5B = os.path.join(getResultDirectory(),"DevEM2")
        self.c5B.SetFrameFillColor(0)
        self.c5B.SetFillColor(0);
        self.c5B.SetBorderMode(0); 
        self.c5B.SetGridx(1);
        self.c5B.SetGridy(1);
        self.c5B.cd()
        self.DiffE2 = ROOT.TH1F('DevE2','Deviation for E2 cells;Deviation;N_{chan}',201,-20.05,10.05)
        for x in Dev_diffE2:
            self.DiffE2.Fill(x)
        self.DiffE2.Draw()
        self.c5B.Modified()
        #self.c5B.Print("%s.eps" % (self.plot_name5B))
        #self.c5B.Print("%s.png" % (self.plot_name5B))
        #self.c5B.Print("%s.C" % (self.plot_name5B))

        self.c5C = src.MakeCanvas.MakeCanvas()
        self.plot_name5C = os.path.join(getResultDirectory(),"DevEM3")
        self.c5C.SetFrameFillColor(0)
        self.c5C.SetFillColor(0);
        self.c5C.SetBorderMode(0); 
        self.c5C.SetGridx(1);
        self.c5C.SetGridy(1);
        self.c5C.cd()
        self.DiffE3 = ROOT.TH1F('DevE3','Deviation for E3 cells;Deviation;N_{chan}',201,-20.05,10.05)
        for x in Dev_diffE3:
            self.DiffE3.Fill(x)
        self.DiffE3.Draw()
        self.c5C.Modified()
        #self.c5C.Print("%s.eps" % (self.plot_name5C))
        #self.c5C.Print("%s.png" % (self.plot_name5C))
        #self.c5C.Print("%s.C" % (self.plot_name5C))

        self.c5D = src.MakeCanvas.MakeCanvas()
        self.plot_name5D = os.path.join(getResultDirectory(),"DevEM4")
        self.c5D.SetFrameFillColor(0)
        self.c5D.SetFillColor(0);
        self.c5D.SetBorderMode(0); 
        self.c5D.SetGridx(1);
        self.c5D.SetGridy(1);
        self.c5D.cd()
        self.DiffE4 = ROOT.TH1F('DevE4','Deviation for E4 cells;Deviation;N_{chan}',201,-20.05,10.05)
        for x in Dev_diffE4:
            self.DiffE4.Fill(x)
        self.DiffE4.Draw()
        self.c5D.Modified()
        #self.c5D.Print("%s.eps" % (self.plot_name5D))
        #self.c5D.Print("%s.png" % (self.plot_name5D))
        #self.c5D.Print("%s.C" % (self.plot_name5D))

        self.c7 = src.MakeCanvas.MakeCanvas()
        self.plot_name7 = os.path.join(getResultDirectory(),"DevTot")
        self.c7.SetFrameFillColor(0)
        self.c7.SetFillColor(0);
        self.c7.SetBorderMode(0); 
        self.c7.SetGridx(1);
        self.c7.SetGridy(1);
        self.c7.cd()
        self.DiffTot = ROOT.TH1F('DevTot','Deviation;Deviation;N_{chan}',101,-5.05,25.05)
        for x in Dev_diffTot:
            self.DiffTot.Fill(x)
        self.DiffTot.Draw()
        self.c7.Modified()
        #self.c7.Print("%s.eps" % (self.plot_name7))
        #self.c7.Print("%s.png" % (self.plot_name7))
        #self.c7.Print("%s.C" % (self.plot_name7))


        self.c0 = src.MakeCanvas.MakeCanvas()
        self.plot_name0 = os.path.join(getResultDirectory(),"Diff_HGLG_LD")
        self.c0.SetFrameFillColor(0)
        self.c0.SetFillColor(0);
        self.c0.SetBorderMode(0); 
        self.c0.SetGridx(1);
        self.c0.SetGridy(1);
        self.c0.cd()
        self.DiffHGLGLD = ROOT.TH1F('Diff_HGLG_LD','Ratio of Deviation HG/LG;f_{HG}/f_{LG};N_{chan}',101,0.955,1.055)

        self.c10 = src.MakeCanvas.MakeCanvas()
        self.plot_name10 = os.path.join(getResultDirectory(),"Diff_HGLG_HD")
        self.c10.SetFrameFillColor(0)
        self.c10.SetFillColor(0);
        self.c10.SetBorderMode(0); 
        self.c10.SetGridx(1);
        self.c10.SetGridy(1);
        #self.c10.cd()
        self.DiffHGLGHD = ROOT.TH1F('Diff_HGLG_HD','Ratio of Deviation HG/LG;f_{HG}/f_{LG};N_{chan}',101,0.905,1.105)

        n_flag=0
        n_pb=0
        n_small=0


        for event in LgRun:
            
            pmt_region = str(LgRun[event].region)

            pmt_region_hl=''
            pmt_region_flag=''
            pmt_region_flaghg=''
            pmt_region_flaglg=''
            pmt_channel=''
            for i in range(20):
                pmt_region_hl+=pmt_region[i]

            for x in range(8,11):
                pmt_region_flag+=pmt_region[x]
                pmt_region_flaghg+=pmt_region[x]
                pmt_region_flaglg+=pmt_region[x]
            for x in range(13,19):
                pmt_region_flag+=pmt_region[x]
                pmt_region_flaglg+=pmt_region[x]
                pmt_region_flaghg+=pmt_region[x]

            for x in range(17,19):
                pmt_channel+=pmt_region[x]

            pmt_region_flaghg+=' high gain'
            pmt_region_flaglg+=' low gain'

            region=''
            pmt_region_hl+='highgain'

            for x in range(8,19):
                region+=pmt_region[x]

            Chan_flag[region]=[]

#For each channels we will define at least one flag
            if 'f_laser' in LgRun[event].data:

 # This is the DQ status list that affect laser data
#                DQstatus_list = ['No HV','Wrong HV','ADC masked (unspecified)','ADC dead','Data corruption','Severe data corruption','Severe stuck bit','Large LF noise','Very large LF noise','Channel masked (unspecified)','Bad timing','Stuck bit']
                DQstatus_list = ['No HV','ADC masked (unspecified)','ADC dead','Severe data corruption','Severe stuck bit','Very large LF noise','Channel masked (unspecified)']


#Channels with flag DQ problems
                Chan_DQ[region]=" "
                if 'problems' in LgRun[event].data:
                    for problem in LgRun[event].data['problems']:
                        if Chan_DQ[region]==" ":
                            Chan_DQ[region]=problem
                        else:
                            Chan_DQ[region]=Chan_DQ[region]+","+problem

                        if problem in DQstatus_list:
                            Chan_flag[region].append("DQ_pb")
                            Chan_flag[region].append(problem)
                            n_pb+=1

#Channels with flag OK_pb
                if 'is_OK' in LgRun[event].data:
                    if not LgRun[event].data['is_OK']:
                        Chan_flag[region].append("OK_pb")

                        n_pb+=1

#Channel with flag status_pb
                if (self.status):
                    if 'status' in LgRun[event].data:
                        if (LgRun[event].data['status']&0x10 or LgRun[event].data['status']&0x4):
                            Chan_flag[region].append("status_pb")
                            n_pb+=1

                    

#Channels with fast drift or fiber flags
                if ((pmt_region_flaglg in Flag_Chan) or (pmt_region_flag in Flag_Chan)):
                    if (pmt_region_flaglg in Flag_Chan):
                        if 'Fast Drift'in Flag_Chan[pmt_region_flaglg]:
                            Chan_flag[region].append("Fast Drift")
                            if 'deviation' in LgRun[event].data:
                                Chan_flag[region].append(str(LgRun[event].data['deviation']))
                            else:
                                Chan_flag[region].append("0.")
                            n_flag+=1
                    if (pmt_region_flag in Flag_Chan):
                        if ('Fast Drift'in Flag_Chan[pmt_region_flag] and 'Fiber' in Flag_Chan[pmt_region_flag]):
                            Chan_flag[region].append("Fast Drift")
                            if 'deviation' in LgRun[event].data:
                                Chan_flag[region].append(str(LgRun[event].data['deviation']))
                            else:
                                Chan_flag[region].append("0.")
                            Chan_flag[region].append("Fiber")
                            if 'deviation' in LgRun[event].data:
                                Chan_flag[region].append(str(LgRun[event].data['deviation']))
                            else:
                                Chan_flag[region].append("0.")
                            n_flag+=1
                        elif ('Fast Drift' in Flag_Chan[pmt_region_flag]): 
                            Chan_flag[region].append("Fast Drift")
                            if 'deviation' in LgRun[event].data:
                                Chan_flag[region].append(str(LgRun[event].data['deviation']))
                            else:
                                Chan_flag[region].append("0.")
                            n_flag+=1
                        elif ('Fiber' in Flag_Chan[pmt_region_flag]): 
                            Chan_flag[region].append("Fiber")
                            if 'deviation' in LgRun[event].data:
                                Chan_flag[region].append(str(LgRun[event].data['deviation']))
                            else:
                                Chan_flag[region].append("0.")
                            n_flag+=1

                

                if (LgRun[event].data['f_laser']!=1):

                    if ((pmt_region_hl in HgRun) and ('f_laser' in HgRun[pmt_region_hl].data)):

                        #To do some plot of difference between HG and LG
                        if math.fabs(LgRun[event].data['deviation'])>10:
                            self.DiffHGLGHD.Fill(LgRun[event].data['f_laser']/HgRun[pmt_region_hl].data['f_laser'])
                        else:
                            self.DiffHGLGLD.Fill(LgRun[event].data['f_laser']/HgRun[pmt_region_hl].data['f_laser'])
                     
                    #Channels with a deviatoin below a threshold
                    if ('LB' in pmt_region and (math.fabs(LgRun[event].data['deviation'])<0.5)) or ('EB' in pmt_region and (math.fabs(LgRun[event].data['deviation'])<0.5)):                                              
                        Chan_flag[region].append("No_Dev")
                        n_small+=1
                        
                    #Computation of deviation from HV
                    if self.HVref[pmt_region]>0 and self.HV[pmt_region]>0.:
                        HVG=(pow(self.HV[pmt_region]/self.HVref[pmt_region],self.beta[pmt_region])-1)*100
                    else:
                        HVG=0;

                     #Comparison of deviation with mean deviation and HV deviation for A cells   
                    if self.layer[pmt_region]=='A':

                        if ( (((math.fabs(LgRun[event].data['deviation'])-math.fabs(self.DiffA.GetMean()))>2.5) and (LgRun[event].data['deviation']*self.DiffA.GetMean()>=0)) or (((math.fabs(LgRun[event].data['deviation']-self.DiffA.GetMean()))>2.5) and (LgRun[event].data['deviation']*self.DiffA.GetMean()<0)) ):                   

#                        if (math.fabs(LgRun[event].data['deviation']-self.DiffA.GetMean())>2.5):                   #We look at compatibility between channel deviation and mean deviation of cells of same part A
                                
                            if ((math.fabs(LgRun[event].data['f_laser']*(1+HVG/100)-1)<=0.02 and math.fabs(LgRun[event].data['deviation'])<10) or (math.fabs(LgRun[event].data['f_laser']*(1+HVG/100)-1)<=0.1 and math.fabs(LgRun[event].data['deviation'])>10)):             #We look compatibility between HV and laser
                                Chan_flag[region].append("HVLas_comp")
                                Chan_flag[region].append(str(LgRun[event].data['deviation']))
                            else:
                                Chan_flag[region].append("Bad_Chan")
                                Chan_flag[region].append(str(LgRun[event].data['deviation']))
                        else:
                            Chan_flag[region].append("Mean_Dev_comp")           #Channel deviation compatible with mean deviation
                            Chan_flag[region].append(str(LgRun[event].data['deviation']))
 

                    #Comparison of deviation with mean deviation and HV deviation for BC cells   
                    elif (self.layer[pmt_region]=='B' or self.layer[pmt_region]=='C'):
                                
                        if ( (((math.fabs(LgRun[event].data['deviation'])-math.fabs(self.DiffBC.GetMean()))>2.) and (LgRun[event].data['deviation']*self.DiffBC.GetMean()>=0)) or (((math.fabs(LgRun[event].data['deviation']-self.DiffBC.GetMean()))>2.) and (LgRun[event].data['deviation']*self.DiffBC.GetMean()<0)) ):                   

#                        if (math.fabs(LgRun[event].data['deviation']-self.DiffBC.GetMean())>2.):                  #We look at compatibility between channel deviation and mean deviation of cells of same part BC
                                
                            if ((math.fabs(LgRun[event].data['f_laser']*(1+HVG/100)-1)<=0.02 and math.fabs(LgRun[event].data['deviation'])<10) or (math.fabs(LgRun[event].data['f_laser']*(1+HVG/100)-1)<=0.1 and math.fabs(LgRun[event].data['deviation'])>10)):             #We look compatibility between HV and laser
                                Chan_flag[region].append("HVLas_comp")
                                Chan_flag[region].append(str(LgRun[event].data['deviation']))
                            else:
                                Chan_flag[region].append("Bad_Chan")
                                Chan_flag[region].append(str(LgRun[event].data['deviation']))  
                        else:
                            Chan_flag[region].append("Mean_Dev_comp")                  #Channel deviation compatible with mean deviation
                            Chan_flag[region].append(str(LgRun[event].data['deviation']))

                    #Comparison of deviation with mean deviation and HV deviation for D cells  
                    elif self.layer[pmt_region]=='D':
                            
                        if ( (((math.fabs(LgRun[event].data['deviation'])-math.fabs(self.DiffD.GetMean()))>1.7) and (LgRun[event].data['deviation']*self.DiffD.GetMean()>=0)) or (((math.fabs(LgRun[event].data['deviation']-self.DiffD.GetMean()))>1.7) and (LgRun[event].data['deviation']*self.DiffD.GetMean()<0)) ):                   
#We look at compatibility between channel deviation and mean deviation of cells of same part D
#                        if (math.fabs(LgRun[event].data['deviation']-self.DiffBC.GetMean())>1.7):                  #We look at compatibility between channel deviation and mean deviation of cells of same part BC
  
                            if ((math.fabs(LgRun[event].data['f_laser']*(1+HVG/100)-1)<=0.02 and math.fabs(LgRun[event].data['deviation'])<10) or (math.fabs(LgRun[event].data['f_laser']*(1+HVG/100)-1)<=0.1 and math.fabs(LgRun[event].data['deviation'])>10)):             #We look compatibility between HV and laser
                                Chan_flag[region].append("HVLas_comp")
                                Chan_flag[region].append(str(LgRun[event].data['deviation']))                                    
                            else:
                                Chan_flag[region].append("Bad_Chan")
                                Chan_flag[region].append(str(LgRun[event].data['deviation']))
                        else:
                            Chan_flag[region].append("Mean_Dev_comp")                #Channel deviation compatible with mean deviation
                            Chan_flag[region].append(str(LgRun[event].data['deviation']))
  

                    elif self.layer[pmt_region] in ['E1']:             #We look at compatibility between channel deviation and mean deviation of cells of same part E

#                        if (math.fabs(LgRun[event].data['deviation']-self.DiffE.GetMean())>7.5):
                        if ( ( ((math.fabs(LgRun[event].data['deviation'])-math.fabs(self.DiffE1.GetMean()))>(math.fabs(self.DiffE1.GetMean()))) and (LgRun[event].data['deviation']*self.DiffE1.GetMean()>=0) ) or ( ((math.fabs(LgRun[event].data['deviation']-self.DiffE1.GetMean()))>(math.fabs(self.DiffE1.GetMean()))) and (LgRun[event].data['deviation']*self.DiffE1.GetMean()<0) ) ):                   

                                
                            if ((math.fabs(LgRun[event].data['f_laser']*(1+HVG/100)-1)<=0.04 and math.fabs(LgRun[event].data['deviation'])<10) or (math.fabs(LgRun[event].data['f_laser']*(1+HVG/100)-1)<=0.2 and math.fabs(LgRun[event].data['deviation'])>10)):             #We look compatibility between HV and laser
                                Chan_flag[region].append("HVLas_comp")
                                Chan_flag[region].append(str(LgRun[event].data['deviation']))                               
                            else:
                                Chan_flag[region].append("Bad_Chan") 
                                Chan_flag[region].append(str(LgRun[event].data['deviation']))                                
                        else:
                            Chan_flag[region].append("Mean_Dev_comp")             #Channel deviation compatible with mean deviation
                            Chan_flag[region].append(str(LgRun[event].data['deviation']))

                    elif self.layer[pmt_region] in ['E2']:             #We look at compatibility between channel deviation and mean deviation of cells of same part E

#                        if (math.fabs(LgRun[event].data['deviation']-self.DiffE.GetMean())>7.5):
                        if ( ( ((math.fabs(LgRun[event].data['deviation'])-math.fabs(self.DiffE2.GetMean()))>(math.fabs(self.DiffE2.GetMean()))) and (LgRun[event].data['deviation']*self.DiffE2.GetMean()>=0) ) or ( ((math.fabs(LgRun[event].data['deviation']-self.DiffE2.GetMean()))>(math.fabs(self.DiffE2.GetMean()))) and (LgRun[event].data['deviation']*self.DiffE2.GetMean()<0) ) ):                   

                                
                            if ((math.fabs(LgRun[event].data['f_laser']*(1+HVG/100)-1)<=0.04 and math.fabs(LgRun[event].data['deviation'])<10) or (math.fabs(LgRun[event].data['f_laser']*(1+HVG/100)-1)<=0.2 and math.fabs(LgRun[event].data['deviation'])>10)):             #We look compatibility between HV and laser
                                Chan_flag[region].append("HVLas_comp")
                                Chan_flag[region].append(str(LgRun[event].data['deviation']))                               
                            else:
                                Chan_flag[region].append("Bad_Chan") 
                                Chan_flag[region].append(str(LgRun[event].data['deviation']))                                
                        else:
                            Chan_flag[region].append("Mean_Dev_comp")             #Channel deviation compatible with mean deviation
                            Chan_flag[region].append(str(LgRun[event].data['deviation']))

                    elif self.layer[pmt_region] in ['E3']:             #We look at compatibility between channel deviation and mean deviation of cells of same part E

#                        if (math.fabs(LgRun[event].data['deviation']-self.DiffE.GetMean())>7.5):
                        if ( ( ((math.fabs(LgRun[event].data['deviation'])-math.fabs(self.DiffE3.GetMean()))>(math.fabs(self.DiffE3.GetMean()))) and (LgRun[event].data['deviation']*self.DiffE3.GetMean()>=0) ) or ( ((math.fabs(LgRun[event].data['deviation']-self.DiffE3.GetMean()))>(math.fabs(self.DiffE3.GetMean()))) and (LgRun[event].data['deviation']*self.DiffE3.GetMean()<0) ) ):                   

                                
                            if ((math.fabs(LgRun[event].data['f_laser']*(1+HVG/100)-1)<=0.04 and math.fabs(LgRun[event].data['deviation'])<10) or (math.fabs(LgRun[event].data['f_laser']*(1+HVG/100)-1)<=0.2 and math.fabs(LgRun[event].data['deviation'])>10)):             #We look compatibility between HV and laser
                                Chan_flag[region].append("HVLas_comp")
                                Chan_flag[region].append(str(LgRun[event].data['deviation']))                               
                            else:
                                Chan_flag[region].append("Bad_Chan") 
                                Chan_flag[region].append(str(LgRun[event].data['deviation']))                                
                        else:
                            Chan_flag[region].append("Mean_Dev_comp")             #Channel deviation compatible with mean deviation
                            Chan_flag[region].append(str(LgRun[event].data['deviation']))

                    elif self.layer[pmt_region] in ['E4']:             #We look at compatibility between channel deviation and mean deviation of cells of same part E

#                        if (math.fabs(LgRun[event].data['deviation']-self.DiffE.GetMean())>7.5):
                        if ( ( ((math.fabs(LgRun[event].data['deviation'])-math.fabs(self.DiffE4.GetMean()))>(math.fabs(self.DiffE4.GetMean()))) and (LgRun[event].data['deviation']*self.DiffE4.GetMean()>=0) ) or ( ((math.fabs(LgRun[event].data['deviation']-self.DiffE4.GetMean()))>(math.fabs(self.DiffE4.GetMean()))) and (LgRun[event].data['deviation']*self.DiffE4.GetMean()<0) ) ):                   

                                
                            if ((math.fabs(LgRun[event].data['f_laser']*(1+HVG/100)-1)<=0.04 and math.fabs(LgRun[event].data['deviation'])<10) or (math.fabs(LgRun[event].data['f_laser']*(1+HVG/100)-1)<=0.2 and math.fabs(LgRun[event].data['deviation'])>10)):             #We look compatibility between HV and laser
                                Chan_flag[region].append("HVLas_comp")
                                Chan_flag[region].append(str(LgRun[event].data['deviation']))                               
                            else:
                                Chan_flag[region].append("Bad_Chan") 
                                Chan_flag[region].append(str(LgRun[event].data['deviation']))                                
                        else:
                            Chan_flag[region].append("Mean_Dev_comp")             #Channel deviation compatible with mean deviation
                            Chan_flag[region].append(str(LgRun[event].data['deviation']))

                    elif self.layer[pmt_region]=='MBTS':
                        Chan_flag[region].append("MBTS") 
                        Chan_flag[region].append(str(LgRun[event].data['deviation']))                     
                    else:

                        if ((math.fabs(LgRun[event].data['f_laser']*(1+HVG/100)-1)<=0.02 and math.fabs(LgRun[event].data['deviation'])<10) or (math.fabs(LgRun[event].data['f_laser']*(1+HVG/100)-1)<=0.1 and math.fabs(LgRun[event].data['deviation'])>10)):
                            Chan_flag[region].append("HVLas_comp")
                            Chan_flag[region].append(str(LgRun[event].data['deviation']))
                                                                        
                        else:
                            Chan_flag[region].append("Bad_Chan")
                            Chan_flag[region].append(str(LgRun[event].data['deviation']))

                else :
                    Chan_flag[region].append("f_laser=1")

            else :
                Chan_flag[region].append("No laser")

            
            # force specified channels to be calibrated
            this_module=''
            for x in range(8,15):
                this_module += pmt_region[x]

            if (this_module in self.forceModule):

                if (Chan_flag[region][0]=="Bad_Chan" or Chan_flag[region][0]=="Fast Drift"):
                    print('Warning: Channel ', region,' with flag ',Chan_flag[region][0],' will be calibrated (ForceModule option) with deviation = ', LgRun[event].data['deviation'],'%')
                    Chan_flag[region][0]="Mean_Dev_comp"



            # puting flags in problems #BDE
            # we retrive the flag and add it to problems: useful to make plots of problematic channels
            this_Ch_flag = Chan_flag[region][0]
                
            if (not (this_Ch_flag=="Bad_Chan" and (math.fabs(LgRun[event].data['deviation'])<10))) and (not (this_Ch_flag=="HVLas_comp" and (math.fabs(LgRun[event].data['deviation'])<5))): #these bad cases are ignored
                if (this_Ch_flag=="Bad_Chan"):
                    this_Ch_flag = "Unexplained drift"
                if (this_Ch_flag=="Fast Drift"):
                    this_Ch_flag = "Nonlinear Drift"
                if (this_Ch_flag=="HVLas_comp"):
                    this_Ch_flag = "HV Drift"

                if 'problems' in LgRun[event].data:
                    LgRun[event].data['problems'].add(this_Ch_flag);
                else:
                    LgRun[event].data['problems']=set();
                    LgRun[event].data['problems'].add(this_Ch_flag);


        #self.c0.cd()
        #self.DiffHGLGLD.Draw()
        #self.c0.Modified()
        #self.c0.Print("%s.eps" % (self.plot_name0))
        #self.c0.Print("%s.png" % (self.plot_name0))
        #self.c0.Print("%s.C" % (self.plot_name0))

        #self.DiffHGLGHD.Draw()
        #self.c10.Modified()
        #self.c10.Print("%s.eps" % (self.plot_name10))
        #self.c10.Print("%s.png" % (self.plot_name10))
        #self.c10.Print("%s.C" % (self.plot_name10))

        good_chan=[]
        bad_chan=[]
        unknown_chan=[]

        dqpb=0
        okpb=0
        badpb=0
        statpb=0
        las1=0
        nolaser=0
        nodev=0
        badchan=0
        fastdr=0
        fib=0
        hglginc=0
        hvlascomp=0
        meandev=0
        okishchan=0
        badchan_low=0
        badchan_med=0
        badchan_high=0
        fastdr_low=0
        fastdr_med=0
        fastdr_high=0
        fib_low=0
        fib_med=0
        fib_high=0
        hglginc_low=0
        hglginc_med=0
        hglginc_high=0
        hvlascomp_low=0
        hvlascomp_med=0
        hvlascomp_high=0
        meandev_low=0
        meandev_med=0
        meandev_high=0
        mbts_cell=0

        #I count the number of channels in the different categories ...
        for u in Chan_flag:
            Chanfl=Chan_flag[u][0]
            Chan_dev=Chan_flag[u]
            if ("DQ_pb" in Chanfl or "OK_pb" in Chanfl or "status_pb" in Chanfl or "f_laser=1" in Chanfl or "No laser" in Chanfl or "No_Dev" in Chanfl):
                bad_chan.append(u)
            elif ("Emerg" in Chanfl or  "Bad_Chan" in Chanfl or "Fast Drift" in Chanfl or "Fiber" in Chanfl or "HGLG_incomp" in Chanfl):
                unknown_chan.append(u)
            elif ("HVLas_comp" in Chanfl or "Mean_Dev_comp" in Chanfl):
                good_chan.append(x)

            if "DQ_pb" in Chanfl:
                dqpb+=1
            elif "OK_pb" in Chanfl:
                okpb+=1
            elif "status_pb" in Chanfl:
                statpb+=1
            elif "f_laser=1" in Chanfl:
                las1+=1
            elif "No laser" in Chanfl:
                nolaser+=1
            elif "No_Dev" in Chanfl:
                nodev+=1
            elif ("Bad_Chan" in Chanfl):
                badchan+=1
            elif ("Fast Drift" in Chanfl):
                fastdr+=1
            elif ("Fiber" in Chanfl):
                fib+=1
            elif ("HGLG_incomp" in Chanfl):
                hglginc+=1
            elif ("HVLas_comp" in Chanfl):
                hvlascomp+=1
            elif ("Mean_Dev_comp" in Chanfl):
                meandev+=1
            elif ("MBTS" in Chanfl):
                mbts_cell+=1    

            bool_dev=0
            for r in Chan_flag[u]:
                if ("Deviation" in r) and (bool_dev==0):
                    bool_dev=1
                    dev=''
                    for i in range(10,len(r)-1):
                        dev+=r[i]
                    devi=float(dev)
                    if math.fabs(devi)<5:
                        if ("Bad_Chan" in Chanfl):
                            badchan_low+=1
                        elif ("Fast Drift" in Chanfl):
                            fastdr_low+=1
                        elif ("Fiber" in Chanfl):
                            fib_low+=1
                        elif ("HGLG_incomp" in Chanfl):
                            hglginc_low+=1
                        elif ("HVLas_comp" in Chanfl):
                            hvlascomp_low+=1
                        elif ("Mean_Dev_comp" in Chanfl):
                            meandev_low+=1
                    elif math.fabs(devi)<10:
                        if ("Bad_Chan" in Chanfl):
                            badchan_med+=1
                        elif ("Fast Drift" in Chanfl):
                            fastdr_med+=1
                        elif ("Fiber" in Chanfl):
                            fib_med+=1
                        elif ("HGLG_incomp" in Chanfl):
                            hglginc_med+=1
                        elif ("HVLas_comp" in Chanfl):
                            hvlascomp_med+=1
                        elif ("Mean_Dev_comp" in Chanfl):
                            meandev_med+=1
                    else:
                        if ("Bad_Chan" in Chanfl):
                            badchan_high+=1
                        elif ("Fast Drift" in Chanfl):
                            fastdr_high+=1
                        elif ("Fiber" in Chanfl):
                            fib_high+=1
                        elif ("HGLG_incomp" in Chanfl):
                            hglginc_high+=1
                        elif ("HVLas_comp" in Chanfl):
                            hvlascomp_high+=1
                        elif ("Mean_Dev_comp" in Chanfl):
                            meandev_high+=1

        print("-------------------------------------------------------------")
        print("")
        print('DQ_pb',dqpb)
        print('')
        print('OK_pb',okpb)
        print("")
        print('status_pb',statpb)
        print('')
        print('f_laser=1',las1)
        print('')
        print('No laser',nolaser)
        print('')
        print('No_Dev',nodev)
        print('')
        print('Bad_Chan',badchan)
        print('Bad chan low',badchan_low)
        print('Bad chan med',badchan_med)
        print('Bad chan high',badchan_high)
        print('')
        print('Fast Drift',fastdr)
        print('Fast Drift low',fastdr_low)
        print('Fast Drift med',fastdr_med)
        print('Fast Drift high',fastdr_high)
        print('')
        print('Fiber',fib)
        print('Fiber low',fib_low)
        print('Fiber med',fib_med)
        print('Fiber high',fib_high)
        print('')
        print('HGLG_incomp',hglginc)
        print('HGLG_incomp low',hglginc_low)
        print('HGLG_incomp med',hglginc_med)
        print('HGLG_incomp high',hglginc_high)
        print('')
        print('HVLas_comp',hvlascomp)
        print('HVLas_comp low',hvlascomp_low)
        print('HVLas_comp med',hvlascomp_med)
        print('HVLas_comp high',hvlascomp_high)
        print('')
        print('Mean_Dev_comp',meandev)
        print('Mean_Dev_comp low',meandev_low)
        print('Mean_Dev_comp med',meandev_med)
        print('Mean_Dev_comp high',meandev_high)
        print('')
        print('MBTS cells ',mbts_cell)
        print('')
        print("-------------------------------------------------------------")

        self.c=src.MakeCanvas.MakeCanvas()
        self.plot_name = os.path.join(getResultDirectory(),"LBA")
        self.c.SetFillColor(0)
        self.c.SetBorderMode(0)                   
        self.c.cd()
        self.c.Divide(8,8)
        global Mod_plot
        Mod_plot={}

        #Creation of the map of the different partition which explicit for each modules the numbers of channels in the three main categories
        for i in range(64):
            if i<9:
                Mod_plot["LBA0"+str(i+1)]=[0,0,0]
            else:
                Mod_plot["LBA"+str(i+1)]=[0,0,0]
        for x in Chan_flag:
            if "LBA" in x:
                if (Chan_flag[x][0]=="DQ_pb" or Chan_flag[x][0]=="OK_pb"or Chan_flag[x][0]=="status_pb" or Chan_flag[x][0]=="MBTS"):
                    Mod_plot["LBA"+x[5]+x[6]][0]+=1
                elif (Chan_flag[x][0]=="f_laser=1" or Chan_flag[x][0]=="No Laser" or Chan_flag[x][0]=="No_Dev"):
                    Mod_plot["LBA"+x[5]+x[6]][0]+=1
                elif (Chan_flag[x][0]=="Mean_Dev_comp" or Chan_flag[x][0]=="HVLas_comp"):
                    Mod_plot["LBA"+x[5]+x[6]][1]+=1
                elif (Chan_flag[x][0]=="Emerg?" or Chan_flag[x][0]=="Bad_Chan" or Chan_flag[x][0]=="Fast Drift" or Chan_flag[x][0]=="Fiber" or Chan_flag[x][0]=="HGLG_incomp"):
                    Mod_plot["LBA"+x[5]+x[6]][2]+=1


        self.val=[]
        self.mod=[]
        Value=""
        for i in range(64):
            mod_name=""
            self.c.cd(i+1)
            if i<9:
                mod_name="LBA0"
            else:
                mod_name="LBA"
            if (Mod_plot[mod_name+str(i+1)][1]==0 and Mod_plot[mod_name+str(i+1)][2]==0 ):
                Value=str(Mod_plot[mod_name+str(i+1)][0])+"/"+str(Mod_plot[mod_name+str(i+1)][1])+"/"+str(Mod_plot[mod_name+str(i+1)][2])
                self.c.cd(i+1).SetFillColor(kGreen)
                self.mod.append(ROOT.TText(0.2,0.5,mod_name+str(i+1)))
                self.val.append(ROOT.TText(0.2,0.2,Value))
                self.mod[i].SetTextSize(.25)
                self.val[i].SetTextSize(.25)
                self.mod[i].Draw()
                self.val[i].Draw("same")
                self.c.cd(i+1).Modified()
            elif Mod_plot[mod_name+str(i+1)][2]!=0:
                Value=str(Mod_plot[mod_name+str(i+1)][0])+"/"+str(Mod_plot[mod_name+str(i+1)][1])+"/"+str(Mod_plot[mod_name+str(i+1)][2])
                self.c.cd(i+1).SetFillColor(ROOT.kRed)
                self.mod.append(ROOT.TText(0.2,0.5,mod_name+str(i+1)))
                self.val.append(ROOT.TText(0.2,0.2,Value))
                self.mod[i].SetTextSize(.25)
                self.val[i].SetTextSize(.25)
                self.mod[i].Draw()
                self.val[i].Draw("same")
                self.c.cd(i+1).Modified()
            elif Mod_plot[mod_name+str(i+1)][1]!=0:
                Value=str(Mod_plot[mod_name+str(i+1)][0])+"/"+str(Mod_plot[mod_name+str(i+1)][1])+"/"+str(Mod_plot[mod_name+str(i+1)][2])
                self.c.cd(i+1).SetFillColor(kOrange)
                self.mod.append(ROOT.TText(0.2,0.5,mod_name+str(i+1)))
                self.val.append(ROOT.TText(0.2,0.2,Value))
                self.mod[i].SetTextSize(.25)
                self.val[i].SetTextSize(.25)
                self.mod[i].Draw()
                self.val[i].Draw("same")
                self.c.cd(i+1).Modified()

        self.c.SetFillColor(0)
        self.c.Modified()
        self.c.Print("%s.eps" % (self.plot_name))
        self.c.Print("%s.png" % (self.plot_name))
        self.c.Print("%s.C" % (self.plot_name))



        self.c=src.MakeCanvas.MakeCanvas()
        self.plot_name = os.path.join(getResultDirectory(),"LBC")
        self.c.SetFillColor(0)
        self.c.SetBorderMode(0)                   
        self.c.cd()
        self.c.Divide(8,8)
        Mod_plot={}

        for i in range(64):
            if i<9:
                Mod_plot["LBC0"+str(i+1)]=[0,0,0]
            else:
                Mod_plot["LBC"+str(i+1)]=[0,0,0]
        for x in Chan_flag:
            if "LBC" in x:
                if (Chan_flag[x][0]=="DQ_pb" or Chan_flag[x][0]=="OK_pb" or Chan_flag[x][0]=="status_pb" or Chan_flag[x][0]=="MBTS"):   
                    Mod_plot["LBC"+x[5]+x[6]][0]+=1
                elif (Chan_flag[x][0]=="f_laser=1" or Chan_flag[x][0]=="No Laser" or Chan_flag[x][0]=="No_Dev"):
                    Mod_plot["LBC"+x[5]+x[6]][0]+=1
                elif (Chan_flag[x][0]=="Mean_Dev_comp" or Chan_flag[x][0]=="HVLas_comp"):
                    Mod_plot["LBC"+x[5]+x[6]][1]+=1
                elif (Chan_flag[x][0]=="Emerg?" or Chan_flag[x][0]=="Bad_Chan" or Chan_flag[x][0]=="Fast Drift" or Chan_flag[x][0]=="Fiber" or Chan_flag[x][0]=="HGLG_incomp"):
                    Mod_plot["LBC"+x[5]+x[6]][2]+=1
                   

        self.val=[]
        self.mod=[]
        Value=""
        for i in range(64):
            mod_name=""
            self.c.cd(i+1)
            if i<9:
                mod_name="LBC0"
            else:
                mod_name="LBC"
            if (Mod_plot[mod_name+str(i+1)][1]==0 and Mod_plot[mod_name+str(i+1)][2]==0): 
                Value=str(Mod_plot[mod_name+str(i+1)][0])+"/"+str(Mod_plot[mod_name+str(i+1)][1])+"/"+str(Mod_plot[mod_name+str(i+1)][2])
                self.c.cd(i+1).SetFillColor(kGreen)
                self.mod.append(ROOT.TText(0.2,0.5,mod_name+str(i+1)))
                self.val.append(ROOT.TText(0.2,0.2,Value))
                self.mod[i].SetTextSize(.25)
                self.val[i].SetTextSize(.25)
                self.mod[i].Draw()
                self.val[i].Draw("same")
                self.c.cd(i+1).Modified()
            elif Mod_plot[mod_name+str(i+1)][2]!=0:
                Value=str(Mod_plot[mod_name+str(i+1)][0])+"/"+str(Mod_plot[mod_name+str(i+1)][1])+"/"+str(Mod_plot[mod_name+str(i+1)][2])
                self.c.cd(i+1).SetFillColor(ROOT.kRed)
                self.mod.append(ROOT.TText(0.2,0.5,mod_name+str(i+1)))
                self.val.append(ROOT.TText(0.2,0.2,Value))
                self.mod[i].SetTextSize(.25)
                self.val[i].SetTextSize(.25)
                self.mod[i].Draw()
                self.val[i].Draw("same")
                self.c.cd(i+1).Modified()
            elif Mod_plot[mod_name+str(i+1)][1]!=0:
                Value=str(Mod_plot[mod_name+str(i+1)][0])+"/"+str(Mod_plot[mod_name+str(i+1)][1])+"/"+str(Mod_plot[mod_name+str(i+1)][2])
                self.c.cd(i+1).SetFillColor(kOrange)
                self.mod.append(ROOT.TText(0.2,0.5,mod_name+str(i+1)))
                self.val.append(ROOT.TText(0.2,0.2,Value))
                self.mod[i].SetTextSize(.25)
                self.val[i].SetTextSize(.25)
                self.mod[i].Draw()
                self.val[i].Draw("same")
                self.c.cd(i+1).Modified()

        self.c.SetFillColor(0)
        self.c.Modified()
        self.c.Print("%s.eps" % (self.plot_name))
        self.c.Print("%s.png" % (self.plot_name))
        self.c.Print("%s.C" % (self.plot_name))



        self.c=src.MakeCanvas.MakeCanvas()
        self.plot_name = os.path.join(getResultDirectory(),"EBA")
        self.c.SetFillColor(0)
        self.c.SetBorderMode(0)                   
        self.c.cd()
        self.c.Divide(8,8)
        Mod_plot={}

        for i in range(64):
            if i<9:
                Mod_plot["EBA0"+str(i+1)]=[0,0,0]
            else:
                Mod_plot["EBA"+str(i+1)]=[0,0,0]
        for x in Chan_flag:
            if "EBA" in x:
                if (Chan_flag[x][0]=="DQ_pb" or Chan_flag[x][0]=="OK_pb"  or Chan_flag[x][0]=="status_pb" or Chan_flag[x][0]=="MBTS"):
                    Mod_plot["EBA"+x[5]+x[6]][0]+=1
                elif (Chan_flag[x][0]=="f_laser=1" or Chan_flag[x][0]=="No Laser" or Chan_flag[x][0]=="No_Dev"):
                    Mod_plot["EBA"+x[5]+x[6]][0]+=1
                elif (Chan_flag[x][0]=="Mean_Dev_comp" or Chan_flag[x][0]=="HVLas_comp"):
                    Mod_plot["EBA"+x[5]+x[6]][1]+=1
                elif (Chan_flag[x][0]=="Emerg?" or Chan_flag[x][0]=="Bad_Chan" or Chan_flag[x][0]=="Fast Drift" or Chan_flag[x][0]=="Fiber" or Chan_flag[x][0]=="HGLG_incomp"):
                    Mod_plot["EBA"+x[5]+x[6]][2]+=1

        self.val=[]
        self.mod=[]
        Value=""
        for i in range(64):
            mod_name=""
            self.c.cd(i+1)
            if i<9:
                mod_name="EBA0"
            else:
                mod_name="EBA"
            if (Mod_plot[mod_name+str(i+1)][1]==0 and Mod_plot[mod_name+str(i+1)][2]==0):
                Value=str(Mod_plot[mod_name+str(i+1)][0])+"/"+str(Mod_plot[mod_name+str(i+1)][1])+"/"+str(Mod_plot[mod_name+str(i+1)][2])
                self.c.cd(i+1).SetFillColor(kGreen)
                self.mod.append(ROOT.TText(0.2,0.5,mod_name+str(i+1)))
                self.val.append(ROOT.TText(0.2,0.2,Value))
                self.mod[i].SetTextSize(.25)
                self.val[i].SetTextSize(.25)
                self.mod[i].Draw()
                self.val[i].Draw("same")
                self.c.cd(i+1).Modified()
            elif Mod_plot[mod_name+str(i+1)][2]!=0:
                Value=str(Mod_plot[mod_name+str(i+1)][0])+"/"+str(Mod_plot[mod_name+str(i+1)][1])+"/"+str(Mod_plot[mod_name+str(i+1)][2])
                self.c.cd(i+1).SetFillColor(ROOT.kRed)
                self.mod.append(ROOT.TText(0.2,0.5,mod_name+str(i+1)))
                self.val.append(ROOT.TText(0.2,0.2,Value))
                self.mod[i].SetTextSize(.25)
                self.val[i].SetTextSize(.25)
                self.mod[i].Draw()
                self.val[i].Draw("same")
                self.c.cd(i+1).Modified()
            elif Mod_plot[mod_name+str(i+1)][1]!=0:
                Value=str(Mod_plot[mod_name+str(i+1)][0])+"/"+str(Mod_plot[mod_name+str(i+1)][1])+"/"+str(Mod_plot[mod_name+str(i+1)][2])
                self.c.cd(i+1).SetFillColor(kOrange)
                self.mod.append(ROOT.TText(0.2,0.5,mod_name+str(i+1)))
                self.val.append(ROOT.TText(0.2,0.2,Value))
                self.mod[i].SetTextSize(.25)
                self.val[i].SetTextSize(.25)
                self.mod[i].Draw()
                self.val[i].Draw("same")
                self.c.cd(i+1).Modified()

        self.c.SetFillColor(0)
        self.c.Modified()
        self.c.Print("%s.eps" % (self.plot_name))
        self.c.Print("%s.png" % (self.plot_name))
        self.c.Print("%s.C" % (self.plot_name))



        self.c=src.MakeCanvas.MakeCanvas()
        self.plot_name = os.path.join(getResultDirectory(),"EBC")
        self.c.SetFillColor(0)
        self.c.SetBorderMode(0)                   
        self.c.cd()
        self.c.Divide(8,8)
        Mod_plot={}

        for i in range(64):
            if i<9:
                Mod_plot["EBC0"+str(i+1)]=[0,0,0]
            else:
                Mod_plot["EBC"+str(i+1)]=[0,0,0]
        for x in Chan_flag:
            if "EBC" in x:
                if (Chan_flag[x][0]=="DQ_pb" or Chan_flag[x][0]=="OK_pb" or Chan_flag[x][0]=="status_pb" or Chan_flag[x][0]=="MBTS"):
                    Mod_plot["EBC"+x[5]+x[6]][0]+=1
                elif (Chan_flag[x][0]=="f_laser=1" or Chan_flag[x][0]=="No Laser" or Chan_flag[x][0]=="No_Dev"):
                    Mod_plot["EBC"+x[5]+x[6]][0]+=1
                elif (Chan_flag[x][0]=="Mean_Dev_comp" or Chan_flag[x][0]=="HVLas_comp"):
                    Mod_plot["EBC"+x[5]+x[6]][1]+=1
                elif (Chan_flag[x][0]=="Emerg?" or Chan_flag[x][0]=="Bad_Chan" or Chan_flag[x][0]=="Fast Drift" or Chan_flag[x][0]=="Fiber" or Chan_flag[x][0]=="HGLG_incomp"):
                    Mod_plot["EBC"+x[5]+x[6]][2]+=1

        self.val=[]
        self.mod=[]
        Value=""
        for i in range(64):
            mod_name=""
            self.c.cd(i+1)
            if i<9:
                mod_name="EBC0"
            else:
                mod_name="EBC"
            if (Mod_plot[mod_name+str(i+1)][1]==0 and Mod_plot[mod_name+str(i+1)][2]==0): 
                Value=str(Mod_plot[mod_name+str(i+1)][0])+"/"+str(Mod_plot[mod_name+str(i+1)][1])+"/"+str(Mod_plot[mod_name+str(i+1)][2])
                self.c.cd(i+1).SetFillColor(kGreen)
                self.mod.append(ROOT.TText(0.2,0.5,mod_name+str(i+1)))
                self.val.append(ROOT.TText(0.2,0.2,Value))
                self.mod[i].SetTextSize(.25)
                self.val[i].SetTextSize(.25)
                self.mod[i].Draw()
                self.val[i].Draw("same")
                self.c.cd(i+1).Modified()
            elif Mod_plot[mod_name+str(i+1)][2]!=0:
                Value=str(Mod_plot[mod_name+str(i+1)][0])+"/"+str(Mod_plot[mod_name+str(i+1)][1])+"/"+str(Mod_plot[mod_name+str(i+1)][2])
                self.c.cd(i+1).SetFillColor(ROOT.kRed)
                self.mod.append(ROOT.TText(0.2,0.5,mod_name+str(i+1)))
                self.val.append(ROOT.TText(0.2,0.2,Value))
                self.mod[i].SetTextSize(.25)
                self.val[i].SetTextSize(.25)
                self.mod[i].Draw()
                self.val[i].Draw("same")
                self.c.cd(i+1).Modified()
            elif Mod_plot[mod_name+str(i+1)][1]!=0:
                Value=str(Mod_plot[mod_name+str(i+1)][0])+"/"+str(Mod_plot[mod_name+str(i+1)][1])+"/"+str(Mod_plot[mod_name+str(i+1)][2])
                self.c.cd(i+1).SetFillColor(kOrange)
                self.mod.append(ROOT.TText(0.2,0.5,mod_name+str(i+1)))
                self.val.append(ROOT.TText(0.2,0.2,Value))
                self.mod[i].SetTextSize(.25)
                self.val[i].SetTextSize(.25)
                self.mod[i].Draw()
                self.val[i].Draw("same")
                self.c.cd(i+1).Modified()

        self.c.SetFillColor(0)
        self.c.Modified()
        self.c.Print("%s.eps" % (self.plot_name))
        self.c.Print("%s.png" % (self.plot_name))
        self.c.Print("%s.C" % (self.plot_name))
        

#Creation of the txt file as output
        self.opfile.write("Part  Mod  Chan  Flag  Deviation \n")
        summary = "LASER Status Summary based on run  \n ============ Problematic Channels excluded by default from calibration, To be checked =================\n"
        summary300 = "\n Unexplained significant drifts \n Part Mod Chan Deviation | Existing Flags \n"
        summary301 = "\n Channels with fast drifts\n Part Mod Chan Deviation | Existing Flags \n"
        summary201 = "\n Laser coherent with HV drifts\n Part Mod Chan Deviation | Existing Flags \n"
        summary299 = "Unexplained small drifts\n Part Mod Chan Deviation | Existing Flags \n"
        nbad=0
        n299=0
        for x in Chan_flag:
            part=x[0]+x[1]+x[2]
            mod=x[5]+x[6]
            chann=x[9]+x[10]
            devi="0"
            if (len(Chan_flag[x])>1):
                devi=Chan_flag[x][1]
            if self.printall:
                if (Chan_flag[x][0]=="f_laser=1"):
                    text="%s   %s   %s    100 \n"%(part,mod,chann)
                    self.opfile.write(text)
                elif (Chan_flag[x][0]=="No laser"):
                    text="%s   %s   %s    101 \n"%(part,mod,chann)
                    self.opfile.write(text)
                elif (Chan_flag[x][0]=="No_Dev"):
                    text="%s   %s   %s    102 \n"%(part,mod,chann)
                    self.opfile.write(text)
                elif (Chan_flag[x][0]=="DQ_pb"):
                    text="%s   %s   %s    103 \n"%(part,mod,chann)
                    self.opfile.write(text)
                elif (Chan_flag[x][0]=="OK_pb"):
                    text="%s   %s   %s    104 \n"%(part,mod,chann)
                    self.opfile.write(text)                
                elif (Chan_flag[x][0]=="status_pb"):
                    text="%s   %s   %s    105 \n"%(part,mod,chann)
                    self.opfile.write(text)
                elif (Chan_flag[x][0]=="Mean_Dev_comp"):
                    text="%s   %s   %s    200   %s \n"%(part,mod,chann,devi)
                    self.opfile.write(text)
                elif (Chan_flag[x][0]=="HVLas_comp"):
                    text="%s   %s   %s    201   %s \n"%(part,mod,chann,devi)
                    self.opfile.write(text)
                elif ((Chan_flag[x][0]=="Bad_Chan") and (abs(float(Chan_flag[x][1]))<10.0)):
                    text="%s   %s   %s    299   %s \n"%(part,mod,chann,devi)
                    self.opfile.write(text)
                elif ((Chan_flag[x][0]=="Bad_Chan") and (abs(float(Chan_flag[x][1]))>10.0)):
                    text="%s   %s   %s    300   %s \n"%(part,mod,chann,devi)
                    self.opfile.write(text)
                elif (Chan_flag[x][0]=="Fast Drift"):
                    text="%s   %s   %s    301   %s \n"%(part,mod,chann,devi)
                    self.opfile.write(text)
                elif (Chan_flag[x][0]=="Fiber"):
                    text="%s   %s   %s    302   %s \n"%(part,mod,chann,devi)
                    self.opfile.write(text)
                elif (Chan_flag[x][0]=="HGLG_incomp"):
                    text="%s   %s   %s    303   %s \n"%(part,mod,chann,devi)
                    self.opfile.write(text)
            else:
                if (Chan_flag[x][0]=="Mean_Dev_comp"):
                    text="%s   %s   %s    200   %s \n"%(part,mod,chann,devi)
                    self.opfile.write(text)
                elif (Chan_flag[x][0]=="HVLas_comp"):
                    text="%s   %s   %s    201   %s \n"%(part,mod,chann,devi)
                    self.opfile.write(text)
                    tmptext="%s   %s   %s   %s |"%(part,mod,chann,devi)
                    summary201 = summary201+tmptext+Chan_DQ[x]+"\n"
                elif ((Chan_flag[x][0]=="Bad_Chan") and (abs(float(Chan_flag[x][1]))<10.0)):
                    text="%s   %s   %s    299   %s \n"%(part,mod,chann,devi)
                    self.opfile.write(text)
                    tmptext="%s   %s   %s   %s |"%(part,mod,chann,devi)                                        
                    summary299 = summary299+tmptext+Chan_DQ[x]+"\n" 
                    n299 = n299 + 1
                elif ((Chan_flag[x][0]=="Bad_Chan") and (abs(float(Chan_flag[x][1]))>10.0)):
                    text="%s   %s   %s    300   %s \n"%(part,mod,chann,devi)
                    self.opfile.write(text)
                    tmptext="%s   %s   %s   %s |"%(part,mod,chann,devi)                                        
                    summary300 = summary300+tmptext+Chan_DQ[x]+"\n" 
                    nbad = nbad + 1
                elif (Chan_flag[x][0]=="Fast Drift"):
                    text="%s   %s   %s    301   %s \n"%(part,mod,chann,devi)
                    self.opfile.write(text)
                    tmptext="%s   %s   %s   %s |"%(part,mod,chann,devi)
                    summary301 = summary301+tmptext+Chan_DQ[x]+"\n" 
                elif (Chan_flag[x][0]=="Fiber"):
                    text="%s   %s   %s    302   %s \n"%(part,mod,chann,devi)
                    self.opfile.write(text)
                elif (Chan_flag[x][0]=="HGLG_incomp"):
                    text="%s   %s   %s    303   %s \n"%(part,mod,chann,devi)
                    self.opfile.write(text)
                elif (Chan_flag[x][0]=="MBTS"):
                    text="%s   %s   %s    400   %s \n"%(part,mod,chann,devi)
                    self.opfile.write(text)   

        self.opfile.close()
        print(summary300)
        self.filesummary=os.path.join(getResultDirectory(),"Summary-for-DQ.txt")
        self.summaryfile=open(self.filesummary,"w")
        text="LASER Status Summary based on run %s\n"%(str(self.low_gain))
        self.summaryfile.write(text)
        self.summaryfile.write("Problematic Channels excluded from calibration *to be checked*:")
        self.summaryfile.write(str(nbad))
        self.summaryfile.write("\n")
        self.summaryfile.write("Channels excluded from calibration with known problem:")
        self.summaryfile.write(str(dqpb))
        self.summaryfile.write("\n")
        self.summaryfile.write("Channels excluded from calibration with bad status in Laser data (masked on the fly, low amplitude, no reference):")
        if ((okpb+statpb+las1+nolaser)>0):
            self.summaryfile.write(str(okpb+statpb+las1+nolaser))
        else:
            self.summaryfile.write("0")

        self.summaryfile.write("\n")
        self.summaryfile.write("Channels excluded from calibration for internal reason (fibre):")
        self.summaryfile.write(str(fib))
        self.summaryfile.write("\n")
        self.summaryfile.write("-------------------------------------------------------------------\n")
        self.summaryfile.write("Channels calibrated due to HV:")
        self.summaryfile.write(str(hvlascomp))
        self.summaryfile.write("\n")
        self.summaryfile.write("Channels calibrated with drifts larger then expected:")
        self.summaryfile.write(str(n299))
        self.summaryfile.write("\n")
        self.summaryfile.write("Channels calibrated with normal drifts:")
        self.summaryfile.write(str(meandev))
        self.summaryfile.write("\n")
        self.summaryfile.write("-------------------------------------------------------------------\n")
        self.summaryfile.write("Channels not calibrated (stable):")
        self.summaryfile.write(str(nodev))
        self.summaryfile.write("\n")
        self.summaryfile.write("\n ============ Problematic Channels excluded by default from calibration, To be checked =================\n")
        self.summaryfile.write(summary300)
        self.summaryfile.write(summary301)
        self.summaryfile.write("\n ============ Calibrated Channels, To be checked =================\n")
        self.summaryfile.write(summary299)
        self.summaryfile.write(summary201)

        self.summaryfile.close()
