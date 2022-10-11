# Katie Hughes Oct. 2021

removeBad = 'RemoveBadCIS.txt'
addBad = 'AddBadCIS.txt'
noCIS = None

def ChannelIDs(line):
    line = line.strip('\n')
    lst = line.split('_')
    partition = lst[0]
    module = lst[1]
    module = module.strip('m')
    channel = lst[2]
    channel = channel.strip('c')
    channel = int(channel)
    gain = lst[3].strip()
    if gain == "highgain":
        gain = 1
    elif gain == "lowgain":
        gain = 0
    else:
        gain = -1 # error
        print("ERROR!!!")
    return partition+module, channel, gain

comment = ''

if removeBad is not None:
    comment+="REMOVING BADCIS FOR: "
    with open(removeBad) as f:
        for l in f.readlines():
            try:
                p, c, g = ChannelIDs(l)
                #mgr.delADCProblem(p, c, g, TileBchPrbs.NoCis)
                #mgr.delADCProblem(p, c, g, TileBchPrbs.BadCis)
                print("%s %d %d" % (p,c,g))
                comment+=("%s %d %d, " % (p, c, g))
            except:
                pass

if addBad is not None:
    comment+="ADDING BADCIS FOR: "
    with open(addBad) as f:
        for l in f.readlines():
            try:
                p, c, g = ChannelIDs(l)
                #mgr.addADCProblem(p, c, g, TileBchPrbs.BadCis)
                print("%s %d %d" % (p,c,g))
                comment+=("%s %d %d, " % (p, c, g))
            except:
                pass

if noCIS is not None:
    comment+="SETTING NOCIS FOR: "
    with open(noCIS) as f:
        for l in f.readlines():
            try:
                p, c, g = ChannelIDs(l)
                #mgr.addADCProblem(p, c, g, TileBchPrbs.NoCis)
                print("%s %d %d" % (p,c,g))
                comment+=("%s %d %d, " % (p, c, g))
            except:
                pass
