# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# Define 'region' objects, which is what makes up the detector tree.
# Each 'region' has various attributes: it's parent(s), it child(ren),
# and any 'event'-objects associated with it.  One can also call the
# GetHash() method to get a unique location for this region in the
# detector geometry tree.
#
# NOTE: Do *not* access variables with '__' before them.  Use the
# functions that start with 'Get'.  For instance, GetHash().
#
# March 04, 2009
#
import re


class Region:
    
    def __init__(self, name, type='readout', run2mapping=True):
        # The parents of a node form a list, which is just an ordered
        # set.  The reason for this is that since nodes can have many parents,
        # we need some way to determine what the primary parent is.  This is
        # necessary when trying to determine the hash of a region (ie. where
        # it is in the tree). This is a 'hack' or 'feature' to get around the
        # detector 'tree' actually being a graph... yet we still want it to be
        # tree-like.
        self.__parents = []

        # The children of a node form a set.  No preference is given to one child
        # or anything (like any good parent :P). Unlike the case of many parents,
        # trees are allowed to have many children.  
        self.__children = set()

        # These are the events associated with a particular region. See src/event.py
        self.__events = set()

        # This dictionary (or map) stores a unique identifier for each region.
        # The reason this is a map is because there are many ways this hash
        # can be formed, so we store different hashes for each naming convention
        # and each pseudo-geometry (physical with cells or read-out
        self.__hashs = {}

        # There are many possible names for any given region. For instance,
        # one could call a region PMT 39 or channel 18. The name variable
        # should either be a string or a list of strings, whilst the __name
        # variable is a list of strings.
        assert(isinstance(name, (str, list)))
        if isinstance(name, str):
            self.__names = [name]
        elif isinstance(name, list):
            assert(len(name) > 0)
            for item in name:
                assert(isinstance(item, str))
            self.__names = name

        # The 'type' for any given region says if region is part of
        # the read-out electronics (partitions, modules, channels) or
        # the physical geometry (cells, towers).  In the case of ambiguity,
        # then assume 'readout'.  
        assert(type == 'readout' or type == 'physical' or type == 'b175' or type== 'testbeam')
        self.__type = type
        self.__run2mapping = run2mapping
        self.data = {}
        

    @property
    def events(self):
        '''In reality, events should just be a straight-up attr.  No reason to
        have the Add and Set methods.  The decorators are used for backwards
        compatibility'''
        return self.__events


    @events.setter
    def events(self, value):
        self.__events = value


    def __str__(self):
        return self.GetHash()


    def __repr__(self):
        return self.GetName()


    def parents(self):
        return self.__parents

    def __contains__(self, other_region):

        if '_s' in other_region or '_t' in other_region:
            other_regtype = 'physical'
        else:
            other_regtype = 'readout'

        if self.__type == other_regtype:
            return (str(other_region) in str(self))

        if other_regtype == 'readout':
            chans = self.GetChannels(useSpecialEBmods=True)
            readout = re.sub('(_s[A-E]+)?(_t\d+)?', '', str(self))
            readout += '_c%02d'
            return any(other_region in readout % chan for chan in chans)
        
        elif other_regtype == 'physical':
            chans = Region(other_region, type='physical').GetChannels(useSpecialEBmods=True)
            readout = re.sub('(_s[A-E]+)?(_t\d+)?', '', other_region)
            readout += '_c%02d'
            return any(readout % chan in str(self) for chan in chans)

        else:
            print('other_regtype')
            print(other_region)
            return False


    def GetEvents(self):
        return self.__events


    def AddEvent(self,event):
        event.SetRegion(self)
        self.__events.add(event)


    def SetEvents(self,events):
        self.__events = events


    def GetHash(self, name_index=0, parent_index=0):
        assert(isinstance(name_index, int) and name_index >= 0)
        assert(isinstance(parent_index, int) and parent_index >= 0)
        
        key = '%d_%s_%d' % (name_index, self.__type, parent_index)
        if key in self.__hashs:
            return self.__hashs[key]
        
        parent = self.GetParent(self.__type, parent_index)

        if parent:
            self.__hashs[key] = parent.GetHash(name_index, parent_index) + '_' + self.GetName(name_index)
        else:
            self.__hashs[key] = self.GetName(name_index)

        return self.__hashs[key]


    def get_module(self):
        '''Function to get the module.

        This function gives the detector module of the registered event.'''
        
        cell_hash = self.GetHash().split("_")

        module  = [x for x in cell_hash[2] if x.isdigit()]
        
        return module


    def get_channel(self):
        '''Function to get the channel.

        This function gives the detector channel of the registered event.'''


        cell_hash = self.GetHash().split("_")

        channel = ''.join(str(x) for x in cell_hash[3] if x.isdigit())
        
        return channel


    def get_gain(self):
        '''Function to get the gain.

        This function gives the gain of the registered event.'''

        cell_hash = self.GetHash().split("_")

        gain = cell_hash[4]

        return gain


    def get_partition(self):
        '''Function to get the partition.

        This function gives the partition of the registered event.'''

        cell_hash = self.GetHash().split("_")

        partition = cell_hash[1]

        return partition


    def GetName(self, name_index=0):
        assert(isinstance(name_index, int) and name_index >= 0)
        if 0 <= name_index < len(self.__names):
            return self.__names[name_index]
        else:
            return self.__names[0]


    def GetChildren(self, type):
        # Return regions that are of the type requested. If none
        # exist, then return all regions.
        assert(type == 'readout' or type == 'physical' or type == 'b175' or type== 'testbeam')
        if not self.__children or self.__children == set():
            return set()
        
        found = False
        newregions= set()
        for region in self.__children:
            if region.GetType() == type:
                newregions.add(region)
                found = True
                
        if found:
            return newregions
        else:
            return self.__children


    def SetChildren(self, children):
        # The children should either be a region or set of regions
        assert(isinstance(children,(Region, set)))
        if isinstance(children, Region):
            self.__children = self.__children | set([children])
        elif isinstance(children, set):
            for item in children:
                assert(isinstance(item, Region))
            self.__children = self.__children | children


    def GetType(self):
        return self.__type


    def GetParent(self, type='readout', parent_index = 0):
        assert(type == 'readout' or type == 'physical' or type == 'b175' or type== 'testbeam')
        assert(isinstance(parent_index, int) and parent_index >= 0)

        if not self.__parents or len(self.__parents) == 0:
            return None
        
        for p in self.__parents:
            if p.GetType()==type:
                return p
        
        if 0 <= parent_index < len(self.__parents):
            return self.__parents[parent_index]
        else:
            return self.__parents[0]
    

    def SetParent(self, parent):
        # The name should either be a region or list of regions
        assert(isinstance(parent,(Region, list)))
        if isinstance(parent, Region):
            self.__parents.append(parent)
        elif isinstance(parent, list):
            for item in parent:
                assert(isinstance(item, Region))
                self.__parents.append(item)


    def SanityCheck(self):
        if self.__parents:
            for region in self.__parents:
                if self not in region.__children:
                    print("Error: My parents have disowned me")

        if self.__children:
            for region in self.__children:
                if self not in region.__parents:
                        print("Error: My children have disowned me")
    
    # The depth corresponds to how far down the tree the Print() method
    # should go before stopping.  A depth of -1 means that this parameter
    # is ignored and the whole tree is printed.
    def Print(self, depth = -1, name_index=0, type='readout', parent_index=0):
        print((self.GetName(name_index), self.GetHash(name_index, type, parent_index)))
        depth = depth - 1

        if depth != 0 and self.GetChildren(type) != set():
            for child in self.GetChildren(type):
                child.Print(depth)

    
    def RegionGenerator(self,type='readout'):
        if self.GetChildren(type):
            for child in self.GetChildren(type):
                for i in child.RegionGenerator(type):
                    yield i
        yield self


    def RecursiveGetEvents(self,type='readout'):
        newevents = set()
        if self.GetEvents():
            newevents = newevents | self.GetEvents()
        if self.GetChildren(type) != set():
            for region in self.GetChildren(type):
                newevents = newevents | region.RecursiveGetEvents()
        return newevents
                

    def GetNumber(self, name_index=0, parent_index=0):
        hash = self.GetHash(name_index)
        if hash.startswith('TILECAL'):
            hash = hash.split('_')[1:]
        else:
            hash = hash.split('_')
        number = []
        if len(hash) >= 1: # get partition or side
            part = {'LBA':1,'LBC':2,'EBA':3,'EBC':4}
            number.append(part[hash[0]])
        if len(hash) >= 2: # get module
            number.append(int(hash[1][1:]))
        if len(hash) >= 3: # get channel or sample
            if self.__type == 'physical':
                samp= {'A':0,'BC':1,'D':2,'E':3}
                number.append(samp[hash[2][1:]])
            else:
                number.append(int(hash[2][1:]))
        if len(hash) >= 4: # get ADC
            if self.__type == 'physical':
                if hash[3][0] == 't':
                    number.append(int(hash[3][1:]))
                elif hash[3][:4] == 'MBTS':
                    number.append(15)
            else:
                gain = {'lowgain':0,'highgain':1}
                number.append(gain[hash[3]])
        return number
    

    def GetChannels(self,useSpecialEBmods):
        '''Returns list of channel names belonging to tower'''
        chans = []
        if 'MBTS' in self.GetName():
            if self.__run2mapping:
                part, module, sample, tower = self.GetNumber()
                # in run 2 the MBTS are attached to the pmt 5 and 13, killing some C10 and E1 pmts.
                if (module>=39 and module<=42) or (module>=55 and module<=58):
                    return [4]
                else:
                    return [12]
            else:
                return [0]      # in run 1 the MBRTS where killing some E3 pmts 
        
        elif not 't' in self.GetName():
            print('GetChannels only meaningful for tower regions')
            return chans
        # returns list of channels in cell
        # -1 denotes special PMT in D0 that is actually on LBC
        cell2chan= [\
                    #LB
                    [\
                       #A
                       [ [1,4],[5,8],[9,10],[15,18],[19,20],[23,26],[29,32],[35,38],[37,36],[45,46] ],\
                       #BC
                       [ [3,2],[7,6],[11,12],[17,16],[21,22],[27,28],[33,34],[39,40],[47,42] ],\
                       #D
                       [ [-1,0],[],[13,14],[],[25,24],[],[41,44] ],\
                       #E
                       []
                    ],\
                    #EB
                    [\
                       #A
                       [ [],[],[],[],[],[],[],[],[],[],[],[7,6],[11,10],[21,20],[32,31],[40,41] ],\
                       #BC
                       [ [],[],[],[],[],[],[],[],[],[5,4],[9,8],[15,14],[23,22],[35,30],[36,39] ],\
                       #D
                       [ [],[],[],[],[],[],[],[],[3,2],[],[17,16],[],[37,38] ],\
                       #E
                       [ [],[],[],[],[],[],[],[],[],[],[12],[13],[],[0],[],[1] ] \
                    ]\
                   ]
        
        part, module, sample, tower = self.GetNumber()
        if part<=2: 
            barrel=0
        else: 
            barrel=1

        # special modules: EBA15 and EBC18
        if useSpecialEBmods and ((part==3 and module==15) or (part==4 and module==18)):
            # fix it
            cell2chan= [\
                    #LB
                    [],
                    #EB
                    [\
                       #A
                       [ [],[],[],[],[],[],[],[],[],[],[],[7,6],[11,10],[21,20],[32,31],[40,41] ],\
                       #BC
                       [ [],[],[],[],[],[],[],[],[],[5,4],[9,8],[15,14],[23,22],[35,30],[36,39] ],\
                       #D  - D5 (or D10) merged with D4 (or D08)
                       [ [],[],[],[],[],[],[],[],[],[],[17,16],[],[37,38] ],\
                       #E
                       # E3, E4 -> chan 18, 19
                       [ [],[],[],[],[],[],[],[],[],[],[12],[13],[],[18],[],[19] ] \
                    ]\
                   ]            

            
        chans = cell2chan[barrel][sample][tower]
        return chans


    def GetEtaPhi(self):
        '''Return (eta,phi) of cell position, return None for other region types'''
        if '_t' not in self.GetHash():
            return
        part,module,sample,tower = self.GetNumber()
        if module<33: phi = (module-0.5)/32.0*3.14
        else:         phi = (module-64.5)/32.0*3.14
        if sample < 2:
            eta = tower*0.1+0.05
        elif sample < 3:
            eta = tower*0.1
        else:
            eta= 1.0
        
        if part==2 or part==4:
            eta *= -1.0

        return eta,phi
       

    def GetMBTStype(self):
        """
        Checks if module has MBTS connected to channel 0 and if crack scintillator is missing.
        returns int:
        0 => no MBTS
        1 => MBTS present and crack missing
        2 => MBTS present and crack present
        
        for RUN2 
        0 => no MBTS
        5 => Outer MBTS
        6 => Inner MBTS

        """
        numbers = self.GetNumber()
        if len(numbers)<2:
            print("GetMBTStype error: This should only be called at the module level or lower.")
        part   = numbers[0]
        module = numbers[1]

        if part<3: # LB, no MBTS here
            return 0 
        # Now we are in Extended barrel 
        if self.__run2mapping:
            #if module in [8,24,43,54]: return 5
            if (part==3 and module in [3,8,20,24,43,46,54,59]) or (part==4 and module in [3,8,19,24,43,46,54,59]): return 5 # outer MBTS cell
            if module in [39,40,41,42,55,56,57,58]: return 6 # inner MBTS cell
            return 0
        else:
            if part==3:
                if   module in [3,12,23,30,35,44,53,60]: return 1
                elif module in [4,13,24,31,36,45,54,61]: return 2
                else:                                     return 0
            elif part==4:
                if   module in [4,13,20,28,37,45,54,61]: return 1
                elif module in [5,12,19,27,36,44,55,62]: return 2
                else:                                     return 0


    def GetCellName(self, special_names=False):
        numbers = self.GetNumber(1)
        if len(numbers)<2:
            return "Not part of a cell"
        part   = numbers[0]
        module = numbers[1]
        pmt    = numbers[2]
        
        if self.__run2mapping:
            if part<3: # Long Barrel
                cell_name = [ 'D0',  'A1',          'BC1',         'BC1', 'A1',  'A2',
                              'BC2', 'BC2',         'A2',          'A3',  'A3',  'BC3',
                              'BC3', 'D1',          'D1',          'A4',  'BC4', 'BC4',
                              'A4',  'A5',          'A5',          'BC5', 'BC5', 'A6',
                              'A6',  'D2',          'D2',          'A7',  'BC6', 'BC6',
                              'A7',  'Unconnected', 'Unconnected', 'A8',  'BC7', 'BC7',
                              'A8',  'A9',          'A9',          'D3',  'BC8', 'BC8',
                              'D3',  'Unconnected', 'B9',          'B9',  'A10', 'A10'  ]
                
            else:      # Extended Barrel
                if (part==3 and module==15) or (part==4 and module==18):
                    cell_name = ['Unconnected', 'Unconnected', 'Unconnected', 'Unconnected', 'C10', 'C10',
                                 'A12',         'A12',         'B11',         'B11',         'A13', 'A13',
                                 'E1',          'E2',          'B12',         'B12',         'D45', 'D45',
                                 'E3',          'E4',          'A14',         'A14',         'B13', 'B13',
                                 'Unconnected', 'Unconnected', 'Unconnected', 'Unconnected', 'A15', 'A15',
                                 'Unconnected', 'Unconnected', 'B14',         'B14',         'Unconnected', 'Unconnected', 
                                 'D6',          'D6',          'Unconnected', 'Unconnected', 'A16', 'A16',
                                 'B15',         'B15',         'Unconnected', 'Unconnected', 'Unconnected', 'Unconnected']
                else:
                    
                    cell_name = ['E3',          'E4',          'D4',          'D4',          'C10', 'C10',
                                 'A12',         'A12',         'B11',         'B11',         'A13', 'A13',
                                 'E1',          'E2',          'B12',         'B12',         'D5',  'D5',
                                 'Unconnected', 'Unconnected', 'A14',         'A14',         'B13', 'B13',
                                 'Unconnected', 'Unconnected', 'Unconnected', 'Unconnected', 'A15', 'A15', 
                                 'Unconnected', 'Unconnected', 'B14',         'B14',         'Unconnected', 'Unconnected', 
                                 'D6',          'D6',          'Unconnected', 'Unconnected', 'A16', 'A16',
                                 'B15',         'B15',         'Unconnected', 'Unconnected', 'Unconnected', 'Unconnected']

                if module in [39,40,41,42,55,56,57,58]: # inner MBTS cell
                    cell_name[4] = 'E6'
                    if special_names:
                        cell_name[5] = 'spC10'

                elif (part==3 and module in [3,8,20,24,43,46,54,59]) or (part==4 and module in [3,8,19,24,43,46,54,59]) : # outer MBTS cell
                    cell_name[12] = 'E5'


                if special_names:
                    if (part == 4) and (module in [29,32,34,37]): # E4 prime
                        cell_name[12] = "E4'"

                    elif (part == 4) and (module in [28,31,35,38]): # E1 merged because of E4 prime
                        cell_name[12] = "E1m"

