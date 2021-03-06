#!/usr/local/apps/Python/2.7.3/bin/python
###!/usr/bin/env python
import os
import numpy as np
from netCDF4 import Dataset
#from Scientific.IO.NetCDF import NetCDFFile
from datetime import date

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
	#conc = NetCDFFile(fpath, 'a')
        conc = Dataset(fpath, 'w', format='NETCDF4')

	conc.createDimension('TSTEP', nt)
	conc.createDimension('LAY',   nk)
	conc.createDimension('ROW',   nj)
	conc.createDimension('COL',   ni)
	conc.createDimension('VAR',   len(species))
	conc.createDimension('DATE-TIME', 2)

	# This is a julian date...
	year  = int(str(d)[:4])
	month = int(str(d)[4:6])
	day   = int(str(d)[6:])
	date_base = date(year, 1, 1)
	date_act  = date(year, month, day)
	jday      = (date_act - date_base).days
	jdate=str(year)+str(jday+1)
	setattr(conc, 'SDATE', jdate)

	# Create tflag
	var=conc.createVariable('TFLAG', 'i', ('TSTEP', 'VAR', 'DATE-TIME'))
	dts=np.zeros((nt,len(species),2), dtype=np.int32)
	for h in range(0,25):
		dts[h]=[d, h*10000]
	#print "dts.shape=", dts.shape
	#var.assignValue(dts)
        
        var[:] = dts

	for s in species:
		fld = np.zeros((nt,nk,nj,ni), dtype=np.float32)

		if s is 'O3':
			fld[7:16,0,1:3,1:4] = 8

		var = conc.createVariable(s, 'f', ('TSTEP', 'LAY', 'ROW', 'COL'))
		var[:] = fld # var.assignValue(fld)

	conc.close()

# Create time zones
fpath = 'timezones.nc'
if os.path.exists(fpath):
	os.remove(fpath)
#tz = NetCDFFile(fpath, 'a')
tz = Dataset(fpath, 'w',format='NETCDF4')
tz.createDimension('TSTEP', 1)
tz.createDimension('LAY',   1)
tz.createDimension('ROW',   nj)
tz.createDimension('COL',   ni)

# Create LTIME
var=tz.createVariable('LTIME', 'f', ('TSTEP', 'LAY', 'ROW', 'COL'))
tzfield=np.zeros((1, 1, nj,ni), dtype=np.float32)

for i in range(ni-1, -1, -1):
	tzfield[0,0,:,i] = i-ni+1
#tzfield[0,0,:,:]=-1

print tzfield
var[:] = tzfield #var.assignValue(tzfield)
tz.sync()
tz.close()
