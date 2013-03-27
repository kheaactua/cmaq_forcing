# Maybe I should use the netcdf4 package?  I'll do this in another branch.
#from Scientific.IO.NetCDF import NetCDFFile
from DataFile import DataFile

from numpy import shape
import os
import numpy as np
import re
import math
from datetime import date

from extendedClasses import dateE

# This is mostly for debugging..  Just ansi colours
from bcolours import bcolours as bc, colouredNum as ci
from bcolours import colouredNum as ci

def getForcingObject(ni,nj,nk,nt):
	return ForceOnSpecies(ni,nj,nk,nt)

# Abstract
class Forcing(object):
	""" Class set up to take in all required inputs and generate forcing fields.

	    This class can handle different time averaging, and layer, [2d] domain, species
	    and time masks.  This class is designed to be used with a CLI interface of a wxpython GUI.

		Specific forcing functions are implemented by inheriting this class.

		Usage example::

		   # Choose what kind of forcing
		   f = ForceOnAverageConcentration()

		   # Initialize the object and give it some concentration files
		   f.loadDims(sample_concentration_file_name)
		   f.loadConcentrationFiles(concentration_files)

		   # Define the parts of the domain to operate
		   f.layers=layers_to_use
		   f.species=["O3"]

		   # What kind of time averaging?
		   f.setAveraging("Max 8 hr")

		   # Set up output parameters
		   fc.outputFormat = 'Force.TYPE.YYYYMMDD'
		   f.outputPath=os.getcwd() + 'output/'

		   # Set up time zones
		   f.griddedTimeZone = 'GriddedTimeZoneMask.nc'

		   # Run
		   f.produceForcingField()

	"""

	avgoptions = [{'key': 'AVG_MAX8', 'label': 'Max 8 hr', 'winLen': 8},
	              {'key': 'AVG_MAX', 'label': 'Max 1 hr', 'winLen': 1},
	              {'key': 'AVG_MAX24', 'label': 'Max 24 hr', 'winLen': 24},
	              {'key': 'AVG_MASK', 'label': 'Local Hours', 'winLen': None},
	              {'key': 'AVG_NONE', 'label': 'None', 'winLen': None}]

	# Concentration files
	conc_files = []

	# Concentration file path
	inputPath = None

	# True for forward, false for backward.  I'm told
	# the standard is forward
	default_averaging_direction = True

	# Obvious, but used a lot
	dayLen=24

	# Output file name format
	outputFormat = 'Force.TYPE.YYYYMMDD'

	# Output path
	_outputPath = None

	# Layers to process
	_layers = []

	# Gridded timezone file.  Ideally, in the future we'll be able to figure these
	# out with shape files, rather than having a pre-gridded file
	_griddedTimeZone = None
	# The actual gridded field
	griddedTimeZoneFld = None

	# Averaging option.  This should probably be on a subclass, but for now it's so widely
	# used that it was put right here.
	_averaging = None

	# Used for debugging
	debug_i = 2
	debug_j = 2

	# Debugging messages
	@staticmethod
	def debug(*arg):
		""" Debug method, to help me remove all the python 2 style prints, and also
			to put it somewhere better (maybe a log?) """
		Forcing.output(bc.colours['blue'], "".join(map(str, arg)))
	@staticmethod
	def log(*arg):
			Forcing.output(0, "".join(map(str, arg)))
	@staticmethod
	def warn(*arg):
			Forcing.output(bc.colours['yellow'], "".join(map(str, arg)))
	@staticmethod
	def error(*arg):
			Forcing.output(bc.colours['red'], "".join(map(str, arg)))
	@staticmethod
	def output(colour, msg):
		c=bc()
		if colour == 0:
			colour = c.colours['clear']
		print "%s%s%s"%(c.ansiColour(colour), msg.strip(), c.clear)

	@staticmethod
	def printVec(vec, c, cstr):
		""" Debugging function, will dissapear at some point """
		red=c.red
		outs=""
		for i in range(0, len(vec)):
			v=vec[i]
			if v > 0:
				outs=outs+"%s%4.3f%s"%(red, v, cstr)
			else:
				outs=outs+"%4.3f"%(v)
			if i<len(vec)-1:
				outs=outs+" "
		return outs


	def __init__(self,ni=0,nj=0,nk=0,nt=0,sample_conc=''):
		""" Initialize Forcing object.  Dimentions will be used if given,
		    but if a sample concentration file is given, it will be read
		    instead.  (So, either provide dims, a file, or none.)  When nothing
		    is really provided, the user will typically use
			the static method loadDims() to set the dims later

		Keyword Arguments:

		ni:*int*
		   Columns

		nj:*int*
		   Rows

		nk:*int*
		   Layers

		nt:*int*
		   Time steps

		sample_conc:*string*
		   Name of sample concentration file
		"""

		if len(sample_conc):
			dims=Forcing.loadDims(sample_conc)
			#print dims
			self.ni = dims['ni']
			#print "type(self.ni) = %s"%type(self.ni)
			self.nj = dims['nj']
			self.nk = dims['nk']
			self.nt = dims['nt']
		else:
			# Set up full dimensions
			#print "Received ni=%d nj=%d nk=%d nt=%d" % (ni,nj,nk,nt)
			self.ni=ni
			self.nj=nj
			self.nk=nk
			self.nt=nt

		# Offer some protection against bad files
		if self.nt is not self.dayLen+1:
			raise ValueError("This application is only designed to work with 24 hour time files.  Given nt=%d"%self.nt)


		# Initialize vectors, space is done differently
		self.times = range(1,nt)
		self.layers = range(1,nk)

		self.species = []

		# Set a default mask of everything
		# Note it's transposed, as that's how netcdf saves it
		# Probably be more efficient to initialize this to boolean values rather
		# than converting it.. but can't seem to find out how to do that. 
		self.space=np.ones((self.nj,self.ni)) == 1

		# Set up default timezones incase they aren't given.  Set everything
		# to 0
		self.griddedTimeZoneFld = np.zeros((self.nj, self.ni))

		# Empty set of concentration files
		self.conc_files = []

		self._outputPath = os.getcwd() + '/output'

	@staticmethod
	def loadDims(filename):
		""" Load the dimensions from a netcdf file, then close the file.
		    Validator initializer also does this.

		Keyword Arguments:

		filename:*string*
		   Netcdf file name

		Returns:
		   dict of ni,nj,nk,nt
		"""

		conc = DataFile(filename, mode='r', open=True)
		dims={'ni': conc.dimensions['COL'], \
		'nj': conc.dimensions['ROW'], \
		'nk': conc.dimensions['LAY']}

		# TSTEP is unlimited, so python has problems reading it
		# So instead we'll examine the shape of a variable
		# Let's assume TFLAG exists
		shape = conc.variables['TFLAG'].shape
		# This first element is TSTEP
		dims['nt'] = shape[0]

		conc.close()

		return dims

	def generateForceFileName(self, conc, fmt = None):
		""" Generate a forcing file name based on the input file name.
			This is used because often CMAQ is cycled, and files are
			named something.ACONC.DATE, and forcing files are expected
			to be in the format something.DATE

			Warning, if there are search/replace values in the path leading
		    the file name, they may also be replaced right now.  (Should fix this)

		Keyword Arguments:

		conc:*Datafile*
		   Datafile of the concentration file

		fmt:*string*
		  Format of the forcing file.  Replacement strings:
		  YYYY  - replaced with four digit year
		  YY    - replaced with two digit year
		  MM    - replaced with two digit month
		  DD    - replaced with two digit day
		  TYPE  - Forcing function type

		  Defaults to the format set on this object


		Returns:
		   *string* Forcing file path (/directory/and/filename)
		"""

		if not isinstance(conc, DataFile):
			raise TypeError("Concentration input must be a data file")

		if fmt == None:
			fmt = self.outputFormat

		if fmt == None:
			raise ValueError( "Output file format not specified." )

		# Start replacing stuff..
		name = fmt
		date = conc.date

		types = str(type(self))
		#print "Starting with: %s"%types
		types = re.sub(r"[^\.]*\.", '', types)
		#print "Middle with: %s"%types
		types = re.sub(r"'.*$", '', types)
		#print "Ended with: %s"%types
		#os._exit(1)

		month="%0.2d"%date.month
		day="%0.2d"%date.day
		julday="%0.3d"%date.julday

		name = re.sub(r'YYYY', str(date.year), name)
		name = re.sub(r'YY',   str(date.year)[2:], name)
		name = re.sub(r'MM',   month, name)
		name = re.sub(r'DD',   day, name)
		name = re.sub(r'JJJ',  julday, name)

		name = re.sub(r'TYPE', types, name)

		return self.outputPath + '/' + name

	@property
	def species(self):
		""" Getter for the concentration path """
		return self._species
	@species.setter
	def species(self, species_list):
		""" Setter for the species attribute.  How species are considered
			is contingent on the actual forcing function.

		Keyword Arguments:

		species_list:*string[]*
		   List of species
		"""
		self._species=species_list

	@property
	def outputPath(self):
		return self._outputPath
	@outputPath.setter
	def outputPath(self, path):
		self._outputPath = path


	@property
	def griddedTimeZone(self):
		return self._griddedTimeZone
	@griddedTimeZone.setter
	def griddedTimeZone(self, path):
		""" Load a gridded NetCDF file of time zones (so every cell has a value
		    based on it's geographical location such as -5 for example.)

			Though time zones are time-variant, this code does not yet consider that.
		    It reads one field, and applies to at all time.

		    Currently this function is designed to use the format we use in the group,
		    i.e. a NetCDF file with a variable LTIME(TSTEP, LAY, ROW, COL) where the
		    data can be found at TSTEP=0, LAY=0
		"""

		if path is not None:

			self._griddedTimeZone = path

			# Open the file and load in the field
			try:
				tz = DataFile(path, mode='r', open=True)
			except IOError as ex:
				print "Error!  Cannot open gridded timezone file %s"%(path)
				raise

			# The field should be at t=0,k=0
			fld = tz.variables['LTIME'][0,0]
			#print "shape(timezones) = ", fld.shape

			if fld.shape != (self.nj, self.ni):
				raise ValueError("Error.  Gridded time zone file has a different domain than input concentration files.  Current domain=%s, timezone domain=%s"%(str(fld.shape), str( (self.ni, self.nj) ) ))

			self.griddedTimeZoneFld=fld


	# Should replace this setter with a property
	@property
	def averaging(self):
		return self._averaging
	@averaging.setter
	def averaging(self, avg):
		""" Set averaging option, e.g. max 8-hr, etc

		Keyword Arguments:

		avg:*string*
		   Any of the self.avgoptions values
		"""

		found = False
		for t in self.avgoptions:
			if avg==t['label']:
				found = True
				self._averaging=t['key']
				self.averaging_window=t['winLen']

		if found == False:
			raise ValueError("Averaging %s does not exist."%avg);

		#print "Set averaging to %s"%self.averaging

	def maskTimes(self, mask):
		""" Set time mask

		Keyword arguments:

		mask:*int[]*
		   vector of times that WILL be used
		"""
		self.times=mask;

	# Deprecated
	def maskLayers(self, mask):
		""" Set layer mask

		Keyword arguments:

		mask:*int[]*
		   vector of the layers that WILL be used
		"""

		self.layers=mask

	@property
	def layers(self):
		return self._layers+1
	@layers.setter
	def layers(self, mask):
		# Minus 1 because layer 1 is at index 0
		self._layers=np.zeros(len(mask))
		for i in range(0, len(mask)-1):
			self._layers[i] = mask[i]-1

		# The nk we'll be using for the forcing output
		# Typically the user will only force on layer 0 (so the +1 means we'll have one layer)
		# but if they choose layers 1 and 5, we'll need to carry fields of layer dimension 5
		if len(self._layers) > 0:
			self.nk_f = int(max(self._layers)+1)
		else:
			self.nk_f = int(1)

	def maskSpace(self, maskf, variable, value=1):
		""" Set a grid mask

		Keyword arguments:

		maskf:*string*
		   NetCDF file containing the masking field

		variable:*string*
		   Variable in the NetCDF file that is the mask

		value:*int*
		   The masking value of the mask
		"""

		c = bc()
		if maskf is not None:
			try:
				f=DataFile(maskf, mode='r', open=True)
				#print "\n%sOpened spacial mask file %s, variable=%s, val=%s%s\n"%(c.yellow, maskf, variable, value, c.clear)
				mask = f.variables[variable][0][0]
				#print "type(mask)=%s, mask.shape=%s"%(type(mask), mask.shape)
				self.space = mask==value
				if type(self.space) != type(mask):
					print "%sError! self.space's type changed to %s%s"%(c.red, type(self.space), c.clear)
				f.close()
			except Exception as ex:
				print "%sSomething went wrong masking space with mask file %s (exists?: %r) %s%s"%(c.red, maskf, os.path.isfile(maskf), ex, c.clear)
				raise

	def produceForcingField(self, progress_callback = None, dryrun = False, debug=False):
		""" Iterate through concentration files, create forcing output netcdf files, prepare them, and call the writing function.  Using the NetCDF 4 library, we could open all the files at opnce, but I don't trust that I/O Api's odd proprietary format would allow the library to properly sort it.  This is something to investigate in the future.

		Keyword Arguments:

		progressWindow:*ProgressFrame*

		progress_callback:*function*
		   Used to send back progress information.
		   It'll call::

		     progressWindow.progress_callback(percent_progress:float, current_file:Datafile)

		"""

