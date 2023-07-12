#!/usr/bin/env python
# Script to calculate ratio of 2 cesium sources activity
# It needs 'csdb.py' from Tucs/src/cesium
# See comment on line 215
# how to run it:
#./intercalibrator.py -p EBA -m 65 -b 17:51:00 -s 23/03
#./intercalibrator.py -p LBA -m 65 -b 18:48:00 -s 23/03
#./intercalibrator.py -p LBC -m 65 -b 20:30:00 -s 23/03



import MySQLdb,datetime,math,time
import getopt
import ROOT
import os, sys
sys.path.insert(0, os.getenv('TUCS','.'))
from src.oscalls import *

def usage():
    print "valid options:"
    print "  -p partition"
    print "  -m module"
    print "  -b start time hh:mm:ss"
    print "  -e end time hh:mm:ss"
    print "  -s start date dd/mm/yy"
    print "  -d end date dd/mm/yy"
    print "  -c comment. Extract data with specific comment."
    print "  -w write changes to file"
    print "  -T calculate mean and RMS"
    print ""
try:
    (opts,args) = getopt.getopt(sys.argv[1:], "hwb:e:s:d:p:m:T")
except getopt.GetoptError, err:
        # print help information and exit:
        print str(err)
        usage()
        sys.exit(2)
format='%d/%m/%y %H:%M:%S'
today=datetime.datetime.today()
starts=datetime.datetime(1990, 1, 1).strftime(format)
ends=datetime.datetime(2060, 12, 31, 23, 59, 59).strftime(format)
modules=[65]
partitions=['LBA']
comment=""
write=False
setmean=False

#print 'opts ',opts
for pair in opts:
    if '-b' in pair:
        starts=today.strftime(format)
    if '-e' in pair:
        ends=today.strftime(format)

for o,a in opts:
    if o=='-p':
        partitions=[a]
    elif o=='-m':
        modules=[int(a)]
    elif o=='-b':
        starts=starts[:9]+a+starts[9+len(a):]
    elif o=='-e':
        ends=ends[:9]+a+ends[9+len(a):]
    elif o=='-s':
        starts=a+starts[len(a):]
    elif o=='-d':
        ends=a+ends[len(a):]
    elif o=='-w':
        write=True
    elif o=='-c':
        comment=a
    elif o=='-T':
        setmean=True
    elif o=='-h':
        usage()
        exit()

print partitions,modules,'from',starts,'to',ends
#print '2 seconds to start'
#time.sleep(2)
print 'proceeding'
start=datetime.datetime.strptime(starts,format)
end=datetime.datetime.strptime(ends,format)
#print 'in mysql format:'
#print start.strftime("%Y-%m-%d %H:%M:%S")

sys.path.insert(0, getTucsDirectory("src/cesium"))
from chanlists import deadchan,wrongchan,unstabchan
#from csdb import readces,readhv,intnorm,closeall
import csdb
readces=csdb.readces
closeall=csdb.closeall
readhv=csdb.readhv
#from csdb import intpath,rawpath


#reading defaults
import pickle
#f=open(os.path.join(getResultDirectory(),"tbldump_t.pickle"),"r")
try:
    f=open(os.path.join(getResultDirectory(),"csref.pickle"),"r")
    tbl=pickle.load(f)
    f.close()
except IOError,e:
    print e
    print 'creating an empty table'
    tbl={}

Ebad = [3,4,5,6]
def if_ok(dbdict):
    retlist=[]
    par=dbdict['partition']
    mod=dbdict['module']
    print "run",dbdict['run']

    for pmt in xrange(1,49):
        if par in deadchan and mod in deadchan[par] and pmt in deadchan[par][mod]:
            print 'dead channel: ',par,mod,pmt
            continue
        if par in wrongchan and mod in wrongchan[par] and pmt in wrongchan[par][mod]:
            print 'wrong channel, using as is',par,mod,pmt
            retlist.append(pmt)
            continue
        if par in unstabchan and mod in unstabchan[par] and pmt in unstabchan[par][mod]:
            print 'unstable channel, using as is',par,mod,pmt
            retlist.append(pmt)
            continue
        if dbdict['statusPMT'+"%02i"%pmt]=='OK':
            retlist.append(pmt)
            continue
        if 0 and par[0]=='E' and pmt in Ebad and dbdict['statusPMT'+"%02i"%pmt]=='wrong number of peaks':
            print 'suppressing  wrong number of peaks ',par,mod,pmt
            retlist.append(pmt)
            continue
    return retlist

