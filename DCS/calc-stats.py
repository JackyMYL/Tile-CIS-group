#!/usr/bin/env python
import numpy as np
import pprint as pp
import os
import sys
import datetime

# Define all functions inside the class otherwise they cannot be accessed

class calc():
    """
    **********************************************************************
                                calc-stats.py

    Description:  Open datafiles from DDV query and calculates statistics

                                *** NOTE ***
              This script is part of the collection of auto-plot-lvps

    Author:       Miguel F. Medeiros (TileDCS)    
    Contact:      miguel.fontes.medeiros@cern.ch       
    ***********************************************************************
    """
    def __init__(self, outfile,  digits=3, verbose=True):
        """ Initialize class """
        self.digits=digits
        self._verbose=verbose
        self._FILENAME=outfile
        self._file_header()

    def write(self, text, wr_mode='a'):
        """ Writes a text string to file """
        with open(self._FILENAME, wr_mode) as fout:
            fout.write(text +"\n")

    def _file_header(self):
        """ Writes the header to the output stats file """ 
        labels=["n_size","RMS","Mean","Median","Std","Max","Max_date","Min","Peak2Peak","Max-RMS", "invalids/excluded"]
        s1 = ",".join(['fullset_{0}'.format(l)    for l in labels])
        """ 
        If we need to print the labels for all the subsets in the file 
        s2 = ",".join(['set_before_{0}'.format(l) for l in labels])
        s3 = ",".join(['set_after_{0}'.format(l)  for l in labels]) 
        full_header="file,"+s1+s2+s3    	
        """
        full_header="file,"+s1          	# full string to output to file
        self.write(full_header, 'w')
    
    def get_RMS(self, val):
        """ Returns the RMS value for a given list """
        return round(np.sqrt(np.mean(np.square(val))), self.digits)
 
    def get_MAX_RMS(self, val_list):
        """ Returns the MAX-RMS value for a given list """
        return round(np.max(val_list), self.digits)-self.get_RMS(val_list)
    
    def get_weighted_mean(self, val_list, date_list):
        """Returns the time-weighted average mean current"""
        total_time = 0
        weighted_mean = 0
        print(len(date_list))
        print(len(val_list))
        for k in range(len(date_list)-1):
            date_time_0  = date_list[k]
            date_time_1 = date_list[k+1]

        
            #Parse date and time from beginning of the interval
            date_time_object_0 = datetime.datetime.strptime(date_time_0, "%d-%m-%Y %H:%M:%S:%f")
            #Parse date and time at the endpoint of the interval
            date_time_object_1 = datetime.datetime.strptime(date_time_1, "%d-%m-%Y %H:%M:%S:%f")

            # Calculate difference
            delta = date_time_object_1-date_time_object_0 #Parse time difference internally
            dt = delta.total_seconds()


            total_time += dt
            weighted_mean += dt*float(val_list[k])
        return weighted_mean/total_time
    
    def _calc_full(self, module, val_lst, date, date_lst):
        """ Calculates statistics with the data lists """

        self._specs={
                        'module':   module,
                        'len':      len(val_lst),
                        'rms':      self.get_RMS(val_lst),
                        'mean':     round(np.mean(val_lst),   self.digits),		
                        'median':   round(np.median(val_lst), self.digits),	 
                        'std' :     round(np.std(val_lst),    self.digits),	
                        'max':      round(np.max(val_lst),    self.digits),
                        'date':     date,					
                        'min' :     round(np.min(val_lst),    self.digits),    	 
                        'p2p':      round(np.ptp(val_lst),    self.digits),    # peak-to-peak
                        'max-rms':  self.get_MAX_RMS(val_lst),
                        'weighted-mean':self.get_weighted_mean(val_lst, date_lst)                
                    }

        stats_lst=[
                    self._specs['len'], 
                    self._specs['rms'],
                    self._specs['mean'],
                    self._specs['median'],
                    self._specs['std'],
                    self._specs['max'],
                    self._specs['date'],
                    self._specs['min'],
                    self._specs['p2p'],
                    self._specs['max-rms'],
                    self._specs['weighted-mean']
                  ]

        stats_str=",".join(map(str, stats_lst))
        return self._specs, stats_str
    
    def _calc_before_after(self, module, val_lst, date, date_lst):
        """ Calculates statistics with the data lists (only used for printing to console) """

        self._specs={
                        'module':   module,
                        'len':      len(val_lst),
                        'rms':      self.get_RMS(val_lst),
                        'mean':     round(np.mean(val_lst),   self.digits),		
                        'median':   round(np.median(val_lst), self.digits),	 
                        'std' :     round(np.std(val_lst),    self.digits),	
                        'max':      round(np.max(val_lst),    self.digits),
                        'date':     date,					
                        'min' :     round(np.min(val_lst),    self.digits),    	 
                        'p2p':      round(np.ptp(val_lst),    self.digits),    # peak-to-peak
                        'max-rms':  self.get_MAX_RMS(val_lst)               
                    }

        stats_lst=[
                    self._specs['len'], 
                    self._specs['rms'],
                    self._specs['mean'],
                    self._specs['median'],
                    self._specs['std'],
                    self._specs['max'],
                    self._specs['date'],
                    self._specs['min'],
                    self._specs['p2p'],
                    self._specs['max-rms']
                  ]

        stats_str=",".join(map(str, stats_lst))
        return self._specs, stats_str
    
    # Writes the statistcs file (see run for when the data is read in )
    
    def calc_stats(self, module):
        """ Calculate statistics for each module """ 

        #---Splits the data in two subsets (before peak value & after peak value)
        values=self.list_values
        idx_max=np.argmax(values)			        # index of maximum

        # subset after peak
        subset_after=values[idx_max+1:]			        # subset value list after the peak value (the +1 removes the peak point)
        subset_after_dates=self.list_dates[idx_max+1:]		# subset date list after the peak value	(the +1 removes the peak point)
        idx_max_after=np.argmax(subset_after)			# index of maximum    
        # subset before peak
        subset_before=values[:idx_max]			        # subset value list before the peak value (excluding peak)
        subset_before_dates=self.list_dates[:idx_max]		# subset date list before the peak value (excluding peak) 
        idx_max_before=np.argmax(subset_before)			# index of maximum 

        #---Calculate statistics for each data subset
        self.full,   full_str   = self._calc_full(module, values,        self.list_dates[idx_max], self.list_dates)
        self.before, before_str = self._calc_before_after(module, subset_before, subset_before_dates[np.argmax(subset_before)], self.list_dates)
        self.after,  after_str  = self._calc_before_after(module, subset_after,  subset_after_dates[np.argmax(subset_after)], self.list_dates)
	
        #---Prepare full string to write to the file
        sl1=module+","+full_str+","+str(self.count_invalids)+"/"+str(self.count_excluded)

        #---Write fiel using full dataset (before, after are unused)
        self.write(sl1)

	#---Output to console	
        if self._verbose:
            print("====="*20)
            print(module)
            print("-----"*20)
        print("---full data set---","\t","  ---subset before max---  ","---subset after max---")
        print("n_size:  \t",  self.full['len'],     "\t|\t", self.before['len'],     "\t\t|\t", self.after['len'])
        print("RMS:     \t",  self.full['rms'],     "\t|\t", self.before['rms'],     "\t\t|\t", self.after['rms'])
        print("Mean:    \t",  self.full['mean'],    "\t|\t", self.before['mean'],    "\t\t|\t", self.after['mean'])
        print("Median:  \t",  self.full['median'],  "\t|\t", self.before['median'],  "\t\t|\t", self.after['median'])
        print("Std:     \t",  self.full['std'],     "\t|\t", self.before['std'],     "\t\t|\t", self.after['std'])
        print("Max:     \t",  self.full['max'],     "\t|\t", self.before['max'],     "\t\t|\t", self.after['max'])
        print("Min:     \t",  self.full['min'],     "\t|\t", self.before['min'],     "\t\t|\t", self.after['min'])
        print("Peak2Peak\t",  self.full['p2p'],     "\t|\t", self.before['p2p'],     "\t\t|\t", self.after['p2p'])
        print("Max-RMS  \t",  self.full['max-rms'], "\t|\t", self.before['max-rms'], "\t\t|\t", self.after['max-rms'])
        print("---Max/peak details---")
        print("Max_full:  \t",round(np.max(values),        self.digits), "\t", self.list_dates[idx_max])
        print("Max_before:\t",round(np.max(subset_before), self.digits), "\t", subset_before_dates[idx_max_before])
        print("Max_after: \t",round(np.max(subset_after),  self.digits), "\t", subset_after_dates[idx_max_after])
    
    # Writes the files and runs the statistics
    def run(self, path, low_thresh):
        """ Runs on the specified path and applies the statistics """
        file_stats={}

        for filename in os.listdir(path):	                                        # loops every file in a given directory
            self.list_values=[]
            self.list_dates=[]
            self.count_excluded=0						    
            self.count_invalids=0
            self.count_skipped=0
            self.count_unknown=0

            with open(path+filename) as file_in:
                for count, line in enumerate(file_in.readlines()[1:], 1):               # skip first line (header of the downloaded file)
                    try:
                        values, sdate, stime, valid_field= line.split()			# split the data line
                        
                        if(valid_field=="valid" and float(values)>=low_thresh):		# only fill the lists if they are valid and above threshold
                            self.list_values.append(float(values))			
                            self.list_dates.append(sdate+" "+stime)			

                        elif(valid_field=="valid" and float(values)<low_thresh):
                            self.count_excluded+=1
	
                        elif(valid_field=="invalid"): 
                            self.count_invalids+=1		                         

                        else:
                            self.count_unknown+=1
		    
                    except:
                            self.count_skipped+=1
                print(filename)

            self.calc_stats(filename)						# calculate statistics on the data 
        
            file_stats[filename]={
                                        'total':                 count,
                                        'excluded-by-threshold': self.count_excluded,
                                        'excluded-by-invalid':   self.count_invalids,
                                        'excluded-by-skipped':   self.count_skipped,
                                        'excluded-by-unknown':   self.count_unknown,
                                        'valids':                len(self.list_values), 
                                        '% useful data':         '%.3f' % round((float(len(self.list_values))/float(count))*100,   self.digits),
                                        '% cut data':            '%.3f' % round((1-float(len(self.list_values))/float(count))*100, self.digits)
                                     }
        if self._verbose:
            print("====="*20)
            print("GLOBAL STATS")
            print("-----"*20)
            pp.pprint(file_stats)

#============================
#          MAIN
#============================

if __name__ == "__main__":
    OUTPUT_FILE="stats/stats_"+sys.argv[1]+"_"+sys.argv[2]+"_"+sys.argv[3]+".txt"
    print(OUTPUT_FILE)

    LOW_THRESHOLD=8.0      # Threshold for narrowing power-cycles, modules off, etc									    
    PATH="clean/"          # The path to run the statistics 
    
    stats=calc(OUTPUT_FILE)
    stats.run(PATH, LOW_THRESHOLD)