#                    if module in [7, 25, 44, 53] or ((part == 4) and (module in [28, 31, 35, 38])): # E1 merged
                    elif (part==3 and module in [4,7,21,25,44,47,53,60]) or (part==4 and module in [4,7,18,25,44,47,53,60]) :  # This are merged cells to give space to the MBTS 
                        cell_name[12] = "E1m"

            return cell_name[pmt-1] 
        else:
            return "not implemented for run1"

    def GetLayerName(self):
        numbers = self.GetNumber(1)
        if len(numbers)<2:
            return "Not part of a cell"
        
        part   = numbers[0]
        module = numbers[1]
        pmt    = numbers[2]
        
        if self.__run2mapping:
            if part<3: # Long Barrel
                layer_name = [ 'D',  'A', 'BC', 'BC', 'A',  'A',
                              'BC', 'BC','A',  'A',  'A',  'BC',
                              'BC', 'D', 'D',  'A',  'BC', 'BC',
                              'A',  'A', 'A',  'BC', 'BC', 'A',
                              'A',  'D', 'D',  'A',  'BC', 'BC',
                              'A',  '',  '',   'A',  'BC', 'BC',
                              'A',  'A', 'A',  'D',  'BC', 'BC',
                              'D',  '',  'B',  'B',  'A',  'A'  ]
                
            else:      # Extended Barrel
                if (part==3 and module==15) or (part==4 and module==18):
                    layer_name = [ '',   '',   '',   '', 'C', 'C',
                                   'A',  'A',  'B', 'B', 'A', 'A',
                                   'E1', 'E2', 'B', 'B', 'D', 'D',
                                   'E3', 'E4', 'A', 'A', 'B', 'B',
                                   '',   '',    '', '',  'A', 'A',                       
                                   '',   '',   'B', 'B', '',  '', 
                                   'D',  'D',  '',  '',  'A', 'A',
                                   'B',  'B',  '',  '',  '', '']
                else:
                    
                    layer_name = ['E3', 'E4', 'D', 'D', 'C', 'C',
                                  'A',  'A',  'B', 'B', 'A', 'A',
                                  'E1', 'E2', 'B', 'B', 'D', 'D',
                                  '',   '',   'A', 'A', 'B', 'B',
                                  '',   '',   '',  '',  'A', 'A',                       
                                  '',   '',   'B', 'B', '',  '', 
                                  'D',  'D',  '',  '',  'A', 'A',
                                  'B',  'B',  '',  '',  '',  '']
                    
                if module in [39,40,41,42,55,56,57,58]: # inner MBTS cell
                    layer_name[4] = 'MBTS'
                elif (part==3 and module in [3,8,20,24,43,46,54,59]) or (part==4 and module in [3,8,19,24,43,46,54,59]): # outer MBTS cell
                    layer_name[12]  = 'MBTS'
            return layer_name[pmt-1] 

        
    def GetMBTSname(self):
        '''Returns MBTS name stub consistent with L1 trigger name'''
        numbers = self.GetNumber()
        if len(numbers)<2:
            print("GetMBTSname error: This should only be called at the module level or lower.")
        part   = numbers[0]
        module = numbers[1]
        nameStr = ''
        if self.__run2mapping:
            if part==3:
                nameStr +='A'
            elif part==4:
                nameStr +='C'
            if (part==3 and module in [3,8,20,24,43,46,54,59]) or (part==4 and module in [3,8,19,24,43,46,54,59]): # outer MBTS cell
                nameStr +'_Outer'
                if module==3:
                    nameStr +'8'
                elif module==8:
                    nameStr +'9'
                elif module==19 or module==20:
                    nameStr +'10'
                elif module==24:
                    nameStr +'11'
                elif module==43:
                    nameStr +'12'
                elif module==46:
                    nameStr +'13'
                elif module==54:
                    nameStr +'14'
                elif module==59:
                    nameStr +'15'
            elif module in [39,40,41,42,55,56,57,58]: # inner MBTS cell
                nameStr +'_Inner'
                if module==39:
                    nameStr += '2'
                elif module==40:
                    nameStr += '3'
                elif module==41:
                    nameStr += '4'
                elif module==42:
                    nameStr += '5'
                elif module==55:
                    nameStr += '6'
                elif module==56:
                    nameStr += '7'
                elif module==57:
                    nameStr += '0'
                elif module==58:
                    nameStr += '1'

        return nameStr


    def GetCrackPartner(self):
        '''Returns module name of partner module 
        with which region shares crack scintillator'''
        numbers = self.GetNumber()
        if len(numbers)<2:
            print("GetCrackPartner error: This should only be called at the module level or lower.")
        part   = numbers[0]
        module = numbers[1]
        modName = ''
        if part==3:
            for pair in [(3,4),(12,13),(23,24),(30,31),(35,36),(44,45),(53,54),(60,61)]:
                if module == pair[0]:   modName = 'm%02d' % pair[1]
                elif module == pair[1]: modName = 'm%02d' % pair[0]
        elif part==4:
            for pair in [(4,5),(13,12),(20,19),(28,27),(37,36),(45,44),(54,55),(61,62)]:
                if module == pair[0]:   modName = 'm%02d' % pair[1]
                elif module == pair[1]: modName = 'm%02d' % pair[0]
        return modName
    
        
