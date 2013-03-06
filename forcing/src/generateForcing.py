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
	d=datetime.now()
	print "Time: %0.2d:%0.2d.%0.2d: Progress %f, filename: %s"%(d.hour,d.minute,d.second, prog, filename)
	print "\n------------------------------------------------------------\n"

if args.cli:

	setup=1

	if setup==0:
		fc = f.ForceOnAverageConcentration(sample_conc='conc.nc')
		date_min = dateE(1999,07,03)
		date_max = dateE(1999,07,06)
		fc.conc_path = os.getcwd() + '/concentrations/'
	elif setup==1:
		fc = f.ForceOnAverageConcentration(sample_conc='basic_concentrations/CCTM.20050505')
		fc.conc_path = os.getcwd() + '/basic_concentrations/'
		date_min=None
		date_max=None
	elif setup==2:
		fc = f.ForceOnAverageConcentration(sample_conc='/mnt/mediasonic/opt/output/base/CCTM_fwdACONC.20070501')
		date_min = dateE(2007,05,01)
		date_max = dateE(2007,05,01)
		fc.conc_path = '/mnt/mediasonic/opt/output/base/'


	fc.setAveraging('Max 8 hr')

	fc.maskLayers([1])
	fc.species=['O3']

	# These two are default values
	#fc.outputFormat = 'Forcing.TYPE.YYYYMMDD'
	#fc.outputPath=os.getcwd() + 'output/'

	if setup==0:
		conc_files=fc.FindFiles(file_format="CCTM.YYYYMMDD", path=fc.conc_path, date_min=date_min, date_max=date_max)

	elif setup==1:
		#fc.griddedTimeZone = 'basic_concentrations/timezones.nc'
		conc_files=fc.FindFiles(file_format="CCTM.YYYYMMDD", path=fc.conc_path, date_min=date_min, date_max=date_max)
	elif setup==2:
		fc.griddedTimeZone = 'GriddedTimeZoneMask.nc'
		conc_files=fc.FindFiles(file_format="CCTM_fwdACONC.YYYYMMDD", path=fc.conc_path, date_min=date_min, date_max=date_max)
		# Mask space
		fc.maskSpace('/opt/home/morteza/Codes/Force8hr/usa.nc', 'USA', 2)


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



