import getopt,sys
import ROOT

letters = "hd:e:r:R:p:m:ch:n:g"
keywords = ["help","date=","enddate=","region=","Run=","part=","modu=","channel=","num=","gain="]

def usage():
    print('Usage %s [options]' % sys.argv[0])
    for option in keywords:
        if option.find('=')>0:
            print('--%svalue' % option)
        else:
            print('--%s' % option)


try:
    opts, extraparams = getopt.getopt(sys.argv[1:],letters,keywords)
except getopt.GetoptError as err:
    print(str(err))
    usage()
    sys.exit(2)


date     = '2012-01-01'
enddate  = ''
twoinput = False
region   = None
doRun    = False
#default: all regions
part     = 5
modu     = 64
channel  = 48
num      = 1 #for averaging num for macro plotPMTCurrentVsInstLumi
gain     = 0

[LBA, LBC, EBA, EBC] = [1, 2, 3, 4]

for o, a in opts:
    if o in ("-d","--date"):
        date = a
        runs = date
    elif o in ("-e","--enddate"):
        enddate = a
        twoinput = True
    elif o in ("-r","--region"):
        region = a
        print("Using region: ",region)
    elif o in ("-R","--Run"):
        runs = [int(a)]
        doRun = True
        print(runs)
    elif o in ("-h","--help"):
        usage()
        sys.exit(2)
    elif o in ("-p","--part"):
        part = a
        print("using partition: ", part)
    elif o in ("-m","--modu"):
        modu = a
        print("using module: ", modu)
    elif o in ("-ch","--channel"):
        channel = a
        print("using channel: ", channel)
    elif o in ("-n","--num"):
        num = int(a)
        print("averaging over %i consecutive entries" % (num))
    elif o in ("-g","--gain"):
        gain = int(a)
        print("getting information for gain %i " % (gain))    
    else:
        assert False, "unhandeled option"
#hardcoding
if not doRun:
    #information from AtlCoolConsole
    timestamp = [#[101410, ROOT.TDatime('2009-01-28')],
                 #[101413, ROOT.TDatime('2009-01-28')],
                 [115551, '2009-05-18'],
                 [129857, '2009-09-15'],
                 [148890, '2010-02-24'],
                 [149659, '2010-03-04'],
                 [200499, '2012-03-30']
                 ]

    runs = []
    if twoinput:
        #time1 = ROOT.TDatime(date)
        #time2 = ROOT.TDatime(enddate)
        for i in range(len(timestamp)):
            if(timestamp[i][1]>date and timestamp[i][1]<enddate):
                runs.append(timestamp[i][0])
    else:
        print(date)
        #time1 = ROOT.TDatime(date)
        for i in range(len(timestamp)):
            if(timestamp[i][1]>date):
                runs.append(timestamp[i][0])
