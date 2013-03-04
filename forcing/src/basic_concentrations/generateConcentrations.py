#!/usr/bin/env python
import os
import numpy as np
from Scientific.IO.NetCDF import NetCDFFile

# Read in dimensions from a sample concentration
#...

# Make up dimensions for simplicity
nt=25
nk=1
species=['O3']
ni=5
nj=4
ndays = 5
sdate = 20050505
edate = sdate+ndays

# Open the file
# fpath should not exist
for d in range(sdate, edate):
	fpath = 'CCTM.%s'%str(d)
	if os.path.exists(fpath):
		os.remove(fpath)

	#print "Opening %s for writing"%fpath
	conc = NetCDFFile(fpath, 'a')

	conc.createDimension('TSTEP', nt)
	conc.createDimension('LAY',   nk)
	conc.createDimension('ROW',   nj)
	conc.createDimension('COL',   ni)

	for s in species:
		fld = np.zeros((nt,nk,nj,ni), dtype=np.float32)

		if s is 'O3':
			print "Throwing in some values"
			for t in range(0,nt):
				fld[t,0,1:3,1:4] = 8

		var = conc.createVariable(s, 'f', ('TSTEP', 'LAY', 'ROW', 'COL'))
		var.assignValue(fld)

	conc.close()

