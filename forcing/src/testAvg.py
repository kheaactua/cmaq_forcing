#!/usr/bin/env python

from DoForce import *
import numpy as np
import sys, os
from Scientific.IO.NetCDF import NetCDFFile

# This is mostly for debugging..  Just ansi colours
from bcolours import bcolours as bc
c = bc()

def printVec(vec, c, cstr):
	outs=""
	for i in range(0, len(vec)):
		v=vec[i]
		if v > 0:
			outs=outs+"%s%4.2f%s"%(c.red, v, cstr)
		else:
			outs=outs+"%4.2f"%(v)
		if i<len(vec)-1:
			outs=outs+" "
	return outs


#
# Cell of choice

winLen=8

#debug_i=2
#debug_j=2
debug_i=72
debug_j=19


# Timezone?
tzf=os.environ['HOME'] + "/cmaq_forcing/forcing/src/GriddedTimeZoneMask.nc"
src=NetCDFFile(tzf, 'r')
# Get the variable
var = src.variables['LTIME']
timezone=var.getValue()[0][0][debug_j][debug_i]

#print "Sys.argv[%d]: "%len(sys.argv), sys.argv
if len(sys.argv) == 2:
	timezone=int(sys.argv[1])

#print "Using timezone %d"%timezone

#yesterday=range(-24,0)
#today=range(0,24)
#tomorrow=range(24,48)

yesterday=np.zeros((24), dtype=np.float32)
today    =np.zeros((24), dtype=np.float32)
tomorrow =np.zeros((24), dtype=np.float32)
#today[7:15]=1

## From Morteza's files, cell i=60,j=30, 2007 may1-3
#yesterday=[0.0486, 0.0481, 0.0456, 0.0424, 0.0401, 0.0389, 0.0387, 0.0388, 0.0385, 0.0378, 0.0369, 0.0361, 0.0355, 0.0359, 0.0393, 0.0441, 0.0485, 0.0529, 0.0580, 0.0615, 0.0637, 0.0652, 0.0662, 0.0671]
#today=[0.0675, 0.0673, 0.0650, 0.0617, 0.0588, 0.0558, 0.0524, 0.0494, 0.0474, 0.0457, 0.0437, 0.0412, 0.0392, 0.0376, 0.0390, 0.0406, 0.0428, 0.0468, 0.0500, 0.0515, 0.0521, 0.0528, 0.0538, 0.0549]
#tomorrow=[0.0564, 0.0566, 0.0565, 0.0551, 0.0541, 0.0532, 0.0522, 0.0513, 0.0505, 0.0499, 0.0497, 0.0496, 0.0496, 0.0498, 0.0509, 0.0536, 0.0560, 0.0577, 0.0572, 0.0567, 0.0565, 0.0559, 0.0552, 0.0545]

# From Morteza's files, cell i=72,j=19, 2007 may1-3
#yesterday[:]=[0.0289, 0.0281, 0.0264, 0.0256, 0.0254, 0.0253, 0.0254, 0.0269, 0.0296, 0.0322, 0.0343, 0.0358, 0.0367, 0.0368, 0.0372, 0.0380, 0.0392, 0.0403, 0.0411, 0.0414, 0.0413, 0.0409, 0.0407, 0.0405]
today[:]=[0.0395, 0.0388, 0.0380, 0.0382, 0.0393, 0.0405, 0.0412, 0.0417, 0.0421, 0.0419, 0.0413, 0.0408, 0.0408, 0.0401, 0.0382, 0.0366, 0.0370, 0.0370, 0.0374, 0.0381, 0.0391, 0.0397, 0.0396, 0.0387]
tomorrow[:]=[0.0356, 0.0343, 0.0328, 0.0329, 0.0335, 0.0346, 0.0359, 0.0364, 0.0361, 0.0355, 0.0346, 0.0336, 0.0325, 0.0316, 0.0312, 0.0307, 0.0311, 0.0324, 0.0344, 0.0366, 0.0382, 0.0393, 0.0398, 0.0404]
#day_after_tomorrow=np.zeros((24), dtype=np.float32)
#day_after_tomorrow[:]=[0.0388, 0.0363, 0.0309, 0.0271, 0.0249, 0.0241, 0.0238, 0.0234, 0.0229, 0.0224, 0.0218, 0.0215, 0.0206, 0.0224, 0.0245, 0.0262, 0.0287, 0.0311, 0.0331, 0.0346, 0.0371, 0.0385, 0.0386, 0.0367]
## Shift back a day
#tomorrow=day_after_tomorrow.copy()
#yesterday=today.copy()
#today=tomorrow.copy()


#!#cbase='/mnt/mediasonic/opt/output/base/'
#!#cfiles=[
#!#   "CCTM_fwdACONC.20070501",
#!#   "CCTM_fwdACONC.20070502",
#!#   "CCTM_fwdACONC.20070503",
#!##   "CCTM_fwdACONC.20070504",
#!#   ]
#!#counter=0
#!#for f in cfiles:
#!#	fp=cbase+f
#!#	src=NetCDFFile(fp, 'r')
#!#
#!#	# Get the variable
#!#	var = src.variables['O3']
#!#	data=var.getValue()
#!#
#!#	vec=np.zeros((24), dtype=np.float32)
#!#	vec[:]=data[:24,0,debug_j,debug_i]
#!#
#!#	src.close()
#!#
#!#	if counter==0:
#!#		yesterday=vec.copy()
#!#	elif counter==1:
#!#		today=vec.copy()
#!#	elif counter==2:
#!#		tomorrow=vec.copy()
#!#	else:
#!#		print "Too many files, not sure what to do"
#!#
#!#	counter=counter+1


print "%sTimezone=%d, i=%d, j=%d, k=0, t=:24%s"%(c.HEADER, timezone, debug_i, debug_j, c.clear)
print "Yest: %s%s%s"%(c.yesterday, ' '.join('%6.5f' % v for v in yesterday), c.clear)
print "Toda: %s%s%s"%(c.today, ' '.join('%6.5f' % v for v in today), c.clear)
print "Tomo: %s%s%s"%(c.tomorrow, ' '.join('%6.5f' % v for v in tomorrow), c.clear)
print "\n"

#vecs={-1: yesterday, 0: today, 1: tomorrow}
vecs={0: today, 1: tomorrow}
vec = Forcing.prepareTimeVectorForAvg(vecs, winLen=winLen, timezone=timezone, debug=True)

avgs = Forcing.calcMovingAverage(vec, winLen=winLen, debug=True)


print ""
# Where's the max?
max_val=max(avgs)
max_idx=avgs.index(max_val)

print "Max: avgs[%d]=%f"%(max_idx, max_val)

vecs = Forcing.applyForceToAvgTime(avgs, days=vecs.keys(), winLen=winLen, timezone=timezone)

print "GMT:     %s"%('  '.join('%3.0d' % v for v in range(1,25)))
for d,vec in vecs.iteritems():
	print "%s: %s%s%s"%(DayIterator.labels[d], getattr(c, DayIterator.clabels[d]), printVec(vec, c, getattr(c, DayIterator.clabels[d])), c.clear)

#print "Toda: %s%s%s"%(c.today, printVec(today, c, c.today), c.clear)
#print "Tomo: %s%s%s"%(c.tomorrow, printVec(tomorrow, c, c.tomorrow), c.clear)

