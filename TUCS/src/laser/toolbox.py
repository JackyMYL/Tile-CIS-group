# Author: Seb Viret <viret@in2p3.fr>
#
# July 07, 2009
# Modifications :
#        November 2011, D. Boumediene, E. Dubreuil
#                  Functions get_stable_cells and get_cells_index
#                  (commited)
#        July 2013, R. Pedro
#                  Function getDMU

class LaserTools:
    "This is the laser toolbox"

    # Get the channel position (SV: how to get that from region.py???)
    def GetNumber(self, hash):
        "This produces part [1-4], module[1-64], chan [0-47] and gain strings"
        
        split = hash.split('_')[1:]
        number = []
        if len(split) >= 1:
            if   split[0] == 'LBA': number.append(1)
            elif split[0] == 'LBC': number.append(2)
            elif split[0] == 'EBA': number.append(3)
            elif split[0] == 'EBC': number.append(4)
            else:
                number.append(-1)
        if len(split) >= 2:
            number.append(int(split[1][1:]))
        if len(split) >= 3:
            number.append(int(split[2][1:]))
        if len(split) >= 4:
            if   split[3] == 'lowgain':  number.append(0)
            elif split[3] == 'highgain': number.append(1)
            else:
                number.append(-1)

        return number


    def get_index(self, ros, drawer, chan, gain):
        "This takes ros [0-3], drawer [0-63], chan [0-47], gain numbers" 
        return ros  *64*48*2\
            + drawer   *48*2\
            + chan        *2\
            + gain

    
    def get_rev_index(self, index):
        "This produces ros [0-3], drawer [0-63], chan [0-47, gain numbers" 
        number = []

        gain = index%2
        index -= gain

        chan = (index%96)//2
        index -= 2*chan

        drawer = (index%6144)//96 
        index -= 96*drawer

        part = index//6144

        number.append(part)
        number.append(drawer)
        number.append(chan)
        number.append(gain)

        #print part, drawer, chan, gain

        return number
            
    
    def get_PMT_index(self,ros,drawer,chan):
        "Reorder the PMTs (SV: how to get that from region.py???)"
        "This takes ros [0-3], drawer [0-63], chan [0-47], gain numbers"     
        chan2PMT_Special=[-1,-2,-3,-4,5,6,7,8,9,10, 
              11,12,13,14,15,16,17,18, 19, 20, 
              21,22,23,24,-27,-26,-25,-31,-32,-28, 
              33,29,30,-36,-35,34,44,38,37,43,42, 
              41,-45,-39,-40,-48,-47,-46]
  
        chan2PMT_LB=[1,2,3,4,5,6,7,8,9,10,
                     11,12,13,14,15,16,17,18,19,20,
                     21,22,23,24,27,26,25,30,29,28,
                     -33,-32,31,36,35,34,39,38,37,42,41,
                     40,45,-44,43,48,47,46]
        
        chan2PMT_EB=[1,2,3,4,5,6,7,8,9,10,
                     11,12,13,14,15,16,17,18,-19,-20,
                     21,22,23,24,-25,-26,-27,-28,-31,-32,
                     33,29,30,-35,-36,34,44,38,37,43,42,
                     41,-39,-40,-45,-46,-47,-48]

        if ros == 2 and drawer == 14:
            return chan2PMT_Special[chan]

        if ros == 3 and drawer == 17:
            return chan2PMT_Special[chan]
  
        if ros <= 1: 
            chan = chan2PMT_LB[chan]
        else:
            chan = chan2PMT_EB[chan]
    
        return chan

    
    def is_instrumented(self,ros,drawer, pmt):
        "Tells you if a PMT hole is instrumented or not"
        "This takes ros [0-3], drawer [0-63], !!pmt [1-48]!!, gain numbers" 
        chan2PMT_Special=[-1,-2,-3,-4,5,6,7,8,9,10, 
              11,12,13,14,15,16,17,18, 19, 20, 
              21,22,23,24,-27,-26,-25,-31,-32,-28, 
              33,29,30,-36,-35,34,44,38,37,43,42, 
              41,-45,-39,-40,-48,-47,-46]
  
        chan2PMT_LB=[1,2,3,4,5,6,7,8,9,10,
                     11,12,13,14,15,16,17,18,19,20,
                     21,22,23,24,27,26,25,30,29,28,
                     -33,-32,31,36,35,34,39,38,37,42,41,
                     40,45,-44,43,48,47,46]
        
        chan2PMT_EB=[1,2,3,4,5,6,7,8,9,10,
                     11,12,13,14,15,16,17,18,-19,-20,
                     21,22,23,24,-25,-26,-27,-28,-31,-32,
                     33,29,30,-35,-36,34,44,38,37,43,42,
                     41,-39,-40,-45,-46,-47,-48]

        if ros == 2 and drawer == 14:
            if pmt in chan2PMT_Special:
                return True
            else:
                return False
        elif ros == 3 and drawer == 17:
            if pmt in chan2PMT_Special:
                return True
            else:
                return False            
        elif ros <= 1 and pmt in chan2PMT_LB: 
            return True
        elif ros > 1 and pmt in chan2PMT_EB: 
            return True
        else:
            return False


        
    # Macro necessary for the fiber re-ordering

    def get_fiber_index(self, ros, drawer, pmt):
        "This takes ros [0-3], drawer [0-63], pmt [1-48], gain numbers" 
        if ros <= 1: 
            return  int(128*self.get_part(ros)\
                   +2*drawer+ros+2*(0.5-ros)*(pmt%2))
        else:
            return  int(128*self.get_part(ros)\
                   +2*drawer+(pmt%2))    

    
    # Also for fiber stuff
    def get_part(self, ros):
        if ros <= 1: 
            return  0
        else: 
            return  ros-1


    def get_partition_name(self,ros):

        part_names = ['LBA','LBC','EBA','EBC']

        return part_names[ros]

         
    def get_module_name(self,rosnum,drawer):

        part_names = ['LBA','LBC','EBA','EBC']
        return "%s%02d" % (part_names[rosnum],drawer+1)

    
    def get_fiber_name(self,index):

        cylinder_names   = ['LB','EBA','EBC']
        parityeb = ['E','O']
        paritylb = ['C','A']
        extendedbarrel = index//128
        module  = (index%128)//2 + 1
        parity = index%2

        my_string = "%s%02d%s"

        if extendedbarrel != 0:
            val = (cylinder_names[extendedbarrel], module,parityeb[parity]) 
        else:
            val = (cylinder_names[extendedbarrel], module,paritylb[parity])

        return my_string % val

         
    def get_channel_name(self, ros, drawer, chan):
        "This takes ros [0-3], drawer [0-63], chan [0-47], gain numbers" 
        part_names = ['LBA','LBC','EBA','EBC']
        return "%s%02d_c%02d" % (part_names[ros],drawer+1,chan)
     

    def get_channel_name_index(self, index):
        "This uses ros [0-3], drawer [0-63], chan [0-47], gain numbers" 
        [ros,drawer,chan,gain] =  self.get_rev_index(index)
        return self.get_channel_name(ros,drawer,chan)

        
    def get_pmt_name(self, ros, drawer, chan):
        "This takes ros [0-3], drawer [0-63], chan [0-47], gain numbers" 
        part_names = ['LBA','LBC','EBA','EBC']
        return "%s%02d_pmt%02d" % (part_names[ros],drawer+1,self.get_PMT_index(ros,drawer,chan))


    def get_pmt_name_index(self, index):
        "This uses ros [0-3], drawer [0-63], chan [0-47], gain numbers" 
        [ros, drawer, chan, gain] =  self.get_rev_index(index)
        pmt = self.get_PMT_index(ros,drawer,chan)
        cell = self.get_cell_index(ros, drawer+1, pmt)
        if cell!=600:
            return "%s %s%02d" % ( self.get_pmt_name(ros, drawer, chan),
                                   self.get_pmt_layer(ros, drawer+1, pmt),
                                   cell%100)
        else: 
            return "%s %s" % ( self.get_pmt_name(ros, drawer, chan),
                               self.get_pmt_layer(ros, drawer+1, pmt))

                
    def get_pmt_layer(self, ros, mod, pmt):
        "This takes ros [0-3], !! module [1-64] !!, !! pmt [1-48] !!" 
        a = 'A'
        b = 'B' 
        bc = 'BC'
        c = 'C'
        d = 'D'
        e = 'E'
        u = 'Unconnected'
        m = 'MBTS'
        