def fillstats(stats,csconsts,dict,dblist,norm=True):
    for pmt in dblist:        
        if csconsts[pmt]>5000 or csconsts[pmt]<0.0:
            dblist.remove(pmt)
            #a dirty hack
            continue
        if not pmt in stats:
            stats[pmt]={}
            stats[pmt]['sum']=0
            stats[pmt]['sum2']=0
            stats[pmt]['N']=0   
        stats[pmt]['N']+=1
        nrm=1.0
        if norm:
            nrm=intnorm(dict['source'],dict['time'])
        #print 'nrm=',nrm
        stats[pmt]['sum']+=csconsts[pmt]/nrm
        stats[pmt]['sum2']+=(csconsts[pmt]/nrm)**2
    return stats



#cycle over modules and partitions:
#extract all data for given period
#check default, mean, sigma
#write to file:
#raw Cs constant, normalized Cs constant, HV, temperature, status, comment
cslist=[]
onesource=True
source=''
stability={}

processingDir='/data/cs'

for par in partitions:
    if not par+'source' in tbl:
        tbl[par+'source']='no source'
    
    for mod in modules:
        stats={}
        #making MySQL query
        db = MySQLdb.connect(host='pcata007',db='tile')
        c = db.cursor(MySQLdb.cursors.DictCursor)
        querystring="time<'%s' AND time>'%s' AND partition='%s' AND module=%i AND comment='%s'"%\
                     (end.strftime("%Y-%m-%d %H:%M:%S"),start.strftime("%Y-%m-%d %H:%M:%S"),par,mod,comment)
        c.execute("""SELECT * FROM runDescr WHERE """+querystring+""" ORDER BY time DESC""")
        print """SELECT * FROM runDescr WHERE """+querystring+""" ORDER BY time DESC"""
        dbdicts = c.fetchall()
        
        for dict in dbdicts:
            #make list of good channels, consider database only
            dblist=if_ok(dict)
            csrun=dict['run']
            if csrun<=196: year=2008
            else: year=2009
            csdb.rawpath=processingDir+'/'+str(year)+'/data'
            csdb.intpath=processingDir+'/'+str(year)+'/int'
            
            csconsts=readces(dict['run'],par,mod)
            if csconsts==None:
                print "Can't read cs constants for run",dict['run'],"par",par,"mod",mod
                continue
            
            hvtemp=readhv(dict['run'],par,mod)
            if hvtemp==None:
                print "Can't read HV and temperature for run",dict['run'],"par",par,"mod",mod
                continue

            #another hack
            #csconsts=[]
            #print hvtemp
            #for HVcTc in hvtemp:
            #    if HVcTc==-1: HVcTc=(0.0,0.0)
            #    HVc,Tc=HVcTc
            #    csconsts.append(HVc)
            
            for pmt in dblist:
                print "pmt %i %f"%(pmt,csconsts[pmt]),
                cslist.append((csconsts,dblist,dict['time']))
            #check if all data releted to one source
            if source=='':
                source=dict['source']
            elif source!=dict['source']:
                onesource=False
            #print csconsts
            print
            #average over all runs for each channel
            # if you want to compare data for different periods
            # you need to use this line instead:
            #fillstats(stats,csconsts,dict,dblist,True)
            fillstats(stats,csconsts,dict,dblist,False)

        #it is important to close all ROOT files before creating a histogram
        closeall()

        #cycle again over all runs and make a "normalized" histogram
        hh=ROOT.TH1F(par+str(mod)+'norm',par+str(mod)+' norm. '+dict['source'],400,0.8,1.2);
        hhraw=ROOT.TH1F(par+str(mod)+'raw',par+str(mod)+' raw. '+dict['source'],600,2000,4000);
        gr=ROOT.TGraphErrors()
        gr.SetMarkerStyle(20)
        grpoint=0
        for (cs,dbl,t) in cslist:
            #one point per run
            stb={}
            for pmt in stats:
                if pmt!=11: continue
                if pmt in dbl:
                    val=cs[pmt]/(stats[pmt]['sum']/stats[pmt]['N'])
                    hh.Fill(val)
                    hhraw.Fill(cs[pmt])
                    #calculation of mean drift from run to run
                    fillstats(stb,[0,val],{},[1],False)
            if 1 in stb and stb[1]['N']>=1:
                val=stb[1]['sum']/stb[1]['N']
                vale=math.sqrt(stb[1]['sum2']/stb[1]['N']-(stb[1]['sum']/stb[1]['N'])**2)
                gr.SetPoint(grpoint,time.mktime(t.timetuple()),val)
                gr.SetPointError(grpoint,0,vale)
                grpoint+=1
                    

        
        print "stats"
        if not onesource:
            print 'Analyzed data was acquired for different sources!!!'
            print 'Values will not be written to the ref. file!'
            write=False
        #print tbl
        #make comparison for mean value of each channel
        cmpstat={}
        
        for pmt in stats:
            if (par,mod,pmt) not in tbl:
                tbl[(par,mod,pmt)]={}
                tbl[(par,mod,pmt)]['csconst']=1.0
                tbl[(par,mod,pmt)]['N']=0
            
            if 'csconst' in tbl[(par,mod,pmt)]:
                print "pmt %2i source %s  %f | %s  mean %f  sigma %f  N %i"%\
                      (pmt,tbl[par+'source'],tbl[(par,mod,pmt)]['csconst'],\
                       dict['source'],stats[pmt]['sum']/stats[pmt]['N'],\
                       math.sqrt(stats[pmt]['sum2']/stats[pmt]['N']-(stats[pmt]['sum']/stats[pmt]['N'])**2),\
                       stats[pmt]['N'])
                if stats[pmt]['N']>3 and tbl[(par,mod,pmt)]['N']>3:
                    fillstats(cmpstat,[0,stats[pmt]['sum']/stats[pmt]['N']/tbl[(par,mod,pmt)]['csconst']],{},[1],False)
                #write constants to file to compare with others 
                if setmean:
                    tbl[(par,mod,pmt)]['csconst']=stats[pmt]['sum']/stats[pmt]['N']
                    tbl[(par,mod,pmt)]['sigma']=math.sqrt(stats[pmt]['sum2']/stats[pmt]['N']-\
                                                          (stats[pmt]['sum']/stats[pmt]['N'])**2)
                    tbl[(par,mod,pmt)]['N']=stats[pmt]['N']
        #now print differense
        print
        #print cmpstat
        if 1 in cmpstat:
            print 'comparison of data: ',dict['source'],'/',tbl[par+'source']
            print 'mean %f  sigma %f  N %i'%(cmpstat[1]['sum']/cmpstat[1]['N'],math.sqrt(cmpstat[1]['sum2']/cmpstat[1]['N']-(cmpstat[1]['sum']/cmpstat[1]['N'])**2),cmpstat[1]['N'])
        tbl[par+'source']=dict['source']
        

