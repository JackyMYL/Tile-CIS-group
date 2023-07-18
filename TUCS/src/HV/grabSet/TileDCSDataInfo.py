#!/bin/env python
# Author: nils.gollub@cern.ch

import re
from src.oscalls import *

class TileDCSDataInfo:
    """
    Keeps a list of drawer, variable <---> folder, channel
    associations and provides information about the available
    variables and their datatypes.
    """

    LVPS_AI     = ("/TILE/DCS/LVPS/", "/AI")
    LVPS_STATES = ("/TILE/DCS/LVPS/", "/STATES") 
    VARS_HV     = ("/HVdummy/", "/HVdummy")
    type_float  = ('f','/F')
    type_int    = ('i','/I')

    vars_LVPS_STATES = {"FORDAQ_MB"      : [ LVPS_STATES, type_int],
                        "FORDAQ_HV"      : [ LVPS_STATES, type_int],
                        "FORDAQ_MBHV"    : [ LVPS_STATES, type_int]}

    vars_LVPS_AI = {"15VMB_OUTPUT_I"      : [ LVPS_AI, type_float],
                    "M5VMB_TEMP2"         : [ LVPS_AI, type_float],
                    "M5VMB_SENSES"        : [ LVPS_AI, type_float],
                    "M5VMB_OUTPUT_V"      : [ LVPS_AI, type_float],
                    "M5VMB_OUTPUT_I"      : [ LVPS_AI, type_float],
                    "M5VMB_INPUT_V"       : [ LVPS_AI, type_float],
                    "15VHV_INPUT_V"       : [ LVPS_AI, type_float],
                    "M15VHV_TEMP3"        : [ LVPS_AI, type_float],
                    "M15VHV_TEMP2"        : [ LVPS_AI, type_float],
                    "15VHV_OUTPUT_I"      : [ LVPS_AI, type_float],
                    "M15VHV_OUTPUT_V"     : [ LVPS_AI, type_float],
                    "M15VHV_OUTPUT_I"     : [ LVPS_AI, type_float],
                    "M15VHV_INPUT_V"      : [ LVPS_AI, type_float],
                    "15VHV_OUTPUT_V"      : [ LVPS_AI, type_float],
                    "EXT_TEMP2"           : [ LVPS_AI, type_float],
                    "15VMB_TEMP3"         : [ LVPS_AI, type_float],
                    "3VDIG_INPUT_V"       : [ LVPS_AI, type_float],
                    "3VDIG_OUTPUT_I"      : [ LVPS_AI, type_float],
                    "3VDIG_OUTPUT_V"      : [ LVPS_AI, type_float],
                    "3VDIG_SENSES"        : [ LVPS_AI, type_float],
                    "15VMB_TEMP2"         : [ LVPS_AI, type_float],
                    "3VDIG_TEMP2"         : [ LVPS_AI, type_float],
                    "3VDIG_TEMP3"         : [ LVPS_AI, type_float],
                    "15VMB_SENSES"        : [ LVPS_AI, type_float],
                    "5VDIG_INPUT_V"       : [ LVPS_AI, type_float],
                    "5VDIG_OUTPUT_I"      : [ LVPS_AI, type_float],
                    "5VDIG_OUTPUT_V"      : [ LVPS_AI, type_float],
                    "5VDIG_SENSES"        : [ LVPS_AI, type_float],
                    "15VMB_OUTPUT_V"      : [ LVPS_AI, type_float],
                    "5VDIG_TEMP2"         : [ LVPS_AI, type_float],
                    "5VDIG_TEMP3"         : [ LVPS_AI, type_float],
                    "M5VMB_TEMP3"         : [ LVPS_AI, type_float],
                    "5VHV_INPUT_V"        : [ LVPS_AI, type_float],
                    "5VHV_OUTPUT_I"       : [ LVPS_AI, type_float],
                    "5VHV_OUTPUT_V"       : [ LVPS_AI, type_float],
                    "15VMB_INPUT_V"       : [ LVPS_AI, type_float],
                    "5VHV_TEMP2"          : [ LVPS_AI, type_float],
                    "5VHV_TEMP3"          : [ LVPS_AI, type_float],
                    "15VHV_TEMP3"         : [ LVPS_AI, type_float],
                    "5VMB_INPUT_V"        : [ LVPS_AI, type_float],
                    "5VMB_OUTPUT_I"       : [ LVPS_AI, type_float],
                    "5VMB_OUTPUT_V"       : [ LVPS_AI, type_float],
                    "5VMB_SENSES"         : [ LVPS_AI, type_float],
                    "15VHV_TEMP2"         : [ LVPS_AI, type_float],
                    "5VMB_TEMP2"          : [ LVPS_AI, type_float],
                    "5VMB_TEMP3"          : [ LVPS_AI, type_float],
                    "EXT_TEMP1"           : [ LVPS_AI, type_float]}

    vars_HV = {}
    for i in range(48):
        i = str(i+1)
        vars_HV["hvOut"+i] = [ VARS_HV, type_float ]
    for i in range(4):
        i = str(i+1)
        vars_HV["hvIn"+i]  = [ VARS_HV, type_float ]
    for i in range(7):
        i = str(i+1)
        vars_HV["volt"+i]  = [ VARS_HV, type_float ]
        vars_HV["temp"+i]  = [ VARS_HV, type_float ]


    systemID = { "LBA" : 88 ,
                 "LBC" : 87 ,
                 "EBA" : 86 ,
                 "EBC" : 89 ,
                 "SCS" : 80 }

    partitionID = { 0 : "EBA",
                    1 : "LBA",
                    2 : "LBC",
                    3 : "EBC"}
    
    def __init__( self, dbstring=None ):

        self.vars = {}
        for var, info in self.vars_LVPS_AI.items():
            self.vars[var] = info 
        for var, info in self.vars_LVPS_STATES.items():
            self.vars[var] = info 
        for var, info in self.vars_HV.items():
            self.vars[var] = info 

        self.folderDrawer_to_channel = {}
        self.folderChannel_to_drawer = {}
        self.folderDrawer_to_oracleId  = {}

        lines = open(os.path.join(getTucsDirectory(),"src/HV/grabSet/cool_channel_id.dat"),"r").readlines()
        for line in lines:
                line = line.strip()
                folder, drawer, channel, oracleId = line.split()

                keyFolderDrawer = ( folder , drawer) 
                if keyFolderDrawer in self.folderDrawer_to_channel:
                    raise "trying to generate key twice: " + keyFolderDrawer
                self.folderDrawer_to_channel[ keyFolderDrawer] = int(channel)
                self.folderDrawer_to_oracleId[keyFolderDrawer] = oracleId

                keyFolderChannel = ( folder , int(channel))
                if keyFolderChannel in self.folderChannel_to_drawer:
                    raise "trying to generate key twice: " + keyFolderChannel
                self.folderChannel_to_drawer[keyFolderChannel] = drawer
                
                

    def get_channel(self, folder, drawer):

        if not self.check_drawer_syntax(drawer):
            raise "ERROR: drawer not valid: " + drawer
        key = (folder, drawer )
        if key not in self.folderDrawer_to_channel:
            print("get_channel WARNING, can not resolve key: ", key)
            return None
        return self.folderDrawer_to_channel[key]

    def get_drawer(self, folder, channel):

        key = (folder, channel)
        if key not in self.folderChannel_to_drawer:
            print("get_drawer WARNING, can not resolve key: ", key)
            return None
        return self.folderChannel_to_drawer[key]


    def get_folder_and_channel(self, variable, drawer):
        """
        For a given DCS variable and drawer, return the complete COOL
        folder name and the channel number associated to the drawer
        """
        if variable not in self.vars:
            raise "Variable not known: " + variable
        partition = drawer[0:3]
        folderDef = self.vars[variable][0]
        folder = folderDef[0]+partition+folderDef[1]
        key = (folder, drawer)
        if key not in self.folderDrawer_to_channel:
            print("WARNING, can not resolve key: ", key)
            return None
        channel = self.folderDrawer_to_channel[key]
        return (folder, channel)

    def get_variable_type(self, variable):
        """
        Returns the type of a variable
        """
        if variable not in self.vars:
            raise "Variable not known: " + variable
        return self.vars[variable][1]

    def get_all_variables(self):
        return list(self.vars.keys())

    def check_drawer_syntax(self, drawer):
        partition = drawer[0:3]
        drawerNum = int(drawer[3:5])
        valid = ("LBA" , "LBC", "EBA", "EBC")
        if partition not in valid:
            return False
        if drawerNum<1 or drawerNum>64:
            return False
        return True
    
    def get_variables_by_folder(self, variables, drawer):
        """
        Return a dictionary listing all folders that need to be
        accessed as keys and all variables associated to the key folder
        as values.
        """
        folderDict = {}
        for var in variables:
            if var not in self.vars:
                print("Unknown variable, IGNORING IT: ", var)
            else:
                folder, channel = self.get_folder_and_channel(var,drawer)
                if folder not in folderDict:
                    folderDict[folder] = [var]
                else:
                    folderDict[folder].extend([var])
        return folderDict

