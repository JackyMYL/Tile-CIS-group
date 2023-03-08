# Author: Mikhail Makouski <Mikhail.Makouski@cern.ch>
#
# March 04, 2009
# November 24, 2009 - updated for 2009 AS
# February 24, 2010 - updated for 2010 AS
# February 20, 2011 - updated for 2011 AS
#

# settings for 2010 (not used now)

# PMT's that had wrong constants in 2009 db, updated in 2010

# PMTs that bad in Cs but the problem is in Cs. Readout works fine (keep default value)
deadchan={
    'LBA':{9:[9],17:[15,25],37:[2],50:[19]},
    'LBC':{55:[3]},
    'EBA':{24:[17],61:[17]},
    'EBC':{}
    }

# PMT's that bad in Cs but this is the way they work (keep what was measured by Cs)
# LBC12 pmt 18,24 EBC53 pmt 43, EBC64 pmt 30 added in June 2010
unstabchan={
    'LBA':{15:[17],43:[27],50:[25],59:[37]},
    'LBC':{2:[37],3:[43],12:[18,24],16:[25],21:[46],23:[14],29:[25],36:[27],60:[35]},
    'EBA':{7:[11],12:[33]},
    'EBC':{5:[5],53:[22,43],64:[30]}
    }

# PMT's that had very different value in previous update - should use latest measured value
wrongchan={
    'LBA':{18:[14],36:[3,4,7,8],46:[3,4,7,8]},
    'LBC':{18:[14],
           12:[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48]},
    'EBA':{15:[17,18],19:[3,4],36:[7,8,11,12],37:[7,8,11,12],60:[7,8,11,12],61:[7,8,11,12],62:[5,6]},
    'EBC':{18:[17,18],36:[7,8,11,12],37:[7,8,11,12],60:[7,8,11,12],61:[7,8,11,12]}
    }

# channels to rerun - bad or affected in 2008 and 2009 - fixed in Feb 2010; LBC12 in emergency mode
rerunchan ={
    'LBA':{1:[25],8:[28],9:[9],15:[17],17:[15,25],18:[14,29],26:[1],35:[34],
           36:[3,4,7,8],37:[2],39:[43],43:[27],46:[3,4,7,8],50:[19,25],59:[13,37]},
    'LBC':{2:[37],3:[43],11:[37],16:[25],18:[14],20:[29],21:[46],23:[14],25:[18],29:[25],36:[27],55:[3],60:[35],
           12:[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48]},
    'EBA':{4:[6],7:[11],8:[22],11:[30],12:[33],18:[23],24:[17],53:[5],
           15:[17,18],19:[3,4],36:[7,8,11,12],37:[7,8,11,12],60:[7,8,11,12],61:[7,8,11,12,17],62:[5,6]},
    'EBC':{5:[5],26:[3],43:[5],48:[34],53:[22],
           18:[17,18],36:[7,8,11,12],37:[7,8,11,12],60:[7,8,11,12],61:[7,8,11,12]}
    }

# reset wrongchan array in June 2010 - only EBC42 in emergency mode
wrongchanEBC42={'LBA':{},
           'LBC':{},
           'EBA':{},
           'EBC':{42:[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48]}
           }


# settings for 2011 (not used now)

# PMTs that bad in Cs but the problem is in Cs. Readout works fine (keep default value)
# LBA50 pmt19 was in the list of bad chan in 2010 and has been put back in Jul-2011
# LBA51 pmt10 is almost dead since Jan-2010 (126 counts) - adding to dead list
# EBC18 pmt16 is almost dead since Apr-2010 (228 counts) - adding to dead list
# LBA62 pmt19 - dead since Jul-2011 - adding to dead list
#
deadchan={
    'LBA':{9:[9],17:[15,25],
           37:[2],50:[19],51:[10]
           },
    'LBC':{55:[3]},
    'EBA':{24:[17],61:[17]},
    'EBC':{18:[16]}
    }

