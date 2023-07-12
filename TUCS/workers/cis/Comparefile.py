# Author: Joshua Montgomery <joshua.montgomery@cern.ch>
# Sept. 23, 2011
# This is designed to compare two text files in archive format
# typically produced by the StudyFlag macro
# It outputs the common channels


from src.oscalls import *
from operator import itemgetter


class Comparefile():
    "This worker compares two archive text files from Study Flag and outputs common channels"
    
    def __init__(self, pathlist=[], flagtype='Fail Likely Calib.', startdate='01_05_2011', enddate='05_10_2011'):

        self.flagtype = flagtype
        self.path1  = os.path.join(getResultDirectory(),'update_log.log')
        self.path2  = os.path.join(getResultDirectory(),'update_log.log')
        self.paths = [self.path1, self.path2]
        self.startdate = startdate
        self.enddate = enddate
        self.log_tdiff = open(os.path.join(getResultDirectory(),'slimmed_total.log'), 'w')
        self.log_tdiff_friend = open(os.path.join(getResultDirectory(),'_slimmed_tot_Macro_Friendly.log'), 'w')

    def ReadLog(self, path):

        high = set()
        low = set()
        

        for line in open(path,'r'):

            if 'region' and 'TILECAL_' in line:

                 left, t_hash = line.split(':  ')
                 tag = t_hash.split('_')
                 det, part, module, channel, gain = tag[0], tag[1], int(tag[2].replace(
                                         'm', '')), int(tag[3].replace('c', '')), tag[4]
                                         
                 gain, bs = gain.split(' ')
                
                 if 'highgain' in gain:
                      high.add((part, module, channel, gain))
                 else:
                     low.add((part, module, channel, gain))

                    

            if 'slimmed' in line:
                left, t_hash = line.split(':')
                tag = t_hash.split('_')
                part, module, channel, gain = tag[0], int(tag[1]
                                                  ), int(tag[2]), tag[3]
                part = part.lstrip()
                gain = gain.rstrip('\n')

                if 'highgain' in gain:
                    high.add((part, module, channel, gain))
                else:
                    low.add((part, module, channel, gain))
                    
            else: print('i dont understand this file')

        tot = [high, low]

        return high, low, tot
        


    def ProcessStart(self):

        print('flag type is', self.flagtype)
        print('This is the correct file')

        high_list = []
        low_list = []
                
        for path in self.paths:
            high, low, total = self.ReadLog(path)
            high_list.append(high)
            low_list.append(low)

        setnum = len(high_list)
        highset = high_list[0]
        lowset = low_list[0]
        
        for x in range(setnum):
            highset = highset & high_list[x] 
            lowset = lowset & low_list[x]
            
        totalset = highset | lowset

        sortcomp = list(totalset)
        sortcomp = sorted(sortcomp, key=itemgetter(0,1,2,3))

        self.log_tdiff_friend.write('selected_region = [')
        p, m, c, g = sortcomp[0]
        self.log_tdiff_friend.write('\'%s_m%02d_c%02d_%s\'' %(p, int(m), int(c), g))
        
        for part, mod, chan, gain in sortcomp[1:]:
           self.log_tdiff.write('slimmed:  %s_m%02d_c%02d_%s\n' %(part, int(mod), int(chan), gain))
           self.log_tdiff_friend.write(', \'%s_m%02d_c%02d_%s\'' %(part, int(mod), int(chan), gain))
        self.log_tdiff_friend.write(']')

    def ProcessStop(self):
       self.log_tdiff.close()
       self.log_tdiff_friend.close()
       return

    def ProcessRegion(self, region):

       return region
                
