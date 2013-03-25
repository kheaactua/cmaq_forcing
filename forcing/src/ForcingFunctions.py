from DataFile import DataFile
from DoForce import Forcing, ForcingException, ForcingFileDimensionException
import numpy as np
import re

class ForceWithThreshold(Forcing):
	# Concentration threshold
	_threshold=None

	@property
	def threshold(self):
		return self._threshold
	@threshold.setter
	def threshold(self, val):
		# If 0, set as None
		if val == 0 or val is None:
			self._threshold = None
		else:
			print "val = ", val
			self._threshold = float(val)

class ForceWithTimeInvariantScalarFld(Forcing):
	# Time invariant scalar multiplcative fld (nj, ni)
	timeInvariantScalarMultiplcativeFld = None

class ForceOnAverageConcentration(ForceWithThreshold, ForceWithTimeInvariantScalarFld):
	""" These are here and not in the panel's such that they can
	work via the command line """

	# Time Mask
	timeMask=range(0,Forcing.dayLen+1)

	# Override default outputFormat
	outputFormat = 'Force.TYPE.AVG.YYYYMMDD'

	def generateForceFileName(self, conc, fmt = None):
		""" Get averaging in the output file name """
		fname = super(ForceOnAverageConcentration, self).generateForceFileName(conc, fmt)
		fname = re.sub(r"AVG", self.averaging, fname)
		return fname		


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

		#print "In ForceOnAverageConcentration:generateForcingFields()"

		# Some variable used later
		scalar = None

		if self.griddedTimeZoneFld == None:
			# Assume all timezones are GMT
			print "Warning!  No gridded time zone information loaded.  Using a field of zeros."
			tz = np.zeros((self.ni,self.nj))
		else:
			tz = self.griddedTimeZoneFld

		if len(self.species) == 0:
			raise NoSpeciesException("Must specify species")
			return

		# We doing time averaging?
		if self.averaging in ['AVG_MAX', 'AVG_MAX8', 'AVG_MAX24']:
			do_averaging=True
			averaging_window = 8 # Default
			averaging_window = 1  if self.averaging == 'AVG_MAX'   else averaging_window
			averaging_window = 8  if self.averaging == 'AVG_MAX8'  else averaging_window
			averaging_window = 24 if self.averaging == 'AVG_MAX24' else averaging_window
		else:
			do_averaging=False
			averaging_window = None
			#if self.averaging == 'AVG_MASK' or self.averaging == 'AVG_NONE'
			if self.averaging == 'AVG_NONE':
				# Ensure this is set right
				self.timeMask = range(0,25)
			# If it's the mask, then the timemask should already be set

		# Create zero fields to allocate our arrays
		fld_empty=np.zeros((len(self.species), self.nt, self.nk_f, self.nj, self.ni), dtype=np.float32)

		flds={'yesterday': fld_empty, 'today': fld_empty.copy(), 'tomorrow': fld_empty.copy()}


		# This is NOT efficient.  Could probably easily make it
		# more efficient by implementing some sort of cache though..
		for idx_s, species in enumerate(self.species):
			#print "Iteratiing through species %d=%s"%(idx_s, species)
			if conc_yest is None:
				# If we're on day 1..
				# This is inefficient, will upgrade later
				data_yest = np.zeros((self.nt, self.nk_f, self.nj, self.ni))
				# Using nk_f here instead of nk, because we'll never be looking outside
				# of nk_f
			else:
				var_yest  = conc_yest.variables[species]
				data_yest = var_yest[:]

			if conc_tom is None:
				data_tom   = np.zeros((self.nt, self.nk_f, self.nj, self.ni))
			else:
				#print "Looking for variable %s"%species
				var_tom   = conc_tom.variables[species]
				data_tom  = var_tom[:]

			data_today  = conc_today.variables[species][:]

			# This used to copy data_yest's shape, but now we override some dims (like layers)
			fld_yest  = np.zeros((self.nt, self.nk_f, self.nj, self.ni), dtype=np.float32)
			fld_today = fld_yest.copy()
			fld_tom   = fld_yest.copy()


			# Recall, mask is already considered in these vectors
			for k in self._layers:
				# I think there's a better way to do the next two loops, don't know it though.
				for i in range(0,self.ni):
					for j in range(0,self.nj):

						# Spatial mask
						if not self.space[j,i]:
							# This is masked out.  Set to zero and go to the next cell
							fld_yest[0:self.nt,k,j,i]  = np.zeros((self.nt), dtype=np.float32)
							fld_today[0:self.nt,k,j,i] = np.zeros((self.nt), dtype=np.float32)
							fld_tom[0:self.nt,k,j,i]   = np.zeros((self.nt), dtype=np.float32)
							continue
						#else:
						#	# TEMP HACK!!
						#   # This temp hack is used to ensure the mask is working
						#	fld_yest[0:self.nt,k,j,i]  = np.ones((self.nt), dtype=np.float32)
						#	fld_today[0:self.nt,k,j,i] = np.ones((self.nt), dtype=np.float32)
						#	fld_tom[0:self.nt,k,j,i]   = np.ones((self.nt), dtype=np.float32)
						#	continue


						# Take averaging into consideration
						# For almost all of these averagings, we'll have to
						# build a vector of all values for all times at that
						# cell.  Unfortunately, the data is organized in the 
						# opposite way as we want (time is the top index..)
						if do_averaging:
							vec_yest  = data_yest[:Forcing.dayLen,k,j,i]
							vec_today = data_today[:Forcing.dayLen,k,j,i]
							vec_tom   = data_tom[:Forcing.dayLen,k,j,i]

							# REMOVE!
							#if i==self.debug_i and j==self.debug_j:
							#	print "vec_today[%d,%d]: "%(self.debug_j, self.debug_i), vec_today

							# Prepares a vector of values with respect to the
							# direction we're going to calculate the average
							# (forward/backward), the window size, and time
							# zone 

							vec = Forcing.prepareTimeVectorForAvg(vec_yest, vec_today, vec_tom, timezone=tz[j][i], winLen=averaging_window, debug=False)
							#print "i=%d,j=%d, preped vec[%d] = %s"%(i,j,len(vec)," ".join(map(str, vec)))

							# Calculate the moving window average
							avgs = Forcing.calcMovingAverage(vec, winLen=averaging_window)
							#print "i=%d,j=%d, avg vec[%d]    = %s"%(i,j,len(avgs)," ".join(map(str, avgs)))

							# And then, for the 8-hour max to be used for a
							# forcing term, generate a vector for yesterday,
							# today and tomorrow with the forcing terms in them

							if self.timeInvariantScalarMultiplcativeFld is not None:
								scalar = self.timeInvariantScalarMultiplcativeFld[j][i]/averaging_window

							yesterday, today, tomorrow = Forcing.applyForceToAvgTime(avgs, winLen=averaging_window, timezone=tz[j][i], min_threshold=self.threshold, forcingValue=scalar)


							fld_yest[:Forcing.dayLen,k,j,i]  = yesterday[:Forcing.dayLen]
							fld_today[:Forcing.dayLen,k,j,i] = today[:Forcing.dayLen]
							# REMOVF!
							#if i==self.debug_i and j==self.debug_j:
							#	print "Today: ", today
							fld_tom[:Forcing.dayLen,k,j,i]   = tomorrow[:Forcing.dayLen]

						elif self.averaging == 'AVG_MASK' or self.averaging == 'AVG_NONE':
