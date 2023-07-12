############################################################
#
# FillBetaHVNom.py
#
############################################################
#
# Author: Henric
#
# Input parameters are:
# Even though its not FORTRAN, its good to be able to print....
#        1         2         3         4         5         6         7         8 
#2345678901234567890123456789012345678901234567890123456789012345678901234567890
#
###########################################################

from src.GenericWorker import *
from src.oscalls import *

class FillBetaHVNom(GenericWorker):
    "This macro reads the Beta & HVnom values from a files and adds it to the PMT region data"
    
    def __init__(self, filename='data/PMT_new-2017.dat'):
        self.filename = os.path.join(getTucsDirectory(),filename)
        self.dict = {}
        
    def ProcessStart(self):
        for part in ['LBA', 'LBC','EBA', 'EBC']:
            for drawer in range(64):
                module_name = '%s%02d'%(part,drawer+1)
                self.dict[module_name] = []
                for pmt in range(48):
                    self.dict[module_name].append({})
        
        
        f = open(self.filename,'r')
        for line in f:
            list = line.split(";")
            if len(list)==5:
                [serial, module, pmt, beta, Unom] = list
                if module not in ['LBA00', 'LBC00', 'EBA00','EBC00', '']:
                    try:
                        pmtdata = self.dict[module][int(pmt)-1]
                        pmtdata['serial'] = serial
                        pmtdata['beta'] = float(beta)
                        pmtdata['Unom'] = float(Unom)
                    except:
                        print(("Error parsing", line))
                    
        #print self.dict        
        f.close()

    def ProcessRegion(self, region):
        r = region.GetNumber(1)

        if len(r)==3: # This is a PMT channel
            det, part, mod, chan = region.GetHash().split('_')
            ipart, imod, ipmt = r
            module = '%s%02d' % (part, imod)
            thisdict = self.dict[module][ipmt-1]                      
            for key, value in list(thisdict.items()):
                region.data[key] = value
        pass

    def ProcessStop(self):
        del self.dict
    
