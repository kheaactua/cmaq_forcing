from Scientific.IO.NetCDF import NetCDFFile
from numpy import shape
import os
import numpy as np
import re
import dateutil.parser as dparser
from datetime import *

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
		   fc.outputFormat = 'Forcing.TYPE.YYYYMMDD'
		   f.outputPath=os.getcwd() + 'output/'

		   # Set up time zones
		   f.griddedTimeZone = 'GriddedTimeZoneMask.nc'

		   # Run
		   f.produceForcingField()

	"""

	avgoptions={'AVG_NONE': 'None', 'AVG_MAX': 'Max 1 hr', 'AVG_MAX8': 'Max 8 hr', 'AVG_MAX24': 'Max 24 h', 'AVG_MASK': 'Local Hours'}

	# Concentration files
	conc_files = []

	# Concentration file path
	_conc_path = None

	# True for forward, false for backward.  I'm told
	# the standard is forward
	default_averaging_direction = True

	# Obvious, but used a lot
	dayLen=24

	# Output file name format
	_outputFormat = 'Forcing.TYPE.YYYYMMDD'

	# Output path
	_outputPath = None

	# Layers to process
	_layers = []

	# Gridded timezone file.  Ideally, in the future we'll be able to figure these
	# out with shape files, rather than having a pre-gridded file
	_griddedTimeZone = None
	# The actual gridded field
	griddedTimeZoneFld = None

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
			self.ni = dims['ni']
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
		self.space=np.ones((self.nj,self.ni))

		# Set up default timezones incase they aren't given.  Set everything
		# to 0
		self.griddedTimeZoneFld = np.zeros((self.nj, self.ni))

		# Empty set of concentration files
		self.conc_files = []
		self.conc_path  = None

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


		conc=NetCDFFile(filename, 'r')
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

	# Not a good use of a property, but it's my first one
	@property
	def conc_path(self):
		""" Getter for the concentration path """
		return self._conc_path
	@conc_path.setter
	def conc_path(self, path):
		""" Path that'll be used to look for concentration files """
		self._conc_path = path

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
	def outputFormat(self):
		return self._outputFormat
	@outputFormat.setter
	def outputFormat(self, fmt):
		""" Format for output files.  See generateForceFileName for notes on format """
		self._outputFormat=fmt

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
		self._griddedTimeZone = path

		# Open the file and load in the field
		try:
			tz = NetCDFFile(path, 'r')
		except IOError as ex:
			print "Error!  Cannot open gridded timezone file %s"%(path)
			raise

		var = tz.variables['LTIME']
		# The field should be at t=0,k=0
		fld = var.getValue()[0,0]
		#print "shape(timezones) = ", fld.shape

		if fld.shape != (self.nj, self.ni):
			raise ValueError("Error.  Gridded time zone file has a different domain than input concentration files.  Current domain=%s, timezone domain=%s"%(str(fld.shape), str( (self.ni, self.nj) ) ))

		self.griddedTimeZoneFld=fld


	# Should replace this setter with a property
	def setAveraging(self, avg):
		""" Set averaging option, e.g. max 8-hr, etc

		Keyword Arguments:

		avg:*string*
		   Any of the self.avgoptions values
		"""

		for key,val in self.avgoptions.items():
			if avg==val:
				self.averaging=key

		# Should probably raise an exception if it's not found		


	def maskTimes(self, mask):
		""" Set time mask

		Keyword arguments:

		mask
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
			sekf._layers[i] = mask[i]-1

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

		try:
			f=NetCDFFile(maskf, 'r')
			var = f.variables[variable]
			mask=var.getValue()[0][0]
			self.space = mask==value
			f.close()
		except Exception as ex:
			print "Something went wrong masking space\n", ex
			raise



#	def produceForcingField(self, progressWindow = None, progress_callback = None):
	def produceForcingField(self, progress_callback = None, dryrun = False):
		""" Iterate through concentration files, create forcing output netcdf files, prepare them, and call the writing function

		Keyword Arguments:

		progressWindow:*ProgressFrame*

		progress_callback:*function*
		   Used to send back progress information.
		   It'll call::

		     progressWindow.progress_callback(percent_progress:float, current_file:Datafile)

		"""

		print "Processing... Domain=(ns=%d, nt=%d, nk=%d, ni=%d, nj=%d)"%(len(self.species), self.nt, self.nk, self.ni, self.nj)

		#
		# Iterate through concentration files
		conc_yest  = None
		conc_today = None
		conc_tom   = None

		force_yest  = None
		force_today = None
		force_tom   = None

		# In order to keep the code below clean, all the files are
		# initiate in this first loop
		conc_files = []
		force_files = []
		for conc_datafile in self.conc_files:
			force_path=self.generateForceFileName(conc_datafile)
			conc_files.append(conc_datafile.path)
			force_files.append(force_path)

			# Open the concentration file
			try:
				conc = NetCDFFile(conc_datafile.path, 'r')
			except IOError as ex:
				print "Error!  Cannot open concentration file %s"%(conc_datafile.name)
				raise

			# Initialize the file
			try:
				force = self.initForceFile(conc, force_path)
			except IOError as ex:
				print "Error! %s already exists.  Please remove the forcing file and try again."%force_path
				# HACK TEMP, remove
				os.remove(force_path)

			# Clean up and close the files
			conc.close()
			force.close()
		# End of initiation loop

		# List of full file paths
		conc_files  = [None] + conc_files  + [None]
		force_files = [None] + force_files + [None]

		#print "Conc_datafiles: %s"%(" ".join(map(str, self.conc_files)))
		#print "Conc_files: ", conc_files

		# Index of concentration file
		for conc_idx in range(1, len(conc_files)-1):

			#print "conc_idx = %d"%conc_idx

			if not dryrun:

				# Grab the files
				conc_yest_path = conc_files[conc_idx-1]
				force_yest_path = force_files[conc_idx-1]

				conc_today_path = conc_files[conc_idx]
				force_today_path = force_files[conc_idx]

				conc_tom_path = conc_files[conc_idx+1]
				force_tom_path = force_files[conc_idx+1]

				# Close files that we're done with
				if conc_yest is not None:
					# This is now the day before yesterday, close it.
					conc_yest.close()
					#print "Closed %s"%conc_yest
					conc_yest = None
					force_yest.close()
					force_yest = None

				# Open the files
				if conc_yest_path != None:
					# Shift this to yesterday
					conc_yest = conc_today
					force_yest = force_today

				if conc_tom == None and conc_yest_path == None:
					# First time around
					conc_today  = NetCDFFile(conc_today_path, 'r')
					force_today = NetCDFFile(force_today_path, 'a')
				elif conc_tom != None:
					# Not the first or last
					# Shift tomorrow to today
					conc_today = conc_tom
					force_today = force_tom

				if conc_tom_path != None:
					conc_tom  = NetCDFFile(conc_tom_path, 'r')
					force_tom = NetCDFFile(force_tom_path, 'a')
				else:
					conc_tom = None
					force_tom = None

				## What days are we working with?
				#print "\n"
				#print "Yesterday: ", force_yest
				#print "Today:     ", force_today
				#print "Tomorrow:  ", force_tom
				#print "\n"

				# Generate a list[yesterday, today, tomorrow]
				# where every "day" is a list with species indices (from self.species) for
				# keys, and values of the domain (ni*nj*nk) for that species
				flds = self.generateForcingFields(conc_idx=conc_idx,
				   conc_yest=conc_yest,   conc_today=conc_today,   conc_tom=conc_tom,
				   force_yest=force_yest, force_today=force_today, force_tom=force_tom)

				# Flds[day] is now a ndarray[species][nt][nk][nj][ni]
				idx_s = 0
				for species in self.species:
					#print "Using species index idx_s: %d = species %s"%(idx_s, species)
					species = self.species[idx_s]
					# Get the netcdf variables
					# Get the values
					# add the values
					# write them back to the file

					# Yesterday
					if force_yest is not None:
						var = force_yest.variables[species]
						sum_fld = flds['yesterday'][idx_s] + var.getValue()
						var.assignValue(sum_fld)

					# Today's...
					#print "Today's conc:\n", conc_today.variables[species].getValue()[8]
					#print "Today's force idx_s=%d:\n"%idx_s, flds['today'][idx_s][8]
					var = force_today.variables[species]
					base_fld = var.getValue()
					sum_fld = base_fld + flds['today'][idx_s]
					#print "base_fld.shape: ", base_fld.shape
					#print "sum_fld.shape:  ", sum_fld.shape
					#print "Today's total force:\n", sum_fld[8]
					var.assignValue(sum_fld)


					# Tomorrow
					if force_tom is not None:
						var = force_tom.variables[species]
						var.assignValue(flds['tomorrow'][idx_s] + var.getValue())


					# In species loop
					idx_s = idx_s + 1

				# Sync netcdf files
				if force_yest is not None:
					force_yest.sync()
				force_today.sync()
				if force_tom is not None:
					force_tom.sync()

			# endif dryrun

			# Perform a call back to update the progress
			progress_callback(float(conc_idx)/len(self.conc_files), conc_files[conc_idx])

		# endfor days loop (day1, day2, day3, ...)

		# Probably have to close conc_today


	def initForceFile(self, conc, fpath, species = None):
		""" Initialize a forcing file.
			This method opens the NetCDF file in read/write mode, copies the
			dimensions, copies I/O Api attributes over, and any other common
		    initialization that should be applied to all files

		Keyword Arguments:

		conc:*NetCDFFile*
		   Concentration file to use as a template

		fpath:*string*
		   Path (dir and name) of the forcing file to initialize

		species:*string[]*
		   List of species to create

		Returns:

		NetCDFFile
		   Writable NetCDF File
		"""

		# fpath should not exist
		if os.path.exists(fpath):
			# TEMP, remove
			os.remove(fpath)
			#print "Deleted %s !"%fpath
			#raise IOError("%s already exists."%fpath)

		#print "Opening %s for writing"%fpath
		force = NetCDFFile(fpath, 'a')

		Forcing.copyDims(conc, force)
		Forcing.copyIoapiProps(conc, force)

		if species is None:
			species = self.species

		# Create the variables we'll be writing to
		print "Working on %s"%fpath
		for s in species:
			try:
				var = force.createVariable(s, 'f', ('TSTEP', 'LAY', 'ROW', 'COL'))
				var.assignValue(np.zeros((self.nt,self.nk,self.nj,self.ni), dtype=np.float32))
			except IOError as ex:
				print "Writing error trying to create variable %s in today's file"%s, ex
				print "Current variable names: %s\n"%(" ".join(map(str, force.variables.keys())))

		# Copy over TFLAG
		vsrc = conc.variables['TFLAG']
		force.createVariable('TFLAG', 'i', ('TSTEP', 'VAR', 'DATE-TIME'))
		vdest = force.variables['TFLAG']
		#print "shape(vsrc)=%s, shape(vdest)=%s"%(str(vsrc.shape), str(vdest.shape))
		vdest.assignValue(vsrc.getValue())


		## Fix geocode data
		## http://svn.asilika.com/svn/school/GEOG%205804%20-%20Introduction%20to%20GIS/Project/webservice/fixIoapiProjection.py
		## fixIoapiSpatialInfo

		# Sync the file before sending it off
		force.sync()

		return force

	def generateForcingFields(self, conc_idx):
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
	def copyDims(src, dest):
		""" Copy dimensions from src netcdf file to dest.

		Keyword Arguments:

		src:*NetCDF*
		   NetCDF source file

		dest:*NetCDF*
			NetCDF destinatin file
		"""
		dims = src.dimensions.keys()
		for d in dims:
			v = src.dimensions[d]
			try:
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

		#if path == None:
		#	path = self.conc_path
		if path == None:
			raise ValueError("Must provide a path to search")

		#files=os.listdir( "/mnt/mediasonic/opt/output/morteza/frc-8h-US/" ) # Obviously change this..
		files=os.listdir(path)


		if date_min!=None and not isinstance(date_min, date):
			raise TypeError("Minimum date may either be None or a DateTime")
			#raise TypeError("Minimum date may either be None or a date, currently %s, type(date_min)=%s, isinstance(date_min, date)=%s"%(datetime, type(date_min), isinstance(date_min, date)))
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
			if re.search(reg, f):
				#print "%s matches"%f
				df=DataFile(f, path=path+f, file_format=file_format)
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
	def prepareTimeVectorForAvg(yesterday, today, tomorrow, timezone=0, winLen=8, forwards_or_backwards = default_averaging_direction):
		""" Prepare a vector for a sliding window

		Keywords:

		yesterday[], today[], tomorrow[]
		   24 element vectors starting at index 0
		timezone:*int*
		   Shift the vector to reflect your timezone
		winLen:*int*
		   the size of the window
		forwards_or_backwards:*bool*
		   True means set it up for a forward avg

		Returns:

		*float*[] of length 24+winLen:
		   The values to be averaged adjusted for whether we're calculating
		   forwards or backwards.
		"""

		if len(yesterday)<Forcing.dayLen:
			print yesterday
			raise ValueError("\"yesterday\" vector must be 24 elements long.  Given len=%d"%len(yesterday))
		if len(today)<Forcing.dayLen:
			raise ValueError("\"today\" vector must be 24 elements long.  Given len=%d"%len(today))
		if len(tomorrow)<Forcing.dayLen:
			raise ValueError("\"tomorrow\" vector must be 24 elements long.  Given len=%d"%len(tomorrow))

		data=np.concatenate([yesterday, today, tomorrow])
		#print "Combined Data:\n%s "%', '.join(map(str, data))

		if forwards_or_backwards:
			# Moving forward
			idx_start = Forcing.dayLen
			idx_end = 2*Forcing.dayLen+winLen-1
		else:
			# Moving backward
			idx_start = Forcing.dayLen-winLen+1
			idx_end = 2*Forcing.dayLen

		# Apply time zone  i.e. Montreal is -5
		idx_start = idx_start + timezone
		idx_end   = idx_end   + timezone

		vec = data[idx_start:idx_end]

		return vec

	@staticmethod
	def calcMovingAverage(data, winLen = 8):
		""" Calculate a sliding/moving window average over the data.

		Keywords:
		data
		   Data vector.  If calculating forwards, this should have 24+winLen vals
		   hours are [0 1 2 3 ... 24 25 26 27 28 29 30]
		   If calculating backwards, this should have winLen+24 vals
		   hours are [-3 -2 -1 0 1 2 3 ... 23]
		winLen:*int*
		   size of window

		Returns:

		*float*[]: Float representing TODAY's X hour averages.
		"""

		# The algorithm we use has some options, this is just
		# setting it to move one at a time
		winOverlap=winLen-1

		dl=len(data)
		proper_data_len=Forcing.dayLen + winLen - 1
		if dl != proper_data_len:
			raise RuntimeWarning("Invalid length of data.  Data should be %d elements for an %d-window.  Given %d."%(proper_data_len, winLen, dl))

		y = []

		i = 0
		# Loop over 24 hours.  Recall, prepareTimeVectorForAvg already accounted for wether we are counting
		# forwards or backwards
		while i < Forcing.dayLen:
			#print "i=%0.2d"%(i)
			#print "Forward Window[%d:%d] (or hours [%d:%d])\n"%(i,i+winLen, i,i+winLen)
			vec=data[i:i+winLen]
			#print "Stats of [%s]: Count: %d, Sum: %d, Avg: %f"%(', '.join(map(str, vec)), len(vec), sum(vec), float(sum(vec))/winLen)
			y.append(float(sum(data[i:i+winLen]))/winLen)

			i += winLen - winOverlap

		return y

	@staticmethod
	def applyForceToAvgTime(avgs_today, winLen=8, forwards_or_backwards = default_averaging_direction):
		""" Apply the forcing terms to the max X-hour average.

		Returns:

		*dict[yesterday[], today[], tomorrow[]]*:
		   Forcing terms to be applied to yesterday, today and today.  For instance, if the max
		   occured right in the middle of today, say at noon (and we're calculating forward), then
		   12:00-20:00 will have a value of 1/8 (say winLen==8)
		   The max could happen at the start of end of the day, where it would cause forcing in
		   yesterday or today.. So the outputs (yesterday, tomorrow) can be added to whatever
		   those values happen to be when this is called.
		"""
		   

		#data=np.concatenate([yesterday, today, tomorrow])
		forcing=np.zeros(Forcing.dayLen*3)

		# Set up 3 day vector of averages, probably a slow way, but
		# for now will help keep track of indicies
		avgs=np.zeros(Forcing.dayLen*3)
		# I know it seems like it should be to Forcing.dayLen*2-1... but the way it is
		# is myteriously correct..
		avgs[Forcing.dayLen:Forcing.dayLen*2]=avgs_today

		#print "\n\nTesting.. Averages (len=%d):\n%s "%(len(avgs_today), ', '.join(map(str, avgs_today)))
		#i = 0
		#for v in avgs:
		#	if i%24==0 and i!=0:
		#		print "\n"
		#	print "%2d: %2f"%(i,v)
		#	i = i+1


		# Where's the max?
		#max_val=max(avgs.all())
		#max_idx=avgs.index(max_val)
		max_idx=avgs.argmax()	

		if forwards_or_backwards == True:
			# Moving forward
			forcing[max_idx-1:max_idx+winLen-1] = float(1)/winLen
		else:
			forcing[max_idx-winLen:max_idx] = float(1)/winLen

		yesterday = forcing[0:Forcing.dayLen]
		today = forcing[Forcing.dayLen:Forcing.dayLen*2]
		tomorrow = forcing[Forcing.dayLen*2:Forcing.dayLen*3]
		#yesterday = np.arange(0, 24)
		#today = np.arange(24, 48)
		#tomorrow = np.arange(48, 72)

		return {'yesterday': yesterday, 'today': today, 'tomorrow': tomorrow}

class DataFile(object):
	""" Used encase we want any more info on the input files.
	Currently, name, path and date are all we care about
	"""

	_date = None
	@property
	def date(self):
		return self._date
	@date.setter
	def date(self, dt):
		self._date=dateE(dt.year, dt.month, dt.day)

	# Simply the file name (basename)
	name = None

	# Full path and file name
	path = None

	def __init__(self, filename, path="./", file_format=""):
		self.name=filename
		self.path=path

		# Try to determine the date
		try:
			# Should check if day is first
			day_is_first=None
			try:
				day_is_first = file_format.index('MM') > file_format.index('DD')
			except ValueError:
				# Meh
				day_is_first=None

			#print "Day is first? ", day_is_first
			self.date=dparser.parse(filename, fuzzy=True, dayfirst=day_is_first)
		except ValueError as e:
			print "Manually interpreting %s"%filename

			# YYYYMMDD
			match = re.match(r'.*[^\d]\d{4}\d{2}\d{2}.*', filename)
			if match:
				datestr = re.search(r'[^\d](\d{4})(\d{2})(\d{2})', '\1-\2-\3', filename)
				self.date=dparser.parse(datestr, fuzzy=True, dayfirst=day_is_first)
				return

			# Is it a julian date?
			match = re.match('.*[^\d]\d{4}\d{3}.*', filename)
			print match
			if match:
				raise NotImplementedError( "[TODO] Interpreting Julian date is not yet implemented" )
				return

	def __str__(self):
		return self.name

	# Used for sorting
	def __cmp__(self, other):
		if self._date > other._date:
			return 1
		elif self._date < other._date:
			return -1
		else:
			return 0 

class dateE(date, object):
	""" Extends datetime.datetime by adding juldate operators """

	_julday = -1

	def __init__(self, year, month, day):
		date.__init__(year, month, day)

		self.SetJulDay(year, month, day)

	@property
	def julday(self):
		#date_s = datetime.datetime(self.year, 1, 1)
		#date_e = datetime.datetime(self.year, self.month, self.day)
		#delta = date_s - date_e
		#self.julday = delta.days
		return self._julday
	@julday.setter
	def julday(self, val):
		# Needs to know the year
		raise NotImplementedError( "Not yet implemented" )

	def SetJulDay(self, year, month, day):
		date_s = datetime(self.year, 1, 1)
		date_e = datetime(self.year, self.month, self.day)
		delta = date_s - date_e
		self._julday = delta.days

