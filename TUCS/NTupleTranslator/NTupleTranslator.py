
#!usr/bin/env python

####################################################################################################
# Translator for CIS ntuples to common format:
#   March 2012 , Sam Meehan , samuel.meehan@cern.ch
#
# This is a translator intended to be used to be able to translate the following calibration systems
# from their own calibration outputs into a common format that contains only the necessary information
# for cross comparison:
#
#   1) CIS
#   2) Laser
#   3) Cesium
#   4) MinBias
#   
# Each system has its own section below in which all functions necessary for the translation of 
# that system are to be written and used by that translator.  In addition, their are some common 
# functionalities for all systems.  The output of each translator is an ntuple with branches as 
# below:
#
# -  runtype : Specifies the system that the ntuple is devired from
# -  runnumber : RunNumber corresponding to calibration data taking
# -  quality[5][64][48][2] : This is a bitmask that contains information pertaining to system specific 
#    problems with a given calibration for a channel.  Each system needs to maintain the definition
#    of the bits in this mask in the section describing their translator below
# -  calibration[5][64][48][2] : The relative calibration constant, including any calibrations and
#    corrections that need to be made for a given system.
# -  highvoltage     : value of high voltage during calibration run
# -  highvoltage_set : value to which high voltage was intended to be set during calibration run
#
#
####################################################################################################

import ROOT
from ROOT import TFile, TTree
import numpy as np
import os.path
import argparse

#  SETUP ARGUMENT PARSER FOR COMMAND LINE USAGE
parser = argparse.ArgumentParser(description='Translator used to convert the TileCal \
								calibration system unique ntuples to the common format \
								used by TUCS')
parser.add_argument('--CalibrationSystem', action='store', nargs=1, type=str, default='CIS',
                    required=True, help='Type of calibration system you wish to translate \
                    EXAMPLE: CIS')
parser.add_argument('--InputFile', action='store', nargs=1, type=str, default='/afs/cern.ch/user/t/tilecali/w0/ntuples/cis/tileCalibCIS_188431_CIS.0.root',
                    required=True, help='Path to input file you wish to translate EXAMPLE:\
                    /afs/cern.ch/user/t/tilecali/w0/ntuples/cis/tileCalibCIS_188431_CIS.0.root')
parser.add_argument('--InputTree', action='store', nargs=1, type=str, default='h3000',
                    required=True, help='Name of tree within InputFile that contains the \
                    relevant information to translate into the common format EXAMPLE:h3000')
parser.add_argument('--OutputFile', action='store', nargs=1, type=str, default='testoutputfile.root',
                    required=True, help='Path to output file file you wish to translate noting\
                    that the path will automatically be prefixed with the system being calibrated \
                    EXAMPLE:testoutputfile.root ==> CIS_testoutputfile.root')
parser.add_argument('--OutputTree', action='store', nargs=1, type=str, default='CalibTree',
                    required=True, help='Name of tree within OutputFile that stores common \
                    formatted NTuple EXAMPLE:CalibTree')
parser.add_argument('--debug', action='store_true', default=False,
                    help='Use this tag if you want to print debugging statements during running')
                    
args=parser.parse_args()

calibsystem = args.CalibrationSystem[0]

infilename  = args.InputFile[0]
intreename  = args.InputTree[0]

outfilename = str(calibsystem)+'_'+str(args.OutputFile[0])
outtreename = args.OutputTree[0]

debugargument = 0
if args.debug:
    debugargument = 1

##########################################################################################
#    DEFINE TRANSLATOR CLASS 
#
#    Common functions to be used by all parts of the translator  
##########################################################################################