fff1=ROOT.TFile('nhist.root','UPDATE')
hh.SetDirectory(fff1.GetDirectory('.'))
hhraw.SetDirectory(fff1.GetDirectory('.'))

c1=ROOT.TCanvas()
#hh.Draw()
#c1.Print('hh'+par+'.png')
#hhraw.Draw()
#c1.Print('hhraw'+par+'.png')

gr.SetTitle('stability for '+par+str(mod))
gr.Draw('AP')
gr.GetXaxis().SetTimeDisplay(1)
gr.GetXaxis().SetTimeOffset(0,'gmt')
gr.GetXaxis().SetTimeFormat('%d%b%y')
gr.GetYaxis().SetRangeUser(0.99,1.01)
#gr.GetYaxis().SetRangeUser(0.9997,1.0003)
#plotting decay exponent
tref = datetime.datetime(2009,1,1)
tbeg = datetime.datetime(2008,9,15)
tend = datetime.datetime(2009,7,1)
decf=ROOT.TF1("decay","expo(0)",time.mktime(tbeg.timetuple()),time.mktime(tend.timetuple()))
decf.SetParameter(0, 0.693147/952387200*time.mktime(tref.timetuple()))
decf.SetParameter(1,-0.693147/952387200)#Cs137 half-life in seconds
#gr.Fit(decf)
decf.Draw("SAME")

c1.Print('stab'+par+str(mod)+'.png')


hh.Write()
hhraw.Write()
fff1.Write()
fff1.Close()
if write:
    f=open(os.path.join(getResultDirectory(),"csref.pickle"),"w")
    pickle.dump(tbl,f)
    f.close()