# Todo:
# Replace all the logic below by a three-day-iterator object that knows the timezone range and the averaging direction.  It can then provide the files.  Make sure that the averaging functions also know when they're dealing with a "yesterday" or a "today" (because their mightn't be a yesterday)

		c = bc()

		Forcing.warn("Processing... Domain=(ns=%d, nt=%d, nk=%d, ni=%d, nj=%d)"%(len(self.species), self.nt, self.nk, self.ni, self.nj))

		#
		# Iterate through concentration files


		# In order to keep the code below clean, all the files are
		# initiate in this first loop
		inputs = []
		outputs = []
		for conc in self.conc_files:
			inputs.append(conc)

			force_path=self.generateForceFileName(conc)

			# Initialize the forcing file
			try:
				force = self.initForceFile(conc, force_path)
			except IOError as ex:
				Forcing.warn("Error! %s already exists.  Please remove the forcing file and try again."%force_path)
				# HACK TEMP, remove
				os.remove(force_path)
			except BadSampleConcException as ex:
				Forcing.error("Error!")
				raise

			outputs.append(force)

			# Clean up and close the files
		# End of initiation loop

		# Create file iterator
		iterator = DayIterator(inputs, outputs)
		rdays = iterator.recommendDaysToCarry(timeZoneFld=self.griddedTimeZoneFld, averaging_window=self.averaging_window)
		Forcing.log("For current setup, using days: %s"%(", ".join("'%s'"%iterator.labels[l].strip() for l in rdays)))

		# Index of concentration file
		for conc_idx in range(0, len(iterator)):

			#print "conc_idx = %d"%conc_idx

			# Should re-think where this dry-run goes and what it's for
			if not dryrun:

				# Grab the files
				inputs, outputs = iterator[rdays]

				# What days are we working with?
				if debug:
					Forcing.log("\n")
					for key,f in outputs.iteritems():
						if f is not None:
							bn=f.basename
						else:
							bn="None"
						Forcing.debug("%s: %s"%(iterator.labels[key], bn))
					Forcing.log("\n")

				# Generate a dict of day vectors, e.g. {-1: yesterday, 0: today, 1: tomorrow]
				# where every "day" is a list with species indices (from self.species) for
				# keys, and values of the domain (ni*nj*nk) for that species
				flds = self.generateForcingFields(conc_idx=conc_idx, inputs=inputs, outputs=outputs)

				# Flds[day] is now a ndarray[species][nt][nk][nj][ni]
				idx_s = 0
				for idx_s, species in enumerate(self.species):
					#Forcing.debug("Using species index idx_s: %d = species %s"%(idx_s, species))
					# Get the netcdf variables
					# Get the values
					# add the values
					# write them back to the file

					if debug:
						Forcing.log("\n%si=%d, j=%d, k=0, t=:24"%(c.HEADER, self.debug_i, self.debug_j))
						Forcing.log("GMT:     %s\n"%('  '.join('%4.0d' % v for v in range(1,25))))

					
					for d,f in outputs.iteritems():
						# Our forcing variable (read from the file)
						#print "f.variables [%r] (%s): "%(f._isOpen, f.basename), f.variables._vars
						fvar = f.variables[species]

						# Our base field (what's already in the file)
						base_fld = fvar[:]

						# Overlay the new field to it (additive)
						sum_fld = fvar[:] + flds[d][idx_s]

						# Assign the field to the DataFile
						fvar[:] = sum_fld
						f.sync()
						f.close()

						inputs[d].close()

						if debug:
							l = iterator.labels[d]
							cl = c.light(iterator.clabels[d])
							cn = getattr(c, iterator.clabels[d])
							cd = c.dark(iterator.clabels[d])
							if d == -1:
								col=c.light('yesterday')
							Forcing.debug("%s%sb: %s"%(cl, l, Forcing.printVec(base_fld[:24,0,self.debug_j,self.debug_i], c, cl)))
							Forcing.debug("%s%s:  %s"%(cn, l, Forcing.printVec(flds[d][idx_s][:24,0,self.debug_j,self.debug_i], c, cn)))
							Forcing.debug("%s%ss: %s"%(cd, l, Forcing.printVec(sum_fld[:24,0,self.debug_j,self.debug_i], c, cd)))
							Forcing.debug("\n")

					# endfor outputs
				#endfor species

				# Move the iterator ahead one
				iterator.next()

			# endif dryrun

			# Perform a call back to update the progress
			progress_callback(float(conc_idx)/len(inputs), self.conc_files[conc_idx])

		# endfor days loop (day1, day2, day3, ...)

