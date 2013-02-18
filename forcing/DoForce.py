from Scientific.IO.NetCDF import NetCDFFile
from numpy import shape
from os import listdir
import numpy as np
import re
import dateutil.parser as dparser
from datetime import *

def getForcingObject(ni,nj,nk,nt):
	return ForceOnSpecies(ni,nj,nk,nt)

# Abstract
class Forcing:

	avgoptions=['None', 'Max 1 hr', 'Max 8 hr', 'Max 24 h', 'Local Hours', 'Other']

	def __init__(self,ni,nj,nk,nt):
		"""Initialize Forcing object

		Keyword Arguments:
		ni -- Columns
		nj -- Rows
		nk -- Layers
		nt -- Time steps
		"""

		# Set up full dimensions
		#print "Received ni=%d nj=%d nk=%d nt=%d" % (ni,nj,nk,nt)
		self.ni=ni
		self.nj=nj
		self.nk=nk
		self.nt=nt

		# Initialize vectors, space is done differently
		self.times = range(1,nt);
		self.layers = range(1,nk);

		self.species = []

		# Set a default mask of everything
		self.space=np.ones((ni,nj));

	@staticmethod
	def loadDims(filename):
		"""Load the dimensions from a netcdf file, then close the file

		Keyword Arguments:
		filename -- Netcdf file name

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
	def genForceFileName(conc):
		"""Generate a forcing file name based on the input file name.
			This is used because often CMAQ is cycled, and files are
			named something.ACONC.DATE, and forcing files are expected
			to be in the format something.DATE

		Keyword Arguments:
		conc -- The name of the concentration file

		Returns:
		Forcing file name
		"""

		# Implement this later..
		raise NotImplementedError( "[TODO] Implement this" )
		return 'OutForcing.nc'

	def setAveraging(self, option):
		""" Set averaging option, e.g. max 8-hr, etc """
		
		self.averaging=option

	def maskTimes(self, mask):
		""" Set time mask

		Keyword arguments:
		mask -- vector of times that WILL be used
		"""
		self.times=mask;

	def maskLayers(self, mask):
		""" Set layer mask

		Keyword arguments:
		mask -- vector of the layers that WILL be used
		"""

		self.layers=mask;

	def maskSpace(self, mask):
		""" Set a grid mask

		Keyword arguments:
		mask -- (ni x nj) binary array.  1 means use, 0 means don't use
		"""

		raise NotImplementedError( "Not yet implemented" )

	def setSpecies(self,species):
		""" Specify which species to consider.  How they're considered
			is contingent on the actual forcing function."""

		self.species=species


	def produceForcingField(self, conc_name):
		""" Open files, prepare them, and call the writing function

		Keyword Arguments:
		conc_name  -- File name of concentration.  This has to be changed to a dict[today, tomorrow] so we can handle localtimes
		"""

		# Generate a file name
		force_name=self.generateForceFileName(conc_name)

		conc  = NetCDFFile(conc_name, 'r')
		force = NetCDFFile(force_name, 'w')

		# Copy over dimensions
		self.copyDims(conc, force)

		# Copy all the attributes over
		self.copyIoapiProps(conc, force)
#		# Fix geocode data
#		# http://svn.asilika.com/svn/school/GEOG%205804%20-%20Introduction%20to%20GIS/Project/webservice/fixIoapiProjection.py
#		# fixIoapiSpatialInfo

		# Generate a dict of forcing fields
		flds = self.generateForcingFields(conc);

		# Create the forcing variable in the output file
		for key in flds.keys():
			var = force.createVariable(key, 'f', ('TSTEP', 'LAY', 'ROW', 'COL'))
			# Write forcing field
			var.assignValue(flds[key])

		# Close the file
		force.close()


	def generateForcingFields(self, conc):
		raise NotImplementedError( "Abstract method" )


	def copyIoapiProps(self, src, dest):
		""" Copy I/O Api attributes from NetCDF file into new file

		Keyword Arguments:
		src  -- Open netcdf source file
		dest -- Open netcdf destination file
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
		""" Copy dimensions from src netcdf file to dest """
		dims = src.dimensions.keys()
		for d in dims:
			v = src.dimensions[d]
			dest.createDimension(d, v)
		dest.sync()

	@staticmethod
	def FindFiles(file_format):
		print "[TODO] Fix path..."
		files=listdir( "/mnt/mediasonic/opt/output/morteza/frc-8h-US/" ) # Obviously change this..

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
				cfiles.append(DataFile(f, file_format=file_format))
		return sorted(cfiles)


	@staticmethod
	def prepareTimeVectorForAvg(yesterday, today, tomorrow, timezone=0, winLen=8, forwards_or_backwards = True):
		""" Prepare a vector for a sliding window

		Keywords:
		timezone - Shift the vector to reflect your timezone
		winLen - the size of the window
		forwards_or_backwards - True means set it up for a forward avg
		"""

		daylen=24
		if len(yesterday)<daylen:
			print yesterday
			raise ValueError("\"yesterday\" vector must be 24 elements long.  Given len=%d"%len(yesterday))
		if len(today)<daylen:
			raise ValueError("\"today\" vector must be 24 elements long.  Given len=%d"%len(today))
		if len(tomorrow)<daylen:
			raise ValueError("\"tomorrow\" vector must be 24 elements long.  Given len=%d"%len(tomorrow))

		data=np.concatenate([yesterday, today, tomorrow])
		#print "Combined Data:\n%s "%', '.join(map(str, data))

		if forwards_or_backwards:
			idx_start = 24
			idx_end = 2*daylen+winLen-1
		else:
			idx_start = 24-winLen+1
			idx_end = 2*daylen-1

		# Apply time zone  i.e. Montreal is -5
		idx_start = idx_start + timezone
		idx_end   = idx_end   + timezone

		print "Using indices: [%d, %d]"%(idx_start, idx_end)

		## Old way, can't handle time zones
		#if forwards_or_backwards:
		#	# Forward
		#	vec = np.concatenate([today, tomorrow[0:winLen-1]], axis=1)
		#else:
		#	# Backward
		#	l = len(yesterday)
		#	vec = np.concatenate([yesterday[l-winLen+1:l], today], axis=1)

		vec = data[idx_start:idx_end]

		return vec

	@staticmethod
	def calcMovingAverage(data, winLen = 8, forwards_or_backwards = True):
		""" Calculate a sliding/moving window average over the data.

		Keywords:
		data - Data vector.  If calculating forwards, this should have 24+winLen vals
		                     hours are [0 1 2 3 ... 24 25 26 27 28 29 30]
		                     If calculating backwards, this should have winLen+24 vals
		                     hours are [-3 -2 -1 0 1 2 3 ... 23]
		winLen - int size of window
		"""

