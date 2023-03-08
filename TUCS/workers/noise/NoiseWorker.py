# NoiseWorker.py
# Parent Class for all noise workers
# Author: Brian Martin (brian.thomas.martin@cern.ch)
from src.region import *
from src.GenericWorker import *
from src.oscalls import *
import logging
import math
import ROOT

# Non-class utilities
def getMean(numbers):
    if len(numbers)==0:
        return 0
    else:
        return 1.0*sum(numbers)/len(numbers)

def getMedian(numbers):
    '''Takes a list of numbers, returns the median'''
    size = len(numbers)
    numbers = sorted(numbers)
    if size==0:
        return 0
    if size==1:
        return numbers[0]
    if (size%2) == 0:
        med = (numbers[int(size/2)]+numbers[int(size/2)-1])/2
    else:
        med = numbers[int((size-1)/2)]

    return med

def getRMS(numbers):
    '''Takes list of numbers, returns RMS difference'''
    if len(numbers)==0:
        return 0
    mean = getMean(numbers)
    rms = 0.
    for num in numbers:
        rms += (num-mean)**2
    rms /= len(numbers)
    rms = math.sqrt(rms)
    
    return rms

def DoubleG(xx, par):
    '''Defines generic double gaussian function for use by DoubleGaussian()'''
    x = xx[0]
    return ROOT.TMath.Exp(-1*(x**2/(2*par[0])**2))+par[1]*ROOT.TMath.Exp(-1*(x**2/(2*par[2])**2))
 
def DoubleGaussian(name,sigma1,ratio,sigma2):
    '''Return TF1 of double gaussian PDF constructed with args'''

    if abs(sigma1<10E-4):
        print('Warning: artificially infalating sigma1 for K-S test')
        sigma1=0.0001

    if abs(sigma2<10E-4):
        print('Warning: artificially infalating sigma2 for K-S test')
        sigma2=0.0001

    fit = ROOT.TF1(name,DoubleG,-5000,5000,3)
    fit.SetParameters(sigma1,ratio,sigma2)
    fit.SetParNames("Sigma1","Ratio","Sigma2")

    return fit

def parallelSort(list1,list2):
    '''sort list1 and list 2 according to values in list 1'''
    list12 = list(zip(list1,list2))
    list12.sort()
    set1,set2 = list(zip(*list12))
    list1=list(set1)
    list2=list(set2)

def ConvertCellHash2TucsHash(cellHash):
    '''Takes a cell hash and returns a Tucs Hash'''
    hash =-1
    cellFound=False
    for sec in range(1,4):
        for sid in [-1,1]:
            for mod in range(1,65):
                for tow in range(16):
                    for samp in range(4):
                        if cellFound: break
                        if samp==0: 
                            if sec==1:
                                if tow>9: continue
                            elif sec==2:
                                if (tow<11 or tow>15): continue
                            elif sec==3: continue
                        elif samp==1:
                            if sec==1:
                                if tow>8: continue
                            elif sec==2:
                                if tow<10 or tow>14: continue
                            elif sec==3:
                                if tow!=9: continue
                        elif samp==2:
                            if sec==1:
                                if sid== -1: 
                                    if tow not in [2,4,6]: continue
                                elif sid == 1: 
                                    if tow not in [0,2,4,6]: continue
                            elif sec==2:
                                if tow not in [10,12]: continue
                            elif sec==3:
                                if tow!=8: continue
                        elif samp==3:
                            if sec!=3:
                                continue
                            elif sec==3:
                                if tow not in [10,11,13,15]: continue
                        # if reaches this point, cell exists
                        hash +=1
                        cellFound = (hash == cellHash)
                        if cellFound:
                            if sid>0:
                                if sec==1: partStr='LBA'
                                else:      partStr='EBA'
                            else:
                                if sec==1: partStr='LBC'
                                else:      partStr='EBC'
                            
                            modStr = '%02d' % mod
                            if   samp==0: sampStr='A'
                            elif samp==1: sampStr='BC'
                            elif samp==2: sampStr='D'
                            elif samp==3: sampStr='E'
                            
                            towStr = '%02d' % tow
                            
                            regionHash = 'TILECAL_'+partStr+'_m'+modStr+'_s'+sampStr+'_t'+towStr

                            print('Resolved CellHash: ',cellHash,' to RegionHash: ',regionHash)
                            return regionHash
    
    
        
