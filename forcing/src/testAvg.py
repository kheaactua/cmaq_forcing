#!/usr/bin/env python

from DoForce import *
import numpy as np
import sys

def printVec(vec):
	red="\033[91m"
	clear="\033[0m"
	outs=""
	for i in range(0, len(vec)):
		v=vec[i]
		if v > 0:
			outs=outs+"%s%4.2f%s"%(red, v, clear)
		else:
			outs=outs+"%4.2f"%(v)
		if i<len(vec)-1:
			outs=outs+" "
	return outs

green='\033[92m'
blue='\033[94m'
yellow='\033[33m'
clear='\033[0m'

#print "Sys.argv[%d]: "%len(sys.argv), sys.argv
timezone=0
if len(sys.argv) == 2:
	timezone=int(sys.argv[1])

print "Using timezone %d"%timezone

#yesterday=range(-24,0)
#today=range(0,24)
#tomorrow=range(24,48)

yesterday=np.zeros((24))
today    =np.zeros((24))
tomorrow =np.zeros((24))
#today[8:16]=1

# From Morteza's files, cell i=60,j=30, 2007 may1-3
yesterday=[0.0486, 0.0481, 0.0456, 0.0424, 0.0401, 0.0389, 0.0387, 0.0388, 0.0385, 0.0378, 0.0369, 0.0361, 0.0355, 0.0359, 0.0393, 0.0441, 0.0485, 0.0529, 0.0580, 0.0615, 0.0637, 0.0652, 0.0662, 0.0671]
today=[0.0675, 0.0673, 0.0650, 0.0617, 0.0588, 0.0558, 0.0524, 0.0494, 0.0474, 0.0457, 0.0437, 0.0412, 0.0392, 0.0376, 0.0390, 0.0406, 0.0428, 0.0468, 0.0500, 0.0515, 0.0521, 0.0528, 0.0538, 0.0549]
#yesterday=[0.0486, 0.0481, 0.0456, 0.0424, 0.0401, 0.0389, 0.0387, 0.0388, 0.0385, 0.0378, 0.0369, 0.0361, 0.0355, 0.0359, 0.0393, 0.0441, 0.0485, 1.0529, 1.0580, 1.0615, 1.0637, 1.0652, 1.0662, 1.0671]
#today=[10.0675, 0.0673, 0.0650, 0.0617, 0.0588, 0.0558, 0.0524, 0.0494, 0.0474, 0.0457, 0.0437, 0.0412, 0.0392, 0.0376, 0.0390, 0.0406, 0.0428, 0.0468, 0.0500, 0.0515, 0.0521, 0.0528, 0.0538, 0.0549]
tomorrow=[0.0564, 0.0566, 0.0565, 0.0551, 0.0541, 0.0532, 0.0522, 0.0513, 0.0505, 0.0499, 0.0497, 0.0496, 0.0496, 0.0498, 0.0509, 0.0536, 0.0560, 0.0577, 0.0572, 0.0567, 0.0565, 0.0559, 0.0552, 0.0545]


print "Timezone = %d"%timezone
print "Yest: %s%s%s"%(green, ' '.join('%4.3f' % v for v in yesterday), clear)
print "Toda: %s%s%s"%(blue, ' '.join('%4.3f' % v for v in today), clear)
print "Tomo: %s%s%s"%(yellow, ' '.join('%4.3f' % v for v in tomorrow), clear)
print "\n"

vec = Forcing.prepareTimeVectorForAvg(yesterday, today, tomorrow, timezone=timezone, debug=True)
#vec = Forcing.prepareTimeVectorForAvg(yesterday, today, tomorrow)
#print "\nCompiled vector(len=%d): %s \n"%(len(vec), ', '.join(map(str, vec)))
##print "Triple check values"
##print vec
##print excel
##for i in range(0,len(vec)):
##	# i is for vec
##	# j is for excel
##
##	j = i + 7
##
##	if excel[j] != vec[i]:
##		print "Index %d doesn't match! vec=%d, excel=%d"%(i, vec[i], excel[j])
##		sys.exit()
##	#else:
##	#	print "%d %d"%(excel[i], threedays[j])

avgs = Forcing.calcMovingAverage(vec, debug=True)
#if Forcing.default_averaging_direction == False:
#	avgs[0]=100

# Averages
#print "Averages (len=%d):\n%s "%(len(avgs), ' '.join(map(str, avgs)))

print ""
# Where's the max?
max_val=max(avgs)
max_idx=avgs.index(max_val)

print "Max: avgs[%d]=%f"%(max_idx, max_val)

fs=Forcing.applyForceToAvgTime(avgs, timezone=timezone)
print "GMT:  %s"%('  '.join('%3.0d' % v for v in range(1,25)))
print "Yest: %s"%printVec(fs['yesterday'])
print "Toda: %s"%printVec(fs['today'])
print "Tomo: %s"%printVec(fs['tomorrow'])

