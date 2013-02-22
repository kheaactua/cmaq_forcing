import wx
import ForcingFunctions as f
import DoForce as df


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

	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
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
		wx.Panel.__init__(self, parent, style)
		self.parent = parent

		txt=wx.StaticText(self, label="Please choose a forcing function on the left panel")

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
		#avgtimes = ['None', 'Max 1 hr', 'Max 8 hr', 'Max 24 h', 'Local Hours', 'Other']
		avgtimes=df.Forcing.avgoptions.values()
		rsizer=wx.FlexGridSizer(rows=len(avgtimes),cols=2,hgap=5)
		for lbl in avgtimes:
			radioinput=wx.RadioButton(self, label=lbl, name="avgtimes")
			radioinput.Bind(wx.EVT_RADIOBUTTON, self.chooseAveraging, radioinput)
			rsizer.Add(radioinput)
			avghelp = wx.StaticText(self, label="Help")
			avghelp.SetForegroundColour((0,0,255))
			font=avghelp.GetFont();
			font.SetUnderlined(True)
			avghelp.SetFont(font)
			#avghelp.Bind(wx.EVT_LEFT_DOWN, self.ShowAvgHelp, lbl)
			rsizer.Add(avghelp)

		lbltimes = wx.StaticText(self, label="Use Hours:")
		# Take times from the top frame (it read them from the sample conc file)
		times_list=self.top.times_list
		print "Times_list: ", times_list
		self.times = wx.CheckListBox(self, size=(self.input_width, 6*self.dline), choices=times_list)
		self.Bind(wx.EVT_CHECKLISTBOX, self.choseTimes, self.times)
		self.times.Enable(False)

		sizerCombos.Add(lblAvg)
		sizerCombos.Add(lbltimes)
		sizerCombos.Add(rsizer)
		sizerCombos.Add(self.times)

		sizer.Add(sizerCombos)

		# Time (hour) Mask
		time_warning=wx.StaticText(self, label="Note, there is currently no functionality to exclude specific days.")

		sizer.Add(time_warning)

		return sizer

	def getAveraging(self):
		rstr=self.avgoption
		return rstr.split(' ')

	def chooseAveraging(self, event):
		radioSelected = event.GetEventObject()
		val = radioSelected.GetLabelText()
		if val == "Other" or val == "Local Hours":
			self.times.Enable(True)
		else:
			self.times.Enable(False)

		self.avgoption = val

		event.Skip()

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

		# Get an instance of our forcing class
		tv=self.top.validator
		self.forcingClass=f.ForceOnAverageConcentration(tv.ni,tv.nj,tv.nk,tv.nt)

		mySize=self.parent.GetSize()
		#mySize[0]=mySize[0]*0.98
		mySize[0]=300

		sizer = wx.FlexGridSizer(rows=3, cols=1)
		sizerHead = wx.BoxSizer(wx.VERTICAL)
		sizerOpts = wx.GridBagSizer(10,10)

		"""
		User Edit: Enter the title and description
		"""

		# Title
		title_txt=self.name

		# Description
		descrip_txt="Represents the spatial and temporal average of a particular species for the selected running period and layers in the previous step. The user should specify"


		"""
		/User Edit
		"""

		title=wx.StaticText(self, label=title_txt)
		descrip=wx.StaticText(self, label=descrip_txt)
		descrip.Wrap(mySize[0])

		# Add title and description to sizer
		sizerHead.Add(title, 0, wx.ALL)
		sizerHead.Add(descrip, 1, wx.EXPAND)


		"""
		User Edit: Create options for the forcing function
		"""

		# Options
		threshold_lbl = wx.StaticText(self, label="Specify threshold (ppb):")
		self.threshold = wx.TextCtrl(self, value="Threshold avg conc", size=(300,-1))

		# Add Options to sizer
		sizerOpts.Add(threshold_lbl, pos=(1,1))
		sizerOpts.Add(self.threshold, pos=(2,1))

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

	def runForce(self, common):

		# Forcing class
		fc = self.forcingClass

		# Get all the info we need
		print "fc: ", fc
		layers = common.getLayers()
		print "layers: ", layers
		fc.maskLayers(common.getLayers())
		fc.setSpecies(common.getSpecies())
		fc.setOutputFormat(common.getOutputFormat())
		fc.setAveraging(self.getAveraging())

		fformat = common.getFormat()
		concs=fc.FindFiles(self.top.conc_path, fformat, self.top.date_min, self.top.date_max)
		fc.loadConcentrationFiles(concs)

		# Produce the forcing feilds
		fc.produceForcingField(self.top.SimpleProgress, dryrun=False)

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

		title=wx.StaticText(self, label=title_txt)
		descrip=wx.StaticText(self, label=descrip_txt)

		# Add title and description to sizer
		sizerHead.Add(title, wx.ALL)
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
		self.baseline = wx.Button(self, label="Browse..")

		pop_lbl = wx.StaticText(self, label="Population File Mortality:")
		self.pop = wx.Button(self, label="Browse..")


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

		self.SetSizer(sizer)



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

		title=wx.StaticText(self, label=title_txt)
		descrip=wx.StaticText(self, label=descrip_txt)

		# Add title and description to sizer
		sizerHead.Add(title, wx.ALL)
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
