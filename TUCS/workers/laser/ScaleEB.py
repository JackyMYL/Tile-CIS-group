############################################################
#
# scaleEB.py
#
############################################################
#
#
#############################################################


from src.GenericWorker import *
from src.region import *


class scaleEB(GenericWorker):
    " This worker scale EB constants "    

        
    def __init__(self):

        pass
#        try:
 #           print "Using a correction factor = ",EBScale,"%"
  #      except Exception,e:
   #         print "No correction factor defined."

    def ProcessRegion(self, region):
       
        pmt_region = region.GetHash()
    
        for event in region.GetEvents():
            if 'deviation' in event.data:
                
                #pmt_region = str(event.region)
                scale = 0.0
                if pmt_region.find("EB")==-1:
                    return
                try:
                    scale=event.run.data["EBScale"]
                    # scale = EBScale
                except Exception as e:
                    scale=0.0
                #print('scale= ', scale,'run= ', event.run.runNumber)
                
                #print(event.data['deviation'], event.data['deviation']+scale)
                event.data['deviation'] = event.data['deviation']+scale
                if event.data['deviation'] > -100:  
                    event.data['f_laser'] = 1.0/(1.0+(event.data['deviation']/100.0))
