#!/usr/bin/env python

# CLI arguments
import argparse

# System functions
import sys

from Scientific.IO.NetCDF import NetCDFFile
import numpy as np

sys.path.append('../')
from bcolours import bcolours

## Colour code things
#class bcolours:
#
#	red="\033[91m"
#	green='\033[92m'
#	blue='\033[94m'
#	yellow='\033[33m'
#	purple='\033[35m'
#	clear='\033[0m'
#
#	HEADER = '\033[95m'
#	OKBLUE = '\033[94m'
#	OKGREEN = '\033[92m'
#	WARNING = yellow
#	FAIL = red
#	ENDC = clear
#
#	yesterday=green
#	today=blue
#	tomorrow=purple

#
# Cell of choice

# Match!
#i=60
#j=30

i=72
j=19

print "Cell i=%d j=%d"%(i,j)

# Timezone?
tzf="../GriddedTimeZoneMask.nc"
src=NetCDFFile(tzf, 'r')

# Get the variable
var = src.variables['LTIME']
data=var.getValue()[0][0]
print "Timezone: %d"%(data[j][i])

# Copy over the value
src.close()




files=["CCTM_fwdACONC.20070501", "CCTM_fwdACONC.20070502", "CCTM_fwdACONC.20070503"]
ffiles=["/mnt/mediasonic/opt/output/morteza/frc-8h-US/CCTM_fwdFRC.20070501", "/mnt/mediasonic/opt/output/morteza/frc-8h-US/CCTM_fwdFRC.20070502", "/mnt/mediasonic/opt/output/morteza/frc-8h-US/CCTM_fwdFRC.20070503"]
colours=[bcolours.yesterday, bcolours.today, bcolours.tomorrow]

allfiles=files+ffiles

c_idx=0
for f in allfiles:
	#print "Opening %s"%f
	src=NetCDFFile(f, 'r')

	# Get the variable
	var = src.variables['O3']

	data=var.getValue()

	vec=np.zeros((25), dtype=np.float32)
	vec[:]=data[:,0,j,i]

	print "%s%s%s"%(colours[c_idx%len(colours)], ", ".join('%6.4f' % v for v in vec[:24]), bcolours.clear)

	# Copy over the value
	src.close()

	c_idx=c_idx+1

