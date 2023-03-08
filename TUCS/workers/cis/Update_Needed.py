from src.GenericWorker import *
from subprocess import call

# Define your worker class here, and be sure to change the name
class Update_Needed(GenericWorker):
	"Determines which ADC's need databasecalibration constant updates \
         by comparing current and newly-calculated DB constants"

	def __init__(self, recalALL = False, multiple_iov = False, run_type = 'CIS',threshold = None):
		self.recalALL = recalALL
		self.multiple_iov = multiple_iov
		self.run_type = run_type
	
		if threshold is None:
			if self.run_type == 'CIS':
				self.threshold = 0.005 #set by G Wilburn and A Solodkov, 2/2015
			elif self.run_type == 'LAS':
				self.threshold = 0.007
			elif self.run_type == 'CES':
				self.threshold = 0.007
			#Include other calibration types?
				
			else:
				print(("ERROR: UNKNOWN RUN TYPE %s" % self.run_type))
				sys.exit(0)
		else:

			self.threshold = threshold 


	def ProcessStart(self):
		global mod_update_dict 
		mod_update_dict = {}

			
		
		self.last_run_all =  sorted(db_run_list)[-1]
		if not self.multiple_iov:
			mod_update_dict[self.last_run_all] = {}

	
	def ProcessStop(self):
		pass
		
	def ProcessRegion(self, region):
		if region.GetEvents() == set():
			return
				
		gh = region.GetHash()

		#Find the module name for this adc
		gh_list = gh.split('_')
		mod_name = gh_list[1] + '_' + gh_list[2]


		if len(db_update[gh]) == 0:
			return
		#if --multipleiov flag is useda
		if self.multiple_iov:
			first_run = True
			first_write = False
			for event in sorted(region.GetEvents(), key=lambda x:x.run.runNumber):
				run = event.run.runNumber
				#Only use CIS runs for CIS updates
				if self.run_type == 'CIS' and event.run.runType == 'CIS' and "calibration" in event.data:
					good_run = True
					run = event.run.runNumber
					old_db = event.data['f_cis_db']
				#Modify for other calibraion systems...
				else:
					good_run = False
			
				#Loop through all runs of the appropriate type
				if good_run:
					write = False

					#For later runs if the new DB value and the old DB value differ greatly, we write the new DB value 
					if not self.recalALL:
						if (abs((db_update[gh][run] - old_db) / old_db ) > self.threshold and db_update[gh][run] > 0) or first_write:
							if not first_run:
								if abs((db_update[gh][run] - previous_run) / previous_run) > self.threshold:
									write = True
									first_write = True
									db_update_list.append(gh)
							else:
								write = True
								first_write = True
								db_update_list.append(gh)
						# print(f"run{run} \n\n*****\n\n*****")
						# print(f"Old db value {old_db}")
						# print(f"get_hash:{gh}")
						# print(f"db_update: {db_update}")
						# print(f"db_update_list: {db_update_list}")
							
					elif self.recalALL:
						write = True
						if (abs((db_update[gh][run] - old_db) / old_db ) > self.threshold and db_update[gh][run] > 0):
							db_update_list.append(gh)
					

					#Here we store the values to be written in a nested dictionary
					if write:
						#Make sure the run is in the dictionary
						if not run in mod_update_dict:					
							mod_update_dict[run] = {}
						#Make sure the module is in the dictionary	
						if not mod_name in mod_update_dict[run]:
							mod_update_dict[run][mod_name] = {}
						mod_update_dict[run][mod_name][gh] = db_update[gh][run]	
						# print(f"mod update dict: {mod_update_dict}")
				if run in db_update[gh]:
					previous_run = db_update[gh][run]
					first_run = False
		#	for run in sorted(mod_update_dict):
		#		for mod in mod_update_dict[run]:
 		#			for adc in mod_update_dict[run][mod]:
		#				print adc, run, mod_update_dict[run][mod][adc]
		#For the standard, single iov update
		else:
			#We only care about the value for the last run
			last_run = sorted(calib_dict[gh])[-1]
			for event in sorted(region.GetEvents(), key=lambda x: x.run.runNumber):
				if int(event.run.runNumber) == int(last_run):
					print((event.run.runNumber, "passed the last run cut"))
					if self.run_type == 'CIS': #Modify for other calib types
						old_db = event.data['f_cis_db']

					#If the new DB value and old DB value differ greatly, we write the new DB value to the sql file
					if (abs( (db_update[gh][last_run] - old_db) / old_db) > self.threshold and db_update[gh][last_run] > 0) or self.recalALL:
						if not mod_name in mod_update_dict[self.last_run_all]:
							mod_update_dict[self.last_run_all][mod_name] = {}
						mod_update_dict[self.last_run_all][mod_name][gh] = db_update[gh][last_run]
						if (not self.recalALL) or abs( (db_update[gh][last_run] - old_db) / old_db) > self.threshold:
							db_update_list.append(gh)