### DELETE ME
##	def produceForcingFieldOld(self, progress_callback = None, dryrun = False, debug=False):
##		""" Iterate through concentration files, create forcing output netcdf files, prepare them, and call the writing function.  Using the NetCDF 4 library, we could open all the files at opnce, but I don't trust that I/O Api's odd proprietary format would allow the library to properly sort it.  This is something to investigate in the future.
##
##		Keyword Arguments:
##
##		progressWindow:*ProgressFrame*
##
##		progress_callback:*function*
##		   Used to send back progress information.
##		   It'll call::
##
##		     progressWindow.progress_callback(percent_progress:float, current_file:Datafile)
##
##		"""
##
### Todo:
### Replace all the logic below by a three-day-iterator object that knows the timezone range and the averaging direction.  It can then provide the files.  Make sure that the averaging functions also know when they're dealing with a "yesterday" or a "today" (because their mightn't be a yesterday)
##
##		c = bc()
##		if debug:
##			def printVec(vec, c, cstr):
##				red=c.red
##				outs=""
##				for i in range(0, len(vec)):
##					v=vec[i]
##					if v > 0:
##						outs=outs+"%s%4.3f%s"%(red, v, cstr)
##					else:
##						outs=outs+"%4.3f"%(v)
##					if i<len(vec)-1:
##						outs=outs+" "
##				return outs
##
##		print "Processing... Domain=(ns=%d, nt=%d, nk=%d, ni=%d, nj=%d)"%(len(self.species), self.nt, self.nk, self.ni, self.nj)
##
##		#
##		# Iterate through concentration files
##		conc_yest  = None
##		conc_today = None
##		conc_tom   = None
##
##		force_yest  = None
##		force_today = None
##		force_tom   = None
##
##		# In order to keep the code below clean, all the files are
##		# initiate in this first loop
##		conc_files = []
##		force_files = []
##		for conc_datafile in self.conc_files:
##			force_path=self.generateForceFileName(conc_datafile)
##			conc_files.append(conc_datafile.path)
##			force_files.append(force_path)
##
##			# Open the concentration file
##			try:
##				#print "conc_datafile.path=%s"%conc_datafile.path
##				conc = DataFile(conc_datafile.path, mode='r', open=True)
##			except IOError as ex:
##				print "Error!  Cannot open concentration file %s"%(conc_datafile.name)
##				raise
##
##			# Initialize the file
##			try:
##				force = self.initForceFile(conc, force_path)
##			except IOError as ex:
##				print "Error! %s already exists.  Please remove the forcing file and try again."%force_path
##				# HACK TEMP, remove
##				os.remove(force_path)
##			except BadSampleConcException as ex:
##				print "%sError!%s %s"%(c.red, c.clear, ex)
##				raise
##
##			# Clean up and close the files
##			conc.close()
##			force.close()
##		# End of initiation loop
##
##		# List of full file paths
##		conc_files  = [None] + conc_files  + [None]
##		force_files = [None] + force_files + [None]
##
##		#print "Conc_datafiles: %s"%(" ".join(map(str, self.conc_files)))
##		#print "Conc_files: ", conc_files
##
##		# Index of concentration file
##		for conc_idx in range(1, len(conc_files)-1):
##
##			#print "conc_idx = %d"%conc_idx
##
##			if not dryrun:
##
##				# Grab the files
##				conc_yest_path = conc_files[conc_idx-1]
##				force_yest_path = force_files[conc_idx-1]
##
##				conc_today_path = conc_files[conc_idx]
##				force_today_path = force_files[conc_idx]
##
##				conc_tom_path = conc_files[conc_idx+1]
##				force_tom_path = force_files[conc_idx+1]
##
##				# Close files that we're done with
##				if conc_yest is not None:
##					# This is now the day before yesterday, close it.
##					conc_yest.close()
##					conc_yest = None
##
##					force_yest.close()
##					force_yest = None
##
##				# Open the files
##				if conc_yest_path is not None:
##					# Shift this to yesterday
##					conc_yest = conc_today
##					force_yest = force_today
##
##				if conc_tom is None and conc_yest_path is None:
##					# First time around
##					conc_today  = DataFile(conc_today_path, mode='r', open=True)
##					#print "%sSet conc_today (%s) = DataFile%s"%(c.blue, conc_today.basename, c.clear)
##					force_today = DataFile(force_today_path, mode='a', open=True)
##				elif conc_tom is not None:
##					# Not the first or last
##					# Shift tomorrow to today
##					conc_today = conc_tom
##					#print "%sSet conc_today (%s) = conc_tom%s"%(c.red, conc_today.basename, c.clear)
##					force_today = force_tom
##
##				if conc_tom_path != None:
##					conc_tom  = DataFile(conc_tom_path, mode='r', open=True)
##					force_tom = DataFile(force_tom_path, mode='a', open=True)
##				else:
##					conc_tom = None
##					force_tom = None
##
##				## What days are we working with?
##				#print "\n"
##				#print "Yesterday: ", force_yest
##				#print "Today:     ", force_today
##				#print "Tomorrow:  ", force_tom
##				#print "\n"
##
##				# Generate a list[yesterday, today, tomorrow]
##				# where every "day" is a list with species indices (from self.species) for
##				# keys, and values of the domain (ni*nj*nk) for that species
##				flds = self.generateForcingFields(conc_idx=conc_idx,
##				   conc_yest=conc_yest,   conc_today=conc_today,   conc_tom=conc_tom,
##				   force_yest=force_yest, force_today=force_today, force_tom=force_tom)
##
##				# Flds[day] is now a ndarray[species][nt][nk][nj][ni]
##				idx_s = 0
##				for species in self.species:
##					#print "Using species index idx_s: %d = species %s"%(idx_s, species)
##					species = self.species[idx_s]
##					# Get the netcdf variables
##					# Get the values
##					# add the values
##					# write them back to the file
##
##					if debug:
##						print "\n%si=%d, j=%d, k=0, t=:24%s"%(c.HEADER, self.debug_i, self.debug_j, c.clear)
##						print "GMT:   %s\n"%('  '.join('%4.0d' % v for v in range(1,25)))
##
##					# Yesterday
##					if Forcing.default_averaging_direction == False:
##						# In the NA domain (negative timezones), with a forward
##						# forcing average, we'll never see it reach back into
##						# yesterday.  So, if this is false, don't do it
##						if force_yest is not None:
##							var = force_yest.variables[species]
##							sum_fld = np.add(flds['yesterday'][idx_s], var[:])
##
##							#print "Shapes:"
##							#print "shape(var.getValue()): %s"%str(var.getValue().shape)
##							#print "shape(fld[..]):        %s"%str(flds['yesterday'][idx_s].shape)
##							#print "shape(sum_fld):        %s"%str(sum_fld.shape)
##							#print ""
##
##							#print "t=12, base: %4.3f, fld: %4.3f, sum: %s%4.3f%s, manual sum: %4.3f"%(var.getValue()[12,0,self.debug_j,self.debug_i], flds['yesterday'][idx_s][12,0,self.debug_j,self.debug_i], c.red, sum_fld[12,0,self.debug_j,self.debug_i], c.clear, var.getValue()[12,0,self.debug_j,self.debug_i] + flds['yesterday'][idx_s][12,0,self.debug_j,self.debug_i])
##
##
##							if debug:
##								print "Yestb: %s%s%s"%(c.light('yesterday'), printVec(var[:24,0,self.debug_j,self.debug_i], c, c.light('yesterday')), c.clear)
##								print "Yest:  %s%s%s"%(c.yesterday, printVec(flds['yesterday'][idx_s][:24,0,self.debug_j,self.debug_i], c, c.yesterday), c.clear)
##								print "Yests: %s%s%s"%(c.dark('yesterday'), printVec(sum_fld[:24,0,self.debug_j,self.debug_i], c, c.dark('yesterday')), c.clear)
##								print "\n"
##
##
##							var.assignValue(sum_fld)
##							force_yest.sync()
##
##					# Today's...
##					#print "Today's conc:\n", conc_today.variables[species].getValue()[8]
##					#print "Today's force idx_s=%d:\n"%idx_s, flds['today'][idx_s][8]
##					var = force_today.variables[species]
##					#base_fld = var.getValue()
##					#sum_fld = var.getValue() + flds['today'][idx_s]
##					sum_fld = force_today.variables[species][:] + flds['today'][idx_s]
##					fld_matt = flds['today'][idx_s]
##
##					if debug:
##						#print "base_fld.shape: ", base_fld.shape
##						#print "sum_fld.shape:  ", sum_fld.shape
##						print "Todab: %s%s%s"%(c.light('today'), printVec(var[:24,0,self.debug_j,self.debug_i], c, c.light('today')), c.clear)
##						print "Toda:  %s%s%s"%(c.today, printVec(flds['today'][idx_s][:24,0,self.debug_j,self.debug_i], c, c.today), c.clear)
##						print "Todas: %s%s%s"%(c.dark('today'), printVec(sum_fld[:24,0,self.debug_j,self.debug_i], c, c.dark('today')), c.clear)
##						print "\n"
##
##
##					var[:] = sum_fld
##					force_today.sync()
##
##
##					# Tomorrow
##					if force_tom is not None:
##						var = force_tom.variables[species]
##						# Tomorrow shouldn't have any values already, so that's why we're not fetching them here
##
##						if debug:
##							#print "Tomob: %s%s%s"%(c.light('tomorrow'), printVec(var.getValue()[:24,0,self.debug_j,self.debug_i], c, c.light('tomorrow')), c.clear)
##							print "Tomo:  %s%s%s"%(c.tomorrow, printVec(flds['tomorrow'][idx_s][:24,0,self.debug_j,self.debug_i], c, c.tomorrow), c.clear)
##							#print "Tomos: %s%s%s"%(c.dark('tomorrow'), printVec(sum_fld[:24,0,self.debug_j,self.debug_i], c, c.dark('tomorrow')), c.clear)
##							print "\n"
##
##						var[:]=flds['tomorrow'][idx_s] + var[:]
##						force_tom.sync()
##
##					# In species loop
##					idx_s = idx_s + 1
##
##			# endif dryrun
##
##			# Perform a call back to update the progress
##			progress_callback(float(conc_idx)/(len(conc_files)-2), self.conc_files[conc_idx-1])
##
##		# endfor days loop (day1, day2, day3, ...)
##
##		# Make sure things are closed
##		del conc_yest
##		del conc_today

	def initForceFile(self, conc, fpath, species = None):
		""" Initialize a forcing file.
			This method opens the NetCDF file in read/write mode, copies the
			dimensions, copies I/O Api attributes over, and any other common
		    initialization that should be applied to all files

		Keyword Arguments:

		conc:*DataFile*
		   Concentration file to use as a template

		fpath:*string*
		   Path (dir and name) of the forcing file to initialize

		species:*string[]*
		   List of species to create

		Returns:

		NetCDFFile
		   Writable NetCDF File
		"""

		if not isinstance(conc, DataFile) or conc is None:
			raise ValueError("Concentration file must be a DataFile")

		# Make sure the concentration file is open
		conc.open()

		# Debug
		c=bc()

		# fpath should not exist
		if os.path.exists(fpath):
			# TEMP, remove
			os.remove(fpath)
			Forcing.debug("Deleted %s!"%(fpath))
			#raise IOError("%s already exists."%fpath)

		#print "Opening %s for writing"%fpath
		force = DataFile(fpath, mode='w', open=True)

		# Exceptions, so we don't needlessly create huge forcing files
		exceptions={'LAY': self.nk_f}
		Forcing.copyDims(conc, force, exceptions=exceptions)
		Forcing.copyIoapiProps(conc, force)

		if species is None:
			species = self.species

		# First, check the sample concentration file vs the concentration file
		try:
			#var = conc.variables['TFLAG'].getValue()
			var = conc.variables['TFLAG']
		except IOError as e:
			# Pointless try loop for now, but I'll add to it later if needed.
			raise

		if var.shape[0] != self.nt:
			#print "conc.shape = %s, sample.shape = %s"%(str(var.shape), str((self.nt, self.nk, self.nj, self.ni)))
			raise BadSampleConcException("Input file's dimensions (time steps) not not match those of the sample concentration file!  Cannot continue.")

		# Create the variables we'll be writing to
		#print "Initializing %s"%fpath
		for s in species:
			try:
				var = force.createVariable(s, 'f', ('TSTEP', 'LAY', 'ROW', 'COL'))
				z=np.zeros((self.nt,self.nk_f,self.nj,self.ni), dtype=np.float32)
				var[:,:,:,:] = z
				#Forcing.debug("Created zero variable %s in %s"%(s, force.basename))
			except (IOError, ValueError) as ex:
				print "%sWriting error %s%s when trying to create variable %s (%sTSTEP=%d, LAY=%d, ROW=%d, COL=%d%s)=%s%s%s in today's file.\n"%(c.red, type(ex), c.clear, s, c.blue, self.nt, self.nk_f, self.nj, self.ni, c.clear, c.orange, str(z.shape), c.clear), ex
				print "Current variable names: %s\n"%(" ".join(map(str, force.variables.keys())))

		# Copy over TFLAG
		vsrc = conc.variables['TFLAG'][:]

		force.createVariable('TFLAG', 'i', ('TSTEP', 'VAR', 'DATE-TIME'))
		vdest = force.variables['TFLAG']
		try:
			vdest[:]=vsrc[:]
		except (IOError, ValueError) as ex:
			print "%sWriting error %s%s when trying to write TFLAG variable"%(c.red, type(ex), c.clear)
			print "%sshape(vsrc)=%s, shape(vdest)=%s%s"%(c.cyan, str(vsrc.shape), str(vdest.shape), c.clear)
			raise


		## Fix geocode data
		## http://svn.asilika.com/svn/school/GEOG%205804%20-%20Introduction%20to%20GIS/Project/webservice/fixIoapiProjection.py
		## fixIoapiSpatialInfo

		# Sync the file before sending it off
		force.sync()

		# Close the files
		conc.close()
		force.close()

		# From now on, force will be read and written to, so change the mode
		force.mode='a'

		return force

	def generateForcingFields(self, conc_idx, inputs, outputs):
		""" Generate a forcing field.  *Abstract*

		Keyword Arguments:

		conc_idx:*int*
		   Index of the concentration file in self.conc_files

		"""
		raise NotImplementedError( "Abstract method" )


	@staticmethod
	def copyIoapiProps(src, dest):
		""" Copy I/O Api attributes from NetCDF file into new file

		Keyword Arguments:

		src:*NetCDFFile*
		   Open netcdf source file
		dest:*NetCDFFile*
		   Open netcdf destination file
		"""

		# I/O Api attributes
		attrs=["IOAPI_VERSION", "EXEC_ID", "FTYPE", "CDATE", "CTIME", "WDATE", "WTIME", "SDATE", "STIME", "TSTEP", "NTHIK", "NCOLS", "NROWS", "NLAYS", "NVARS", "GDTYP", "P_ALP", "P_BET", "P_GAM", "XCENT", "YCENT", "XORIG", "YORIG", "XCELL", "YCELL", "VGTYP", "VGTOP", "VGLVLS", "GDNAM", "UPNAM", "VAR-LIST", "FILEDESC", "HISTORY"]

		for attr in attrs:
			# Read the attribute
			if hasattr(src, attr): 
				attrVal = getattr(src, attr);
				# Write it to the new file
				setattr(dest, attr, attrVal)
			#else:
			#	# HACK uncomment this
			#	print attr, "does not exist in this NetCDF file %s." % src

		dest.sync()

	@staticmethod
	def copyDims(src, dest, exceptions=dict()):
		""" Copy dimensions from src netcdf file to dest.

		Keyword Arguments:

		src:*DataFile*
		   NetCDF source file

		dest:*DataFile*
			NetCDF destinatin file

		exceptions:*dict*
		   Keys are dimension names, values are the hard value to set it to.  This is used to avoid
		   copying dimensions that are unused.  For example, if we're forcing on the surface layer, no
		   need to create a forcing file with 34 layers where 33 of them will just be huge zero fields.
		"""
		dims = src.dimensions.keys()
		for d in dims:
			if d in exceptions:
				# Override this value with our exception
				v = exceptions[d]
			else:
				# Copy the dimension straight for the source
				v = src.dimensions[d]
			try:
				# Don't try to print v as a %d if d=TSTEP
				#print "Creating dim %s = "%d, v
				dest.createDimension(d, v)
			except IOError as ex:
				print "Cannot create dimension %s"%d, ex
		dest.sync()

	@staticmethod
	def FindFiles(file_format, path=None, date_min=None, date_max=None):
		""" Find the concentration files that match the pattern/format provided

		Keyword Arguments:

		path:*string*
			Path to look for files

		file_format:*string*
		   A format containing wildcards (*) and date indicators,
		   i.e. YYYY, YY, MM, DD or JJJ for Julian day

		date_min:*Datetime*
		   If set, this is the minimum accepted date

		date_max:*Datetime*
		   If set, this is the maximum accepted date

		Returns:

		*list[DataFile]*
		   Returns a list of Datafiles
		"""

		if path == None:
			path = self.inputPath
		if path == None:
			raise ValueError("Must provide a path to search")
		if path[-1] != "/":
			path=path+"/"

		#files=os.listdir( "/mnt/mediasonic/opt/output/morteza/frc-8h-US/" ) # Obviously change this..
		files=os.listdir(path)


		if date_min!=None and not isinstance(date_min, date):
			raise TypeError("Minimum date may either be None or a DateTime")
		if date_max!=None and not isinstance(date_max, date):
			raise TypeError("Maximum date may either be None or a DateTime")

		# Backup
		reg=file_format

		# Year
		reg=re.sub(r'YYYY', '\\d{4}', reg) 
		reg=re.sub(r'MM', '\\d{2}', reg) 
		reg=re.sub(r'DD', '\\d{2}', reg) 
		reg=re.sub(r'JJJ', '\\d{3}', reg) 
		reg=re.sub(r'\*', '.*', reg) 

		#print "RE: %s"% reg
		cfiles=[]

		for f in files:
			#print "Does %s match?"%f
			if re.search(reg, f):
				#print "%s matches"%f
				df=DataFile(f, path=path, file_format=file_format)
				df.loadDate()

				#is_between_date = df.date>=date_min and df.date<=date_max
				#print "df.date=%s, between [%s %s]?=%r type(df.date)=%s, type(date_min)=%s"%(df.date, date_min, date_max, is_between_date, type(df.date), type(date_min))

				if (date_min == None and date_max == None) or ( (date_min != None and df.date >= date_min) and (date_max != None and df.date <= date_max) ):
					#print "File added"
					cfiles.append(df)

		#return sorted(cfiles, key=lambda student: .age)
		return sorted(cfiles)

	def loadConcentrationFiles(self, files):
		""" Load concentration files.  The old architecture assumed each file
		    could be processed individually, but time zones and time averaging
		    requires that "yesterday" and/or "tomorrow" are required, so now
		    all files are loaded into the object and then iterated on.

		Keyword Arguments:

		files:*Datafile[]
		   The concentration files to use.  It is assumed that
		   file[n-1], file[n] and file[n+1] are continuous
		   (yesterday, today and tomorrow.)  If there are gaps
		   then the end results will be wrong, as averaging would
		   not have been aware of the gaps.
		"""

		self.conc_files = files


	@staticmethod
	def prepareTimeVectorForAvg(vecs, timezone=0, winLen=8, forwards_or_backwards = default_averaging_direction, debug=False):
		""" Prepare a vector for a sliding window.  Given a vector of values
		for three days (yesterday, today and tomorrow), this considers the direction of
		your averaging (8 hours forwards, backwards, or maybe central one day) and
		outputs a vector that can be used for averaging.

		So, given::

		   vecs={-1: yesterday, 0: today, 1: tomorrow} # where,
		   yesterday=[0 ... 0] (24 elements)
		   today    =[0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 1 0 ... 0] (24 elements)
		   tomorrow =[0 ... 0] (24 elements)

		   winLen=8
		   timezone=0
		   forwards_or_backwards=forwards

		This function will then return a 32 element vector consisting of [today tomorrow[0:8]]

		If however *timezone* = -5, then this function will return::

		   [yesterday[-5:] today tomorrow[0:3]

		Keywords:

		vec*dict[[]:*numpy.ndarray*
		   keys are the offset of the day (so, -1 is yesterday), values are 24 element vectors starting at index 0
		timezone:*int*
		   Shift the vector to reflect your timezone
		winLen:*int*
		   the size of the window
		forwards_or_backwards:*bool*
		   True means set it up for a forward avg

		debug:*bool*
		   Temporary variable that outputs the vector colour coded. Green for parts from yesterday, blue for today and orange for tomorrow

		Returns:

		*ndarray((24+winLen), dtype=float32)*
		   The values to be averaged adjusted for whether we're calculating
		   forwards or backwards.
		"""

		for d,v in vecs.iteritems():
			if len(v) != 24:
				raise ValueError("Vector %d has an invalid length.  Vectors must have a length of %d, given len=%d"%(d, Forcing.dayLen, len(yesterday)))

		data=np.concatenate(vecs.values(), axis=1)
		#Forcing.debug("Combined Data:\n%s "%', '.join(map(str, data)))

		if timezone > 0:
			raise NotImplementedError("Error!  Positive timezones are not yet implemented.")

		# Calculate how many days were given before "today"
		days_before_today = 0
		for d in vecs.keys():
			if d<0:
				days_before_today=days_before_today + 1
			else:
				break

		if forwards_or_backwards:
			# Moving forward

			# Index should start at today.  So, 24*number of vectors before day 0
			idx_start=days_before_today*Forcing.dayLen

			# Ending index must span at least 1 day + winLen
			idx_end = idx_start+Forcing.dayLen+winLen-1
		else:
			# Moving backward

			# We need all of today, plus a window length's into yesterday
			idx_start=(days_before_today*Forcing.dayLen) - winLen+1
			idx_end = (days_before_today+1)*Forcing.dayLen

		#Forcing.debug("idx_start=%d, idx_end=%d, diff=%d"%(idx_start, idx_end, idx_end-idx_start))

		# Apply time zone  i.e. Montreal is -5
		if math.floor(timezone) != timezone:
			raise NotImplementedError("Timezone must be an integer.  Fractional timezones (e.g. Newfoundland) is not yet supported.")
		idx_start = int(idx_start - timezone)
		idx_end   = int(idx_end   - timezone)

		if idx_end > len(data):
			raise ValueError("Averaging window is outside of the three day data that was predicted!  Cannot continue.")

		#print "idx_start=%d , idx_end=%d, diff=%d, timezone=%d"%(idx_start, idx_end, idx_end-idx_start, timezone)

		vec = data[idx_start:idx_end]

		###
		# Debug stuff
		###

		if debug:

			# Colours
			b = bc()

			# Create coloured ints, and re-create the list
			cdata=[]
			for d,ve in vecs.iteritems():
				for val in ve:
					cdata.append(ci(val, getattr(b, "_%s"%DayIterator.clabels[d])))

			# Slice the list the same way
			cvec = cdata[idx_start:idx_end]
			print "Preped vec(len=%d) = %s"%(len(cvec), " ".join(map(str, cvec)))

			same=True
			for idx, val in enumerate(vec):
				if val != cvec[idx].val:
					same=False
					break

			if not same:
				print "%sError!!%s The debug vector does not match the actual returned vector"%(b.red, b.clear)
				print "Act    vec(len=%d) = %s\n"%(len(vec), ' '.join('%4.3f' % v for v in vec))

		###
		# /Debug stuff
		###

		return vec

	@staticmethod
	def calcMovingAverage(data, winLen=8, debug=False):
		""" Calculate a sliding/moving window average over the data and return a 24 element vector of averages.

		The keyword arguments below assume a winLen = 8

		Keywords:

		data:*ndarray((1, 24+winLen), dtype=float32)*
		   Data vector.  If calculating forwards, this should have 24+winLen values.
		   Or in hours: [0 1 2 3 ... 24 25 26 27 28 29 30 31]

		   If calculating backwards, this should have winLen+24 values
		   hours are [-7 -6 -5 -4 -3 -2 -1 0 1 2 3 ... 23]

		winLen:*int*
		   size of window

		Returns:

		*ndarray((1, 24), dtype=float32)*: Float representing TODAY's X hour averages.
		"""

		# The algorithm we use has some options, this is just
		# setting it to move one at a time
		winOverlap=winLen-1

		dl=max(data.shape)
		proper_data_len=Forcing.dayLen + winLen - 1
		if dl != proper_data_len:
			raise RuntimeWarning("Invalid length of data.  Data should be %d elements for an %d-window.  Given %d."%(proper_data_len, winLen, dl))

		if winLen == 1:
			y = data[0:Forcing.dayLen]
		else:
			y = []

			i = 0
			# Loop over 24 hours.  Recall, prepareTimeVectorForAvg already accounted for whether we are counting
			# forwards or backwards
			while i < Forcing.dayLen:
				#print "i=%0.2d"%(i)
				#print "Forward Window[%d:%d] (or hours [%d:%d])\n"%(i,i+winLen, i,i+winLen)
				vec=data[i:i+winLen]
				#print "Stats of [%s]: Count: %d, Sum: %d, Avg: %f"%(', '.join(map(str, vec)), len(vec), sum(vec), float(sum(vec))/winLen)
				y.append(float(sum(data[i:i+winLen]))/winLen)

				i += winLen - winOverlap

		###
		# Debug stuff
		###

		# Hard programmed for 8 hr

		if debug:
			red="\033[91m"
			blue="\033[94m"
			clear="\033[0m"
			outs=""
			max_val = max(y)
			max_idx=y.index(max_val)
			for i in range(0, len(y)):
				if Forcing.default_averaging_direction:
					# Forward
					if i == max_idx:
						outs=outs+"%s"%(red)
					elif i==max_idx+1:
						outs=outs+"%s"%(blue)
					elif i==max_idx+8:
						outs=outs+"%s"%(clear)
				else:
					# Backward
					if i == max_idx:
						outs=outs+"%s"%(red)
					elif i==max_idx+1:
						outs=outs+"%s"%(clear)
					elif i==max_idx-8:
						outs=outs+"%s"%(blue)

				outs = outs + "%5.4f "%(y[i])

			print "Avgs(len=%d): %s"%(len(y), outs)

		###
		# /Debug stuff
		###

		return y

	@staticmethod
	def applyForceToAvgTime(avgs_today, days, winLen=8, timezone = 0, min_threshold = None, forcingValue = None, forwards_or_backwards = default_averaging_direction, debug=False):
		""" Apply the forcing terms to the max X-hour average.

		This function finds the max value in the provided list and writes a 1/winLen to the return vector at the location of the max and for the next (if forward) or last (if backward) winLen-1 elements.

		So, if the max occurred at hour 0, we were calculating forward and winLen=8, and forcingValue=1/8 (or None in this case), the return value would be::

		   [1/8 1/8 1/8 1/8 1/8 1/8 1/8 1/8 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0]

		Note, this method also returns a vector for yesterday and tomorrow, which in this example would be all zeros.

		Keyword Arguments:

		avgs_today:*float32[]*
		   24 element list of X-hour averages.

		days:*int[]*
		   List of relative days that we're working on, e.g. -1 = yesterday, 0 = today, ..

		winLen=8:*int*
		   Length of the window

		timezone=0:*float32*
		   Timezone that this occurs in.  This is required to re-shift the values back into GTM, as they were earlier shifted into local time by prepareTimeVectorForAvg

		min_threshold:*float32*
		   Minimum acceptable value.  If the max is below this, discard it (as if it were 0)

		forcingValue:*float32*
		   Value to insert when forcing.  By default it's 1/winLen

		forwards_or_backwards:*bool*
		   True means set it up for a forward avg

		debug:*bool*
		   Prints out some extra information

		Returns:

# UPDATE THIS
		*dict[yesterday[], today[], tomorrow[]]*:
		   Forcing terms to be applied to yesterday, today and today.  For instance, if the max
		   occurred right in the middle of today, say at noon (and we're calculating forward), then
		   12:00-20:00 will have a value of 1/8 (say winLen==8)
		   The max could happen at the start of end of the day, where it would cause forcing in
		   yesterday or today.. So the outputs (yesterday, tomorrow) can be added to whatever
		   those values happen to be when this is called.
		"""

		# Number of days we have to work with
		ndays=len(days)

		# Calculate how many days were given before "today"
		days_before_today = 0
		for d in days:
			if d<0:
				days_before_today=days_before_today + 1
			else:
				break

		#data=np.concatenate([yesterday, today, tomorrow])
		forcing=np.zeros(Forcing.dayLen*ndays)

		# Set up multi day vector of averages, probably a slow way, but
		# for now will help keep track of indices
		avgs=np.zeros(Forcing.dayLen*ndays)
		# I know it seems like it should be to Forcing.dayLen*2-1... but the
		# way it is is mysteriously correct (seems like python interprets
		# ranges as [start,end[ (non-inclusive on end index))..
		#
		# Anyways, apply todays averages to today
		avgs[Forcing.dayLen*days_before_today:Forcing.dayLen*(days_before_today+1)]=avgs_today

		# Where's the max?
		max_idx=avgs.argmax()
		if min_threshold is not None:
			if avgs[max_idx]<min_threshold:
				# Leave the whole vector as zero
				if debug:
					Forcing.debug("Max value (%f) is below threshold (%f).  Returning zero vectors"%(avgs[max_idx], min_threshold))
				vecs = {}
				for d in days:
					vec[d] = np.zeros((Forcing.dayLen), dtype=np.float32)
				return vecs

		# If there is no threshold, or we haven't hit it, continue on..

		# Reverse the timezone shift
		max_idx = max_idx - timezone

		if forcingValue is None:
