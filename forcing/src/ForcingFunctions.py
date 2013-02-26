from DoForce import Forcing
import numpy as np

class ForceOnAverageConcentration(Forcing):
	""" These are here and not in the panel's such that they can
	work via the command line """

	threshold = 0
	
	def setThreshold(self, threshold):
		self.threshold=threshold

	def generateForcingFields(self, conc_idx,
 	   conc_yest,  conc_today,  conc_tom,
	   force_yest, force_today, force_tom):
		""" UPDATE THIS DESCRIPTION!
		    Generate a forcing field, for each species, write a
			field of all 1's (this is a simply case), with respect
			to all the masks of course.

		Keyword Arguments:

		conc_idx:*int*
		  Index of concentration file in self.conc_files.  Done this way
		  so that it's easy to access yesterday's and tomorrow's files.

		conc_ and force_:*NetCDFFile*
		   NetCDF files

		Returns:

		Warning:  This pretty much assumes each file is a day
		A dictionary, where key names are variable names, and each
		contain a float32 3D field.
		"""

		print "In ForceOnAverageConcentration:generateForcingFields()"

		# TEMP HACK!
		# Assume all timezones are GMT
		tz = np.zeros((self.ni,self.nj))
		# /TEMP HACK!

		if len(self.species) == 0:
			raise NoSpeciesException("Must specify species")
			return

		flds={}

		# This is NOT efficient.  Could probably easily make it
		# more efficient by implementing some sort of cache though..
		for s in self.species:
			if conc_yest == None:
				# If we're on day 1..
				data_yest = np.zeros((self.ni, self.nj))
			else:
				var_yest  = conc_yest.variables[s]
				data_yest  = var_yest.getValue()


			if conc_tom == None:
				data_tom   = np.zeros((self.ni, self.nj))
			else:
				var_tom   = conc_tom.variables[s]
				data_tom   = var_tom.getValue()

			var_today = conc_today.variables[s]
			data_today = var_today.getValue()

#			src_yesterday=conc_yest.getValue()
#			data=np.concatenate([yesterday, today, tomorrow])

			fld_yest  = np.zeros(data_yest.shape, dtype=np.float32)
			fld_today = np.zeros(data_today.shape, dtype=np.float32)
			fld_tom   = np.zeros(data_tom.shape, dtype=np.float32)

			# Recall, mask is already considered in these vectors
			for k in self.layers:
				# I think there's a better way to do the next two loops, don't know it though.
				for i in range(0,self.ni-1):
					for j in range(0,self.nj-1):

						# Take averaging into consideration
						# For almost all of these averagings, we'll have to
						# build a vector of all values for all times at that
						# cell.  Unfortunately, the data is organized in the 
						# opposite way as we want (time is the top index..)
						if self.averaging == 'AVG_MAX8':
							vec_yest  = np.zeros(self.nt, dtype=np.float32)
							vec_today = np.zeros(self.nt, dtype=np.float32)
							vec_tom   = np.zeros(self.nt, dtype=np.float32)
							for t in range(0, self.nt-1):
								print "Reading %s at (%d,%d) t=%d"%(s,i,j,t)
								# Make sure I'm not transposing this...
								vec_yest[t]  = data_yest[t][k][j][i]
								vec_today[t] = data_today[t][k][j][i]
								vec_tom[t]   = data_tom[t][k][j][i]

							## Put it together in one long matrix
							#vec3day = np.concatenate([data_yest, today, tomorrow])

							# Prepares a vector of values with respect to the
							# direction we're going to calculate the average
							# (forward/backward), the window size, and time
							# zone 

							vec = Forcing.prepareTimeVectorForAvg(vec_yest, yest_today, yest_tomorrow, timezone=tz[i][j])

							# Calculate the moving window average
							avgs = Forcing.calcMovingAverage(vec)

							# And then, for the 8-hour max to be used for a
							# forcing term, generate a vector for yesterday,
							# today and tomorrow with the forcing terms in them
# NOTE: Ensure that this is above the threshold
							forcing_vectors = Forcing.applyForceToAvgTime(avgs)

							# Now, write these out to the flds
							for t in range(0, self.dims['nt']-1):
								print "Reading %s at (%d,%d) t=%d"%(s,i,j,t)
								# Make sure I'm not transposing this...
								fld_yest[t][k][j][i]  = forcing_vectors['yesterday'][t]
								fld_today[t][k][j][i] = forcing_vectors['yesterday'][t]
								fld_tom[t][k][j][i]   = forcing_vectors['yesterday'][t]

#						for t in self.times:
#							if self.space[i][j] == 1:
#								fld[t][k][j][i]=1

			flds['yesterday'][s] = fld_yest
			flds['today'][s]     = fld_today
			flds['tomorrow'][s]  = fld_tom

		return flds

class ForcingException(Exception):
	pass

class NoSpeciesException(ForcingException):
	pass
