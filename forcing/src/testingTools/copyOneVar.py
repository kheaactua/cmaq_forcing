#!/usr/bin/env python

# CLI arguments
import argparse

# System functions
import sys, os

from Scientific.IO.NetCDF import NetCDFFile
import numpy as np

sys.path.append(os.environ['HOME'] + "/cmaq_forcing/forcing/src/")
from bcolours import bcolours as bc

src_file="FWD.0703"
var_name="O3"

src=NetCDFFile(src_file, 'r')
src_var = src[var_name]

# Create a new file
dest = NetCDFFile("%s.%s"%(src_file, var_name), 'w')
# Create the dimensions
for d,v in src.dimensions.iteritems():
	dest.createDimension(d, v)

# Create variable
dest_var = dest.createVariable(var_name, 'f', ('TSTEP', 'LAY', 'ROW', 'COL'))
dest_var[:] = src_var[:]

src.close()
dest.close()