def constructTileCal(useMBTS=True, useSpecialEBmods=True, RUN2=True):
    """
    constructTileCal() will construct all of the regions of TileCal:
    partitions, module, channels/pmts, gains, cells, and towers.  It
    will also appropriately set the parents and children of each module.
    So, for example, LBA module 32 has a child called PMT 3. This function
    will first construct the 'readout' tree (ie. no cells, towers).  Then
    it will appropriately add cells and towers. In the future, it may contain
    digitizers, DMUs, etc.
    """
    print("Constructing TileCal detector tree: ")
    if RUN2:
        print("\tRUN2: MBTS mapping is enabled, AFAIK, Henric")

    if useMBTS and not RUN2: 
        print("\tATTENTION: MBTS mapping using RUN1 cabling is enabled")
        print("\t           If you need RUN2 cabling, set RUN2=True in Go(...)")

    if useSpecialEBmods: print("\tSpecial mapping in EBA15 and EBC18 enabled")
    #
    # Level 1: TileCal and it's partitions
    #

    # TileCalorimeter
    tilecal = Region('TILECAL', run2mapping=RUN2)

    # there are 4 partitions
    partitions = set([Region('EBA', run2mapping=RUN2),  \
                          Region('LBA', run2mapping=RUN2),\
                          Region('LBC', run2mapping=RUN2),\
                          Region('EBC', run2mapping=RUN2)])
                  
    # set parents and children
    tilecal.SetChildren(partitions)
    for partition in partitions:
        partition.SetParent(tilecal)

    #
    # Level 2: Tell the partitions which modules they have modules
    #

    # holder for LBC's D0 channel
    chD0 = {}

    # holder for EB's cross module crack scintillators
    chCrack = {}
    chCrack['EBA'] = {}
    chCrack['EBC'] = {}
    
    for partition in tilecal.GetChildren(type='readout'):
        # construct each of the 64 modules
        modules = set([Region('m%02d' % x, run2mapping=RUN2) for x in range(1, 65)])

        #modules.add(Region('m00', type='testbeam'))
        #modules.add(Region('m65', type='b175'))
        
        # and make them children of the partition
        partition.SetChildren(modules)
        for module in modules:
            # tell the modules who their parent is
            module.SetParent(partition)
        
        # The chan2pmt variable provides the mapping between channel number
        # and PMT number.  Negative values means the PMT doesn't exist. Use
        # the variable as follows: pmt_number = chan2pmt[channel_number]
        chan2pmt = []
        EB = False
        if partition.GetName() == 'EBA' or partition.GetName() == 'EBC':
            EB = True
            chan2pmt=[1,   2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12,  \
                          13, 14, 15, 16, 17, 18,-19,-20, 21, 22, 23, 24,  \
                         -27,-26,-25,-31,-32,-28, 33, 29, 30,-36,-35, 34, \
                          44, 38, 37, 43, 42, 41,-45,-39,-40,-48,-47,-46]
        elif partition.GetName() == 'LBA' or partition.GetName() == 'LBC':
            EB = False
            chan2pmt=[1,   2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, \
                          13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, \
                          27, 26, 25, 30, 29, 28,-33,-32, 31, 36, 35, 34, \
                          39, 38, 37, 42, 41, 40, 45,-44, 43, 48, 47, 46]

        # EBA15 and EBC18 are special
        # https://twiki.cern.ch/twiki/bin/view/Atlas/SpecialModules#Module_Type_11
        # The PMT mapping is a little different since it's a physically
        # smaller drawer
        chan2pmtSpecial = [-1, -2, -3, -4,  5,  6,  7,  8,  9, 10, 11, 12, \
                           13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, \
                          -27,-26,-25,-31,-32,-28, 33, 29, 30,-36,-35, 34, \
                           44, 38, 37, 43, 42, 41,-45,-39,-40,-48,-47,-46]
        
        for module in partition.GetChildren(type='readout'):
            # For each module, create the PMTs/channels within it
            if useSpecialEBmods and \
              ((partition.GetName() == 'EBA' and module.GetName() == 'm15') or\
               (partition.GetName() == 'EBC' and module.GetName() == 'm18')):
                channels = set([Region(['c%02d' % x, 'p%02d' % chan2pmtSpecial[x]]) for x in range(48) if chan2pmtSpecial[x] > 0])