# Remember to revert this!
			#forcingValue=float(1)/winLen
			forcingValue=1.0

		if debug:
			print "max_idx=%d\nwinLen=%d\ttimezone=%d\nValue = %f"%(max_idx, winLen, timezone, forcingValue)

		# Apply the forcing term to the appropriate place in the vector
		if forwards_or_backwards == True:
			# Moving forward
			forcing[max_idx:max_idx+winLen] = forcingValue
		else:
			forcing[max_idx-winLen+1:max_idx+1] = forcingValue

		vecs = {}
		i = 0
		for d in days:
			vecs[d] = forcing[Forcing.dayLen*i:Forcing.dayLen*(i+1)]
			i=i+1

		return vecs

class DayIterator(object):
	""" Purpose of this class is to be used by
	produceForcingField to iterate through each day.  All the logic that was in
	that function has been moved here.  This way, it's easier to consider averaging
	direction and timezones.  Before when we were only considering "yesterday",
	"today" and "tomorrow", we were often carrying around an unused day and
	couldn't do 24 hour averaging when timezones were considered. """

	# Averaging directopm
	default_averaging_direction = Forcing.default_averaging_direction

	""" Sets labels for the days.  This is mostly used for debugging.
		labels:*dict*
		   For example, {-1: 'Yesterday', 0: 'Today', 1: 'Tomorrow'}
	"""
	labels={-2: 'Bef Yest', -1: 'Yesterday', 0: 'Today   ', 1: 'Tomorrow', 2: 'Next Day'}
	# Colours.  Defined here so 'yesterday's are always the same colour, for example.
	clabels={-2: 'byesterday', -1: 'yesterday', 0: 'today', 1: 'tomorrow', 2: 'ntomorrow'}

	_idx=None

	# List of relative days.  Typically this is the output of recommendDaysToCarry
	days = []

	def __init__(self, days, forcedays):
		"""

		Keyword Arguments:

		days:*Datafile[]* closed
		   Ordered list of days not yet opened.  (Doesn't matter if they're open, but this method will open and close them

		forcedays:*Datafile[]* closed
		   Ordered list of not yet opened forcing files.  (Doesn't matter if they're open, but this method will open and close them
		"""

		self.inputs=days
		Forcing.debug("Setup DayIterator with files: %s"%(" ".join(map(str, self.inputs))))
		self.outputs=forcedays
		self._idx=0 # Pointing at the first element

	def recommendDaysToCarry(self, timeZoneFld, averaging_window=None, averaging_direction=Forcing.default_averaging_direction):
		""" Determines the range of the timezone, this helps us choose how many files we need, and which files """
		tz_min = timeZoneFld.min()
		tz_max = timeZoneFld.max()

		days = []

		if tz_min > 0 or tz_max > 0:
			raise NotImplementedError( "Positive timezones not yet implemented (min=%d, max=%d)"%(tz_min, tz_max) )

		if math.fabs(tz_min) > math.fabs(tz_max):
			# This is the condition we're used to

			if averaging_direction is True:
				# Spare hours is the number of hours between the extent of the averaging window, and where we loose data in "tomorrow"
				# spare_hours = (48-tz)-(24+winLen)
				# A positive spare_hours means we only need today and tomorrow, otherwise, we need the next day too
				spare_hours = Forcing.dayLen-math.fabs(tz_min)-averaging_window

				if spare_hours > 0:
					# This is the case this was actually built on.  In this case, yesterday is
					# never used
					Forcing.log("Averaging window (%d) is smaller than max time zone shirt (%d).  Using days 0 and 1"%(averaging_window, tz_min))
					days = [0, 1]
				else:
					# Averaging window is too big when we consider our time shift.  So we'll need an extra day

					Forcing.log("Averaging window (%d) is larger than max time zone shirt (%d).  Using days 0,1,2"%(averaging_window, tz_min))
					days = [0, 1, 2]
			else:
				raise NotImplementedError( "not yet implemented" )
		else:
			raise NotImplementedError( "Positive timezones not yet implemented" )

		self.days=days
		return days

