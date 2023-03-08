###########################
#
# compute_EBScale.py
#
#Auther = Ammara with the help of Henric
#       Oct 2017
#Computes EB scaling over all given runs
#
#
#
###########################




from src.GenericWorker import *
from src.region import *

class compute_EBScale(GenericWorker):
    "This worker compute EB scaling for all given runs"

    def __init__(self, cells=['A10','A14']):

        self.cells = cells
        self.histo = dict()
    def ProcessStart(self):
        global run_list
        ordered_list = sorted(run_list.getRunsOfType('Las'), key=lambda run: run.runNumber)
        graph_lim = 10.
        for run in ordered_list:
            lbtitle = 'A10 channel variation %d'% run.runNumber
            ebtitle = 'A14 channel variation %d'% run.runNumber
            self.histo[run] = [ROOT.TH1F(lbtitle, '', 100, -graph_lim, graph_lim), ROOT.TH1F(ebtitle, '', 100, -graph_lim, graph_lim)]


    def ProcessRegion(self,region):
        numbers = region.GetNumber(1)
        if len(numbers)!=4:
            return region
        # only for ADCs 
        [part, module, pmt, gain] = numbers
        layer =  region.GetLayerName()
        cell  = region.GetCellName()
      #  print'cell =', cell
        for event in region.GetEvents():
               if event.run.runType!='Las':
                   continue
               if 'deviation' in event.data:
                   if cell.find('A10')!=-1:
                       self.histo[event.run][0].Fill(event.data['deviation'])
                   if cell.find('A14')!=-1:
                       self.histo[event.run][1].Fill(event.data['deviation'])
                   
    def ProcessStop(self):
        for run in list(self.histo.keys()):
            result = [0., 0.]
            for cell in [0,1]:
                hist = self.histo[run][cell]
                fit1 = ROOT.TF1("fit1", "gaus")
                fit1.SetParameter(1,hist.GetMean())
                fit1.SetParameter(2,max(hist.GetRMS(),0.1))
                if hist.GetEntries()>4:
                    hist.Fit(fit1,"L")
                    result[cell]  = fit1.GetParameter(1)
                else:
                    print('not enough entries')
    
            EBScale= result[0]-result[1]
            run.data['EBScale']= EBScale
            print('EBScale= ', EBScale,'run= ', run.runNumber)
