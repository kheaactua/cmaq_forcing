from DoForce import Forcing
import numpy as np
import copy

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

		#print "ni, nj: %d, %d"%(self.ni, self.nj)


		# Create zero fields to allocate our arrays
		#print "111 Self.species: ", self.species
		fld_empty=range(0, len(self.species))
		for idx_s in range(0, len(self.species)):
			species = self.species[idx_s]
			fld_empty[idx_s] = np.zeros((self.nt, self.nk, self.nj, self.ni))

		#print "222 Self.species: ", self.species
		flds={'yesterday': fld_empty, 'today': fld_empty, 'tomorrow': fld_empty}

		# This is NOT efficient.  Could probably easily make it
		# more efficient by implementing some sort of cache though..
		for idx_s in range(0, len(self.species)):
			species = self.species[idx_s]
			if conc_yest == None:
				# If we're on day 1..
				# This is inefficient, will upgrade later
				data_yest = np.zeros((self.nt, self.nk, self.nj, self.ni))
			else:
				var_yest  = conc_yest.variables[species]
				data_yest  = var_yest.getValue()


			if conc_tom == None:
				data_tom   = np.zeros((self.nt, self.nk, self.nj, self.ni))
			else:
				#print "Looking for variable %s"%species
				var_tom   = conc_tom.variables[species]
				data_tom   = var_tom.getValue()

			var_today = conc_today.variables[species]
			data_today = var_today.getValue()

			print "Initialized data_today with shape=", data_today.shape
			print "data_today[t=8]: ", data_today[8,:,:,:]

#			src_yesterday=conc_yest.getValue()
#			data=np.concatenate([yesterday, today, tomorrow])

			fld_yest  = np.zeros(data_yest.shape, dtype=np.float32)
			fld_today = np.zeros(data_today.shape, dtype=np.float32)
			fld_tom   = np.zeros(data_tom.shape, dtype=np.float32)

			#print "Initialized fld_today with shape=", fld_today.shape

			# Recall, mask is already considered in these vectors
			for k in self._layers:
				# I think there's a better way to do the next two loops, don't know it though.
				for i in range(0,self.ni):
					for j in range(0,self.nj):

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
								#print "Reading %s at (%d,%d) t=%d"%(self.species[idx_s],i,j,t)
								# Make sure I'm not transposing this...
								#print "shape(vec_yest)=%s, shape(data_yest)=%s.  Tyrying to access data_yest[%d][%d][%d][%d]"%(vec_yest.shape, data_yest.shape, t, k, j, i)
								vec_yest[t]  = data_yest[t][k][j][i]
								#print "shape(vec_today)=%s, shape(data_today)=%s"%(vec_today.shape, data_yest.shape)
								vec_today[t] = data_today[t][k][j][i]
								vec_tom[t]   = data_tom[t][k][j][i]

							## Put it together in one long matrix
							#vec3day = np.concatenate([data_yest, today, tomorrow])

							# Prepares a vector of values with respect to the
							# direction we're going to calculate the average
							# (forward/backward), the window size, and time
							# zone 

							vec = Forcing.prepareTimeVectorForAvg(vec_yest, vec_today, vec_tom, timezone=tz[i][j])
							#print "i=%d,j=%d, preped vec[%d] = %s"%(i,j,len(vec)," ".join(map(str, vec)))

							# Calculate the moving window average
							avgs = Forcing.calcMovingAverage(vec)
							#print "i=%d,j=%d, avg vec[%d]    = %s"%(i,j,len(avgs)," ".join(map(str, avgs)))

							# And then, for the 8-hour max to be used for a
							# forcing term, generate a vector for yesterday,
							# today and tomorrow with the forcing terms in them
# NOTE: Ensure that this is above the threshold
							forcing_vectors = Forcing.applyForceToAvgTime(avgs)
							#print "i=%d,j=%d, avg fvec[%d]   = %s"%(i,j,len(forcing_vectors['today'])," ".join(map(str, forcing_vectors['today'])))

							# Now, write these out to the flds
							#print "Shape(fld_yest): ", fld_yest.shape, ", shape(forcing_vectors['yesterday']): ", forcing_vectors['yesterday'].shape
							#print "yesterday: ", forcing_vectors['yesterday']
							#print "len(yesterday) : ", len(forcing_vectors['yesterday'])
							#print "len(today) : ", len(forcing_vectors['today'])
							#print "len(tomorrow) : ", len(forcing_vectors['tomorrow'])
							for t in range(0, self.nt-1):
								#print "Reading %s at (%d,%d) t=%d"%(self.species[idx_s],i,j,t)
								# Make sure I'm not transposing this...
								#print "fld_yest[t][k][j][i] = ", fld_yest[t][k][j][i]
								#print "forcing_vectors['yesterday'][t] = ", forcing_vectors['yesterday'][t]
								fld_yest[t][k][j][i]  = forcing_vectors['yesterday'][t]
								fld_today[t][k][j][i] = forcing_vectors['today'][t]
								fld_tom[t][k][j][i]   = forcing_vectors['tomorrow'][t]

						#endif averaging
					#endfor j
				#endfor i
			#endfor k
			print "fld_today[t=8]:\n",fld_today[8,:,:,:]


			flds['yesterday'][idx_s] = fld_yest
			flds['today'][idx_s]     = fld_today
			flds['tomorrow'][idx_s]  = fld_tom

			#print "flds['yesterday'][%s].shape = "%(species), flds['yesterday'][idx_s].shape
			#print "BREAKING!!!"
			#break

		#endfor species

		return flds

class ForcingException(Exception):
	pass

class NoSpeciesException(ForcingException):
	pass
