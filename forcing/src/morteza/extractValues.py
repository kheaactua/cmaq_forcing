#!/usr/bin/env python

# CLI arguments
import argparse

# System functions
import sys

from Scientific.IO.NetCDF import NetCDFFile
from numpy import shape

fname=""
if len(sys.argv) == 2:
	fname=sys.argv[1]
else:
	print "Must provide a name"
	sys._exit(1)
outname="out.%s"%fname

src=NetCDFFile(fname, 'r')
dest=NetCDFFile(outname, 'a')

dims = src.dimensions.keys()
for d in dims:
	v = src.dimensions[d]
	try:
		dest.createDimension(d, v)
	except IOError as ex:
		print "Cannot create dimension %s"%d, ex
dest.sync()

# Get the variable
var = src.variables['O3']

# Copy over the value
dvar = dest.createVariable('O3', 'f', ('TSTEP', 'LAY', 'ROW', 'COL'))
dvar.assignValue(var.getValue())

dvar.sync()
var.close()
