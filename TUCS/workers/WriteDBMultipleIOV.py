# Author: Grey Wilburn <gwwilburn@uchicago.edu>
# Date: Ocotber 2014
# 
# Based on "WriteDBNew.py by Henric Wilkens
#
# Edited heavily by A. Solodkov <Sanya.Solodkov@cern.ch>
# Date: November 2014
#
# Edited by Mengyang Li & Peter Camporeale
# Date: May 2023

from src.ReadGenericCalibration import *

# For reading from DB
from TileCalibBlobPython import TileCalibTools
from TileCalibBlobPython.TileCalibTools import MINRUN, MINLBK, MAXRUN, MAXLBK, LASPARTCHAN
from TileCalibBlobObjs.Classes import *

# For turning off annoying logging
import logging
from TileCalibBlobPython.TileCalibLogger import TileCalibLogger, getLogger


class WriteDBMultipleIOV(ReadGenericCalibration):
	
	"Writeout database constants sorted by UpdateNeeded.py"

	def __init__( self, input_schema = 'OFL',
			output_schema = 'sqlite://;schema=tileSqlite.db;dbname=CONDBR2',
			folder='CALIB/CIS',
			intag = 'CURRENT',
			tag='RUN2-HLT-UPD1-00',
			run_type='CIS',
			data='DATA',
			multiple_iov = False,
			recalALL = False,
			iov=(0,0)):

		self.input_schema  = input_schema
		self.output_schema  = output_schema
		self.folder  = folder
		self.intag = intag
		self.data = data
		self.tag = tag
		self.iov_dict = {}
		self.mod_dict = {}
		self.multiple_iov = multiple_iov
		self.recalALL = recalALL
		self.run_type = run_type
