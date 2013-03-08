#!/usr/bin/env python

# CLI arguments
import argparse

# System functions
import sys

from Scientific.IO.NetCDF import NetCDFFile
import numpy as np


# Cell of choice
i=60
j=30

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

allfiles=files+ffiles


for f in allfiles:
	#print "Opening %s"%f
	src=NetCDFFile(f, 'r')

	# Get the variable
	var = src.variables['O3']

	data=var.getValue()

	vec=np.zeros((25), dtype=np.float32)
	vec[:]=data[:,0,j,i]

	print "%s"%(", ".join('%6.4f' % v for v in vec))

	# Copy over the value
	src.close()

