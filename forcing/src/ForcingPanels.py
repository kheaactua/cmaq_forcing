import wx
import ForcingFunctions as ff
from DoForce import Forcing
from extendedClasses import HelpLink, SingleFileChooser

# Just for debugging
from bcolours import bcolours as bc

class ForcingPanelManager:
	panels=['ForcingPanelBlank', 'ForcingPanelAverageConcentration',
		   'ForcingPanelMortality', 'ForcingPanelDistance']

	@staticmethod
	def getNames():
		names=[]
		for pc in ForcingPanelManager.panels:
			c = globals()[pc]
			if c.appearInList is True:
				#print "Name: %s"%c.name
				names.append(c.name)
		return names

	@staticmethod
	def factory(name, parent):
		""" Return an object that has the class name.name of name """
		for className in ForcingPanelManager.panels:
			c = (globals()[className])(parent)
			if c.name == name:
				return c

		raise ForcingException("No forcing method found for %s"%name)

class ForcingException(Exception):
	pass

class ForcingPanel(wx.Panel):
	""" This is the generic forcing panel
	This class will be put in a separate file such that users can more easily modify it

	All modifiable info, like which forcing files, which panel to use, etc.. should all
	be done here.
	"""

	parent = None

	# The name of the forcing function
	name = "Blank"

	# Whether this should appear in the user selection for forcing functions
	appearInList=False

	# Store the panel
	panel = None

	# Forcing class to use
	forcingClass=None

	# The main frame
	top = None

	def __init__(self, parent, style=0):
		wx.Panel.__init__(self, parent=parent, style=style)
		self.parent=parent

		# Find the main frame
		self.top = parent.FindWindowByName('TopFrame')

		#self.Bind(wx.EVT_SIZE, self.OnReSize)

	def OnReSize(self, event):
		""" Wrap all the static texts

		Doesn't work because the initial wrap put line breaks in the label..
		"""
		size=self.GetSize()
		children=self.GetChildren()
		for c in children:
			if isinstance(c, wx.StaticText):
				print "Resizing: ", c.Label
				c.Wrap(size[0]*0.9)
			else:
				print "Skipping ", c
		event.Skip()

	def runForce(self, common):
		""" This method passes all the required info to the actual forcing function.

		Keyword Arguments:
		common The parent frame with all the getters.  If CLI, this could be
		whatever object has the getters on it.
		"""
		raise NotImplementedError( "Abstract Method" )

	@staticmethod
	def ProcessCLI():
		""" Designed to be able to process command line arguments when
		this whole app is being used through the command line """
		raise NotImplementedError( "Abstract Method" )
	@staticmethod
	def help():
		""" Return a help message, used for when calling this from the cli """

class ForcingPanelBlank(ForcingPanel):
	# The name of the forcing function
	name = "Blank"

	# Whether this should appear in the user selection for forcing functions
	appearInList=False

	def __init__(self, parent, style=wx.TAB_TRAVERSAL):

		#wx.Panel.__init__(self, parent, style=wx.SIMPLE_BORDER)
		ForcingPanel.__init__(self, parent, style)
		self.parent = parent

		txt=wx.StaticText(self, label="Please choose a forcing function on the left panel", size=(self.parent.col2_width, -1))

		sizer = wx.BoxSizer(wx.ALIGN_CENTER_VERTICAL)
		sizer.Add(txt, 0, wx.EXPAND)
		self.SetSizer(sizer)

class ForcingPanelWithAveraging(ForcingPanel):
	""" Most cost functions require the averaging, so putting this in as a class.
		If theres another input common to almost all, but could be applied to a
		class that doesn't need this, then it'll be time to jump into multiple
		inheritance
	"""

	# The times CheckListBox
	times = None

	# Magic number used to size some inputs
	input_width=180
	# Magic number used to size line heights
	dline = 18

	# Averaging options
	avgoption = "None"

	def __init__(self, parent):
		raise NotImplementedError( "Abstract method" )

	def getAveragingControls(self):
		""" Creates the averaging controls, and returns a sizer

		Returns:
		sizer - The controls in a sizer
		"""

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizerCombos = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=10)

		lblAvg = wx.StaticText(self, label="Averaging Time")
		rsizer=wx.FlexGridSizer(rows=len(Forcing.avgoptions),cols=2,hgap=5)
		for at in Forcing.avgoptions:
			radioinput=wx.RadioButton(self, label=at[1], name="avgtimes")
			radioinput.Bind(wx.EVT_RADIOBUTTON, self.chooseAveraging, radioinput)
			rsizer.Add(radioinput)
			avghelp = HelpLink(self, label="Help", onClick=self.ShowAvgHelp)
			rsizer.Add(avghelp)

		# Need to set the default.  Assuming that the first one is the default selected
		# radiobutton (this isn't a great assumption, fix when I have more time.)
		self.avgoption = Forcing.avgoptions[0][1]

		lbltimes = wx.StaticText(self, label="Use Hours:")
		# Take times from the top frame (it read them from the sample conc file)
		times_list=self.top.valid_times
		self.times = wx.CheckListBox(self, size=(self.input_width, 6*self.dline), choices=map(str, times_list))
		self.Bind(wx.EVT_CHECKLISTBOX, self.choseTimes, self.times)
		self.times.Enable(False)

		atdescription = wx.StaticText(self, size=(self.top.col2_width, -1),
		   label="This option finds the maximum X-hr average in a day and applies the forcing term to hours in that X-hr block.  Timezones are taken into account if input.")
		atdescription.Wrap(self.top.col2_width*.95)
		sizer.Add(atdescription)

		sizerCombos.Add(lblAvg)
		sizerCombos.Add(lbltimes)
		sizerCombos.Add(rsizer)
		sizerCombos.Add(self.times)

		sizer.Add(sizerCombos)

		# Time (hour) Mask
		time_warning=wx.StaticText(self, label="Note, there is currently no functionality to exclude specific days.", size=(self.parent.col2_width, -1))
		time_warning.Wrap(self.parent.col2_width*0.95)

		sizer.Add(time_warning)

		return sizer

