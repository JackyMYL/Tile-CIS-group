#!/usr/bin/env python
import pdb

def channelToCelltype(channelname):
    try:
        channelsplit = channelname[0].split('/')
    except IndexError:
        channelsplit = ['']
    if len(channelsplit)>2:
        ros = int(channelsplit[0])
        mod = int(channelsplit[1])
        chan = int(channelsplit[2])
        
        celltype = 'none'
        if ros in [1,2]:
            if chan in [1,4,5,8,9,10,15,18,19,20,23,26,29,32,35,38,36,37,45,46]:
                celltype = 'A'
            elif chan in [2,3,6,7,11,12,16,17,21,22,27,28,33,34,39,40,42,47]:
                celltype = 'BC'
            elif chan in [0,13,14,24,25,41,44]:
                celltype = 'D'
            elif chan in [30,31,33]:
                celltype = '0'
            else:
                celltype = 'none'

        elif ros in [3,4]:
            if chan in [0,1,13,12]:
                celltype = 'E'
            elif chan in [6,7,10,11, 20, 21, 31, 32, 40, 41]:
                celltype = 'A'
            elif chan in [8,9,14,15,22,23,30,35,36,39]:
                celltype = 'BC'
            elif chan in [2,3,16,17,37,38]:
                celltype = 'D'
            elif chan in [18,19,23,24,25,26,27,28,29,33,34,42,43,44,45,46,47]:
                celltype = '0'
            else:
                celltype = 'none'

            if (ros==3 and mod==14) or (ros==4 and mod==17):
                if chan in [0,1,2,3]:
                    celltype = '0'
                elif chan in [18,19]:
                    celltype = 'E'

        else:
            celltype = 'none'
    else:
        celltype = 'none'
    return celltype
            
                
#    def __str__(self):
#        return "{0}/{1}/{2}".format(self.ros,self.mod,self.chan)
#    def __repr__(self):
#        return "{0}/{1}/{2}".format(self.ros,self.mod,self.chan)
        
idtool={}
def hwidToCell(ros,mod,chan):
    if len(idtool)==0:
        for line in open('/afs/cern.ch/user/t/tilecali/w0/sqlfiles/Noise/cell_hash').readlines():
            if len(line.strip())==0: continue
            #print "Parse: '%s'" % line.strip()
            idx = line.split()[3][4:]
            val = (int(line.split()[1]),int(line.split()[5][-1:]))
            #print "Initialize %s = %s" % (idx,str(val))
            idtool[idx] = val
    idx="%i/%i/%i" % (ros,mod,chan)
    if idx in idtool:
        return idtool[idx]
    else:
        return None

def cellToHwid(cell):
    hwid=[]
    for idx in idtool:
        if idtool[idx]==cell:
            hwid.append(idx)
    return hwid

#ros = 1
#mod = 0
#chn = 0
#cell = hwidToCell(ros,mod,chn)
#hwid = cellToHwid(cell)
#print "cell = ", cell
#print "hwid = ", hwid
#new_cell = cellToHwid((1410, 0))
#print "new_cell = ", new_cell
#print "hwid = ", hwid
#print "ros %i mod %02i chan %02i cell %s " %(ros,mod,chn,cell)

dummy = hwidToCell(0,0,0)
#for ros in xrange(1,5):
#    for mod in xrange(64):
#        for chn in xrange(48):
#            cell = hwidToCell(ros,mod,chn)
#            if cell==None: continue
#            hwid = cellToHwid(cell)
#            print "ros %i mod %02i chan %02i cell %s ==> %s" %(ros,mod,chn,cell,str(hwid))