# NOT YET TESTED
							raise NotImplementedError( "Mask timing or no averaging is not yet tested.  Averaging options=%s"%self.averaging )
							# The comments assume timezone = -6
							for t_gmt in self.timeMask:
								# when t_gmt = 0, t_loc = -6, so we're into yesterday
								t_loc = t_gmt + tz[j][i]

								# Reference the arrays
								if t_loc < 0:
									dfld = data_yest
									#ffld = fld_yest
								elif t_loc>0 and t_loc<Forcing.dayLen:
									dfld = data_today
									#ffld = fld_today
								else:
									dfld = data_tomorrow
									#ffld = fld_tomorrow

								# I have to write in GMT
# This is wrong, as local times can write into another day.. maybe.. but since there's no averaging, another iteration will take care of that..
								ffld = fld_today

								# fld[-6] is fld[18]
								val=dfld[t_loc,k,j,i]
								if threshold is not None:
									if val > threshold:
										force = 1
								else:
									if val > 0.0:
										force = 1

								# Set the field in the referenced forcing field
								ffld[t_loc,k,j,i] = force

						else:
							raise NotImplementedError( "Unavailable time averaging method (%s) selected"%self.averaging )

						#endif averaging
					#endfor j
				#endfor i
			#endfor k

			#print "fld_today[t=8] idx_s=%d:\n"%idx_s,fld_today[8,:,:,:]


			flds['yesterday'][idx_s] = fld_yest
			flds['today'][idx_s]     = fld_today
			flds['tomorrow'][idx_s]  = fld_tom

		#endfor species

		return flds


######################################################################
# Mortality
######################################################################

