# Author: Joshua Montgomery <joshua.montgomery@cern.ch>
#
# August 05, 2011
#
# This worker takes the output of MapFlagFailure (typically run from the
# StudyFlag Macro), or an equivalent slimmed data file, and analyzes it,
# looking for patterns of failures at the PMT, DMU, Digitizer, and Motherboard levels
# and outputing what it finds into an appropriate directory.
# Given a second path to a slimmed file from the output of StudyFlag/MapFlagFailure
# it will compare that data to the data being processed in the first path and writes
# to a file the intersection of the two.


import os.path
import src.oscalls
from operator import itemgetter

class SortFlagFailure(GenericWorker):
    "This worker sorts the channels failing a flag as determined by MapFlagFailure"

    def __init__(self, flagtype, path1='output/temp_flag_{0}.log', rundate='', pathlist=[''],
                startdate='', enddate='', compare_files=False):
        
        super(SortFlagFailure, self).__init__()

        self.flagtype      = flagtype
        self.path1         = os.path.join(src.oscalls.getResultDirectory(),path1.format(self.flagtype))
        self.path          = os.path.dirname(self.path1)+"/"
        self.rundate       = rundate
        self.pathlist      = []
        for pa in pathlist:
            self.pathlist.append(self.path+pa)
        self.startdate     = startdate
        self.enddate       = enddate
        self.compare_files = compare_files
        if not self.rundate:
            rundate = datetime.date.today().strftime('%Y_%m_%d')
            self.rundate = rundate

        ##### FOR THE ARCHIVE FUNCTIONALITY ##########
        ndir = self.path+'flaglogs/{0}/{0}_txt/{1}/'.format(self.rundate, self.flagtype)
        src.oscalls.createDir(ndir)

        self.log_pmt = open(ndir+'{0}_bad_pmts.log'.format(self.flagtype), 'w') 
        self.log_dmu = open(ndir+'{0}_bad_dmus.log'.format(self.flagtype), 'w')
        self.log_digit = open(ndir+'{0}_bad_digit.log'.format(self.flagtype), 'w')
        self.log_motherb = open(ndir+'{0}_bad_motherboards.log'.format(self.flagtype), 'w')
        self.slimmed_total = open(ndir+'{0}_slimmed_tot.log'.format(self.flagtype), 'w')
        self.slimmed_Friendly = open(ndir+'{0}_slimmed_tot_Friendly.log'.format(self.flagtype), 'w')

        if self.compare_files:        
        #### FOR THE COMPARE-FILES FUNCTIONALITY ##########

            listdir = self.path+'flaglogs/flaglogs_export/{0}_to_{1}/{0}_to_{1}_txt/{2}/'.format(self.startdate, self.enddate, self.flagtype)
            src.oscalls.createDir(listdir)
            self.log_tdiff = open(listdir+'{0}_slimmed_total.log'.format(self.flagtype), 'w')
            self.log_tdiff_friend = open(listdir+'{0}_slimmed_tot_Macro_Friendly.log'.format(self.flagtype), 'w')



        ignore_Ebarrels = ['EBA','EBC']
        ignore_Lbarrels = ['LBA','LBC']
        ignore_modules = [modules for modules in range(1,65)]
        ignore_channels_EB = [24, 25, 26, 27, 28, 29, 42, 43, 44, 45, 46, 47]
        bad_channels_EB = [18, 19, 33, 34]
        bad_channels_LB = [30, 31, 43]
        ignore_channels_Special = [0, 1, 2, 24, 25, 26, 27, 28, 29, 42, 43, 44, 45, 46, 47]
        bad_channels_Special = [3, 33, 34] # these are also uninstrumented, but they do not take up whole digitizers like the others
        ignore_gainlist = ['highgain', 'lowgain']
        ignore_extras = []
        ignore_list = []
        bad_list = []
        for gains in ignore_gainlist:
            
            for bars in ignore_Ebarrels:
                for mods in ignore_modules:
                    if bars in ['EBC'] and mods in [18]:
                        for chans in ignore_channels_Special:
                            ignore_list.append((bars, mods, chans, gains))
                        for chans in bad_channels_Special:
                            bad_list.append((bars, mods, chans, gains))
                    elif bars in ['EBA'] and mods in [15]:
                        for chans in ignore_channels_Special:
                            ignore_list.append((bars, mods, chans, gains))
                        for chans in bad_channels_Special:
                            bad_list.append((bars, mods, chans, gains))
                    else:
                        for chans in ignore_channels_EB:
                            ignore_list.append((bars, mods, chans, gains))
                        for chans in bad_channels_EB:
                            bad_list.append((bars, mods, chans, gains))
                            
            for bars in ignore_Lbarrels:
                for mods in ignore_modules:
                    for chans in bad_channels_LB:
                        bad_list.append((bars, mods, chans, gains))
                        
        self.ignore_list = ignore_list
        self.bad_list    = bad_list
        self.blist_h = []
        self.blist_l = []
        
        for (bars, mods, chans, gains) in self.bad_list:
            if gains in ['highgain']:
                self.blist_h.append((bars, mods, chans, gains))
                
            elif gains in ['lowgain']:
                self.blist_l.append((bars, mods, chans, gains))
    
    def ProcessStart(self):
           
        high, low, total = self.ReadLog(self.path1)
        self.ProcessData(high, low, total)
   

    ## Make sure the default setting of Path in the init function is 'output/temp_flag.log'

    def ReadLog(self, path):
        
        if not 'stablist' in globals():
            raise exception('\
            GLOBAL VARIABLE \'stablist\' IS MISSING. SHOULD HAVE BEEN CREATED \
            IN THE MAPFLAGFAILURE.PY MODULE')        
        global stablist
        self.stablist = stablist
        print('SortFlag is getting this list: \n', self.stablist)

        high = set()
        low = set()
        
        for entry in self.stablist:
            tag = entry.split('_')
            det, part, module, channel, gain = tag[0], tag[1], int(tag[2].replace(
                                'm', '')), int(tag[3].replace('c', '')), tag[4]

            if 'highgain' in gain:
                high.add((part, module, channel, gain))
            else:
                low.add((part, module, channel, gain))

