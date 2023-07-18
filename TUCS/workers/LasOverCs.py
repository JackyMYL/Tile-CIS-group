# Author: Henric <henric.wilkens@cern.ch>
#
# Sept, 2012
#

from src.GenericWorker import *

class LasOverCs(GenericWorker):
    "A class for Makeing laser/Cs ratio"

    def __init__(self,verbose=False,type='readout'):
        self.verbose = verbose
        self.type = type
        self.summary_cs = ROOT.TH2F('summary_cs', '',2000, 0., 1.5, 2000, 0., 1.5)
        self.summary_cs_LB = ROOT.TH2F('summary_cs_LB', '',2000, 0., 1.5, 2000, 0., 1.5)
        self.summary_cs_EB = ROOT.TH2F('summary_cs_EB', '',2000, 0., 1.5, 2000, 0., 1.5)
        self.summary_cs2 = ROOT.TH2F('summary_cs2', '',2000, 0., 1.5, 2000, 0., 1.5)
        self.hist = ROOT.TH1F('aHistogram','laser over Cesium',100, 0.8, 1.2) 
        self.hist_LB = ROOT.TH1F('aHistogram','laser over Cesium LB',100, 0.8, 1.2)
        self.hist_EB = ROOT.TH1F('aHistogram','laser over Cesium EB',100, 0.8, 1.2)
        self.count_entries = 0
        self.count_filled = 0

        try:
            self.HistFile.cd()
        except:
            self.initHistFile("output/Tucs.HIST.root")
        self.HistFile.cd()
        ROOT.gDirectory.mkdir("Laser")
        ROOT.gDirectory.cd("Laser")

    def ProcessRegion(self, region):
        las = []
        ces = []
        numbers = region.GetNumber()

#        print numbers
#        for event in sorted(region.GetEvents(), key=lambda event: event.run.time):                                         
#            print 'type = ',event.run.runType                                                                            

        self.count_entries = self.count_entries+1

        if len(numbers)!=3: # This is were the cesium is 
#            print ' ==> to be rejected, ',len(numbers), region.GetHash()
            return
#        else:
#            print ' +=> to be kept, ',len(numbers), region.GetHash()
        for event in sorted(region.GetEvents(), key=lambda event: event.run.time):
            if event.run.runType != 'Las':
#                print 'here is cesium'
                if 'calibration' in event.data:
#                    print 'cesium = ',event.data['calibration'],event.run.time
                    if event.data['calibration']==None:
                        ces.append(0)
                    else:
                        ces.append(event.data['calibration'])
#                        print event.data['calibration']



        for childregion in region.GetChildren('readout'): # The laser is below
            for event in sorted(childregion.GetEvents(), key=lambda event: event.run.time):
                if event.run.runType == 'Las':
                    #print 'Las added',event.data['f_laser'],event.run.time
                    las.append(event.data['f_laser'])
        

        [part, module, chan] = region.GetNumber()
#        print '  ---> ', part, module, chan, ' len las+ces ',len(las), len(ces)
        if len(las) == 2 and len(ces) >= 2:
            cesindex = len(ces)-1
            self.count_filled = self.count_filled+1
            print((region.GetNumber(),'Laser = ', las[0], las[1], (1.+las[0]-las[1]), ' Cesium = ', (1.+ces[0]-ces[cesindex])))


            if ((las[0]!=las[1]) and (ces[0]!=ces[cesindex])):
                self.hist.Fill((las[1])/(1.+ces[0]-ces[cesindex]))
                self.summary_cs.Fill((1.+las[1]-las[0]),(1.+ces[0]-ces[cesindex]))
#                self.summary_cs.Fill((las[1]-las[0]),(1.+ces[0]-ces[cesindex]))

                if (abs(las[1]+ces[cesindex]-ces[0])>0.04):
                    print(('<<!>> Laser = ', las[0], las[1], (1.+las[0]-las[1]), ' Cesium = ', (1.+ces[0]-ces[cesindex])))
                if ces[0]!=0:
                    self.summary_cs2.Fill((las[1]/las[0]),(ces[cesindex]/ces[0]))


                if part == 1 or part == 2:
                    self.hist_LB.Fill((las[1])/(1.+ces[0]-ces[cesindex]))
                    self.summary_cs_LB.Fill((1.+las[1]-las[0]),(1.+ces[0]-ces[cesindex]))

                elif part == 3 or part == 4:
                    self.hist_EB.Fill((las[1])/(1.+ces[0]-ces[cesindex]))
                    self.summary_cs_EB.Fill((1.+las[1]-las[0]),(1.+ces[0]-ces[cesindex]))
                

