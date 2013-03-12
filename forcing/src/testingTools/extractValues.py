#!/usr/bin/env python

# CLI arguments
import argparse

# System functions
import sys, os

from Scientific.IO.NetCDF import NetCDFFile
import numpy as np

sys.path.append(os.environ['HOME'] + "/cmaq_forcing/forcing/src/")
from bcolours import bcolours as bc


#
# Cell of choice

# Match!
#i=60
#j=30

i=72
j=19

print "Cell i=%d j=%d"%(i,j)

# Timezone?
tzf=os.environ['HOME'] + "/cmaq_forcing/forcing/src/GriddedTimeZoneMask.nc"
src=NetCDFFile(tzf, 'r')

# Get the variable
var = src.variables['LTIME']
data=var.getValue()[0][0]
print "Timezone: %d"%(data[j][i])

# Colours
b = bc()

# Copy over the value
src.close()

allfiles=[]

#cbase=os.environ['HOME'] + "/cmaq_forcing/forcing/src/morteza/"
cbase='/mnt/mediasonic/opt/output/base/'
cfiles=["CCTM_fwdACONC.20070501", "CCTM_fwdACONC.20070502", "CCTM_fwdACONC.20070503", "CCTM_fwdACONC.20070504"]
for f in cfiles:
	allfiles.append(cbase+f)

ffiles=["CCTM_fwdFRC.20070501", "CCTM_fwdFRC.20070502", "CCTM_fwdFRC.20070503", "CCTM_fwdFRC.20070504"]
fbase='/mnt/mediasonic/opt/output/morteza/frc-8h-US/'
for f in ffiles:
	allfiles.append(fbase+f)

colours=[b.yesterday, b.today, b.tomorrow, b.cyan]

c_idx=0
for f in allfiles:
	#print "Opening %s"%f
	src=NetCDFFile(f, 'r')

	# Get the variable
	var = src.variables['O3']

	data=var.getValue()

	vec=np.zeros((25), dtype=np.float32)
	vec[:]=data[:,0,j,i]

	print "%s%s%s"%(colours[c_idx%len(colours)], ", ".join('%6.4f' % v for v in vec[:24]), b.clear)

	# Copy over the value
	src.close()

	c_idx=c_idx+1

