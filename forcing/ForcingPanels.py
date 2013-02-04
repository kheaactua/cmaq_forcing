import wx

class ForcingPanelManager:
	panels=['ForcingPanelBlank', 'ForcingPanelAveragingConcentration',
		   'ForcingPanelMortality', 'ForcingPanelRootSquare']

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

class ForcingPanelBlank(ForcingPanel):
	parent = None

	# The name of the forcing function
	name = "Blank"

	# Whether this should appear in the user selection for forcing functions
	appearInList=False

	def __init__(self, parent):

		wx.Panel.__init__(self, parent, style=wx.SIMPLE_BORDER)
		self.parent = parent

		txt=wx.StaticText(self, label="Please choose a forcing function above")

		sizer = wx.BoxSizer(wx.ALIGN_CENTER_VERTICAL)
		sizer.Add(txt, 0, wx.EXPAND)
		self.SetSizer(sizer)

class ForcingPanelAveragingConcentration(ForcingPanel):
	parent = None

	# The name of the forcing function
	name = "Averaging Concentration"

	# Whether this should appear in the user selection for forcing functions
	appearInList=True

	def __init__(self, parent):
		wx.Panel.__init__(self, parent, style=wx.SIMPLE_BORDER)
		self.parent = parent

		mySize=self.parent.GetSize()
		mySize[0]=mySize[0]*0.98

		print "Mysize: ", mySize

		sizer = wx.FlexGridSizer(rows=2, cols=1)
		sizerHead = wx.BoxSizer(wx.VERTICAL)
		sizerOpts = wx.FlexGridSizer(rows=1, cols=2)

		"""
		User Edit: Enter the title and description
		"""

		# Title
		title_txt=self.name

		# Description
		descrip_txt="Nulla eget metus urna, ut convallis elit. Sed vitae sodales sem. Integer fermentum commodo erat sit amet interdum. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Phasellus at mi neque. Vestibulum porttitor elementum risus non auctor."


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
		sizerOpts.Add(threshold_lbl, 1)
		sizerOpts.Add(self.threshold, 2)


		"""
		/User Edit
		"""

		# Add sizers to main sizer
		sizer.Add(sizerHead, wx.EXPAND)
		sizer.AddSpacer(10)
		sizer.Add(sizerOpts, wx.EXPAND)
		self.SetSizer(sizer)

class ForcingPanelMortality(ForcingPanel):
	parent = None

	# The name of the forcing function
	name = "Mortality/Marginal Damage"

	# Whether this should appear in the user selection for forcing functions
	appearInList=True

	def __init__(self, parent):
		wx.Panel.__init__(self, parent, style=wx.SIMPLE_BORDER)
		self.parent = parent

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

		statlife_lbl = wx.StaticText(self, label="Value of statistical life:")
		self.statlife = wx.TextCtrl(self, value="", size=(100,-1))

		baseline_lbl = wx.StaticText(self, label="Baseline Mortality:")
		self.baseline = wx.TextCtrl(self, value="", size=(100,-1))

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



class ForcingPanelRootSquare(ForcingPanel):
	parent = None

	# The name of the forcing function
	name = "Root Square"

	# Whether this should appear in the user selection for forcing functions
	appearInList=True

	def __init__(self, parent):
		wx.Panel.__init__(self, parent, style=wx.SIMPLE_BORDER)
		self.parent = parent

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
		self.obs_lbl = wx.Button(self, label="Browse..")

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