# PMT's that bad in Cs but this is the way they work (keep what was measured by Cs)
# LBA50 pmt19 - bad integrator - declared as unsable only for Feb-Jun 2011 update (to use May-2011 value for it)
# EBA12 pmt33 - good since March 2010 - removed from unstab channel
# EBC05 pmt05 - clear overflow - need to reduce HV
#
# added in Feb 2011:
# LBA14 pmt39, pmt47 - low signal since Oct-2010
# LBA17 pmt07, LBA61 pmt14 - low signal since Feb-2011
# LBC18 pmt14 - low as ususal (since 2008)
# LBC28 pmt34 - low signal since Feb-2011
#
# LBA06 pmt25 - high signal in Feb-2011 (overflow), again OK in Apr-2011 - removed from list
# LBC08 pmt45, LBC51 pmt26 - declared as unstable for Apr-2011 update only (>5% change) - removed from list
# LBC59 pmt36 - new in Apr-2011
# LBC63 pmt40 - new in Apr-2011
# LBC28 pmt05 - new in May-2011 (very small instability) - removed in Aug-2011
# LBC04 pmt21 - new in Jun-2011
#
# EBA25 pmt 16 - bad integrator in Jul-2011 (very unstable ped) and 20% bigger signal
#                do not put it in dead list, it is removed automatically by deviation cut
#
unstabchan={
    'LBA':{14:[39,47],15:[17],17:[7],43:[27],50:[25],59:[37],61:[14]},
    'LBC':{2:[37],3:[43],4:[21],16:[25],18:[14],21:[46],23:[14],28:[34],29:[25],36:[27],59:[36],60:[35],63:[40]},
    'EBA':{7:[11]},
    'EBC':{5:[5],53:[22,43],64:[30]}
    }

# PMT's that had very different value in previous update - should use latest measured value
# reset wrongchan array in Feb 2011 - only LBA24 in emergency mode, LBC12 is good again
# LBA15 changed significantly, put whole module (was needed only in Feb-2011 update)
#
# 'LBA':{6:[25]},'LBC':{8:[45],51:[26]} - new in Apr-2011 (Feb-2011 constant is too big)
#
# in Apr-2011 remove LBA15 from the list
# in May-2011 remove 'LBA':{6:[25]},'LBC':{8:[45],51:[26]} from the list
# in Aug-2011 remove LBA24 from the list - not in emergency mode anymore
#
# LBA22 should be added after 14-Oct-2011 (till the end of 2011)
# if we want to load constants for this module in emergency mode
# 
wrongchan={
    'LBA':{
    #6:[25],
    #15:[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48],
    22:[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48]
    #24:[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48]
    },
    'LBC':{
    #12:[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48],
    #8:[45],51:[26]
    },
    'EBA':{},
    'EBC':{}
    }

# emty lists for tests
#deadchan={
#    'LBA':{},
#    'LBC':{},
#    'EBA':{},
#    'EBC':{}
#    }

#unstabchan={
#    'LBA':{},
#    'LBC':{},
#    'EBA':{},
#    'EBC':{}
#    }


##channel2hole
##negative means not connected !
##
## barrel
##  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12,
## 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,
## 27, 26, 25, 30, 29, 28,-33,-32, 31, 36, 35, 34,
#3 39, 38, 37, 42, 41, 40, 45,-44, 43, 48, 47, 46,
##
## ext.barrel
##  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12,
## 13, 14, 15, 16, 17, 18,-19,-20, 21, 22, 23, 24,
##-27,-26,-25,-31,-32,-28, 33, 29, 30,-36,-35, 34,
## 44, 38, 37, 43, 42, 41,-45,-39,-40,-48,-47,-46,

## pmt to channel conversion
## barrel
##  1 ch00      13 ch12      25 ch26      37 ch38
##  2 ch01      14 ch13      26 ch25      38 ch37
##  3 ch02      15 ch14      27 ch24      39 ch36
##  4 ch03      16 ch15      28 ch29      40 ch41
##  5 ch04      17 ch16      29 ch28      41 ch40
##  6 ch05      18 ch17      30 ch27      42 ch39
##  7 ch06      19 ch18      31 ch32      43 ch44
##  8 ch07      20 ch19     x32 ch31x    x44 ch43x
##  9 ch08      21 ch20     x33 ch30x     45 ch42
## 10 ch09      22 ch21      34 ch35      46 ch47
## 11 ch10      23 ch22      35 ch34      47 ch46
## 12 ch11      24 ch23      36 ch33      48 ch45

## extended barrel
##  1 ch00      13 ch12     x25 ch26      37 ch38
##  2 ch01      14 ch13     x26 ch25      38 ch37
##  3 ch02      15 ch14     x27 ch24     x39 ch43x
##  4 ch03      16 ch15     x28 ch29     x40 ch44x
##  5 ch04      17 ch16      29 ch31      41 ch41
##  6 ch05      18 ch17      30 ch32      42 ch40
##  7 ch06     x19 ch18x    x31 ch27x     43 ch39
##  8 ch07     x20 ch19x    x32 ch28x     44 ch36
##  9 ch08      21 ch20      33 ch30     x45 ch42x
## 10 ch09      22 ch21      34 ch35     x46 ch47x
## 11 ch10      23 ch22     x35 ch34x    x47 ch46x
## 12 ch11      24 ch23     x36 ch33x    x48 ch45x

