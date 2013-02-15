from DoForce import *
import numpy as np
import sys

yesterday=range(-23,0)
yesterday[17:23]=[6,5,5,4,3,2,3]
today=[1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 5, 5, 5, 6, 6, 6, 7, 7, 8, 8, 9, 9]
tomorrow=range(24,48)
tomorrow[0:7] = [10, 12, 12, 12, 13, 13, 14, 15]

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

vec = Forcing.prepareTimeVectorForAvg(yesterday, today, tomorrow)
print "Compiled vector(len=%d): %s "%(len(vec), ', '.join(map(str, vec)))
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
# Almost right
print "Averages: ", avgs