#            elif (partition.GetName() == 'LBA' and module.GetName() == 'm14'): # Demonstrator
#                channels = set(Region(['c%02d' % x, 'p%02d' % (x+1)]) for x in range(48) if not (x==31 or x==32 or x==43#))
            else:
                channels = set([Region(['c%02d' % x, 'p%02d' % chan2pmt[x]]) for x in range(48) if chan2pmt[x] > 0])
            module.SetChildren(channels)
            for channel in module.GetChildren(type='readout'):
                channel.SetParent(module)
                # save D0 channel for later matching with cell
                if partition.GetName()=='LBC' and channel.GetName() == 'c00':
                    chD0[module.GetName()] = channel
                # save E channels connected to neighboring module
                if RUN2:
                    pass
                #  Not sure something is needed here. 
                #   if EB and channel.GetName() == 'c04' and module.GetMBTStype() == 6:
                #   if EB and channel.GetName() == '12' and module.GetMBTStype() == 5:
                else:
                    if EB and channel.GetName() == 'c01' and module.GetMBTStype() == 1:
                        chCrack[partition.GetName()][module.GetName()] = channel

            # Create both gains
            for channel in module.GetChildren(type='readout'):
                gains = set([Region('lowgain', run2mapping=RUN2), Region('highgain', run2mapping=RUN2)])
                channel.SetChildren(gains)
                for gain in channel.GetChildren(type='readout'):
                    gain.SetParent(channel)

    # For each module, create the cells ('physical' part of detector tree)
    for partition in tilecal.GetChildren(type='readout'):
        for module in partition.GetChildren(type='readout'):
            samples = set([Region(name='s%s' % x, run2mapping=RUN2, type='physical') for x in ['A','BC','D','E']])
            module.SetChildren(samples)
            MBTStype = module.GetMBTStype()
            for sample in module.GetChildren('physical'):
                sample.SetParent(module)
                towers = set()
                if 'LB' in partition.GetName():        # Towers in long barrel 
                    if 'A'  in sample.GetName():
                        towers = set([Region('t%02d' % x, type='physical', run2mapping=RUN2) for x in range(10)])
                        
                    elif 'BC' in sample.GetName():
                        towers = set([Region('t%02d' % x, type='physical', run2mapping=RUN2) for x in range(9)])
                        
                    elif  'D' in sample.GetName():
                        if 'LBA' == partition.GetName(): #Draw D0 cell on A-side
                            towers = set([Region('t%02d' % x , type='physical', run2mapping=RUN2) for x in [0,2,4,6]])
                        else:
                            towers = set([Region('t%02d' % x , type='physical', run2mapping=RUN2) for x in [2,4,6]])

                else:                                # Towers in extended barrel 
                    if 'A'  in sample.GetName():
                        towers = set([Region('t%02d' % x , type='physical', run2mapping=RUN2) for x in [11,12,13,14,15]])

                    elif 'BC' in sample.GetName():
                        towers = set([Region('t%02d' % x , type='physical', run2mapping=RUN2) for x in [9,10,11,12,13,14]])

                    elif 'D' in sample.GetName():
                        # Special Modules have D08 merged with D10
                        if useSpecialEBmods and \
                          ((partition.GetName() == 'EBA' and module.GetName() == 'm15') or \
                           (partition.GetName() == 'EBC' and module.GetName() == 'm18')):
                            towers = set([Region('t%02d' % x , type='physical', run2mapping=RUN2) for x in [10,12]])
                        else:
                            towers = set([Region('t%02d' % x , type='physical', run2mapping=RUN2) for x in [8,10,12]])

                    elif 'E' in sample.GetName():
                        if not useMBTS or MBTStype==0: 
                            towers = set([Region('t%02d' % x , type='physical', run2mapping=RUN2) for x in [10,11,13,15]])

                        elif MBTStype==1: # MBTS pass through, crack scintillator missing
                            towers = set([Region('t%02d' % x , type='physical', run2mapping=RUN2) for x in [10,11]])
                            towers.add( Region('MBTS'+sample.GetMBTSname(), type='physical', run2mapping=RUN2) )

                        elif MBTStype>1:
                            towers = set([Region('t%02d' % x , type='physical') for x in [10,11,13,15]])
                            towers.add( Region('MBTS'+sample.GetMBTSname(), type='physical', run2mapping=RUN2) )
                                
                sample.SetChildren(towers)
                for tower in sample.GetChildren(type='physical'):
                    tower.SetParent(sample)
                    # Connect readout channels to physical cells
                    chans = set()
                    chanNumbers = tower.GetChannels(useSpecialEBmods)
                    
                    if -1 in chanNumbers: # take care of D0 cell
                        chans.add(chD0[module.GetName()])
                        for ch in module.GetChildren(type='readout'):
                            if int(ch.GetName()[1:]) == 0:
                                chans.add(ch)
                    # take care of cross-module crack scintillators
                    elif useMBTS and MBTStype==2 and 'sE_t15' in tower.GetHash():
                        chans.add(chCrack[partition.GetName()][tower.GetCrackPartner()])
                    else: # All others
                        for ch in module.GetChildren(type='readout'):
                            if int(ch.GetName()[1:]) in chanNumbers:
                                chans.add(ch)
                    
                    tower.SetChildren(chans)
                    for ch in tower.GetChildren('readout'):
                        ch.SetParent(tower)
                        
    return tilecal

