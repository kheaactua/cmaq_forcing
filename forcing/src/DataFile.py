from __future__ import print_function
import dateutil.parser as dparser
from datetime import date
from extendedClasses import dateE
import os, re

# Which NetCDF library are we using?
netcdf4=False
if False:
	try:
		# On khea (well, ubuntu 12.10), export LD_LIBRARY_PATH=/usr/lib/TEMP_HACK_MATT
		from netCDF4 import Dataset
		netcdf4=True
	except ImportError:
		from Scientific.IO.NetCDF import NetCDFFile
else:
	from Scientific.IO.NetCDF import NetCDFFile


print("Using netcdf4? %r"%netcdf4)

class DataFile(object):
	""" VERY SIMPLE wrapper for NetCDF files, with this we can use
	either library (Scientific.IO.NetCDF or Netcdf4

	http://www-pord.ucsd.edu/~cjiang/python.html

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

	# Mode
	mode = 'r'

	# Is Open
	_isOpen = False

	# Our open file, this is a group if we're using netcdf4
	openFile = None

	# dimension wrapper for netcdf4 so that dimensions return ints
	_dimw = None

	# Variable wrapper
	_varw = None

	def __init__(self, filename, path="", mode="r", file_format="", open=False):
		"""

		Keyword Arguments:

		filename:*string*

		path:*string*
		   Path to the file.  Only use this if only a file name was provided to filename

		file_format:*string*
		   Does the file name have a format that we could read the date from?

		mode:*string*"
		   r=read, w=write

		open:*bool*
		   Open right away?
		"""
		self.name=filename
		self.file_format=file_format

		# Save full path
		if len(path):
			self.path="%s%s%s"%(path, os.sep, filename)
		else:
			self.path = filename
			#"%s%s%s"%(os.getcwd(), os.sep, filename)
		self.path = re.sub("%s%s+"%(os.sep, os.sep), os.sep, self.path)

		self.mode=mode

		#print("Initialized, file: %s"%(os.path.basename(self.path)))

		if open:
			self.open()

	@property
	def basename(self):
		return os.path.basename(self.path)

	def open(self):
		#print("Opening %s"%(self.path))
		if self._isOpen:
			return

		try:
			if netcdf4 == False:
				self.openFile=NetCDFFile(self.path, self.mode)
				#print("Open file %s"%self.basename, self.openFile)
			else:
				#raise NotImplementedError( "NetCDF4 not yet implemented" )
				# This will return a rootgroup
				self.openFile = Dataset(self.path, self.mode, format="NETCDF3_CLASSIC")

			self._isOpen=True
		except RuntimeError as e:
			print("[NetCDF4: %r]: Could not open %s (mode=%s)"%(netcdf4, self.path, self.mode))
			raise e

	def close(self):
		#print("Closing %s"%self.path)
		if not self._isOpen:
			return

		self.openFile.close()
		self._isOpen=False
		self._dimw=None
		self._varw=None

	def __dell__(self):
		if self._isOpen:
			self.close()

# Not ready to implement these yet.  Pretty sure they'd have to be
# on a seperate class
#	def __enter__(self):
#		self.open()
#
#	def __exit__(self, type, value, traceback):
#		self.close()

	def createDimension(self, dim, val):
		if self._isOpen == False:
			raise IOError( "File not open!" )

		# Happens to be the same for NetCDF 3 and 4
		self.openFile.createDimension(dim, val)

	def createVariable(self, name, type, dims):
		if self._isOpen == False:
			raise IOError( "File not open!" )

		# Happens to be the same for NetCDF 3 and 4
		return self.openFile.createVariable(name, type, dims)

	@property
	def variables(self):
		if self._varw is None:
			self._varw = Netcdf4VariableWrapper(self.openFile.variables, netcdf4)
		return self._varw

	@property
	def dimensions(self):
		if not self._isOpen:
			raise IOError("File not open!")

		if netcdf4 == False:
			return self.openFile.dimensions
		else:
			if self._dimw is None:
				self._dimw = Netcdf4DimWrapper(self.openFile.dimensions)
			return self._dimw

#	def __getitem__(self, key):
#		if self._isOpen == False:
#			raise IOError( "File not open!" )
#
#		# Interfaces are the same
#		return self.openFile['key']

	def sync(self):
		if netcdf4 == False:
			self.openFile.sync()
		# There is no sync for netcdf 4 files it seems

	def loadDate(self):
		""" Attempts to load the date.  All attempts are made on the file
		    name first, and if that fails, then it'll look for the SDATE
		    property """

		# Try to determine the date

		# First, does the file format expect a date string in it?
		match_y = re.match("YYYY", self.file_format)
		match_m = re.match("MM", self.file_format)
		match_d = re.match("DD", self.file_format)
		match_j = re.match("JJJ", self.file_format)
		if (match_y and match_j) or (match_y and match_m and match_d):
			try:
				# Should check if day is first
				day_is_first=None
				try:
					day_is_first = self.file_format.index('MM') > self.file_format.index('DD')
				except ValueError:
					# Meh
					day_is_first=None

				#print "Day is first? ", day_is_first
				self.date=dparser.parse(self.path, fuzzy=True, dayfirst=day_is_first)
			except ValueError as e:
				print("Manually interpreting %s"%self.path)

				# YYYYMMDD
				match = re.match(r'.*[^\d](\d{4})(\d{2})(\d{2}).*', self.path)
				if match:
					self.date = dateE(int(match.group(1)), int(match.group(2)), int(match.group(3)))
					return

				# Is it a julian date?
				match = re.match('.*[^\d](\d{4})(\d{3}).*', self.path)
				#print(match)
				if match:
					# Copy juldate reader from Validator..
					year = int(match.group(1))
					jday = int(match.group(2))

					date = datetime.date(year, 1, 1)
					days = datetime.timedelta(days=jday-1) # -1 because we started at day 1
					date=date+days
		
					self.date = dateE(match.group(1), date.month, date.day)

					raise NotImplementedError( "[TODO] Not yet tested" )
					return
		else:
			# Check sdate..
			was_closed=False
			if not self._isOpen:
				was_closed=True
				self.open()

			sdate=str(getattr(self.openFile, 'SDATE'))

			# Sometimes sdate has brackets around it
			if sdate[0] == "[" and sdate[-1] == "]":
				sdate=sdate[1:-1]
			year=int(sdate[:4])
			jday=int(sdate[4:])

			self.date = dateE.fromJulDate(year, jday)

			if was_closed:
				self.close()

	def __str__(self):
		return self.name

	# Used for sorting
	def __cmp__(self, other):
		if other is None:
			raise ValueError("Cannot compare DataFile to None.  Did you mean to check it's type?")

		if self._date > other._date:
			return 1
		elif self._date < other._date:
			return -1
		else:
			return 0 

	@staticmethod
	def test():
		""" Test the class """

		d = DataFile('timezones.nc', path='basic_concentrations/', mode="r")
		d.open()
		print(d)
		print("Dimensions: ", d.dimensions)
		ni = d.dimensions['ROW']
		print("type(ni) = %s"%type(ni))
		#print("ni = %d"%len(ni))
		#print(dir(ni))
		v=d.variables['LTIME'][0][0]
		print(v)
		#print(v.getValue())
		d.close()

		d = DataFile('timezones.nc', path='basic_concentrations/', mode="r")

		## Create a file
		#d = DataFile('delete_me.nc', mode="w", open=True)


class Netcdf4DimWrapper:
	def __init__(self, dimensions):
		""" Imput should be a dict of netCDF4.Dimension objects """
		self._dims=dimensions

	def __getitem__(self, key):
		# Return either an int or none
		if self._dims[key].isunlimited():
			return None
		else:
			return len(self._dims[key])

	def keys(self):
		return self._dims.keys()

class Netcdf4VariableWrapper:
	netcdf4=False
	def __init__(self, variables, netcdf4):
		""" Input should be a dict of netCDF4.Variables objects """
		self._vars=variables

	def __getitem__(self, key):
		return self._vars[key]

	def assignValue():
		raise RuntimeError("Avoid using assignValue");

	def getValue():
		raise RuntimeError("Avoid using getValue");

# Test
#DataFile.test()