class Translator:
    def __init__(self):
        self.Debug = 0
        self.Type           = ''
        self.InputFileName  = ''
        self.InputTreeName  = ''
        self.OutputFileName = ''
        self.OutputTreeName = ''
        
    def DefineTranslator(self, DebugArg, RunType, FileInName, TreeInName, FileOutName, TreeOutName):
        self.Debug          = DebugArg
        self.Type           = RunType
        self.InputFileName  = FileInName
        self.InputTreeName  = TreeInName
        self.OutputFileName = FileOutName
        self.OutputTreeName = TreeOutName
        
        self.outFile = ROOT.TFile.Open(str(self.OutputFileName),"RECREATE")
        self.outTree = ROOT.TTree(str(self.OutputTreeName),"calibration tree")
        
        self.runtype        = np.zeros((0))
        self.runnumber      = np.zeros((0))
        self.highvoltage    = np.zeros((0))
        self.highvoltage_set = np.zeros((0))
        self.quality        = np.zeros((5,64,48,2))
        self.calibration    = np.zeros((5,64,48,2))
    
        self.outTree.Branch("runtype",        self.runtype ,       'runtype/F')
        self.outTree.Branch("runnumber",      self.runnumber,      'runnumber/F');
        self.outTree.Branch("highvoltage",    self.highvoltage,    'highvoltage/F');
        self.outTree.Branch("highvoltage_set",self.highvoltage_set,'highvoltage_set/F');
        self.outTree.Branch("quality",        self.quality,        'quality[5][64][48][2]/I' );
        self.outTree.Branch("calibration",    self.calibration,    'calibration[5][64][48][2]/F' );

    def Print(self):
    	print '\n=============================='
    	print 'Translator Attributes:'
    	print 'RunType : ',self.Type
    	print 'InFile  : ',self.InputFileName
    	print 'InTree  : ',self.InputTreeName
    	print 'OutFile : ',self.OutputFileName
    	print 'OutTree : ',self.OutputTreeName
    	print '==============================\n\n'
    	
    def WriteCommonFormat(self):
        if self.Debug==1 : 
            print ' >>>>>> MOVING INTO FILE >>>>>>'
            self.outTree.Print()
        self.outFile.cd()    

        if self.Debug==1 : 
            print ' >>>>>> WRITEING TREE TO FILE>>>>>>'
        self.outTree.Write()

        if self.Debug==1 : 
            print ' >>>>>> CLOSING FILE >>>>>>'
        self.outFile.Close() 	

        if self.Debug==1 : 
            print ' >>>>>> EXITING >>>>>>'
            
            
    def GetHighVoltage(self):
        return 457
        
    def GetHighVoltageSet(self):
        return 537
        
##########################################################################################
# CIS Specific Functions and Translator
#
##########################################################################################
    
    def GetIndex_CIS(self, ros, mod, chan, gain):
        return ros  *64*48*2\
            + mod      *48*2\
            + chan        *2\
            + gain
            
        
    def CIS_Translate(self):
        if self.Debug==1 : 
            print ' >>>>>> TRANSLATING NTUPLE >>>>>>'
            self.Print()
        
        
        if self.Debug:
            print '>>>>>>> TRANSLATING CESIUM <<<<<<<<'
            
        inFile = ROOT.TFile.Open(self.InputFileName,'read')
        inTree = inFile.Get(self.InputTreeName)
        if self.Debug:
            inTree.Print()
            
        NENTRIES = inTree.GetEntriesFast()
        for ii in range(NENTRIES):
            if self.Debug==1 : print ' >>>>>> PROCESSING >>>>>>'
            inTree.GetEntry(ii)	
                
            self.runtype         = 1
            self.runnumber       = inTree.RunNumber
            self.highvoltage     = self.GetHighVoltage()
            self.highvoltage_set = self.GetHighVoltageSet()
                
            qflag_reshape = np.reshape( inTree.qflag , (5,64,48,2) )
            calib_reshape = np.reshape( inTree.calib , (5,64,48,2) )
    
            if self.Debug:
                print len(qflag_reshape)
                print len(qflag_reshape[0])
                print len(qflag_reshape[0][0])
                print len(qflag_reshape[0][0][0])
    
            for jj in range(5):
                for kk in range(64):
                    for ll in range(48):
                        for mm in range(2):
                            if abs(inTree.calib[self.GetIndex_CIS(jj,kk,ll,mm)]-calib_reshape[jj][kk][ll][mm]) > 0.01:
                                print '>>>>> Problem with reshaping of input flat region array <<<<<'	
                                
                            ErrorMask   = int(qflag_reshape[jj][kk][ll][mm])
                            Calibration = calib_reshape[jj][kk][ll][mm]
                                
                            self.quality[jj][kk][ll][mm]     = ErrorMask
                            self.calibration[jj][kk][ll][mm] = Calibration
                                
            self.outTree.Fill()
                
                
                
