#!/usr/bin/env python

# CLI arguments
import argparse

# System functions
import sys, os

from Scientific.IO.NetCDF import NetCDFFile
import numpy as np

# Graphing
#import matplotlib.pyplot as plt
from matplotlib.pyplot import *

matt_file=os.environ['HOME'] + "/cmaq_forcing/forcing/src/testingTools/myFRC.0702"
mort_file=os.environ['HOME'] + "/cmaq_forcing/forcing/src/testingTools/FRC.0702"
#matt_file='conc/CCTM_fwdACONC.20070502'
#mort_file='conc/CCTM_fwdACONC.20070502'


#
# Cell of choice

# Match!
#i=60
#j=30

#i=72
#j=19

i=69
j=69

print "Cell i=%d j=%d"%(i,j)

# Timezone?
tzf=os.environ['HOME'] + "/cmaq_forcing/forcing/src/GriddedTimeZoneMask.nc"
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
var_mort = mort.variables['FORCE']

data_matt=var_matt.getValue()
data_mort=var_mort.getValue()

vec_matt=np.zeros((24), dtype=np.float32)
vec_mort=np.zeros((24), dtype=np.float32)

vec_matt[:]=data_matt[:24,0,j,i]
vec_mort[:]=data_mort[:24,0,j,i]


print "Time: %s"%("    ".join('%5.0d' % v for v in range(1,25)))
print "Mort: %s"%(", ".join('%2.1e' % v for v in vec_mort))
print "Matt: %s"%(", ".join('%2.1e' % v for v in vec_matt))

# Plot the data
fig=figure()
print "Morteza blue, matt red"
#ax.plot(range(1,26), vec_mort, 'b-', label="Morteza")
#ax.plot(range(1,26), vec_matt, 'r-', label="Matt")
markerline_matt, stemlines_mort, baseline_mort = stem(range(1,25), vec_mort, linefmt='b-', markerfmt='b')
stem(range(1,25), vec_matt, linefmt='ro', markerfmt='r')

setp(stemlines_mort, linewidth=4)

legend(('Morteza', 'Matt'))
show()


matt.close()
mort.close()
