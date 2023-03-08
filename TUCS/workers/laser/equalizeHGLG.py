############################################################
#
# equalizeHGLG.py
#
############################################################
#
#
#############################################################




from src.GenericWorker import *
from src.region import *

from src.laser.toolbox import *

class equalizeHGLG(GenericWorker):
    " This worker compare HG and LG contants and keep them if they are compatible"
        
    def __init__(self, useDB=False):
        self.useDB  = useDB
        self.PMTool   = LaserTools()
        
        self.fLas_lg = [[[-1 for i in range(50)] for j in range(70)] for k in range(4)] #PMT,module,part
        self.fLas_hg = [[[-1 for i in range(50)] for j in range(70)] for k in range(4)]

        self.nocalib = []

    def ProcessStart(self):

        #this is the bad channels list, the 60 channels which were excluded during 2012
        #we add also here the channels linked to MBTS

        self.nocalib.append('EBA_m15_c05')
        self.nocalib.append('EBA_m15_c07')
        self.nocalib.append('EBA_m15_c09')
        self.nocalib.append('EBA_m15_c11')
        self.nocalib.append('EBA_m15_c13')
        self.nocalib.append('EBA_m15_c15')
        self.nocalib.append('EBA_m15_c17')
        self.nocalib.append('EBA_m15_c18')
        self.nocalib.append('EBA_m15_c19')
        self.nocalib.append('EBA_m15_c21')
        self.nocalib.append('EBA_m15_c23')
        self.nocalib.append('EBA_m15_c32')
        self.nocalib.append('EBA_m15_c35')
        self.nocalib.append('EBA_m15_c36')
        self.nocalib.append('EBA_m15_c37')
        self.nocalib.append('EBA_m15_c40')
        self.nocalib.append('LBA_m04_c44')
        self.nocalib.append('LBA_m11_c10')
        self.nocalib.append('LBA_m13_c35')
        self.nocalib.append('LBA_m16_c35')
        self.nocalib.append('LBA_m17_c06')
        self.nocalib.append('LBA_m21_c19')
        self.nocalib.append('LBA_m23_c36')
        self.nocalib.append('LBA_m29_c01')
        self.nocalib.append('LBA_m29_c02')
        self.nocalib.append('LBA_m29_c05')
        self.nocalib.append('LBA_m37_c19')
        self.nocalib.append('LBA_m38_c15')
        self.nocalib.append('LBA_m47_c04')
        self.nocalib.append('LBA_m50_c42')
        self.nocalib.append('LBA_m50_c44')
        self.nocalib.append('LBA_m50_c45')
        self.nocalib.append('LBA_m50_c46')
        self.nocalib.append('LBA_m50_c47')
        self.nocalib.append('LBA_m53_c33')
        self.nocalib.append('LBA_m58_c22')
        self.nocalib.append('LBA_m59_c38')
        self.nocalib.append('LBA_m61_c13')
        self.nocalib.append('LBA_m62_c18')
        self.nocalib.append('LBA_m64_c14')
        self.nocalib.append('LBC_m02_c38')
        self.nocalib.append('LBC_m03_c44')
        self.nocalib.append('LBC_m09_c40')
        self.nocalib.append('LBC_m11_c45')
        self.nocalib.append('LBC_m18_c13')
        self.nocalib.append('LBC_m21_c47')
        self.nocalib.append('LBC_m23_c13')
        self.nocalib.append('LBC_m26_c38')
        self.nocalib.append('LBC_m29_c26')
        self.nocalib.append('LBC_m34_c02')
        self.nocalib.append('LBC_m36_c24')
        self.nocalib.append('LBC_m39_c07')
        self.nocalib.append('LBC_m50_c24')
        self.nocalib.append('LBC_m50_c25')
        self.nocalib.append('LBC_m50_c26')
        self.nocalib.append('LBC_m50_c27')
        self.nocalib.append('LBC_m50_c28')
        self.nocalib.append('LBC_m50_c29')
        self.nocalib.append('LBC_m55_c27')
        self.nocalib.append('LBC_m59_c33')
        self.nocalib.append('LBC_m60_c29')
        self.nocalib.append('LBC_m62_c32')
        self.nocalib.append('LBC_m63_c41')
        self.nocalib.append('EBA_m03_c39')
        self.nocalib.append('EBA_m22_c41')
        self.nocalib.append('EBA_m29_c23')
        self.nocalib.append('EBA_m57_c22')
        self.nocalib.append('EBA_m61_c15')
        self.nocalib.append('EBA_m63_c15')
        self.nocalib.append('EBC_m05_c20')
        self.nocalib.append('EBC_m08_c35')
        self.nocalib.append('EBC_m20_c10')
        self.nocalib.append('EBC_m22_c36')
        self.nocalib.append('EBC_m43_c04')
        self.nocalib.append('EBC_m44_c30')
        self.nocalib.append('EBC_m53_c39')
        self.nocalib.append('EBC_m56_c36')
        self.nocalib.append('EBC_m63_c15')
        self.nocalib.append('EBC_m64_c31')
        self.nocalib.append('EBC_m64_c32')

        self.nocalib.append('EBA_m03_c00')
        self.nocalib.append('EBA_m04_c00')
        self.nocalib.append('EBA_m12_c00')
        self.nocalib.append('EBA_m13_c00')
        self.nocalib.append('EBA_m23_c00')
        self.nocalib.append('EBA_m24_c00')
        self.nocalib.append('EBA_m30_c00')
        self.nocalib.append('EBA_m31_c00')
        self.nocalib.append('EBA_m35_c00')
        self.nocalib.append('EBA_m36_c00')
        self.nocalib.append('EBA_m44_c00')
        self.nocalib.append('EBA_m45_c00')
        self.nocalib.append('EBA_m53_c00')
        self.nocalib.append('EBA_m54_c00')
        self.nocalib.append('EBA_m60_c00')
        self.nocalib.append('EBA_m61_c00')
        #
        self.nocalib.append('EBC_m04_c00')
        self.nocalib.append('EBC_m05_c00')
        self.nocalib.append('EBC_m12_c00')
        self.nocalib.append('EBC_m13_c00')
        self.nocalib.append('EBC_m19_c00')
        self.nocalib.append('EBC_m20_c00')
        self.nocalib.append('EBC_m27_c00')
        self.nocalib.append('EBC_m28_c00')
        self.nocalib.append('EBC_m36_c00')
        self.nocalib.append('EBC_m37_c00')
        self.nocalib.append('EBC_m44_c00')
        self.nocalib.append('EBC_m45_c00')
        self.nocalib.append('EBC_m54_c00')
        self.nocalib.append('EBC_m55_c00')
        self.nocalib.append('EBC_m61_c00')
        self.nocalib.append('EBC_m62_c00')
        #
        self.nocalib.append('EBC_m44_c02')
        self.nocalib.append('EBC_m44_c04')
        self.nocalib.append('EBC_m44_c06')
        self.nocalib.append('EBC_m44_c20')
        self.nocalib.append('EBC_m44_c22')
        self.nocalib.append('EBC_m44_c31')
        self.nocalib.append('EBC_m44_c38')
        self.nocalib.append('EBC_m44_c39')

        self.nocalib.append('EBC_m37_c01') #not compatible HG/LG --> see elog change of HV at 20 march 2012
        self.nocalib.append('EBC_m25_c01') #not compatible HG/LG 
        self.nocalib.append('EBC_m25_c00') #not compatible HG/LG

        self.nocalib.append('EBC_m18_c18') #not compatible HG/LG
        self.nocalib.append('EBC_m18_c19') #not compatible HG/LG
        
    def ProcessRegion(self, region):

        # -- loop 


        for event in region.GetEvents():

            thres_max = 2.5
            thres_min = 0.625

            pmt_region = str(event.region)

            if 'HV' in event.data:
                if event.data['HV']<10 or ((event.data['HV']-event.data['hv_db'])>20): #if <10 module in emergency mode, large correction allowed
                    thres_max = 10
                    thres_min = 0.4
            
            if 'f_laser' in event.data:


                if (event.data['f_laser']==-1):
                    event.data['f_laser']=1

                if 'problems' in event.data:
                    if str(event.data['problems']).find('laser')!=-1:
                        event.data['f_laser']=1


                if pmt_region.find('EB')!=-1 and pmt_region.find('c12')!=-1:
                    event.data['f_laser']=1.
                if pmt_region.find('EB')!=-1 and pmt_region.find('c13')!=-1:
                    event.data['f_laser']=1.

                if 'is_OK' in event.data:
                    if not event.data['is_OK']:
                        event.data['f_laser']=1
                        
                if 'status' in event.data:
                    if event.data['status']!=0 and event.data['status']!=2:
                        event.data['f_laser']=1
                    
                if event.data['f_laser'] > thres_max:
                    event.data['f_laser']=thres_max
                if event.data['f_laser'] < thres_min:
                    event.data['f_laser']=thres_min
                
                if 'wheelpos' in event.run.data:
                    filter = event.run.data['wheelpos']
                else:
                    filter = 0
                
                f_las = event.data['f_laser']

                if pmt_region.find('EBC_m53_c39')!=-1:
                    print('debug',f_las,event.data['status'])

                [part_num, i, j, w] = event.region.GetNumber()
                        
                if (filter == 6):


                    if (self.fLas_lg[part_num-1][i][j] == -1):
                        self.fLas_lg[part_num-1][i][j]=f_las # first call

                    else:
                        f_lg = f_las
                        f_hg = self.fLas_hg[part_num-1][i][j]
                        if ( (pmt_region.find('EB')==-1) or ((pmt_region.find('_c01')==-1) and (pmt_region.find('_c00')==-1))  ):
                            if ((f_lg != 1)and(f_hg == 1)):  ## LG drift, no HG drift : no LG correction kept
                                event.data['f_laser']=1
                                print("LG cst set to 1 because low HG deviation",pmt_region)

                            if f_lg > 1 and f_hg < 1:
                                event.data['f_laser']=1
                                print('HG and LG are not compatible in region :',pmt_region)
                            if f_lg < 1 and f_hg > 1:
                                event.data['f_laser']=1
                                print('HG and LG are not compatible in region :',pmt_region)
                                
                        for k in range(0,len(self.nocalib)):
                            if pmt_region.find(self.nocalib[k])!=-1:
                                event.data['f_laser']=1

                if (filter == 8):

                    if (self.fLas_hg[part_num-1][i][j] == -1):
                        self.fLas_hg[part_num-1][i][j]=f_las #first call
                    else:
                        f_hg = f_las
                        f_lg = self.fLas_lg[part_num-1][i][j]
                        if ( (pmt_region.find('EB')==-1) or ((pmt_region.find('_c01')==-1) and (pmt_region.find('_c00')==-1))  ):
                            if ((f_lg == 1)and(f_hg != 1)):  ## LG drift, no HG drift : no LG correction kept
                                event.data['f_laser']=1
                                print("HG cst set to 1 because low LG deviation",pmt_region)
 
                            if f_lg > 1 and f_hg < 1:
                                event.data['f_laser']=1
                                print('HG and LG are not compatible in region :',pmt_region)
                            if f_lg < 1 and f_hg > 1:
                                event.data['f_laser']=1
                                print('HG and LG are not compatible in region :',pmt_region)

                        else :
                            if ( (event.data['f_laser']!=1) and (self.fLas_lg[part_num-1][i][j]!=-1) ): # HG erased with LG
                                event.data['f_laser']=self.fLas_lg[part_num-1][i][j]

                        for k in range(0,len(self.nocalib)):
                            if pmt_region.find(self.nocalib[k])!=-1:
                                event.data['f_laser']=1
            ## -- end of loop



        