############################################################################################
# Laser Specific Functions and Translator
#
##########################################################################################
    
    def GetLaserGlobalShift(self, ros, mod, chan, gain):
    	return 666;
    
    def GetLaserFibreShift(self, ros, mod, chan, gain):
    	return 187;
    	
    def GetLaserErrorMask(self, ros, mod, chan, gain):
    	return 16;
    	
    def Laser_Translate(self):
        if self.Debug==1 : 
            print ' >>>>>> TRANSLATING NTUPLE >>>>>>'
            self.Print()
            
        if self.Debug==1:
            print '>>>>>>> TRANSLATING LASER <<<<<<<<'
            
        self.runtype         = 2
        self.runnumber       = 1
        self.highvoltage     = self.GetHighVoltage()
        self.highvoltage_set = self.GetHighVoltageSet()
            
        for jj in range(5):
            for kk in range(64):
                for ll in range(48):
                    for mm in range(2):                            	
                            	
                        GlobalShift = self.GetLaserGlobalShift(jj,kk,ll,mm)
                        FibreShift  = self.GetLaserFibreShift(jj,kk,ll,mm)
                        ErrorMask   = self.GetLaserErrorMask(jj,kk,ll,mm)
                            	
                        self.quality[jj][kk][ll][mm]     = ErrorMask
                        self.calibration[jj][kk][ll][mm] = GlobalShift * FibreShift
                                
        self.outTree.Fill()   
        
#############################################################################################
# Cesium Specific Functions and Translator
#
##########################################################################################

    def GetCesiumCalibration(self, ros, mod, chan, gain):
    	return 187;
    	
    def GetCesiumErrorMask(self, ros, mod, chan, gain):
    	return 16;
    	
    def Cesium_Translate(self):
        if self.Debug==1 : 
            print ' >>>>>> TRANSLATING NTUPLE >>>>>>'
            self.Print()
            
        if self.Debug==1:
            print '>>>>>>> TRANSLATING CESIUM <<<<<<<<'
            
        self.runtype         = 3
        self.runnumber       = 1
        self.highvoltage     = self.GetHighVoltage()
        self.highvoltage_set = self.GetHighVoltageSet()
                
        for jj in range(5):
            for kk in range(64):
                for ll in range(48):
                    for mm in range(2):                            	
                            	
                        Calibration = self.GetCesiumCalibration(jj,kk,ll,mm)
                        ErrorMask   = self.GetCesiumErrorMask(jj,kk,ll,mm)
                            	
                        self.quality[jj][kk][ll][mm]     = ErrorMask
                        self.calibration[jj][kk][ll][mm] = Calibration
                                
        self.outTree.Fill()
        
        
##############################################################################################	
# MinBias Specific Functions and Translator
#
##########################################################################################
    
    def GetMinBiasCalibration(self, ros, mod, chan, gain):
    	return 187;
    	
    def GetMinBiasErrorMask(self, ros, mod, chan, gain):
    	return 16;
    	
    def MinBias_Translate(self):
        if self.Debug==1 : 
            print ' >>>>>> TRANSLATING NTUPLE >>>>>>'
            self.Print()
            
        if self.Debug==1:
            print '>>>>>>> TRANSLATING MINBIAS <<<<<<<<'
            
        self.runtype         = 4
        self.runnumber       = 1
        self.highvoltage     = self.GetHighVoltage()
        self.highvoltage_set = self.GetHighVoltageSet()
                               
        for jj in range(5):
            for kk in range(64):
                for ll in range(48):
                    for mm in range(2):                            	
                            	
                        Calibration = self.GetMinBiasCalibration(jj,kk,ll,mm)
                        ErrorMask   = self.GetMinBiasErrorMask(jj,kk,ll,mm)
                            	
                        self.quality[jj][kk][ll][mm]     = ErrorMask
                        self.calibration[jj][kk][ll][mm] = Calibration
                                
        self.outTree.Fill() 
            
            



####################################################################################
# Execution of translator 
#
##########################################################################################

t = Translator()

t.DefineTranslator( debugargument, calibsystem, infilename, intreename, outfilename, outtreename)

if calibsystem == 'CIS':
    t.CIS_Translate()
    
if calibsystem == 'CS':
    t.Cesium_Translate()
    
if calibsystem == 'LASER':
    t.Laser_Translate()
    
if calibsystem == 'MINBIAS':
    t.MinBias_Translate()


t.WriteCommonFormat()