#	def setWindowRange(self, r):
#		""" Sets the window range we'll use.  This will likely be the output from the recommendDaysToCarry function.  All this is for is to tell the iterator what days we'll be using, so if we pass any, we know we can safely close them.  This is designed with the iterator only moving forward """
#		self.earliest_window=math.min(r)

	def __getitem__(self, idx):
		""" Returns items at an index relative to our current pointer.  So -1 would be yesterday, or pointer-1

			Idx should also be a range

			Returns: dict(inputs), dict(outputs)
			   Returns two dicts, where the keys are the relative order of the days (or, keys -1 for yesterday, ..)
		"""

		sidx=[]
		for i in idx:
			sidx.append(i+self._idx)

		# Convert to a list
		if type(sidx) is int:
			sidx=[sidx]
		elif type(sidx) is list:
			# good
			pass
		else:
			raise NotImplementedError( "What did you provide?  Makes no sense." )

		inputs={}
		outputs={}

		for i in sidx:
			r = i-self._idx
			if i < 0 or i > len(sidx):
				# Outside of range
				inputs[r]  = None
				outputs[r] = None
			else:
				try:
					self.inputs[i].open()
				except IOError as ex:
					raise IOError( "Error!  Cannot open concentration file %s"%(self.inputs[i].basename) )

				try:
					self.outputs[i].open()
				except IOError as ex:
					raise IOError( "Error!  Cannot open forcing file %s"%(self.outputs[i].basename) )

				inputs[r]  = self.inputs[i]
				outputs[r] = self.outputs[i]

		return inputs, outputs

	@property
	def isFirst(self):
		return self._idx == 0

	@property
	def isLast(self):
		return self._idx == len(self.inputs)-1

	def __len__(self):
		# This has to tell it how many days we can iterate.
		# For example, if we're using "the day after next", this will
		# show one less file that the inputs
		l = len(self.inputs) - (max(self.days))
		return l

	def next(self):
		self._idx = self._idx + 1
		if self._idx > len(self):
			raise ValueError("Iterated out of input files")
		
class ForcingException(Exception):
	pass

class ForcingFileDimensionException(ForcingException):
	pass

class NoSpeciesException(ForcingException):
	pass

class BadSampleConcException(ForcingException):
	pass