#	def getAveraging(self):
#		rstr=self.avgoption
#		return rstr.split(' ')

	def chooseAveraging(self, event):
		radioSelected = event.GetEventObject()
		val = radioSelected.GetLabelText()
		if val == "Other" or val == "Local Hours":
			self.times.Enable(True)
		else:
			self.times.Enable(False)

		self.avgoption = val

		event.Skip()

	def ShowAvgHelp(self):
		# Fill in later
		pass

	def choseTimes(self, event):
		self.parent.debug('Chose times: [%s]' % ', '.join(map(str, self.times.GetCheckedStrings())))
		event.Skip()



class ForcingPanelAverageConcentration(ForcingPanelWithAveraging):
	# The name of the forcing function
	name = "Average Concentration"

	# Whether this should appear in the user selection for forcing functions
	appearInList=True

	forcingClass = None

	def __init__(self, parent):
		ForcingPanel.__init__(self, parent)

		# Debug stuff
		c = bc()	
		print "\n\n%sInitializing ForcingPanelAverageConcentration%s"%(c.red, c.clear)

		# Get an instance of our forcing class
		tv=self.top.validator
		self.forcingClass=ff.ForceOnAverageConcentration(tv.ni,tv.nj,tv.nk,tv.nt)

		mySize=self.parent.GetSize()
		#mySize[0]=mySize[0]*0.98
		mySize[0]=self.parent.col2_width*0.97

		sizer = wx.FlexGridSizer(rows=3, cols=1)
		sizerHead = wx.BoxSizer(wx.VERTICAL)
		sizerOpts = wx.GridBagSizer(10,10)

		"""
		User Edit: Enter the title and description
		"""

		# Title
		title_txt=self.name

		# Description
		descrip_txt="Represents the spatial and temporal average of a particular species for the selected running period and layers in the previous step. Note, if the threshold is set to \"0\", it will be ignored."


		"""
		/User Edit
		"""

		title=wx.StaticText(self, label=title_txt)
		descrip=wx.StaticText(self, label=descrip_txt, size=(self.parent.col2_width, -1))
		descrip.Wrap(mySize[0])

		# Add title and description to sizer
		sizerHead.Add(title, 0, wx.ALL)
		sizerHead.Add(descrip, 1, wx.EXPAND)


		"""
		User Edit: Create options for the forcing function
		"""

		# Options
		threshold_lbl = wx.StaticText(self, label="Specify threshold (ppb):")
		self.threshold = wx.TextCtrl(self, value="0", size=(40,-1))

		# Add Options to sizer
		sizerOpts.Add(threshold_lbl, pos=(1,1))
		sizerOpts.Add(self.threshold, pos=(1,2))

		# Add averaging and time options
		sizerOpts.Add(self.getAveragingControls(), pos=(3,1), span=(1,2))

		"""
		/User Edit
		"""

		# Add sizers to main sizer
		sizer.Add(sizerHead, wx.EXPAND)
		sizer.AddSpacer(10)
		sizer.Add(sizerOpts, wx.EXPAND)
		self.SetSizer(sizer)

	def runForce(self, top):

		# Forcing class
		fc = self.forcingClass

		# General inputs
		fc.maskLayers(top.layers)
		fc.species = top.species
		fc.maskSpace(top.spacialmask_fname, top.spacialmask_var, top.spacialmask_val)
		fc.griddedTimeZone = top.timezone_fname

		# Custom inputs
		fc.setAveraging(self.avgoption)
		fc.threshold = self.threshold.GetValue()

		# Inputs
		inputPath = top.inputPath
		inputFormat = top.inputFormat

		# Outputs
		fc.outputPath = top.outputPath
		fc.outputFormat = top.outputFormat

		#
		# Find the files we need
		concs=fc.FindFiles(file_format=inputFormat, path=inputPath,
		   date_min=top.date_min, date_max=top.date_max)

		# Load the input files into our forcing generator
		fc.loadConcentrationFiles(concs)

		# Debug..
		top.debug("Starting %s with files %s.\nTimezones=%s\nSpacial Mask File=%s\nAveraging:%s"%(type(fc), " ".join(map(str, concs)), fc.griddedTimeZone, top.spacialmask_fname, fc.averaging))

		#
		# Produce the forcing fields
		top.info("Processing ....")
		fc.produceForcingField(top.SimpleProgress, debug=True)
		top.info("Done!")

