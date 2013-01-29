from Scientific.IO.NetCDF import NetCDFFile
from numpy import shape
import numpy as np

def getForcingObject(ni,nj,nk,nt):
	return Forcing(ni,nj,nk,nt)

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

	# Mask the grid
	# mask is a 2D
	def maskSpace(self, mask):
		""" Set a grid mask

		Keyword arguments:
		mask -- (ni x nj) binary array.  1 means use, 0 means don't use
		"""

		raise NotImplementedError( "Not yet implemented" )

	def produceForcingField():
		raise NotImplementedError( "Abstract method" )

	def writeForcingFiles(conc, force_file):
		raise NotImplementedError( "Abstract method" )


##	def genForcingFiles(conc, output, species, model):
##		prepIoapiOutput(conc, output);
##		# Should probably add my fixGeocodingData
##
##	def prepIoapiOutput(src, dest):
##		# Copy props from input to output
##		copyIoapiProps(conc, output);
##
##		# Fix geocode data
##		# http://svn.asilika.com/svn/school/GEOG%205804%20-%20Introduction%20to%20GIS/Project/webservice/fixIoapiProjection.py
##		# fixIoapiSpatialInfo
##
##	def copyIoapiProps(src, dest):
##		infile  = NetCDFFile(src, 'r')
##		outfile = NetCDFFile(dest, 'w')
##
##		attrs=["IOAPI_VERSION", "EXEC_ID", "FTYPE", "CDATE", "CTIME", "WDATE", "WTIME", "SDATE", "STIME", "TSTEP", "NTHIK", "NCOLS", "NROWS", "NLAYS", "NVARS", "GDTYP", "P_ALP", "P_BET", "P_GAM", "XCENT", "YCENT", "XORIG", "YORIG", "XCELL", "YCELL", "VGTYP", "VGTOP", "VGLVLS", "GDNAM", "UPNAM", "VAR-LIST", "FILEDESC", "HISTORY"]
##
##		for attr in attrs:
##			# Read the attribute
##			if hasattr(infile, attr): 
##				attrVal = getattr(infile, attr);
##				# Write it to the new file
##				setattr(outfile, attr, attrVal)
##			else:
##				print attr, "does not exist in this netCDF file %s." % src
##
##		outfile.sync()
##		outfile.close()

class ForceOnSpecies(Forcing):
	def produceForcingField():
		raise NotImplementedError( "Abstract method" )