#        lb_chan_2_layer = [ d, a, bc, bc, a, a,
#                           bc, bc, a, a, a, bc,
#                           bc, d, d, a, bc, bc,
#                           a, a, a, bc, bc, a,
#                           d, d, a, bc, bc, a,
#                           u, u, a, bc, bc, a,
#                           a, a, a, bc, bc, d,
#                           bc, u, d, a, a, d ]

#        eb_chan_2_layer = [ e, e, d, d, c, c,
#                           a, a, b, b, a, a,
#                           e, e, b, b, d, d,
#                           u, u, a, a, b, b,
#                           u, u, u, u, u, u,
#                           b, a, a, u, u, b,
#                           b, d, d, b, a, a,
#                           u, u, u, u, u, u ]

        lb_pmt_2_layer = [ d, a, bc, bc, a, a,
                           bc, bc, a, a, a, bc,
                           bc, d, d, a, bc, bc,
                           a, a, a, bc, bc, a,
                           a, d, d, a, bc, bc, 
                           a, u, u, a, bc, bc,
                           a, a, a, d, bc, bc,
                           d, u, bc, d, a, a ]

        eb_pmt_2_layer = [ e, e, d, d, c, c,
                           a, a, b, b, a, a,
                           e, e, b, b, d, d,
                           u, u, a, a, b, b,                           
                           u, u, u, u, a, a,
                           u, u, b, b, u, u,
                           d, d, u, u, a, a,
                           b, b, u, u, u, u ]
        if ros <2 :
            return lb_pmt_2_layer[pmt-1]
        else :
            if pmt==1:
                if ros==2:  # MBTS 
                    if mod in (3,4,12,13,23,24,30,31,35,36,44,45,53,54,60,61):
                        return m
                else:
                    if mod in (4,5,12,13,19,20,27,28,36,37,44,45,54,55,61,62):
                        return m
            if (ros==2 and mod == 15) or (ros==3 and mod == 18): # Special modules
                if pmt == 19 or pmt == 20:
                    return 'E'
            return eb_pmt_2_layer[pmt-1]
        return ''

    
    def get_stable_cells(self, ros, pmt):
        """
        Return 3 for cells considered as stable
        0, 1 : for cells mostly affected by luminosity
        -1,-2: error case
        """

        if ros<2:
            if pmt in [2,5,6,9,10,11,16,19,20,21,24,25,28,31,34,37,38,39,47,48]: return 0 #A
            elif pmt in [3,4,7,8,12,13,17,18,22,23,29,30,35,36,41,42]: return 1 #BC
            elif pmt in [1,14,15,26,27]: return 3 #D0-2
            elif pmt in [40,43]: return 4 #D3
            else:                                     return -2 #should not happen
        # else EB
        elif ros>=2:
            if pmt in [17,18,23,24,33,34,37,38,43,44]: return 3 #stables
            elif pmt in [3,4,41,42]: return 1 #intermediaires
            elif pmt in [7,8,11,12,9,10,15,16,21,22,29,30]: return 0 #irradies
            else:                                     return -2 #should not happen
        else:                                         return -1


    def get_cell_index(self, ros, mod, pmt):
        """
        Cell index. Examples : A1 = 101, B2 = 202, C8 = 308
        """
        if ros<2:
            if pmt in [2,5]: return 101 #first A cell
            elif pmt in [6,9]: return 102
            elif pmt in [10,11]: return 103
            elif pmt in [16,19]: return 104
            elif pmt in [20,21]: return 105
            elif pmt in [24,25]: return 106
            elif pmt in [28,31]: return 107
            elif pmt in [34,37]: return 108
            elif pmt in [38,39]: return 109
            elif pmt in [47,48]: return 110 #end of A cells

            elif pmt in [3,4]: return 201
            elif pmt in [7,8]: return 202
            elif pmt in [12,13]: return 203
            elif pmt in [17,18]: return 204
            elif pmt in [22,23]: return 205
            elif pmt in [29,30]: return 206
            elif pmt in [35,36]: return 207
            elif pmt in [41,42]: return 208
            elif pmt in [45,46]: return 209
            