# SHould modify this to use forwards_or_backwards

		hours_in_day=24
		# The algorithm we use has some options, this is just
		# setting it to move one at a time
		winOverlap=winLen-1


#		# indexes for going data, loop should iterate only 24 times
		if True:
#		if forwards_or_backwards:
			# Calculating forward
			idx_start = 0
#		else:
#			# Calculating backwards
#			idx_start = 0

		# Our end index
		idx_end   = idx_start+hours_in_day


		dl=len(data)
		proper_data_len=hours_in_day + winLen - 1
		if dl != proper_data_len:
			raise RuntimeWarning("Invalid length of data.  Data should be %d elements for an %d-window.  Given %d."%(proper_data_len, winLen, dl))

		y = []

		i = idx_start
		j = 0
		#print "Data: ", data
		while i < idx_end:
			#print "i=%0.2d, j=%0.2d"%(i, j)
			if True:
#			if forwards_or_backwards:
				#print "Forward Window[%d:%d] (or hours [%d:%d])\n"%(i,i+winLen, i,i+winLen)
				vec=data[i:i+winLen]
				#print "Stats of [%s]: Count: %d, Sum: %d, Avg: %f"%(', '.join(map(str, vec)), len(vec), sum(vec), float(sum(vec))/winLen)
				y.append(float(sum(data[i:i+winLen]))/winLen)
#			else:
#				print "Backward Window[%d:%d] (or hours [%d:%d])\n\n"%(i-winLen,winLen,i,2*winLen)
#				y[j] = sum(data[i-winLen:winLen])/winLen
			
			i += winLen - winOverlap
			j=j+1

		return y

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
