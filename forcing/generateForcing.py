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

#copyIoapiProps('forcing.nc', 'output.nc')
species_str="O,O3,NO2"
species=species_str.upper()
species=species_str.split(',');

times = [1, 2];
layers = [1];

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
print dims
x = getForcingObject(dims['ni'], dims['nj'], dims['nk'], dims['nt'])

#x = getForcingObject()
#x.produceForcingField()