#            elif pmt in [03,04,07,8,12,13,17,18,22,23,29,30,35,36,41,42]: return (200+pmt) #BC
            
            elif pmt == 1: return 400
            elif pmt in [14,15]: return 401
            elif pmt in [26,27]: return 402
            elif pmt in [40,43]: return 403 #D
            else:                                     return -2
        # else EB
        else:            
            if pmt in [ 7,  8]: return 112
            elif pmt in [11, 12]: return 113
            elif pmt in [21, 22]: return 114
            elif pmt in [29, 30]: return 115
            elif pmt in [41, 42]: return 116
            elif pmt in [ 3,  4]: return 404
            elif pmt in [17, 18]: return 405
            elif pmt in [37, 38]: return 406
            elif pmt in [ 9, 10]: return 211
            elif pmt in [15, 16]: return 212
            elif pmt in [23, 24]: return 213
            elif pmt in [33, 34]: return 214
            elif pmt in [43, 44]: return 215
            elif pmt in [ 5,  6]: return 216
            elif pmt == 13: return 501
            elif pmt == 14: return 502
            elif pmt == 2 or pmt == 20: return 504
            elif (pmt == 1) and (ros == 2) and (mod in [3,4,12,13,23,24,30,31,35,36,44,45,53,54,60,61]): return 600 #MBTS
            elif (pmt == 1) and (ros == 3) and (mod in [4,5,12,13,19,20,27,28,36,37,44,45,54,55,61,62]): return 600 #MBTS
            elif (pmt == 1 or pmt == 19): return 503
            else: return -2
    

    def getDigitizer(self, ros, pmt):
        if ros<2:
            digitizer = 8-int(pmt-1)//6
            if digitizer in [1,2,3,4,5,6,7,8]:
                return digitizer
        else:
            if pmt in [1, 2, 3, 4, 5, 6]:
                return 8
            if pmt in [7, 8, 9, 10, 11, 12]:
                return 7
            if pmt in [13, 14, 15, 16, 17, 18]:
                return 6
            if pmt in [19, 20, 21, 22, 23, 24]:
                return 5
            if pmt in [27, 26, 25, 31, 32, 28]:
                return 4
            if pmt in [33, 29, 30, 36, 35, 34]:
                return 3
            if pmt in [44, 38, 37, 43, 42, 41]:
                return 2
            if pmt in [45, 39, 40, 48, 47, 46]:
                return 1
        return 0

    def getDMU(self, chan):
        dmu = (chan-(chan)%3)//3
        return dmu

    def getNewLVPS(self, part, module):

        if part==1: # LBA
            if module in [3, 8, 11, 15, 19, 21, 25, 27, 31, 36, 39, 41, 47, 49, 53, 55, 57]:
                return True
        if part==2: # LBC
            if module in [3, 6, 9, 13, 15, 18, 20, 24, 26, 29, 33, 36, 40, 41, 42, 43, 44, 45, 46, 47, 49, 52, 57, 62, 63]:
                return True
        if part==3: # EBA
            if module in [39]:
                return True
        if part==4: # EBC
            if module in [39]:
                return True                       
        return False


    def getCellName(self, ros, module, pmt):

        if ros <2: # Long Barrel
            names = ['D0',  'A1',          'BC1',         'BC1', 'A1',  'A2',
                     'BC2', 'BC2',         'A2',          'A3',  'A3',  'BC3',
                     'BC3', 'D1',          'D1',          'A4',  'BC4', 'BC4',
                     'A4',  'A5',          'A5',          'BC5', 'BC5', 'A6',
                     'A6',  'D2',          'D2',          'A7',  'BC6', 'BC6',
                     'A7',  'Unconnected', 'Unconnected', 'A8',  'BC7', 'BC7',
                     'A8',  'A9',          'A9',          'D3',  'BC8', 'BC8',
                     'D3',  'Unconnected', 'BC8',          'B9',  'A10', 'A10'  ]
                     
        else:
            if (ros==2 and module==15) or (ros==3 and module==18):
                names = ['Unconnected', 'Unconnected', 'Unconnected', 'Unconnected', 'C10', 'C10',
                         'A12',         'A12',         'B11',         'B11',         'A13', 'A13',
                         'E1',          'E2',          'B12',         'B12',         'D45', 'D45',
                         'E3',          'E4',          'A14',         'A14',         'B13', 'B13',
                         'Unconnected', 'Unconnected', 'Unconnected', 'Unconnected', 'A15', 'A15',                       
                         'Unconnected', 'Unconnected', 'B14',         'B14',         'Unconnected', 'Unconnected', 
                         'D6',          'D6',          'Unconnected', 'Unconnected', 'A16', 'A16',
                         'B15',         'B15',         'Unconnected', 'Unconnected', 'Unconnected', 'Unconnected']
            else:
                names = ['E3',          'E4',          'D4',          'D4',          'C10', 'C10',
                         'A12',         'A12',         'B11',         'B11',         'A13', 'A13',
                         'E1',          'E2',          'B12',         'B12',         'D5',  'D5',
                         'Unconnected', 'Unconnected', 'A14',         'A14',         'B13', 'B13',
                         'Unconnected', 'Unconnected', 'Unconnected', 'Unconnected', 'A15', 'A15',                       
                         'Unconnected', 'Unconnected', 'B14',         'B14',         'Unconnected', 'Unconnected', 
                         'D6',          'D6',          'Unconnected', 'Unconnected', 'A16', 'A16',
                         'B15',         'B15',         'Unconnected', 'Unconnected', 'Unconnected', 'Unconnected']
        if (pmt == 1):
            if ( ((ros == 2) and (module in [ 3, 4,12,13,23,24,30,31,35,36,44,45,53,54,60,61])) or
                 ((ros == 3) and (module in [ 4, 5,12,13,19,20,27,28,36,37,44,45,54,55,61,62])) ):
                 return 'MBTS'

        return names[pmt-1]
	
    def getRegionName(self, cell):
	# reverse function of getCellName
	# gives back partiton and pmt channel(s)
	# structure: [[A-side,C-side],[pmt1,pmt2]]
        cellmap ={# long barrel
            'A1':[[0,1],[1,4]], 'A2':[[0,1],[5,8]], 'A3':[[0,1],[9,10]], 'A4':[[0,1],[15,18]], 'A5':[[0,1],[19,20]], 'A6':[[0,1],[23,24]], 'A7':[[0,1],[27,30]], 'A8':[[0,1],[33,36]], 'A9':[[0,1],[37,38]], 'A10':[[0,1],[46,47]], 'BC1':[[0,1],[2,3]], 'BC2':[[0,1],[6,7]], 'BC3':[[0,1],[11,12]], 'BC4':[[0,1],[16,17]], 'BC5':[[0,1],[21,22]], 'BC6':[[0,1],[28,29]], 'BC7':[[0,1],[34,35]], 'BC8':[[0,1],[40,41]], 'B9':[[0,1],[44,45]], 'D0':[[0,1],[0,0]], 'D1':[[0,1],[13,14]], 'D2':[[0,1],[25,26]], 'D3':[[0,1],[39,42]],
		  # extended barrel:
                'A12':[[2,3],[6,7]], 'A13':[[2,3],[10,11]], 'A14':[[2,3],[20,21]], 'A15':[[2,3],[28,29]], 'A16':[[2,3],[40,41]], 'B11':[[2,3],[8,9]], 'B12':[[2,3],[14,15]], 'B13':[[2,3],[22,23]],  'B14':[[2,3],[32,33]], 'B15':[[2,3],[42,43]], 'C10':[[2,3],[4,5]], 'D4':[[2,3],[2,3]], 'D5':[[2,3],[16,17]], 'D6':[[2,3],[36,37]], 'E1':[[2,3],[12]], 'E2':[[2,3],[13]], 'E3':[[2,3],[0]], 'E4':[[2,3],[1]]	
            }
		
