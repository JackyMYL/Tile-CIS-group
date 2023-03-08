#
# Read calibration constants from COOL db for Integrator, do distributions
#
##############################
from src.ReadGenericCalibration import *
from src.region import *
from src.oscalls import *

# For reading from DB
from TileCalibBlobPython import TileCalibTools
from TileCalibBlobObjs.Classes import *

# For turning off annoying logging
import logging
from TileCalibBlobPython.TileCalibLogger import TileCalibLogger, getLogger

#file = open("RCFCdebug.txt","wb")

#worker is called by /macros/mbias/readCoolConstants.py
class ReadCool(ReadGenericCalibration):
    "Read database calibration constants from COOL"
    #inherited from ReadCalFromCool.py
    
    def __init__(self, runType='MBias', schema='sqlite://;schema=tileSqlite.db;dbname=CONDBR2', folder='/TILE/OFL02/INTEGRATOR', partition=5, module=64, pmt=48, Gain=0, runNumber=1000000000, verbose=False):
        self.runType   = runType
        self.schema    = schema
        self.folder    = folder
        self.partition = int(partition)
        self.module    = int(module)
        self.pmt       = int(pmt)
        self.gain      = int(Gain)
        self.runNumber = runNumber
        self.verbose   = verbose

        if "sqlite" in schema:
            splitname=schema.split("=")
            if not "/" in splitname[1]: 
                splitname[1]=os.path.join(getResultDirectory(),splitname[1])
                self.schema="=".join(splitname)

        if self.verbose:
            getLogger("ReadCool").setLevel(logging.DEBUG)
            getLogger("TileCalibTools").setLevel(logging.DEBUG)
        else:
            getLogger("ReadCool").setLevel(logging.ERROR)
            getLogger("TileCalibTools").setLevel(logging.ERROR)
        #self.GainsPlot = None #will be a histo    
        self.dir = getPlotDirectory() #where to save the plots

        self.dir      =  os.path.join(src.oscalls.getPlotDirectory(),'mbias2012','CoolConstants')
        src.oscalls.createDir(self.dir)


    def ProcessStart(self):
	    
        try:
            self.dbConstants = TileCalibTools.openDbConn(self.schema, 'READONLY')
        except Exception as e:
            print("ReadCOOL: Failed to open a database connection %s, this can be an AFS token issue" % self.schema)
            print(e)
            sys.exit(-1)
	    
        print("Creating Blob reader for\n folder: %s\n" % (self.folder))
	
	# no tag anymore, since database change (that was before 2014/08/07)
	
        self.blobReader = TileCalibTools.TileBlobReader(self.dbConstants, self.folder)
	
    def ProcessRegion(self, region): #region is irrelevant here, but for sake of time consumption the macro will specify a region	
        pass		
	    
    def ProcessStop(self):
	#and here some plotting...
        Gains = []
        Pedestal = []
        RMS = []
        # this depends on what was specified by the user:
        looprange = []
        name = ''
	
        # if specific pmt: simply print out information 
        if self.partition!=5 and self.module!=64 and self.pmt!=48:
            Drawer = self.blobReader.getDrawer(self.partition, self.module, (self.runNumber,0))
            for gain in range(6):
                print("Gain: ", gain+1)
                print("gain=%f+/-%f "  % (Drawer.getData(self.pmt,gain,0), Drawer.getData(self.pmt,gain,1)))
                print("ped=%f+/-%f "  % (Drawer.getData(self.pmt,gain,3), Drawer.getData(self.pmt,gain,5)))
                print("rms=%f+/-%f "  % (Drawer.getData(self.pmt,gain,6), Drawer.getData(self.pmt,gain,7)))
	    #looprange = [] # don't loop over detector parts	
            return

        # all partitions
        if self.partition==5 and self.module==64 and self.pmt==48:
            looprange = [1,2,3,4] # all partitions
            name = 'all'
	# specified partition
        elif self.partition!=5 and self.module==64 and self.pmt==48:
            looprange.append(self.partition)
            name = 'part_%i' % (self.partition)
	
        #loop over detector parts
        for part in looprange:
            for mod in range(64):
                #get drawer
                Drawer = self.blobReader.getDrawer(part, mod, (self.runNumber,0))
		
                if not Drawer: continue
		   	 	
                for pmt in range(48):
                    gains = []
                    pedestal = []
                    rms = []
                    #for gain in range(6):
                    if(Drawer.getData(pmt,self.gain,3)==-1.):
                        gains.append(0.0)
                        pedestal.append(0.0)
                        rms.append(0.0)
                    else:    	    
                        gains.append(Drawer.getData(pmt,self.gain,0))
                        pedestal.append(Drawer.getData(pmt,self.gain,3))
                        rms.append(Drawer.getData(pmt,self.gain,6))
                            #print "ros/mod/pmt/gain = %i/%2i/%2i/%i : " % (part,mod,pmt,gain)
			    #print "gain=%f+/-%f "  % (Drawer.getData(pmt,gain,0), Drawer.getData(pmt,gain,1))
                            #print "ped=%f+/-%f "  % (Drawer.getData(pmt,gain,3), Drawer.getData(pmt,gain,5))
                            #print "rms=%f+/-%f "  % (Drawer.getData(pmt,gain,6), Drawer.getData(pmt,gain,7))
                    Gains.append(gains)
                    Pedestal.append(pedestal)
                    RMS.append(rms)
		    	
        if self.dbConstants:
            self.dbConstants.closeDatabase()
		    
        #max2 = [0., 0., 0., 0., 0., 0.]
        #min2 = [1000., 1000., 1000., 1000., 1000., 1000.]
	
        #maxped = [0., 0., 0., 0., 0., 0.]
        #minped = [1000., 1000., 1000., 1000., 1000., 1000.]
        #maxrms = [0., 0., 0., 0., 0., 0.]
        #minrms = [1000., 1000., 1000., 1000., 1000., 1000.]
	
        max2 = [0. for x in range(len(gains))]
        min2 = [1000. for x in range(len(gains))]
	
        maxped = [0. for x in range(len(gains))]
        minped = [1000. for x in range(len(gains))]
        maxrms = [0. for x in range(len(gains))]
        minrms = [1000. for x in range(len(gains))]
	
	
        for i in range(len(Gains)):
            for j in range(len(Gains[0])):
                if Gains[i][j]==0.0: continue
                if Gains[i][j]>max2[j]:
                    max2[j] = Gains[i][j]
                if Gains[i][j]<min2[j]:
                    min2[j] = Gains[i][j]
                if Pedestal[i][j]>maxped[j]:
                    maxped[j] = Pedestal[i][j]
                if Pedestal[i][j]<minped[j]:
                    minped[j] = Pedestal[i][j]
                if RMS[i][j]>maxrms[j]:
                    maxrms[j] = RMS[i][j]
                if RMS[i][j]<minrms[j]:
                    minrms[j] = RMS[i][j]

        for plots in range(len(min2)):	
		
            GainsPlot1 = ROOT.TH1F("GainsPlot1", "", 200, min2[plots]-0.2, max2[plots]+0.2)
            PedestalPlot1 = ROOT.TH1F("PedestalPlot1", "", 80, minped[plots]-0.2, maxped[plots]+0.2)
            RMSPlot = ROOT.TH1F("RMSPlot", "", 80, 0., 3.)
            for i in range(len(Gains)):
                if Gains[i][plots]==0.0: continue    
                GainsPlot1.Fill(Gains[i][plots])
                PedestalPlot1.Fill(Pedestal[i][plots])
                RMSPlot.Fill(RMS[i][plots])
	    	
            #new ranges for plotting
            newmax = GainsPlot1.GetMean()+5*GainsPlot1.GetRMS()
            newmin = GainsPlot1.GetMean()-5*GainsPlot1.GetRMS()

            GainsPlot = ROOT.TH1F("GainsPlot", "", 200, newmin, newmax)

            newmax = PedestalPlot1.GetMean()+5*PedestalPlot1.GetRMS()
            newmin = PedestalPlot1.GetMean()-5*PedestalPlot1.GetRMS()

            PedestalPlot = ROOT.TH1F("PedestalPlot","", 80, newmin, newmax)
            
            for i in range(len(Gains)):
                if Gains[i][plots]==0.0: continue    
                GainsPlot.Fill(Gains[i][plots])
                PedestalPlot.Fill(Pedestal[i][plots])

            # gains plot #################################	
            cfit = ROOT.TCanvas('cfit','',700, 500)
		
            GainsPlot.Draw()
            GainsPlot.GetXaxis().SetTitle("Integrator gain [M#Omega]")	
            GainsPlot.GetYaxis().SetTitle("Entries")
            l1 = TLatex()
            l1.SetNDC()
            l1.SetTextSize(0.04)
            l1.DrawLatex(0.26,0.8,"Entries %i" % (GainsPlot.GetEntries()))
            l1.DrawLatex(0.26,0.75,"Mean %0.2f+/-%0.2f" % (GainsPlot.GetMean(), GainsPlot.GetMeanError()))
            l1.DrawLatex(0.26,0.7,"RMS %0.2f+/-%0.2f" % (GainsPlot.GetRMS(), GainsPlot.GetRMSError()))
	   
            self.plot_name = "Gain%i_%i_%s" % (self.gain, self.runNumber, name)
            cfit.Modified()
            cfit.Update()
            cfit.Print("%s/%s.eps" % (self.dir, self.plot_name))
            cfit.Print("%s/%s.png" % (self.dir, self.plot_name))
            cfit.Print("%s/%s.root" % (self.dir, self.plot_name))
		   
            del cfit, GainsPlot
            ##############################################
	    # pedestal plot
            c2 = ROOT.TCanvas('c2','',700, 500)
		
            PedestalPlot.Draw()
            PedestalPlot.GetXaxis().SetTitle("Pedestal [ADC counts]")	
            PedestalPlot.GetYaxis().SetTitle("Entries")
            l1.DrawLatex(0.7,0.8,"Entries %i" % (PedestalPlot.GetEntries()))
            l1.DrawLatex(0.7,0.75,"Mean %0.2f+/-%0.2f" % (PedestalPlot.GetMean(), PedestalPlot.GetMeanError()))
            l1.DrawLatex(0.7,0.7,"RMS %0.2f+/-%0.2f" % (PedestalPlot.GetRMS(), PedestalPlot.GetRMSError()))
    
            plot_name = "Pedestal%i_%i_%s" % (self.gain, self.runNumber, name)
            c2.Modified()
            c2.Update()
            c2.Print("%s/%s.eps" % (self.dir, plot_name))
            c2.Print("%s/%s.png" % (self.dir, plot_name))
            c2.Print("%s/%s.root" % (self.dir, plot_name))
		   
            del c2, PedestalPlot
	    ##############################################
	    # rms plot
            c3 = ROOT.TCanvas('c3','',700, 500)
		
            RMSPlot.Draw()
            RMSPlot.GetXaxis().SetTitle("RMS [ADC counts]")	
            RMSPlot.GetYaxis().SetTitle("Entries")
            l1.DrawLatex(0.7,0.8,"Entries %i" % (RMSPlot.GetEntries()))
            l1.DrawLatex(0.7,0.75,"Mean %0.2f+/-%0.2f" % (RMSPlot.GetMean(), RMSPlot.GetMeanError()))
            l1.DrawLatex(0.7,0.7,"RMS %0.2f+/-%0.2f" % (RMSPlot.GetRMS(), RMSPlot.GetRMSError()))
	   
            plot_name = "RMS%i_%i_%s" % (self.gain, self.runNumber, name)
            c3.Modified()
            c3.Update()
            c3.Print("%s/%s.eps" % (self.dir, plot_name))
            c3.Print("%s/%s.png" % (self.dir, plot_name))
            c3.Print("%s/%s.root" % (self.dir, plot_name))
		   
            del c3, RMSPlot, l1, plot_name
	    ##############################################
	    
        del Gains, Pedestal, RMS, min2, max2, minped, maxped, minrms, maxrms
        
	    
