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
		return 'OutForcing.nc'

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


	def produceForcingField(self, conc_name, force_name):
		""" Open files, prepare them, and call the writing function

		Keyword Arguments:
		conc_name  -- File name of concentration
		force_name -- File name of forcing file
		"""

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
				cfiles.append(DataFile(f), file_format=file_format)
		return sorted(cfiles)

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
				day_is_first = file_format.index('MM') > file_format
			except ValueError:
				# Meh
				day_is_first=None

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

			#
			# This won't work
#			# Mask a copy of the string with the file format
#			# so we get conc.YYYYJJJ or something
#			# and then use the positions of YYYY in that string
#			# in the original string to extract the date info.
#
#			orig=filename
#			mask=filename
#
#			# Ideally, the filename doesn't have YY in it..
#			mask=re.sub(r'YYYY', '(\\d{4})', mask) 
#			mask=re.sub(r'MM', '(\\d{2})', mask) 
#			mask=re.sub(r'DD', '(\\d{2})', mask) 
#			mask=re.sub(r'JJJ', '(\\d{3})', mask) 
#
#			
#			
#
#			year   = None
#			month  = None
#			day    = None
#			julday = None
#			if len(file_format):
#				match = re.search(r'YYYY', mask)
#				if match:
#					idx=mask.index('YYYY')
#					year=orig[idx:idx+4]
#					print "Found year"
#				match = re.search(r'YY', filename)
#				if match:
#					print "[TODO]: Document this YY thing"
#					idx=mask.index('YY')
#					year=orig[idx:idx+2]
#					if year<50:
#						year+=2000
#					else:
#						year+=1900
#
#					print "Year: %d\n"%year
#
#				match = re.search(r'JJJ', filename)
#				if match:
#					idx=mask.index('JJJ')
#					julday=orig[idx:idx+3]
#				else:
#					match = re.search(r'MMM', filename)
#					if match:
#						idx=mask.index('MMM')
#						month=orig[idx:idx+3]
#						print "[TODO]: convert to numeric"
#					else:
#						match = re.search(r'MM', filename)
#						if match:
#							idx=mask.index('MM')
#							month=orig[idx:idx+2]
#
#					match = re.search(r'DD', filename)
#					if match:
#						idx=mask.index('DD')
#						day=orig[idx:idx+2]
#
#				if year is not None:
#					if julday is not None:
#						raise NotImplementedError( "[TODO] Interpreting Jul date is not yet implemented" )
#					else:
#						self.date=datetime.datetime(year, month, day, 0, 0, 0)


	def __str__(self):
		return self.name