#        for i in cellmap:
#            if cell==i:
        return cellmap[cell]

    def getRegionName2015(self, cell, specialModule=False): # this is only to be used for minbias, since the convention has changed for the input files, take special EBA15 and EBC18 modules into account
	# reverse function of getCellName
	# gives back partiton and pmt channel(s)
	# structure: [[A-side,C-side],[pmt1,pmt2]]
        cellmap ={# long barrel
            'A1':[[1,2],[1,4]], 'A2':[[1,2],[5,8]], 'A3':[[1,2],[9,10]], 'A4':[[1,2],[15,18]], 'A5':[[1,2],[19,20]], 'A6':[[1,2],[23,24]], 'A7':[[1,2],[27,30]], 'A8':[[1,2],[33,36]], 'A9':[[1,2],[37,38]], 'A10':[[1,2],[46,47]], 'BC1':[[1,2],[2,3]], 'BC2':[[1,2],[6,7]], 'BC3':[[1,2],[11,12]], 'BC4':[[1,2],[16,17]], 'BC5':[[1,2],[21,22]], 'BC6':[[1,2],[28,29]], 'BC7':[[1,2],[34,35]], 'BC8':[[1,2],[40,41]], 'B9':[[1,2],[44,45]], 'D0':[[1,2],[0,0]], 'D1':[[1,2],[13,14]], 'D2':[[1,2],[25,26]], 'D3':[[1,2],[39,42]],
		  # extended barrel:
                'A12':[[0,3],[6,7]], 'A13':[[0,3],[10,11]], 'A14':[[0,3],[20,21]], 'A15':[[0,3],[28,29]], 'A16':[[0,3],[40,41]], 'B11':[[0,3],[8,9]], 'B12':[[0,3],[14,15]], 'B13':[[0,3],[22,23]],  'B14':[[0,3],[32,33]], 'B15':[[0,3],[42,43]], 'C10':[[0,3],[4,5]], 'D4':[[0,3],[2,3]], 'D5':[[0,3],[16,17]], 'D6':[[0,3],[36,37]], 'E1':[[0,3],[12,12]], 'E2':[[0,3],[13,13]], 'E3':[[0,3],[0,0]], 'E4':[[0,3],[1,1]]	
            }

        if specialModule  and (cell=="E3" or cell=="E4"):
            cellmap = {'E3':[[0,3],[18,18]],'E4':[[0,3],[19,19]] } # EBA15 and EBC18 cabeling
            
		
