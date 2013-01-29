#!/usr/bin/env python

from numpy import shape
from Scientific.IO.NetCDF import NetCDFFile
import numpy as np

def genForcingFiles(conc, output, species, model):
	copyIoapiProps(conc, output);
	# Should probably add my fixGeocodingData

def prepIoapiOutput(src, dest):
	# Copy props from input to output
	copyIoapiProps(conc, output);

	# Fix geocode data
	# http://svn.asilika.com/svn/school/GEOG%205804%20-%20Introduction%20to%20GIS/Project/webservice/fixIoapiProjection.py
	# fixIoapiSpatialInfo

def copyIoapiProps(src, dest):
	infile  = NetCDFFile(src, 'r')
	outfile = NetCDFFile(dest, 'w')

	attrs=["IOAPI_VERSION", "EXEC_ID", "FTYPE", "CDATE", "CTIME", "WDATE", "WTIME", "SDATE", "STIME", "TSTEP", "NTHIK", "NCOLS", "NROWS", "NLAYS", "NVARS", "GDTYP", "P_ALP", "P_BET", "P_GAM", "XCENT", "YCENT", "XORIG", "YORIG", "XCELL", "YCELL", "VGTYP", "VGTOP", "VGLVLS", "GDNAM", "UPNAM", "VAR-LIST", "FILEDESC", "HISTORY"]

	for attr in attrs:
		# Read the attribute
		if hasattr(infile, attr): 
			attrVal = getattr(infile, attr);
			# Write it to the new file
			setattr(outfile, attr, attrVal)
		else:
			print attr, "does not exist in this netCDF file %s." % src

	outfile.sync()
	outfile.close()

def validateSpecies(conc, species_str):
	infile  = NetCDFFile(conc, 'r')

	# Split the species string into an array
	species=species_str.split(',');

	vars = infile.variables.keys()
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

	return notFound


"""
def outputConfFile(name):
	# Generates a conf file that records the state of the UI

def loadConfFile(name):
	# Reads in the conf file and sets the UI state
"""

# MAIN

#copyIoapiProps('forcing.nc', 'output.nc')
species="O,O3,NO2"
species=species.upper()
invalids=validateSpecies('conc.nc', species)
if len(invalids)>0:
	print "There were invalid elements in the list"
else:
	print "List was great"
