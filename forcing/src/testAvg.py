from DoForce import *
import numpy as np
import sys

yesterday=range(-24,0)
#yesterday[17:23]=[6,5,5,4,3,2,3]
#today=[1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 5, 5, 5, 6, 6, 6, 7, 7, 8, 8, 9, 9]
today=range(0,24)
tomorrow=range(24,48)
#tomorrow[0:7] = [10, 12, 12, 12, 13, 13, 14, 15]

excel=[6, 5, 5, 4, 3, 2, 3, 1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 5, 5, 5, 6, 6, 6, 7, 7, 8, 8, 9, 9, 10, 12, 12, 12, 13, 13, 14, 15]
threedays=yesterday+today+tomorrow
##print "Double check values"
##for i in range(0,len(excel)):
##	# i is for excel
##	# j is for three day
##
##	j = i + 17
##
##	if excel[i] != threedays[j]:
##		print "Index %d doesn't match! excel=%d, threedays=%d"%(i, excel[i], threedays[j])
##		sys.exit()
##	#else:
##	#	print "%d %d"%(excel[i], threedays[j])

#print "\n" 

#for i in range(0,23):
#	yesterday[i] =-1*yesterday[i]
#	tomorrow[i]  =-1*tomorrow[i]
print "Yest: %s"%(', '.join(map(str, yesterday)))
print "Toda: %s"%(', '.join(map(str, today)))
print "Tomo: %s"%(', '.join(map(str, tomorrow)))
print "\n"

vec = Forcing.prepareTimeVectorForAvg(yesterday, today, tomorrow, timezone=-5)
#vec = Forcing.prepareTimeVectorForAvg(yesterday, today, tomorrow)
print "Compiled vector(len=%d): %s \n"%(len(vec), ', '.join(map(str, vec)))
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

avgs = Forcing.calcMovingAverage(vec)
if Forcing.default_averaging_direction == False:
	avgs[0]=100

# Almost right
print "Averages (len=%d):\n%s "%(len(avgs), '\n'.join(map(str, avgs)))

# Where's the max?
max_val=max(avgs)
max_idx=avgs.index(max_val)

print "Max: avgs[%d]=%f"%(max_idx, max_val)

fs=Forcing.applyForceToAvgTime(avgs)
print "Yest: %s"%(', '.join(map(str, fs['yesterday'])))
print "Toda: %s"%(', '.join(map(str, fs['today'])))
print "Tomo: %s"%(', '.join(map(str, fs['tomorrow'])))