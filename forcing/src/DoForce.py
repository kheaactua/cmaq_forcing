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
class Forcing:
	""" Class set up to take in all required inputs and generate forcing fields.

	    This class can handle different time averaging, and layer, [2d] domain, species
	    and time masks.  This class is designed to be used with a CLI interface of a wxpython GUI.

		Specific forcing functions are implemented by inheriting this class.

		Usage example::

		   f = ForceOnAverageConcentration()
		   f.loadDims(sample_concentration_file_name)
		   f.loadConcentrationFiles(concentration_files)
		   f.maskLayers(layers_to_use)
		   f.setAveraging("Max 8 hr")
		   f.setSpecies("O3")
		   f.produceForcingField()

	"""

	avgoptions=['None', 'Max 1 hr', 'Max 8 hr', 'Max 24 h', 'Local Hours', 'Other']

	# Concentration files
	conc_files = []

	# Concentration file path
	conc_path = None

	# True for forward, false for backward
	default_averaging_direction = False

	# Obvious, but used a lot
	dayLen=24

	def __init__(self,ni=0,nj=0,nk=0,nt=0):
		""" Initialize Forcing object.  The inputs will typically be
			read from a sample config file using loadDims(), so these
		    inputs may be left blank.

		Keyword Arguments:

		ni:*int*
		   Columns

		nj:*int*
		   Rows

		nk:*int*
		   Layers

		nt:*int*
		   Time steps
		"""

		# Set up full dimensions
		#print "Received ni=%d nj=%d nk=%d nt=%d" % (ni,nj,nk,nt)
		self.ni=ni
		self.nj=nj
		self.nk=nk
		self.nt=nt

		# Initialize vectors, space is done differently
		self.times = range(1,nt)
		self.layers = range(1,nk)

		self.species = []

		# Set a default mask of everything
		self.space=np.ones((ni,nj))

		# Empty set of concentration files
		self.conc_files = []
		self.conc_path  = None


	@staticmethod
	def loadDims(filename):
		""" Load the dimensions from a netcdf file, then close the file

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

	@staticmethod
	def generateForceFileName(conc):
		""" Generate a forcing file name based on the input file name.
			This is used because often CMAQ is cycled, and files are
			named something.ACONC.DATE, and forcing files are expected
			to be in the format something.DATE

		Keyword Arguments:

		conc:*Datafile*
		   Datafile of the concentration file

		Returns:
		   Forcing file name
		"""

		# Implement this later..
		raise NotImplementedError( "[TODO] Implement this" )

		if not isinstance(conc, Datafile):
			raise TypeError("Concentration input must be a data file")

		return 'OutForcing.nc'

	def setPath(self, path):
		""" Path that'll be used to look for concentration files """
		self.conc_path = path

	def setAveraging(self, avg):
		""" Set averaging option, e.g. max 8-hr, etc

		Keyword Arguments:

		avg:*string*
		   Any of the self.avgoptions values
		"""
		
		self.averaging=avg

	def maskTimes(self, mask):
		""" Set time mask

		Keyword arguments:

		mask
		   vector of times that WILL be used
		"""
		self.times=mask;

	def maskLayers(self, mask):
		""" Set layer mask

		Keyword arguments:

		mask
		   vector of the layers that WILL be used
		"""

		self.layers=mask;

	def maskSpace(self, mask):
		""" Set a grid mask

		Keyword arguments:

		mask:*(ni x nj) binary array*
		   1 means use, 0 means don't use
		"""

		raise NotImplementedError( "Not yet implemented" )

	def setSpecies(self,species):
		""" Specify which species to consider.  How they're considered
			is contingent on the actual forcing function."""

		self.species=species


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

		#
		# Iterate through concentration files

		# Index of concentration file
		i = 0
		for conc in self.conc_files:

			# Generate a file name
			force_name=self.generateForceFileName(conc.name)

			if not dryrun:
				conc  = NetCDFFile(conc.name, 'r')
				force = NetCDFFile(force_name, 'w')

				# Copy over dimensions
				self.copyDims(conc, force)

				# Copy all the attributes over
				self.copyIoapiProps(conc.name, force)
		#		# Fix geocode data
		#		# http://svn.asilika.com/svn/school/GEOG%205804%20-%20Introduction%20to%20GIS/Project/webservice/fixIoapiProjection.py
		#		# fixIoapiSpatialInfo

				# Generate a dict of forcing fields
				flds = self.generateForcingFields(conc_idx=i);

				# Create the forcing variable in the output file
				for key in flds.keys():
					var = force.createVariable(key, 'f', ('TSTEP', 'LAY', 'ROW', 'COL'))
					# Write forcing field
					var.assignValue(flds[key])

			
			# Perform a call back to update the progress
			progress_callback(float(i)/len(self.conc_files), conc)

			# Close the file
			force.close()

			i=i+1

			# TEMP HACK
			if i<2 or i>2:
				break


	def generateForcingFields(self, conc_idx):
		""" Generate a forcing field.  *Abstract*

		Keyword Arguments:

		conc_idx:*int*
		   Index of the concentration file in self.conc_files

		"""
		raise NotImplementedError( "Abstract method" )


	def copyIoapiProps(self, src, dest):
		""" Copy I/O Api attributes from NetCDF file into new file

		Keyword Arguments:

		src:*string*
		   Open netcdf source file
		dest:*string*
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
			else:
				print attr, "does not exist in this NetCDF file %s." % src

		dest.sync()

	def copyDims(self, src, dest):
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
			dest.createDimension(d, v)
		dest.sync()

	@staticmethod
	def FindFiles(path, file_format, date_min=None, date_max=None):
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

		#files=os.listdir( "/mnt/mediasonic/opt/output/morteza/frc-8h-US/" ) # Obviously change this..
		files=os.listdir(path)


		if date_min!=None and not isinstance(date_min, datetime):
			raise TypeError("Minimum date may either be None or a DateTime")
		if date_max!=None and not isinstance(date_max, datetime):
			raise TypeError("Maximum date may either be None or a DateTime")

		# Backup
		reg=file_format

		# Year
		reg=re.sub(r'YYYY', '\\d{4}', reg) 
		reg=re.sub(r'MM', '\\d{2}', reg) 
		reg=re.sub(r'DD', '\\d{2}', reg) 
		reg=re.sub(r'JJJ', '\\d{3}', reg) 
		reg=re.sub(r'\*', '.*', reg) 

		print "RE: %s"% reg
		cfiles=[]

		for f in files:
			if re.search(reg, f):
				#print "%s matches"%f
				df=DataFile(f, file_format=file_format)
				if date_min == None and date_max == None:
					cfiles.append(df)
				elif (date_min != None and df.date > date_min) or (date_max != None and df.date < date_max):
					cfiles.append(df)

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

		yesterday = forcing[0:Forcing.dayLen-1]
		today = forcing[Forcing.dayLen:Forcing.dayLen*2-1]
		tomorrow = forcing[Forcing.dayLen*2:]

		return {'yesterday': yesterday, 'today': today, 'tomorrow': tomorrow}

class DataFile:
	""" Used encase we want any more info on the input files.
	Currently, name, path and date are all we care about
	"""

	name = None
	date = None
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

			print "Day is first? ", day_is_first
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