class NoiseWorker(GenericWorker):
    '''Base class for noise workers'''

    def __init__(self):

        #The dictionaries have channel number as key and (pmt, cell
        #name) as value.

        self.lba_lbc = {'42': ('45', 'B9-R'), '43': ('44', 'None'), '24': ('27', 'D2-R'), 
                        '25': ('26', 'D2-L'), '26': ('25', 'A6-R'), '27': ('30', 'BC6-L'), 
                        '20': ('21', 'A5-R'), '21': ('22', 'BC5-L'), '22': ('23', 'BC5-R'), 
                        '23': ('24', 'A6-L'), '46': ('47', 'A10-R'), '47': ('46', 'B9-L'), 
                        '44': ('43', 'D3-R'), '45': ('48', 'A10-L'), '28': ('29', 'BC6-R'), 
                        '29': ('28', 'A7-L'), '40': ('41', 'BC8-R'), '41': ('40', 'D3-L'), 
                        '1': ('2', 'A1-L'), '0': ('1', 'D0'), '3': ('4', 'BC1-L'), 
                        '2': ('3', 'BC1-R'), '5': ('6', 'A2-L'), '4': ('5', 'A1-R'), 
                        '7': ('8', 'BC2-L'), '6': ('7', 'BC2-R'), '9': ('10', 'A3-L'), 
                        '8': ('9', 'A2-R'), '39': ('42', 'BC8-L'), '38': ('37', 'A8-R'), 
                        '11': ('12', 'BC3-L'), '10': ('11', 'A3-R'), '13': ('14', 'D1-L'), 
                        '12': ('13', 'BC3-R'), '15': ('16', 'A4-L'), '14': ('15', 'D1-R'), 
                        '17': ('18', 'BC4-L'), '16': ('17', 'BC4-R'), '19': ('20', 'A5-L'), 
                        '18': ('19', 'A4-R'), '31': ('32', 'None'), '30': ('33', 'None'), 
                        '37': ('38', 'A9-L'), '36': ('39', 'A9-R'), '35': ('34', 'A8-L'), 
                        '34': ('35', 'BC7-R'), '33': ('36', 'BC7-L'), '32': ('31', 'A7-R')}

        self.eba_ebc = {'42': ('45', 'None'), '43': ('39', 'None'), '24': ('27', 'None'), 
                        '25': ('26', 'None'), '26': ('25', 'None'), '27': ('31', 'None'), 
                        '20': ('21', 'A14-R'), '21': ('22', 'A14-L'), '22': ('23', 'B13-R'), 
                        '23': ('24', 'B13-L'), '46': ('47', 'None'), '47': ('46', 'None'), 
                        '44': ('40', 'None'), '45': ('48', 'None'), '28': ('32', 'None'), 
                        '29': ('28', 'None'), '40': ('42', 'A16-L'), '41': ('41', 'A16-R'), 
                        '1': ('2', 'E4'), '0': ('1', 'E3'), '3': ('4', 'D4-L'), '2': ('3', 'D4-R'), 
                        '5': ('6', 'C10-L'), '4': ('5', 'C10-R'), '7': ('8', 'A12-L'), 
                        '6': ('7', 'A12-R'), '9': ('10', 'B11-L'), '8': ('9', 'B11-R'), 
                        '39': ('43', 'B15-R'), '38': ('37', 'D6-R'), '11': ('12', 'A13-L'), 
                        '10': ('11', 'A13-R'), '13': ('14', 'E2'), '12': ('13', 'E1'), 
                        '15': ('16', 'B12-L'), '14': ('15', 'B12-R'), '17': ('18', 'D5-L'), 
                        '16': ('17', 'D5-R'), '19': ('20', 'None'), '18': ('19', 'None'), 
                        '31': ('29', 'A15-R'), '30': ('33', 'B14-R'), '37': ('38', 'D6-L'), 
                        '36': ('44', 'B15-L'), '35': ('34', 'B14-L'), '34': ('35', 'None'), 
                        '33': ('36', 'None'), '32': ('30', 'A15-L')}

        self.eba15_ebc18 = {'42': ('45', 'None'), '43': ('39', 'None'), '24': ('27', 'None'), 
                            '25': ('26', 'None'), '26': ('25', 'None'), '27': ('31', 'None'), 
                            '20': ('21', 'A14-R'), '21': ('22', 'A14-L'), '22': ('23', 'B13-R'), 
                            '23': ('24', 'B13-L'), '46': ('47', 'None'), '47': ('46', 'None'), 
                            '44': ('40', 'None'), '45': ('48', 'None'), '28': ('32', 'None'), 
                            '29': ('28', 'None'), '40': ('42', 'A16-L'), '41': ('41', 'A16-R'), 
                            '1': ('2', 'None'), '0': ('1', 'None'), '3': ('4', 'None'), 
                            '2': ('3', 'None'), '5': ('6', 'C10-L'), '4': ('5', 'C10-R'), 
                            '7': ('8', 'A12-L'), '6': ('7', 'A12-R'), '9': ('10', 'B11-L'), 
                            '8': ('9', 'B11-R'), '39': ('43', 'B15-R'), '38': ('37', 'D6-R'), 
                            '11': ('12', 'A13-L'), '10': ('11', 'A13-R'), '13': ('14', 'E2'), 
                            '12': ('13', 'E1'), '15': ('16', 'B12-L'), '14': ('15', 'B12-R'), 
                            '17': ('18', 'D45-L'), '16': ('17', 'D45-R'), '19': ('20', 'E4'), 
                            '18': ('19', 'E3'), '31': ('29', 'A15-R'), '30': ('33', 'B14-R'), 
                            '37': ('38', 'D6-L'), '36': ('44', 'B15-L'), '35': ('34', 'B14-L'), 
                            '34': ('35', 'None'), '33': ('36', 'None'), '32': ('30', 'A15-L')}
        
    def get_cellName(self, part, mod, ch):
        '''Function to retrieve the cell name form channel.

        This funtion will give the cell name of the corresponding channel.'''

        #Call the dictionaries
        LBA_LBC     = self.lba_lbc
        EBA_EBC     = self.eba_ebc
        EBA15_EBC18 = self.eba15_ebc18

        if(part == 'LBA' or part == 'LBC'):

            if '-' in LBA_LBC[str(ch)][1]:
                
                return LBA_LBC[str(ch)][1][:-2]

            else:

                return LBA_LBC[str(ch)][1]

        if(part == 'EBA' or part == 'EBC'):
                
            if(mod == 15 or mod == 18):

                if '-' in EBA15_EBC18[str(ch)][1]:

                    return EBA15_EBC18[str(ch)][1][:-2]

                else:

                    return EBA15_EBC18[str(ch)][1]

            else:

                if '-' in EBA_EBC[str(ch)][1]:
                    
                    return EBA_EBC[str(ch)][1][:-2]

                else:

                    return EBA_EBC[str(ch)][1]




    def initLog(self,level=logging.CRITICAL):
        '''Set up noise logging streams: one to stdout, one to file'''
        self.noiseLog = logging.getLogger('noiseLog')
        if len(self.noiseLog.handlers) == 0:
            self.noiseLog.propagate = 0 # needed to prevent being picked up by root logger
            self.noiseLog.setLevel(logging.DEBUG)
            fileName = os.path.join(getResultDirectory('output'),'noise.out')
            fileOut = logging.FileHandler(fileName,mode='a')
            fileOut.setLevel(logging.INFO)
            stdOut  = logging.StreamHandler()
            stdOut.setLevel(level)
            self.noiseLog.addHandler(fileOut)
            self.noiseLog.addHandler(stdOut)
    
    def initNoiseHistFile(self,filename='output/Tucs.HIST.root'):
        try:
            self.HistFile.cd()
        except:
            self.initHistFile(filename)
        self.HistFile.cd()
        ROOT.gDirectory.mkdir("Noise")
        ROOT.gDirectory.cd("Noise")
        
            
    def initNoiseNtupleFile(self,filename='noise.NTUP.root'):
        fullfilename=os.path.join(getResultDirectory(),filename)
        self.noiseNtupleFile = ROOT.gROOT.GetFile(fullfilename)
        try:
            self.noiseNtupleFile.cd()
        except:
            self.noiseNtupleFile = ROOT.TFile(fullfilename,'RECREATE')

    def get_index(self, type, part, mod, chan, gain, gainCell=0):
        if type == 'physical':
            samp = chan
            tower= gain
            return side *64*4*17*6\
                + mod      *4*17*6\
                + samp       *17*6\
                + tower         *6\
                + gainCell
        else:
            return part  *64*48*2\
                + mod      *48*2\
                + chan        *2\
                + gain

    def checkForExistingData(self, data):
        '''Check data to see if there are existing values.
           If so rename them so that a second set of data can be read'''
        parameters = []
        if 'Digi' in self.__class__.__name__:
            parameters = ['ped','hfn','lfn','hfnsigma1','hfnsigma2','hfnnorm']
            parameters += ['autocorr'+str(i) for i in range(6)]
        elif 'Chan' in self.__class__.__name__:
            parameters = ['efit_mean','eopt_mean','eopt2_mean']
        elif 'Cell' in self.__class__.__name__:
            for p in ['cellnoise','pilenoise','cellsigma1','cellsigma2','cellnorm']:
                for g in self.gainStr:
                    parameters.append(p+g)
        elif 'Online' in self.__class__.__name__:\
            parameters = ['noise','pilenoise']
        else:
            print('Warning: Parent class is not Digi Chan Cell or Online')
        
        if 'DB' in self.__class__.__name__:
            for i in range(len(parameters)):
                parameters[i] = parameters[i]+'_db'
       
        for p in data:
            if p in parameters:
                data[p+'2'] = data.pop(p)

    def GetCellTypeForADC(self, region):
        # Determine special cell types
        cellname = region.GetCellName(True)
        isMBTS2 = cellname in ['E5', 'E6']
        isE4prime = 'E4\'' == cellname
        isE1merged = 'E1m' == cellname
        isspC10 = 'spC10' == cellname
        isE = cellname in ['E1', 'E2', 'E3', 'E4']
        ctype = ''
        if isMBTS2: ctype = 'MBTS'
        if isE4prime: ctype = 'E4\''
        if isE1merged: ctype = 'E1m'
        if isspC10: ctype = 'spC10'
        if isE: ctype = 'E'
        if int(isMBTS2) + int(isE4prime) + int(isE1merged) + int(isspC10) + int(isE) > 1:
            print("NoiseWorker: ERROR determining cell type for ADC: %s" % region.GetHash())
            return None
        return ctype

    def CheckGrandChild(self, parent, region):
        for c1 in parent.GetChildren('physical'):
            for c2 in c1.GetChildren('physical'):
                if c2.GetHash() == region.GetHash():
                    return True
        print("CheckGrandChild ERROR: Invalid parent %s to region %s" % (parent.GetHash(), region.GetHash()))
        return False

    def GetCellForADC(self, region, ctype):
        for p in region.parents():
                for pp in p.parents():
                    pphash =  pp.GetHash()
                    if ctype == 'MBTS' and 'MBTS' in pphash:
                        return pp if self.CheckGrandChild(pp, region) else None
                    if ctype != 'MBTS' and 'MBTS' not in pphash and '_t' in pphash:
                        return pp if self.CheckGrandChild(pp, region) else None
        print("NoiseWorker: ERROR unable to get cell for ADC: %s" % region.GetHash())

                        
