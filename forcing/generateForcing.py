#!/usr/bin/env python


# Include Forcing.py
from Forcing import *
from ForcingValidator import *





"""
def outputConfFile(name):
	# Generates a conf file that records the state of the UI

def loadConfFile(name):
	# Reads in the conf file and sets the UI state
"""


# MAIN
# Fake inputs.

#copyIoapiProps('forcing.nc', 'output.nc')
species_str="O,O3,NO2"
species=species_str.upper()
species=species_str.split(',');

times = [1, 2];
layers = [1];

files=['conc.nc'];

# Actually do stuff

# Get a validator
try:
	v=ForcingValidator('conc.nc')
	v.validateSpecies(species)

	if len(layers):
		v.validateLayers(layers);

	if len(times):
		v.validateTimes(times);

	# If we got here, it means everything validated
	v.close();
except ValidationError as e:
	print "An exception was raise: ", e

# Now, get the forcing object
dims=Forcing.loadDims('conc.nc')
force = getForcingObject(dims['ni'], dims['nj'], dims['nk'], dims['nt'])
force.setSpecies(species)

for c in files:
	o = Forcing.genForceFileName(c)
	force.produceForcingField(c, o)