## PRESERVING THIS CODE BECAUSE IT COULD BE USEFULL PARSING TEXT WITH REGION
## HASHES IN TEXT FORM.
#         for line in open(path,'r'):
# 
#             if 'region' and 'TILECAL_' in line:
#                 missingregion = True
#                 for entry in self.newlist:
#                     if entry in line:
#                         missingregion = False
#                         self.newlist.remove(entry)
#                         howmany += 1
#                         print howmany
#                 if missingregion:
#                     print 'missing', line
#                     continue
#                         
#                 left, t_hash = line.split('=')
#                 tag = t_hash.split('_')
#                 det, part, module, channel, gain = tag[0], tag[1], int(tag[2].replace(
#                                         'm', '')), int(tag[3].replace('c', '')), tag[4]
# 
#                 gain = gain.rstrip('\n')
#                 
#                 if 'highgain' in gain:
#                     high.add((part, module, channel, gain))
#                 else:
#                     low.add((part, module, channel, gain))
# 
#                     
# 
#             elif 'slimmed' in line:
#                 left, t_hash = line.split(':')
#                 tag = t_hash.split('_')
#                 part, module, channel, gain = tag[0], int(tag[1].lstrip('m')
#                                                   ), int(tag[2].lstrip('c')), tag[3]
#                 part = part.lstrip()
#                 gain = gain.rstrip('\n')
# 
#                 if 'highgain' in gain:
#                     high.add((part, module, channel, gain))
#                 else:
#                     low.add((part, module, channel, gain))

        tot = [high, low]

        return high, low, tot
        


    def ProcessData(self, high, low, total):

        high_nogain = set()
        low_nogain = set()

        for part, mod, chan, gain in high:
            high_nogain.add((part, mod, chan))

        for part, mod, chan, gain in low:
            low_nogain.add((part, mod, chan))

        bad_pmts = high_nogain & low_nogain

        bad_pmt_list = list(bad_pmts)

        bad_pmt_list = sorted(bad_pmt_list, key=itemgetter(0,1,2))

        # print bad_pmt_list 

        for part, mod, chan in bad_pmt_list:
            self.log_pmt.write('PMT: %s_%s_%s\n' %(part, mod, chan))
           
        pastups = []
        pastups = pastups + self.ignore_list
        
        highlist = list(high) #+ self.blist_h
        highlist = sorted(highlist, key=itemgetter(0,1,2,3))
        lowlist = list(low) #+ self.blist_l
        lowlist = sorted(lowlist, key=itemgetter(0,1,2,3))

        listotal = [highlist, lowlist]

        self.slimmed_Friendly.write('selected_region = [')

        for gainset in listotal:
            for part, mod, chan, gain in gainset:

                self.slimmed_Friendly.write('\'%s_m%02d_c%02d_%s\', ' %(part, int(mod), int(chan), gain))
                self.slimmed_total.write('slimmed:  %s_m%02d_c%02d_%s\n' %(part, int(mod), int(chan), gain))

                mval = True
                for offset in range(1, 12):
                    if (part, mod, chan + offset, gain) not in gainset or (
                        part, mod, chan + offset, gain) in pastups:
                       mval = False
                       break
                if mval:
                    self.log_motherb.write('Motherboard: %s_%s_%s_%s through %s\n' %(gain, part, mod, chan, chan+11))
                    for offset in range(0, 12):
                        pastups.append((part, mod, chan + offset, gain))
                    continue

                dval = True
                for offset in range(1, 6):
                    if (part, mod, chan + offset, gain) not in gainset or (
                        part, mod, chan + offset, gain) in pastups:
                       dval = False
                       break
                if dval:
                    self.log_digit.write('\n Digitizer: %s_%s_%s_%s through %s\n' %(gain, part, mod, chan, chan+5))
                    for offset in range(0, 6):
                        pastups.append((part, mod, chan + offset, gain))
                    continue
                
                dmuval = True
                for offset in range(1, 3):
                    if (part, mod, chan + offset, gain) not in gainset or (
                        part, mod, chan + offset, gain) in pastups:
                       dmuval = False
                       break

                if dmuval:
                   self.log_dmu.write('DMU: %s_%s_%s_%s through %s\n' %(gain, part, mod, chan, chan+2))
                   for offset in range(0, 3):
                        pastups.append((part, mod, chan + offset, gain))
                   continue

        self.slimmed_Friendly.write(']')

