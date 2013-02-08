from DoForce import Forcing

class ForceOnAverageConcentration(Forcing):
	""" These are here and not in the panel's such that they can
	work via the command line """

	threshold = 0
	
	def setThreshold(self, threshold):
		self.threshold=threshold

	def generateForcingFields(self, conc):
		""" Generate a forcing field, for each species, write a
			field of all 1's (this is a simply case), with respect
			to all the masks of course.

		Returns:
		A dictionary, where key names are variable names, and each
		contain a float32 3D field.
		"""

		if len(self.species) == 0:
			raise NoSpeciesException("Must specify species")
			return

		flds={}

		for s in self.species:
			data = conc.variables[s]
			fld  = np.zeros(data.shape, dtype=np.float32)

			# Recall, mask is already considered in these vectors
			for t in self.times:
				for k in self.layers:
					# I think there's a better way to do the next two loops, don't know it though.
					for i in range(0,self.ni-1):
						for j in range(0,self.nj-1):
							if self.space[i][j] == 1:
								fld[t][k][j][i]=1

			flds[s] = fld

		return flds

class ForcingException(Exception):
	pass

class NoSpeciesException(ForcingException):
	pass