#        for i in cellmap:
 #           if cell==i:
        return cellmap[cell]

    def getChannelsLaser(self, cell, specialModule=False): # for laser, Partitions probably wrong, not sure if used anywhere...
	# reverse function of getCellName
	# gives back partiton and pmt channel(s)
	# structure: [[A-side,C-side],[pmt1,pmt2]]
        cellmap ={# long barrel
            'A1':[[1,2],[1,4]], 'A2':[[1,2],[5,8]], 'A3':[[1,2],[9,10]], 'A4':[[1,2],[15,18]], 'A5':[[1,2],[19,20]], 'A6':[[1,2],[23,26]], 'A7':[[1,2],[29,32]], 'A8':[[1,2],[35,38]], 'A9':[[1,2],[36,37]], 'A10':[[1,2],[45,46]], 'BC1':[[1,2],[2,3]], 'BC2':[[1,2],[6,7]], 'BC3':[[1,2],[11,12]], 'BC4':[[1,2],[16,17]], 'BC5':[[1,2],[21,22]], 'BC6':[[1,2],[27,28]], 'BC7':[[1,2],[33,34]], 'BC8':[[1,2],[39,40]], 'B9':[[1,2],[42,47]], 'D0':[[1,2],[0,0]], 'D1':[[1,2],[13,14]], 'D2':[[1,2],[24,25]], 'D3':[[1,2],[41,44]],
		  # extended barrel:
                'A12':[[0,3],[6,7]], 'A13':[[0,3],[10,11]], 'A14':[[0,3],[20,21]], 'A15':[[0,3],[31,32]], 'A16':[[0,3],[40,41]], 'B11':[[0,3],[8,9]], 'B12':[[0,3],[14,15]], 'B13':[[0,3],[22,23]],  'B14':[[0,3],[30,35]], 'B15':[[0,3],[36,39]], 'C10':[[0,3],[4,5]], 'D4':[[0,3],[2,3]], 'D5':[[0,3],[16,17]], 'D6':[[0,3],[37,38]], 'E1':[[0,3],[12,12]], 'E2':[[0,3],[13,13]], 'E3':[[0,3],[0,0]], 'E4':[[0,3],[1,1]]	
            }

        if specialModule  and (cell=="E3" or cell=="E4"):
            cellmap = {'E3':[[0,3],[18,18]],'E4':[[0,3],[19,19]] } # EBA15 and EBC18 cabeling
            
		
#        for i in cellmap:
 #           if cell==i:
        return cellmap[cell]


#The End
