#!/usr/bin/env python
from Scientific.IO.NetCDF import NetCDFFile
import numpy as np
import matplotlib.pyplot as plt
import math

class Test:
	def __init__(self, fld_pop):
		self.fld_pop = fld_pop

	def __call__(self,event):
		if event.inaxes:
			i = math.floor(event.xdata)
			j = math.floor(event.ydata)
			print "fld_pop[j=%d, i=%d] %s = : %e"%(j, i, self.fld_pop.shape, self.fld_pop[j,i])
		else:
			print "Outside drawing area!"


f=NetCDFFile('DOMAIN_POP_BMR', 'r')
fld_pop = f.variables['POP'].getValue()[0][0]
fld_bmr = f.variables['BMR'].getValue()[0][0]

debug_i=21
debug_j=46
print "Pop[%d, %d] = %e"%(debug_i, debug_j, fld_pop[debug_i, debug_j])

test = Test(fld_pop)
i = plt.imshow(fld_pop, interpolation='nearest')
plt.gca().invert_yaxis()
plt.connect('button_press_event', test)
plt.show()

test_bmr = Test(fld_bmr)
i = plt.imshow(fld_bmr, interpolation='nearest')
plt.gca().invert_yaxis()
plt.connect('button_press_event', test_bmr)
plt.show()

