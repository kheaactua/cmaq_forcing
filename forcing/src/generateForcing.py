#!/usr/bin/env python

# Gui
import wx
from gui import *

# Include Forcing.py
from DoForce import *
import ForcingFunctions as f
from Validator import *

# Widgit inspection tool
import wx.lib.inspection

# CLI arguments
import argparse

# System functions
import sys

# Date stuff
from datetime import *

# For now, I'll hard code most of the inputs.  Eventually I'll make a config
# file, as there are just too many inputs.
parser = argparse.ArgumentParser(description='Use GUI or CLI?')
parser.add_argument('--cli', action='store_true', help='Use CLI interface')

args = parser.parse_args()
#print args

"""
#
# Can probably delete all this...
#
def outputConfFile(name):
	# Generates a conf file that records the state of the UI

def loadConfFile(name):
	# Reads in the conf file and sets the UI state
"""

def ProgressBarCLI(prog, filename):
	print "Progress %f, filename: %s"%(prog, filename)
	print "\n------------------------------------------------------------\n"

if args.cli:

	#fc = f.ForceOnAverageConcentration(sample_conc='conc.nc')
	#fc = f.ForceOnAverageConcentration(sample_conc='basic_concentrations/CCTM.20050505')
	fc = f.ForceOnAverageConcentration(sample_conc='/mnt/mediasonic/opt/output/base/CCTM_fwdCONC.20070424')

	fc.maskLayers([1])
	fc.species=['O3']

	# These two are default values
	#fc.outputFormat = 'Forcing.TYPE.YYYYMMDD'
	#fc.outputPath=os.getcwd() + 'output/'

	fc.griddedTimeZone = 'GriddedTimeZoneMask.nc'
	#fc.griddedTimeZone = 'basic_concentrations/timezones.nc'
	fc.setAveraging('Max 8 hr')

	#date_min = dateE(1999,07,03)
	#date_max = dateE(1999,07,06)
	date_min = dateE(2007,04,24)
	date_max = dateE(2007,04,28)
	#fc.conc_path = os.getcwd() + '/concentrations/'
	#fc.conc_path = os.getcwd() + '/basic_concentrations/'
	fc.conc_path = '/mnt/mediasonic/opt/output/base/'

	#conc_files=fc.FindFiles(file_format="CCTM.YYYYMMDD", path=fc.conc_path, date_min=date_min, date_max=date_max)
	conc_files=fc.FindFiles(file_format="CCTM_fwdCONC.YYYYMMDD", path=fc.conc_path, date_min=date_min, date_max=date_max)
	fc.loadConcentrationFiles(conc_files)


	fc.produceForcingField(ProgressBarCLI, dryrun=False)


	## Parse species string
	#species_str="O,O3,NO2"
	#species=species_str.upper()
	#species=species_str.split(',');

	#files=['conc.nc'];

##	# Get a validator
##	try:
##		v=ForcingValidator('conc.nc')
##		v.validateSpecies(species)
##
##		if len(layers):
##			v.validateLayers(layers);
##
##		if len(times):
##			v.validateTimes(times);
##
##		# If we got here, it means everything validated
##		v.close();
##	except ValidationError as e:
##		print "An exception was raise: ", e
##
##	# Now, get the forcing object
##	dims=Forcing.loadDims('conc.nc')
##	force = getForcingObject(dims['ni'], dims['nj'], dims['nk'], dims['nt'])
##	force.setSpecies(species)

else:
	# Use GUI
	app = wx.App(False)
	frame = ForcingFrame(None, name="TopFrame")
	frame.Show()

	#wx.lib.inspection.InspectionTool().Show()
	app.MainLoop()



