from numpy import shape
#from Scientific.IO.NetCDF import NetCDFFile
from DataFile import DataFile
import numpy as np
import datetime

# Validate inputs against the base concentration file
class ForcingValidator:

	LAY_SURFACE_NAME='Surface'

	ni=None
	nj=None
	nk=None
	ns=None
	nt=None

	conc = None

	def __init__(self,filename):
		self.conc=DataFile(filename, mode='r', open=True)

		self.ni = self.conc.dimensions['COL']
		self.nj = self.conc.dimensions['ROW']
		self.nk = self.conc.dimensions['LAY']

		# TSTEP is unlimited, so python has problems reading it
		# So instead we'll examine the shape of a variable
		# Let's assume TFLAG exists
		shape = self.conc.variables['TFLAG'].shape
		# This first element is TSTEP
		self.nt = shape[0]

		ns = len(self.conc.variables.keys())


	def close(self):
		try:
			self.conc.close()
		except IOError:
			# nothing.. it's closed.
			self.conc = None

	def __del__(self):
		self.close()

	def changeFile(self, newfile):
		self.conc.close();
		self.conc=DataFile(newfile, mode='r', open=True)

	def getDate(self):
		""" Again, not a validator just a getter.  Useful to know the date
		    of the concentration file being used.  Since we're using an
		    I/O Api file, we'll look at the SDATE attribute.

		Returns:

		datetime
		"""

		# Get the sdate, in the format YYYYJJJ
		if not hasattr(self.conc, 'SDATE'):
			raise IOError("Sample concentration file does not seem to be a proper I/O Api file.")

		sdate=str(getattr(self.conc, 'SDATE'))
		# Sometimes sdate has brackets around it
		if sdate[0] == "[" and sdate[-1] == "]":
			sdate=sdate[1:-1]
		year=int(sdate[:4])
		jday=int(sdate[4:])

		date = datetime.date(year, 1, 1)
		days = datetime.timedelta(days=jday-1) # -1 because we started at day 1
		date=date+days

		return date

	def getLayers(self):
		"""Return a list of layers.  This isn't really a validator, but
		it shares a lot of the functionality.  Assumes that there's
		always a ground layer.

		Returns:
		list of layers
		"""

		num_layers = self.conc.dimensions['LAY']
		layers=[self.LAY_SURFACE_NAME]
		for l in range(2, num_layers):
			layers+=str(l)
		return layers

	def getTimes(self):
		"""Return a list of times(hours).  This isn't really a validator, but
		it shares a lot of the functionality.  Assumes that there's
		always a ground layer.

		Returns:
		list of times
		"""

		shape = self.conc.variables['TFLAG'].shape
		nt = shape[0]

		times=list(xrange(nt))
		# Cut off the 25th time
		for t in range(0, nt-1):
			times[t]=str(t)
		return times

	def getSpecies(self):
		"""Return a list of species.  This isn't really a validator, but
		it shares a lot of the functionality

		Returns:
		list of species
		"""
		vars = self.conc.variables.keys()
		for i, var in enumerate(vars):
			vars[i]=var.upper()

		vars=sorted(vars)

		pri_vars = []
		normal_vars = []

		# Put some of the important ones up top
		for var in vars:
			# Select case basically
			if var in ['O3', 'NO', 'NO2']:
				pri_vars.append(var)
			elif var == "TFLAG":
				continue
			else:
				normal_vars.append(var)

		return pri_vars+normal_vars


	# Check to ensure all the chosen species are available 
	# Species is a string vector
	def validateSpecies(self, species):
		"""Validate species against a sample datafile variables

		Keyword Arguments:
		species -- Vector of species names to use

		Raises:
		ValidationError -  if invalid species is input

		Returns:
		TRUE if valid, false otherwise
		"""

		#print "Got species", '[%s]' % ', '.join(map(str, species))

		vars = self.conc.variables.keys()
		for i in range(0, len(vars)):
			vars[i]=vars[i].upper()

		notFound=[]

		for s in species:
			found=False
			for v in vars:
				if v == s:
					found=True
					break
			if found == False:
				notFound.append(s)

		if len(notFound)>0:
			raise ValidationError("Invalid species: ", '[%s]' % ', '.join(map(str, notFound)))
			return False;
		return True


	def validateLayers(self,layers):
		"""Validate layers against a sample datafile file

		Keyword Arguments:
		layers -- Vector of layers to use

		Raises:
		ValidationError -  if invalid layer is input

		Returns:
		TRUE if valid, false otherwise
		"""

		num_layers = self.conc.dimensions['LAY']
		for l in layers:
			if l > num_layers:
				raise ValidationError("Invalid layer: ", l)
				return False
		return True

	def validateTimes(self,times):
		"""Validate times against a sample datafile file

		Keyword Arguments:
		times -- Vector of times to use

		Raises:
		ValidationError -- if invalid times step is input

		Returns:
		TRUE if valid, false otherwise
		"""

		# Not yet implemented
		return True

	def ValidateDataFileSurface(self, filename):
		""" Validates a datafile by checking if it's 2D surface domani
			(ni,nj) matches the sample file """

		datafile=DataFile(filename, mode='r', open=True)

		#print "COL %d, self.ni: %d   -  ROW: %d, self.nj: %d"%(datafile.dimensions['COL'], self.ni, datafile.dimensions['ROW'], self.nj)
		return datafile.dimensions['COL'] == self.ni and datafile.dimensions['ROW'] == self.nj
			
class ValidationError(Exception):
	pass