#        else:
#             print '++ length Laser Cesium = ',len(las),' ',len(ces)
#             for ic in range(len(ces)):
#                 print '++ ces = ',ces[ic]

                    
    def ProcessStop(self):
        self.HistFile.cd("Laser")
        self.hist.Write()

        self.c1 = src.MakeCanvas.MakeCanvas()
        self.c1.SetTitle("Laser versus Cesium")


        ROOT.gStyle.SetOptStat(0)
        self.summary_cs.GetXaxis().SetLabelOffset(0.015)
        self.summary_cs.GetXaxis().SetLabelSize(0.04)
        self.summary_cs.GetXaxis().SetTitleOffset(1.1)
        self.summary_cs.GetXaxis().SetTitle("Channel variation from LASER system")
        self.summary_cs.GetYaxis().SetLabelOffset(0.015)
        self.summary_cs.GetYaxis().SetLabelSize(0.04)
        self.summary_cs.GetYaxis().SetTitleOffset(1.2)
        self.summary_cs.GetYaxis().SetTitle("Channel variation from Cesium system")

        self.summary_cs.GetXaxis().SetRangeUser(0.93,1.07);
        self.summary_cs.GetYaxis().SetRangeUser(0.93,1.07);

        self.summary_cs.Draw("col")

        ROOT.gStyle.SetPaperSize(26,20)
        self.c1.Print("laser_versus_cesium.eps")
        self.c1.Print("laser_versus_cesium.png")
        self.c1.Write();

        self.summary_cs.Write()

        self.summary_cs_LB.GetXaxis().SetLabelOffset(0.015)
        self.summary_cs_LB.GetXaxis().SetLabelSize(0.04)
        self.summary_cs_LB.GetXaxis().SetTitleOffset(1.1)
        self.summary_cs_LB.GetXaxis().SetTitle("Channel variation from LASER system")
        self.summary_cs_LB.GetYaxis().SetLabelOffset(0.015)
        self.summary_cs_LB.GetYaxis().SetLabelSize(0.04)
        self.summary_cs_LB.GetYaxis().SetTitleOffset(1.2)
        self.summary_cs_LB.GetYaxis().SetTitle("Channel variation from Cesium system")

        self.summary_cs_LB.GetXaxis().SetRangeUser(0.93,1.07);
        self.summary_cs_LB.GetYaxis().SetRangeUser(0.93,1.07);

        self.summary_cs_LB.Draw("col")

        ROOT.gStyle.SetPaperSize(26,20)
        self.c1.Print("laser_versus_cesium_LB.eps")
        self.c1.Print("laser_versus_cesium_LB.png")
        self.c1.Write();

        self.summary_cs_LB.Write()

        self.summary_cs_EB.GetXaxis().SetLabelOffset(0.015)
        self.summary_cs_EB.GetXaxis().SetLabelSize(0.04)
        self.summary_cs_EB.GetXaxis().SetTitleOffset(1.1)
        self.summary_cs_EB.GetXaxis().SetTitle("Channel variation from LASER system")
        self.summary_cs_EB.GetYaxis().SetLabelOffset(0.015)
        self.summary_cs_EB.GetYaxis().SetLabelSize(0.04)
        self.summary_cs_EB.GetYaxis().SetTitleOffset(1.2)
        self.summary_cs_EB.GetYaxis().SetTitle("Channel variation from Cesium system")

        self.summary_cs_EB.GetXaxis().SetRangeUser(0.93,1.07);
        self.summary_cs_EB.GetYaxis().SetRangeUser(0.93,1.07);

        self.summary_cs_EB.Draw("col")

        ROOT.gStyle.SetPaperSize(26,20)
        self.c1.Print("laser_versus_cesium_EB.eps")
        self.c1.Print("laser_versus_cesium_EB.png")
        self.c1.Write();

        self.summary_cs_EB.Write()
        
        self.summary_cs2.GetXaxis().SetLabelOffset(0.015)
        self.summary_cs2.GetXaxis().SetLabelSize(0.04)
        self.summary_cs2.GetXaxis().SetTitleOffset(1.1)
        self.summary_cs2.GetXaxis().SetTitle("Channel variation from LASER system")
        self.summary_cs2.GetYaxis().SetLabelOffset(0.015)
        self.summary_cs2.GetYaxis().SetLabelSize(0.04)
        self.summary_cs2.GetYaxis().SetTitleOffset(1.2)
        self.summary_cs2.GetYaxis().SetTitle("Channel variation from Cesium system")
        self.summary_cs2.Draw()

        self.hist.Draw()

        self.c1.Print("laser_over_cesium.eps")
        self.c1.Print("laser_over_cesium.png")
        self.c1.Write();        

        self.hist_EB.Draw()

        self.c1.Print("laser_over_cesium_EB.eps")
        self.c1.Print("laser_over_cesium_EB.png")
        self.c1.Write(); 

        self.hist_LB.Draw()

        self.c1.Print("laser_over_cesium_LB.eps")
        self.c1.Print("laser_over_cesium_LB.png")
        self.c1.Write();    

        self.summary_cs2.Write()

        print((' Processed ',self.count_entries,' measurements, ',self.count_filled,' Laser Cesium pairs'))