class ForceOnMortality(ForceOnAverageConcentration):
	"""
	Force on mortality.  User must supply:
	- Time variant:
		- Concentration

	- Time invariant:
		- Concentration response factor (beta) = percent increase in deaths per ppb
		- Value of statistical life (in millions of dollars)
		- Gridded baseline mortality file
			- BMR units of deaths per 10^6 or 10^5 population per year.  Divide
			  BMR by 10^6 or 10^5 and divide by 365 to get deaths per day.
	          WARNING:  Leap years are not yet accounted for
		- Gridded populated mortality file

	This class is extremely similar to ForceOnAverageConcentration.  There are ways
	to re-use the code above, but for now we'll just duplicate it.
	"""

	# Conversion for BMR units to be X per year (million per year, etc)
	# BMR is MULTIPLIED by this
	mort_scale=pow(10, -3) # Amanda divids by 10^6 (BMR per million) then multiplies by 10^3 (per ppm)

	# Value of statistical life (millions)
	vsl = None

	# Concentration response factor
	beta = None

	# Gridded baseline mortality file
	_mortality_fname = None
	_mortality_var = None

	def SetMortality(self, fname, var):
		""" Provide a gridded NetCDF file name and variable name.  This will
		save the info for later reading. """

		self._mortality_fname = fname
		self._mortality_var = var

	# Gridded populated mortality file
	_pop_fname = None
	_pop_var = None

	def SetPop(self, fname, var):
		""" Provide a gridded NetCDF file name and variable name.  This will
		save the info for later reading. """

		self._pop_fname = fname
		self._pop_var = var

	# Does this reference work?
	SetPopulation=SetPop

	def loadScalarField(self):
		""" Open up the mortality and population files and read
		their values.  Generate a field to multiply forcing by.

		Forcing = F * Pop * Mortality * VSL
		"""

		if self.beta is None:
			raise ForcingException("Must supply concentration response factor")

		if self._mortality_fname is None or self._mortality_var is None:
			raise ForcingException("Must supply mortality file")

		if self._pop_fname is None or self._pop_var is None:
			raise ForcingException("Must supply population file")

		# This is optional
		#if self.vsl is None:
		#	raise ForcingException("Must specify statistical value of life (in millions)")

		# Open the mortality file
		try:
			mortality = NetCDFFile(self._mortality_fname, 'r')
		except IOError as ex:
			print "Error!  Cannot open mortality file %s"%(self._mortality_fname)
			raise

		# Check dimensions
		if not (mortality.dimensions['COL'] == self.ni and mortality.dimensions['ROW'] == self.nj):
			raise ValueError("Error, dimensions in mortality file %s do not match domain."%self._mortality_fname)

		# Read the field
		try:
			# dims are TSTEP, LAY, ROW, COL.. so skip TSTEP and LAY
			# this should be made more general, or the file should be made better.
			mfld = mortality.variables[self._mortality_var].getValue()[0][0]
		except IOError as e:
			raise e
		except IndexError as e:
			raise ForcingFileDimensionException("Mortality NetCDF file seems to have incompatible dimensions.  Currently require shape (TSTEP, LAY, ROW, COL).  This is marked to be improved, as the data does not vary with time or layer.")

		# Close the file
		if self._pop_fname != self._pop_fname:
			mortality.close()

			# Open the population file
			try:
				pop = NetCDFFile(self._pop_fname, 'r')
			except IOError as ex:
				print "Error!  Cannot open population file %s"%(self._pop_fname)
				raise

			# Check dimensions
			if not (pop.dimensions['COL'] == self.ni and pop.dimensions['ROW'] == self.nj):
				raise ValueError("Error, dimensions in population file %s do not match domain."%self._pop_fname)

		# Read the field
		try:
			# dims are TSTEP, LAY, ROW, COL.. so skip TSTEP and LAY
			pfld = mortality.variables[self._pop_var].getValue()[0][0]
		except IOError as e:
			raise e
		except IndexError as e:
			raise ForcingFileDimensionException("Mortality NetCDF file seems to have incompatible dimensions.  Currently require shape (TSTEP, LAY, ROW, COL).  This is marked to be improved, as the data does not vary with time or layer.")

		# Debug, remember, when debugging this against plotted data or fortran
		# code: values like (70,70) started at index 1 whereas we started at
		# index 0, so (70,70)=(69,69)
		#print "[j=%d,i=%d] = mfld * mfld_scale * pfld * self.beta / 365 = %e %e %e %e %e = %e"%(self.debug_j, self.debug_i, mfld[self.debug_j,self.debug_i], (10.**-4), pfld[self.debug_j,self.debug_i], self.beta, 365.0, mfld[self.debug_j,self.debug_i]*(10.**-4)*pfld[self.debug_j,self.debug_i]*self.beta/365.0)

		# (mfld * pfld) is element wise multiplication, not matrix multiplication
		# Take leap years into account?
		self.timeInvariantScalarMultiplcativeFld = mfld * self.mort_scale / 365.0 * pfld * self.beta
		if self.vsl is not None:
			self.timeInvariantScalarMultiplcativeFld = self.timeInvariantScalarMultiplcativeFld * self.vsl