class ForcingPanelMortality(ForcingPanelWithAveraging):
	# The name of the forcing function
	name = "Mortality/Marginal Damage"

	# Whether this should appear in the user selection for forcing functions
	appearInList=True

	def __init__(self, parent):
		ForcingPanel.__init__(self, parent)

		sizer = wx.FlexGridSizer(rows=2, cols=1)
		sizerHead = wx.BoxSizer(wx.VERTICAL)
		sizerOpts = wx.FlexGridSizer(rows=2, cols=2, vgap=5)

		"""
		User Edit: Enter the title and description
		"""

		# Title
		title_txt=self.name

		# Description
		descrip_txt="My description"


		"""
		/User Edit
		"""

		sizerHead.Add(wx.StaticText(self, label=title_txt))
		descrip=wx.StaticText(self, label=descrip_txt)

		# Add title and description to sizer
		sizerHead.Add(descrip)

		"""
		User Edit: Create options for the forcing function
		"""

		# Options
		threshold_lbl = wx.StaticText(self, label="Concentration Response Factor:")
		self.threshold = wx.TextCtrl(self, value="Threshold morbid", size=(100,-1))

		statlife_lbl = wx.StaticText(self, label="Value of statistical life (M$):")
		self.statlife = wx.TextCtrl(self, value="", size=(100,-1))

		baseline_lbl = wx.StaticText(self, label="Baseline Mortality:")
		self.baseline = SingleFileChooser(self, label="Browse", name="mortality_baseline", fname="Baseline Mortality", fmessage="Choose baseline mortality file")

		pop_lbl = wx.StaticText(self, label="Population File Mortality:")
		self.pop=SingleFileChooser(self, label="Browse", name="pop_button", fname="Population", fmessage="Choose population file")

		# Add Options to sizer
		sizerOpts.Add(threshold_lbl)
		sizerOpts.Add(self.threshold)

		sizerOpts.Add(statlife_lbl)
		sizerOpts.Add(self.statlife)

		sizerOpts.Add(baseline_lbl)
		sizerOpts.Add(self.baseline)

		sizerOpts.Add(pop_lbl)
		sizerOpts.Add(self.pop)



		"""
		/User Edit
		"""

		# Add sizers to main sizer
		sizer.Add(sizerHead, wx.EXPAND)
		sizer.AddSpacer(10)
		sizer.Add(sizerOpts, wx.EXPAND)

		#self.SetSizer(sizer)
		self.SetSizerAndFit(sizer)



class ForcingPanelDistance(ForcingPanelWithAveraging):
	# The name of the forcing function
	name = "Distance"

	# Whether this should appear in the user selection for forcing functions
	appearInList=True

	def __init__(self, parent):
		#wx.Panel.__init__(self, parent, style=wx.SIMPLE_BORDER)
		ForcingPanel.__init__(self, parent)

		sizer = wx.FlexGridSizer(rows=2, cols=1)
		sizerHead = wx.BoxSizer(wx.VERTICAL)
		sizerOpts = wx.FlexGridSizer(rows=2, cols=2, vgap=5)

		"""
		User Edit: Enter the title and description
		"""

		# Title
		title_txt=self.name

		# Description
		descrip_txt="My description"


		"""
		/User Edit
		"""

		sizerHead.Add(wx.StaticText(self, label=title_txt))
		descrip=wx.StaticText(self, label=descrip_txt)

		# Add title and description to sizer
		sizerHead.Add(descrip)

		"""
		User Edit: Create options for the forcing function
		"""

		# Options
		obs_lbl = wx.StaticText(self, label="Observation File")
		self.obs = wx.Button(self, label="Browse..")

		# Add Options to sizer
		sizerOpts.Add(obs_lbl)
		sizerOpts.Add(self.obs)


		"""
		/User Edit
		"""

		# Add sizers to main sizer
		sizer.Add(sizerHead, wx.EXPAND)
		sizer.AddSpacer(10)
		sizer.Add(sizerOpts, wx.EXPAND)

		self.SetSizer(sizer)
