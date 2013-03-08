#!/usr/bin/env python

# CLI arguments
import argparse

# System functions
import sys

from Scientific.IO.NetCDF import NetCDFFile
import numpy as np

# Graphing
import matplotlib.pyplot as plt

#matt_file="../output/Forcing.ForceOnAverageConcentration.20070502"
#mort_file="/mnt/mediasonic/opt/output/morteza/frc-8h-US/CCTM_fwdFRC.20070502"
matt_file='conc/CCTM_fwdACONC.20070502'
mort_file='conc/CCTM_fwdACONC.20070502'


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


matt=NetCDFFile(matt_file, 'r')
mort=NetCDFFile(mort_file, 'r')
#mort=matt

# Get the variable
var_matt = matt.variables['O3']
var_mort = mort.variables['O3']

data_matt=var_matt.getValue()
data_mort=var_mort.getValue()

vec_matt=np.zeros((25), dtype=np.float32)
vec_mort=np.zeros((25), dtype=np.float32)

vec_matt[:]=data_matt[:,0,j,i]
vec_mort[:]=data_mort[:,0,j,i]


print "Time: %s"%("   ".join('%4.0d' % v for v in range(1,26)))
print "Mort: %s"%(", ".join('%4.3f' % v for v in vec_mort))
print "Matt: %s"%(", ".join('%4.3f' % v for v in vec_matt))

## Plot the data
#fig=plt.figure()
#ax = fig.add_subplot(111)
#ax.plot(range(1,26), vec_mort, 'b-')
#ax.plot(range(1,26), vec_matt, 'r-')
#plt.show()


matt.close()
mort.close()