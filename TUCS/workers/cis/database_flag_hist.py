
#!/usr/bin/env python
# Author : Vikram Upadhyay
# Date   : December 08, 2014

#################################################################################
#"This script takes an input of a date range from the user, and plots 
#the number of BAD channels, # channels with different calibration flags changing in that 
#period. The user can look at each calibration flag history individually as well.
#Something nice to put on Tile-in-ONE"
#################################################################################

from src.GenericWorker import *
from src.oscalls import *

import ROOT

import argparse
from subprocess import call
from collections import Counter
from string import punctuation
import numpy as np
import matplotlib as mp
mp.use('Agg')
import matplotlib.pyplot as plt
import datetime as DT
from matplotlib.dates import date2num


class database_flag_hist(GenericWorker):
    
    def __init__(self, calflags='All', savePlot=False):
        print("Init: database_flag_hist() worker has been constructed and is waiting to go!")
        self.calflags = calflags
        self.savePlot = savePlot

        self.dir = getPlotDirectory()
        self.dir = '%s/cis' % self.dir
        createDir(self.dir)
        self.dir = '%s/Public_Plots' % self.dir
        createDir(self.dir)
        self.dir = '%s/COOL_History' % self.dir
        createDir(self.dir)
        print("self.dir=%s"%self.dir)
        self.result = getResultDirectory()
        print("self.result=%s"%self.result)
        
    def ProcessStart(self):
        print("Start: database_flag_hist() worker is about to be sent data")
        print(Use_run_list)
        print("self.dir=%s"%self.dir)
    
    def ProcessRegion(self, region):
        pass
    
    def ProcessStop(self):
        print("Stop: database_flag_hist() worker has finished being sent data, and is going to do it's analysis")
        BAD=[]
        NoCIS=[]
        BadCIS=[]
        NoLas=[]
        BadLas=[]
        NoCs=[]
        BadCs=[]

        for i in Use_run_list:
            call(['ReadBchFromCool.py --tag=UPD4 --run=%d'%i], stdout = open( '%s/Conditions_Database.txt'%self.result, 'w'), shell=True)
            file = open('%s/Conditions_Database.txt'%self.result, 'r')
            word_freq = Counter([word.strip(punctuation) for line in file for word in line.split()])
            BAD.append(word_freq['BAD'])
            BadCIS.append(word_freq['1104'])
            NoCIS.append(word_freq['1103'])
            BadLas.append(word_freq['2101'])
            NoLas.append(word_freq['2100'])
            BadCs.append(word_freq['2103'])
            NoCs.append(word_freq['2102'])
            print("CHECKING RUN NUMBER %s FINISHED" % i)
            print("# of masked channels", BAD)
            print("# of channels flagged BadCIS", BadCIS)
            print("# of channels flagged NoCIS", NoCIS)
            print("# of channels flagged BadLas", BadLas)
            print("# of channels flagged NoLas", NoLas)
            print("# of channels flagged BadCs", BadCs)
            print("# of channels flagged NoCs", NoCs)

        fig, ax = plt.subplots()
        dates=[DT.datetime.strptime(i,"%Y-%m-%d") for i in Use_date_list]
        x=[date2num(j) for j in dates]
        t=[]
        for i in x:
            t.append(i-x[0])
        ticks = [i / max(t) for i in t]
        ticks = np.asarray(ticks)
        print(ticks)

        if self.calflags == 'CIS':
            ax.plot(ticks, BAD, 'ks-', label='Total Masked ADC\'s')
            ax.plot(ticks, BadCIS, 'b*-', label='ADC\'s flagged BadCIS (1104)')
            ax.plot(ticks, NoCIS, 'ro-', label='ADC\'s flagged NoCIS (1103)')
            plt.ylim([-10,max(BAD+BadCs+NoCs)+80])
        
        elif self.calflags == 'Las':
            ax.plot(ticks, BAD, 'ks-', label='Total Masked ADC\'s')
            ax.plot(ticks, BadLas, 'yv-', label='ADC\'s flagged BadLas (2101)')
            ax.plot(ticks, NoLas, 'g^-', label='ADC\'s flagged NoLas (2100)')
            plt.ylim([-10,max(BAD+BadLas+NoLas)+80])
            
        elif self.calflags == 'Cs':
            ax.plot(ticks, BAD, 'ks-', label='Total Masked ADC\'s')
            ax.plot(ticks, BadCs, 'cd-', label='ADC\'s flagged BadCs (2103)')
            ax.plot(ticks, NoCs, 'mp-', label='ADC\'s flagged NoCs (2102)')
            plt.ylim([-10,max(BAD+BadCs+NoCs)+80])
        
        else:
            ax.plot(ticks, BAD, 'ks-', label='Total Masked ADC\'s')
            ax.plot(ticks, BadCIS, 'b*-', label='ADC\'s flagged BadCIS (1104)')
            ax.plot(ticks, NoCIS, 'ro-', label='ADC\'s flagged NoCIS (1103)')
            ax.plot(ticks, BadLas, 'yv-', label='ADC\'s flagged BadLas (2101)')
            ax.plot(ticks, NoLas, 'g^-', label='ADC\'s flagged NoLas (2100)')
            ax.plot(ticks, BadCs, 'cd-', label='ADC\'s flagged BadCs (2103)')
            ax.plot(ticks, NoCs, 'mp-', label='ADC\'s flagged NoCs (2102)')
            plt.ylim([-10,max(BAD+BadCIS+NoCIS+BadLas+NoLas+BadCs+NoCs)+160])
            
        ax.set_xlabel('Time (yyyy-mm-dd)')
        ax.set_ylabel('Number of ADC Channels')
        ax.set_title('COOL Status Database History')
        ax.legend(prop={'size':10}, loc=1 )

        ax.set_xticks(ticks)
        ax.set_xticklabels([i.strftime("%Y-%m-%d") for i in dates], rotation = 90)
        ax.tick_params(axis='both', which='major', labelsize=8)
        ax.tick_params(axis='both', which='minor', labelsize=6)

        fig.savefig('%s/Cool_History.png'%self.dir, bbox_inches='tight')
        
        


    
    




    
    
    



        
        
        
        
        