###### The File Comparing Section: #########

        if self.compare_files:
        
            
            p_high_list = []
            p_low_list = []
                    
            for path in self.pathlist:
                p_high, p_low, p_total = self.ReadLog(path)
                p_high_list.append(high)
                p_low_list.append(low)
    
            setnum = len(p_high_list)
            p_highset = p_high_list[0]
            p_lowset = p_low_list[0]
            
            for x in range(setnum):
                p_highset = p_highset & p_high_list[x] 
                p_lowset = p_lowset & p_low_list[x]
                
            p_totalset = p_highset | p_lowset
    
            sortcomp = list(p_totalset)
            sortcomp = sorted(sortcomp, key=itemgetter(0,1,2,3))
    
            self.log_tdiff_friend.write('selected_region = [')
            p, m, c, g = sortcomp[0]
            self.log_tdiff_friend.write('\'%s_m%02d_c%02d_%s\'' %(p, int(m), int(c), g))
            
            for part, mod, chan, gain in sortcomp[1:]:
               self.log_tdiff.write('slimmed:  %s_m%02d_c%02d_%s\n' %(part, int(mod), int(chan), gain))
               self.log_tdiff_friend.write(', \'%s_m%02d_c%02d_%s\'' %(part, int(mod), int(chan), gain))
            self.log_tdiff_friend.write(']')


    def ProcessStop(self):

#        os.remove(self.path1)

        self.log_pmt.close()
        self.log_dmu.close()
        self.log_digit.close()
        self.log_motherb.close()
        self.slimmed_total.close()
        self.slimmed_Friendly.close()
        
        if self.compare_files:
            self.log_tdiff.close()
            self.log_tdiff_friend.close()

    def ProcessRegion(self, region):

        return region
                