#		if self.run_type == 'CIS':
#			self.folder = '/TILE/OFL02/CALIB/CIS/LIN'
#			self.tag ='RUN2-HLT-UPD1-00'

		#Format input at output schemae
		if "sqlite" in input_schema:
			splitname=input_schema.split("=")
			if not "/" in splitname[1]:
				splitname[1]=os.path.join(getResultDirectory(), splitname[1])
				self.input_schema_full="=".join(splitname)

		if "sqlite" in output_schema:
			splitname=output_schema.split("=")
			if not "/" in splitname[1]:
				splitname[1]=os.path.join(getResultDirectory(), splitname[1])
				self.output_schema="=".join(splitname)
			print(("output schema ", self.output_schema))
		self.latestRun = TileCalibTools.getLastRunNumber()

		# This is used only for reading the old DB
		if iov==(0,0):
			self.iov     = (self.latestRun,0)
		else:
			self.iov     = iov
	

	def ProcessStart(self):

		#Configure blob reader
		if 'OFL' in self.input_schema or 'OFFLINE' in self.input_schema:
			linepath = 'OFL02'
			schemepath = 'COOLOFL'
			own_schema = False
		elif 'ONL' in self.input_schema or 'ONLINE' in self.input_schema:
			linepath = 'ONL01'
			schemepath = 'COOLONL'
			own_schema = False
		elif ".db" in self.input_schema:
			own_schema = True
			print(("\nWriteDBCIS: reading SQL file %s\n" % self.input_schema))
			#self.input_schema_full = self.input_schema_full
		if not own_schema:
			if self.folder == 'CALIB/CIS':
				self.folder_full = '/TILE/%s/CALIB/CIS/LIN' % linepath
			elif self.folder == 'CALIB/LAS':
				self.folder_full = '/TILE/%s/CALIB/LAS/LIN' % linepath
			elif self.folder == 'CALIB/CES':
				self.folder_full = '/TILE/%s/CALIB/CES' % linepath
			elif self.folder == 'CALIB/EMS':
				self.folder_full = '/TILE/%s/CALIB/EMS' % linepath
			elif self.folder == 'INTEGRATOR':
				self.folder_full = '/TILE/%s/INTEGRATOR' % linepath
			elif self.folder == 'CALIB/LAS/FIBER':
				self.folder_full = '/TILE/%s/CALIB/LAS/FIBER' % linepath
			else:
				self.folder_full = self.folder
		else:	
			self.folder_full = self.folder	
		
		if not own_schema:
			if self.data == 'MC':
				self.input_schema_full = '%s_TILE/OFLP200' % schemepath
			else:
				self.input_schema_full = '%s_TILE/CONDBR2' % schemepath

		try:
			self.input_db = TileCalibTools.openDbConn(self.input_schema_full, 'READONLY')
		except Exception as e:
			print("WriteDBCIS: Failed to open a database connection, this can be an AFS token issue")
			print(e)
			sys.exit(-1)
		
		self.input_db = TileCalibTools.openDbConn(self.input_schema_full,'READONLY')
		print((self.input_schema))
		FolderTag = TileCalibTools.getFolderTag(self.input_db, self.folder_full, self.intag)
		print((self.folder_full, FolderTag))
		try:
			self.blobReader = TileCalibTools.TileBlobReader(self.input_db, self.folder_full, FolderTag)
		except Exception as e:
			print("Failed to creat blob reader")
			sys.exit(0)
		#Configure output DB, foldertag
		self.output_db = TileCalibTools.openDbConn(self.output_schema,'UPDATE')
		self.FolderTag = TileCalibUtils.getFullTag(self.folder_full, self.tag)
	
		#Variables used below
		self.numbers_dict = {}

	def ProcessRegion(self,region):
		# If there are no events for this region, do nothing
		if region.GetEvents() == set():
			return
			
		#Get parent drawer	
		parent_drawer = region.GetParent().GetParent()
		
		#Check if this adc needs to be updated; db_update is a global dictionary created in MeanDBUpdate.py
		gh = region.GetHash()
		if gh in db_update:
			self.numbers_dict[gh] = {}

			#Get partition module, channel, gain
			numbers = region.GetNumber()
			part, mod, chan, gain = numbers
			drawer = mod-1
	
			part_name = ['AUX','LBA','LBC','EBA','EBC']
			self.mod_dict[gh] = '%s_m%02d' % (part_name[part],mod)

			self.numbers_dict[gh]['part'] = part
			self.numbers_dict[gh]['drawer'] = drawer
			self.numbers_dict[gh]['chan'] = chan
			self.numbers_dict[gh]['gain'] = gain
			self.numbers_dict[gh]["parent_drawer"] = parent_drawer

			# print(f"DB Update List: {db_update_list}")
			if gh in db_update_list or self.recalALL:				
				iovList = []
				#print part, drawer, gh
				dbobjs = self.blobReader.getDBobjsWithinRange(part, drawer)
				while dbobjs.goToNext():
					obj = dbobjs.currentRef()
					objsince = obj.since()
					sinceRun = objsince >> 32
					sinceLum = objsince & 0xFFFFFFFF
					since    = (sinceRun, sinceLum)
					objuntil = obj.until()
					untilRun = objuntil >> 32
					untilLum = objuntil & 0xFFFFFFFF
					until    = (untilRun, untilLum)
					iov = (since, until)
					iovList.append(iov)
				self.iov_dict[gh] = iovList
				#print(f"iovList: {iovList}")


	def ProcessStop(self):
		modcount = 0
		iov_until = (MAXRUN,MAXLBK)
		author   = "%s" % os.getlogin()					
		last_run = sorted(db_run_list)[-1]

		def partName(x):
			if x == 1:
				return "LBA"
			elif x == 2:
				return "LBC"
			elif x == 3:
				return "EBA"
			elif x == 4:
				return "EBC"

		#Now we will write the information stored in mod_update_dict into our SQLite file, one run at a time
		#A. Solodkov made this bit work...
		blobWriters = []
		# print(f"Sorted mod_update_dict (to loop over runs selected): {sorted(mod_update_dict)}")
		for run in sorted(mod_update_dict):
			print(run)
			try:
				blobWriter = TileCalibTools.TileBlobWriter(self.output_db,self.folder_full, 'Flt')
				blobWriters.append(blobWriter)
			except Exception as e:
				print("Failed to open output database")
				sys.exit(0)
			print("++++++++++++++++++++++++++++")

			change_chan_list = []
			#Set the beginning iov to the current run number
			iov_since = (run, 0)
			print(iov_since)
			#Loop over all of the modules w/ changes, and then write them
			for module in mod_update_dict[run]:
				first = True
				for channel in mod_update_dict[run][module]:
					change_chan_list.append(channel)
					part = self.numbers_dict[channel]['part']
					drawer = self.numbers_dict[channel]['drawer']
					chan = int(self.numbers_dict[channel]['chan'])
					gain = int(self.numbers_dict[channel]['gain'])
					parent_drawer = self.numbers_dict[channel]['parent_drawer']
					print("----------------------------")
					
					valid_run = False
					for iov in self.iov_dict[channel]:
						run_min = int(iov[0][0])
						run_max = int(iov[1][0])
						print(f"Run range:{[run_min, run_max]}")
						if run_min <= run <= run_max:
							valid_run = True
					if not valid_run:
						print("\nCHANGE BEING WRITTEN FOR INVAlID IOV")
						print(("\nRUN: ", run))
						print(("\nCHANNEL: ", channel))
						print(("\n NEW DB VALUE: ", mod_update_dict[run][module][channel]))
						return

					#If this is the first channel from the module, we need to retrieve this module's blob from the database
					if first:
						first = False
						if 'drawerBlob' not in parent_drawer.data:  # Create a drawer BLob for writing
							print(("reading old constants from DB", partName(part), parent_drawer))
							readerDrawerBlob = self.blobReader.getDrawer(part, drawer, iov_since)
							if type(readerDrawerBlob)==type(None):
								print(("Error! Couldn't retreive blob from", self.input_schema))
								sys.exit(0)
						else:
							print(("copying constants from previous IOV", parent_drawer))
							readerDrawerBlob = parent_drawer.data['drawerBlob']
						#Set up blobl writer
						writerDrawerBlob = blobWriter.getDrawer(part, drawer, readerDrawerBlob)
						parent_drawer.data['drawerBlob'] = writerDrawerBlob
					
					CIS_constant = mod_update_dict[run][module][channel]
					#write change for this channel to the ADC		
					writerDrawerBlob.setData(int(chan), int(gain),0,float(CIS_constant))	

			print("============================")
			#write to comment channel
			if self.recalALL:
				blobWriter.setComment(author, "Updated CIS constants for entire detector using --recalALL" % change_chan_list)
			else:
				blobWriter.setComment(author, "Updated CIS constants for %r" % change_chan_list)

			#After looping over all the changed modules for this 
			blobWriter.register(iov_since, iov_until, self.FolderTag)
					
