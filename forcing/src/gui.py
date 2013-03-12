# GUY Lib
import wx, wx.richtext
import os

from Validator import *
from ForcingPanels import *
from DoForce import Forcing
from datetime import date, timedelta

# Just for debugging
from bcolours import bcolours as bc

class ForcingFrame(wx.Frame):
	""" Main window for the forcing app.  The code in this file needs upgrading. (sloppy) """

	LOG_HELP  = 2
	LOG_ERROR = 4
	LOG_WARN  = 8
	LOG_INFO  = 16
	LOG_DEBUG = 32

	# The validator is not much of a validator anymore (it might be once the
	# CLI interface is more complete) but more of a getter from the NetCDF file
	validator=None

	# This does nothing
	col1_width=500
	col2_width=400

	pan_sample_conc = None
	pan_ginputs = None
	fpm = None

	valid_times=[]

	#
	# State varibles
	#
	_species = []
	_layers = []



	# File formats
	inputFormatDefault = "CCTM_fwdACONC*YYYYMMDD"
	outputFormatDefault = "Force.TYPE.YYYYMMDD"
	_inputFormat = "CCTM*YYYYMMDD"
	_outputFormat = "Force.TYPE.YYYYMMDD"

	# Paths
	inputPath = None
	outputPath = None


	#def __init__(self,parent, id=-1, title="Forcing File Generator", pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE, name=wx.FrameNameStr):
	def __init__(self, parent, id=-1, title="Forcing File Generator", pos=(1000,0), size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE, name="TopFrame"):
		wx.Frame.__init__(self, parent, id=id, title=title, pos=pos, size=size, style=style, name=name)

		# Used to capture CTRL-W and CTRL-Q to quit
		randomId = wx.NewId()
		self.Bind(wx.EVT_MENU, self.onKeyCombo, id=randomId)
		accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL,  ord('W'), randomId), (wx.ACCEL_CTRL,  ord('Q'), randomId)])
		self.SetAcceleratorTable(accel_tbl)

		# Create a menu bar
		menubar = wx.MenuBar()
		mfile = wx.Menu()
		mfile.Append(101, '&Load configuration', 'Load configuration options to populate GUI options')
		mfile.Append(102, '&Save configuration', 'Save current settings to a file')
		mfile.Append(103, '&Quit', 'Quit')

		mhelp = wx.Menu()
		mhelp.Append(201, '&About', 'About')

		# Add these to the menu bar
		menubar.Append(mfile, '&File')
		menubar.Append(mhelp, '&Help')

		# Set the menu bar
		self.SetMenuBar(menubar)
		self.CreateStatusBar()


		# Initialize the forcing panel manager
		self.fpm = ForcingPanelManager()

		# Sample concentration Panel
		self.pan_sample_conc = SampleConcPanel(self)

		# Inputs panel
		self.pan_input = InputPanel(self)

		# Outputs panel
		self.pan_output = OutputPanel(self)

		# Dates panel
		self.pan_dates = DatePanel(self)

		# General Inputs Panel
		self.pan_ginputs = GeneralInputsPanel(self)
		self.pan_ginputs.Enable(False)

		# Forcing Panel
		self.pan_force = ForcingPanelBlank(self)

		# Add events
		panels = [self.pan_sample_conc, self.pan_input, self.pan_output, self.pan_dates, self.pan_ginputs, self.pan_force];
		for p in panels:
			p.Bind(wx.EVT_MENU, self.onKeyCombo, id=randomId)
		panels = [self.pan_input, self.pan_output, self.pan_dates, self.pan_ginputs, self.pan_force];
		for p in panels:
			p.Enable(False)


		# Put logger at bottom
		sizerAll = wx.BoxSizer(wx.VERTICAL)

		# Most inputs go in col1, custom forcing goes into two
		self.cols = wx.BoxSizer(wx.HORIZONTAL)

		# Left column
		leftCol = wx.BoxSizer(wx.VERTICAL)
		leftCol.Add(self.pan_sample_conc)
		leftCol.AddSpacer(5)
		leftCol.Add(self.pan_input)
		leftCol.AddSpacer(5)
		leftCol.Add(self.pan_output)
		leftCol.AddSpacer(5)
		leftCol.Add(self.pan_dates)
		leftCol.AddSpacer(5)
		leftCol.Add(self.pan_ginputs)

		# Right column
		rightCol = wx.BoxSizer(wx.VERTICAL)
		title=wx.StaticText(self, label="Cost Function")
		font = wx.Font(15, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
		title.SetFont(font)

		rightCol.Add(title)
		rightCol.AddSpacer(10)
		#self.pan_force.SetSize((-1, self.pan_ginputs.GetSize()[1]*.9))
		rightCol.Add(self.pan_force, flag=wx.EXPAND)

		self.runbtn=wx.Button(self, label="Run", name="runbtn")
		self.runbtn.Bind(wx.EVT_BUTTON, self.runForce)
		self.runbtn.Enable(False)
		rightCol.Add(self.runbtn, flag=wx.ALIGN_BOTTOM|wx.EXPAND)

		# So we can reference it later
		self.forcingSizer=rightCol

		# Add columns
		self.cols.Add(leftCol)
		self.cols.AddSpacer(10)
		self.cols.Add(rightCol, flag=wx.EXPAND)

		# Add columns
		sizerAll.Add(self.cols)
		sizerAll.AddSpacer(5)

		# Add logger
		self.logger=wx.richtext.RichTextCtrl(self, size=(-1, 300), style=wx.TE_MULTILINE | wx.TE_READONLY)
		sizerAll.Add(self.logger, flag=wx.EXPAND)

		#self.SetSizer(sizerAll)
		#self.Fit()
		self.SetSizerAndFit(sizerAll)
		#self.Layout()

		# TEMP!
#		conc_dir = os.getcwd() + '/dena/'
#		self.pan_input.inputPathCtrl.SetValue(conc_dir)
#		self.pan_output.outputPathCtrl.SetValue(os.getcwd() + '/output/')
#		self.validator = ForcingValidator(conc_dir + 'CCTM_fwdACONC.20070910')
#		self.date_min  = date(2007,9,10)
#		self.date_max  = date(2007,9,11)

#!		conc_dir = os.getcwd() + '/basic_concentrations/'
#!		self.pan_input.inputPathCtrl.SetValue(conc_dir)
#!		self.pan_output.outputPathCtrl.SetValue(os.getcwd() + '/output/')
#!		self.validator = ForcingValidator(conc_dir + 'CCTM.20050505')
#!		self.pan_dates.updateDate(date(2005,5,5))
#!		self.pan_dates.updateDate(date(2005,5,7), True)
#!		self.pan_ginputs.timezone_fname.path = conc_dir + 'timezones.nc'
#!
#!		self.debug("Setting min date to sample conc date, i.e. %s"%self.date_min)
#!		self.pan_ginputs.Enable(True)

		# TEMP
#!		self.pan_ginputs.species.SetChecked([0])


		conc_dir = os.getcwd() + '/mortality/'
		self.pan_input.inputPathCtrl.SetValue(conc_dir)
		self.pan_output.outputPathCtrl.SetValue(os.getcwd() + '/output/')
		self.validator = ForcingValidator(conc_dir + 'CCTM_fwdACONC.20070701')
		self.pan_input.inputFormatCtrl.SetValue('CCTM_fwdACONC.YYYYMMDD')
		self.pan_dates.updateDate(date(2007,7,1))
		self.pan_dates.updateDate(date(2007,7,3), True)
		self.pan_ginputs.timezone_fname.path = os.getcwd() + '/GriddedTimeZoneMask.nc'
		self.pan_ginputs.spacialmask_fname.path='SpacialMask.nc'
		self.pan_ginputs.spacialmask_var.SetValue('USA')
		self.pan_ginputs.spacialmask_val.SetValue(str(2))

		self.pan_dates.Enable(True)
		self.pan_ginputs.Enable(True)
		self.pan_ginputs.species.SetChecked([0])
		fp = self.pan_ginputs.setForcingPanel('Mortality/Marginal Damage')
		fp.beta.SetValue(str(0.000427))
		fp.mortality_fname.path=conc_dir + '/DOMAIN_POP_BMR'
		fp.mortality_var.SetValue('BMR')
		fp.pop_fname.path=fp.mortality_fname.path
		fp.pop_var.SetValue('POP')

	def onKeyCombo(self, event):
		self.Close()

	"""
	The following getters are used by the ForcingPanels as they know how to call
	the specific forcing functions.

	So, the save button tells these panels to go, and they call these getters
	and call the forcing functions.

	These getters should be part of an interface
	"""
	@property
	def species(self):
		self._species=list(self.pan_ginputs.species.GetCheckedStrings())
		self.debug("Returning species: %s"%', '.join(map(str, self._species)))
		return self._species

	@property
	def layers(self):
		self._layers=list(self.pan_ginputs.layers.GetCheckedStrings())
		if self._layers[0] == ForcingValidator.LAY_SURFACE_NAME:
			self._layers[0] = 1
		self.debug("Returning layers: %s"%', '.join(map(str, self._layers)))
		return self._layers

	@property
	def inputPath(self):
		return self.pan_input.inputPathCtrl.GetValue()

	@property
	def inputFormat(self):
		_inputFormat=self.pan_input.inputFormatCtrl.GetValue()
		return self._inputFormat

	@property
	def outputPath(self):
		return self.pan_output.outputPathCtrl.GetValue()

	@property
	def outputFormat(self):
		return self.pan_output.outputFormatCtrl.GetValue()

	@property
	def spacialmask_fname(self):
		return self.pan_ginputs.spacialmask_fname.path

	@property
	def spacialmask_var(self):
		return self.pan_ginputs.spacialmask_var.GetValue()

	@property
	def spacialmask_val(self):
		return self.pan_ginputs.spacialmask_val.GetValue()

	@property
	def timezone_fname(self):
		return self.pan_ginputs.timezone_fname.path

	# Boundary dates on concentration files
	@property
	def date_min(self):
		wxdate = self.pan_dates.date_min.GetValue()
		# The +1 is because wxDateTime starts months at 0
		return date(wxdate.GetYear(), wxdate.GetMonth()+1, wxdate.GetDay())
	@property
	def date_max(self):
		wxdate = self.pan_dates.date_max.GetValue()
		return date(wxdate.GetYear(), wxdate.GetMonth()+1, wxdate.GetDay())

	""" Logging Methods """
	def log(self, msg, level):
		""" Basic logging function, intended to be called by self.debug(), or self.warn(), etc.. """
		c = bc()
		if level == self.LOG_ERROR:
			prefix='E'
			mc=c.red
			rc=(255,0,0)
		elif level == self.LOG_WARN:
			prefix='W'
			mc=c.yellow
			rc=(218,165,32)
		elif level == self.LOG_HELP:
			prefix='H'
			mc=c.clear
			rc=(0,0,0)
		elif level == self.LOG_INFO:
			prefix='I'
			mc=c.blue
			rc=(0,0,200)
		elif level == self.LOG_DEBUG:
			prefix = 'D'
			mc=c.green
			rc=(0,200,0)
		else:
			prefix='U'
			mc=c.clear
			rc=(0,0,0)

		coloured_msg = "[%s] %s%s%s"%(prefix, mc, msg, c.clear)
		plain_msg = "[%s] %s\n"%(prefix, msg)
		self.logger.BeginTextColour(rc)
		self.logger.WriteText(plain_msg)
		self.logger.BeginTextColour((0,0,0))
		print coloured_msg

	def info(self, msg):
		""" Generate an 'info' message """
		self.log(msg,self.LOG_INFO)
	def error(self, msg):
		""" Generate an 'error' message """
		self.log(msg,self.LOG_ERROR)
	def warn(self, msg):
		""" Generate a 'warning' message """
		self.log(msg,self.LOG_WARN)
	def debug(self, msg, level=0):
		""" Generate a 'debug' message """
		# HACK
		# Filter out high level (low importance) debug messages
		if level<=1:
		# /HACK
			self.log(msg,self.LOG_DEBUG)
	def help(self, msg):
		""" Generate a 'help' message """
		self.log(msg,self.LOG_HELP)

	def ShowFormatHelp(self, event):
		self.help("To specify a format: year=YYYY (2007) or YY (07), juldate=JJJ, month=MM, day=DD")
		event.Skip()

	#@staticmethod
	def SimpleProgress(self, prog, dfile):
		""" Simple file to output progress to the logging pane

		Keyword Arguments:

		prog:*float*
		   Percentage of files processed

		dfile:*Datafile*
		   The file currently being worked on
		"""

		self.info("Progress: %0.0f%%, file: %s"%(prog*100.0, dfile.name))
		

	def runForce(self, event):
		""" This is the function that should start everything """
		#print "[Todo]: call a forcingPanel.run(), which will call the right Forcing class in ForcingFunctions with all the info it needs."

		self.pan_force.runForce(self)

		event.Skip()


#	def Close(self):
#		wx.Frame.Close(self)

class SampleConcPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)

		self.parent=parent

		# the edit control - one line version.
		instructions = wx.StaticText(self, label="First, choose a sample concentration used to validate options against.", pos=(10,10))

		line2=30
		conc_lbl = wx.StaticText(self, label="Concentration :", pos=(20,line2))
		self.conc_file = wx.TextCtrl(self, value="Concentration file", pos=(150, line2), size=(200,-1))
		self.conc_file.SetEditable(False)
		conc_file_browse = wx.Button(self, label="Choose file", pos=(360, line2))
		conc_file_browse = self.Bind(wx.EVT_BUTTON, self.chooseSampleConc)

	def chooseSampleConc(self, event):
		""" Choose a file, and write it to the text box """
		dlg = wx.FileDialog(self,
		   message="Concentration File",
		   defaultDir=os.getcwd())

		if dlg.ShowModal() == wx.ID_OK:
			paths = dlg.GetPaths()
			path=paths[0]
			self.parent.info("Sample concentration file: %s"%path)
			self.parent.input_path = os.path.dirname(os.path.abspath(path))
			self.parent.debug("Concentration Path: %s"%self.parent.input_path)
			self.conc_file.SetValue(path)
			if self.parent.validator != None:
				del self.parent.validator

			try:
				self.parent.validator = ForcingValidator(path)
				try:
					date_min  = self.parent.validator.getDate()
				except IOError as e:
					self.parent.error("%s.  Please select a new sample concentration file."%str(e))
					return
				#self.parent.date_max  = self.validator.getDate() + datetime.timedelta(days=2)
				self.parent.debug("Setting min date to sample conc date, i.e. %s"%self.parent.date_min)
				self.parent.pan_dates.updateDate(date_min)
				self.parent.pan_dates.updateDate(date_min + timedelta(days=2), True)

				# Enable the input panels
				panels = [self.parent.pan_input, self.parent.pan_output, self.parent.pan_dates, self.parent.pan_ginputs];
				for p in panels:
					p.Enable(True)
			except IOError as e:
				self.parent.error("I/O error({0}): {1}".format(e.errno, e.strerror))
				self.parent.validator = None
				self.parent.pan_ginputs.Enable(False)

class LoggingPanel(wx.Panel):
	logger = None
	def __init__(self, parent, size=wx.DefaultSize):
		wx.Panel.__init__(self, parent, size=size)
		self.parent = parent

		fsize=parent.GetSize()

		#print "Logging Panel [%s]: Parent size: "%parent.GetName(), fsize

		# A multiline TextCtrl - This is here to show how the events work in this program, don't pay too much attention to it
		#self.logger = wx.TextCtrl(self, pos=(10,fsize[1]-200), size=(fsize[0]-20,190), style=wx.TE_MULTILINE | wx.TE_READONLY)
		self.logger = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)
		self.logger.SetSize(fsize)


class InputPanel(wx.Panel):
	""" This panel requests concentration path and format from the user """

	def __init__(self, parent, size = wx.DefaultSize):
		wx.Panel.__init__(self, parent, size=size, style=wx.SUNKEN_BORDER)
		self.parent = parent


		sizerMain = wx.BoxSizer(wx.VERTICAL)

		instFormat = wx.StaticText(self, label="Enter the format pattern for input concentration files.  i.e. aconc.*.YYYYJJJ", size=(self.parent.col1_width, -1))
		#instFormat.Wrap(400)
		sizerMain.Add(instFormat)

		# Create a sub sizer just for these inputs
		sizer = wx.FlexGridSizer(rows=2, cols=2)

		tmp=wx.StaticText(self, label="Format:")
		input_width=parent.col1_width-tmp.GetSize()[0]

		sizer.Add(wx.StaticText(self, label="Path:"))
		self.inputPathCtrl = wx.TextCtrl(self, value=os.getcwd(), size=(input_width,-1))
		sizer.Add(self.inputPathCtrl)

		sizer.Add(tmp)
		self.inputFormatCtrl = wx.TextCtrl(self, value=self.parent.inputFormatDefault, size=(input_width,-1))
		sizer.Add(self.inputFormatCtrl)

		sizerMain.Add(sizer)

		sizerMain.Add(HelpLink(self, label="Need help with formats?", onClick=self.parent.ShowFormatHelp))

		testFormatCtrl = wx.Button(self, label="Test Format", pos=(200, 325))
		testFormatCtrl.Bind(wx.EVT_BUTTON, self.testFormat)
		sizerMain.Add(testFormatCtrl)

		self.SetSizer(sizerMain)

	def testFormat(self, event):
		files=Forcing.FindFiles(file_format=self.inputFormatCtrl.GetValue(), path=self.inputPathCtrl.GetValue())
		self.parent.info("Found files: %s" % ', '.join(map(str, files)))
		# Update date ranges
		# TEMP HACK, commented this out for simplicity
		#self.parent.date_min=files[0].date
		#self.parent.date_max=files[-1].date
		#self.updateDateRange(self.parent.date_min, self.parent.date_max)
		#self.updateDate(self.parent.date_min)
		#self.updateDate(self.parent.date_max, True)
		event.Skip()

class OutputPanel(wx.Panel):
	""" This panel requests output path and format from the user """

	def __init__(self, parent, size = wx.DefaultSize, style=wx.SUNKEN_BORDER):
		wx.Panel.__init__(self, parent, size=size, style=style)
		self.parent = parent

		sizerMain = wx.BoxSizer(wx.VERTICAL)

		instFormat = wx.StaticText(self, label="Enter the format pattern for output concentration files. i.e. Force.TYPE.YYYYJJJ", size=(self.parent.col1_width,-1))
		sizerMain.Add(instFormat)

		# Create a sub sizer just for these outputs
		sizer = wx.FlexGridSizer(rows=2, cols=2)

		tmp=wx.StaticText(self, label="Format:")
		input_width=parent.col1_width-tmp.GetSize()[0]

		sizer.Add(wx.StaticText(self, label="Path:"))
		self.outputPathCtrl = wx.TextCtrl(self, value=os.getcwd() + "/output/", size=(input_width,-1))
		sizer.Add(self.outputPathCtrl)

		sizer.Add(tmp)
		self.outputFormatCtrl = wx.TextCtrl(self, value=self.parent.outputFormatDefault, size=(input_width,-1))
		sizer.Add(self.outputFormatCtrl)

		sizerMain.Add(sizer)

		self.SetSizer(sizerMain)

class DatePanel(wx.Panel):

	date_min = None
	date_max = None

	def __init__(self, parent, size = wx.DefaultSize, style=wx.SUNKEN_BORDER):
		wx.Panel.__init__(self, parent, size=size, style=style)
		self.parent = parent

		sizerMain = wx.BoxSizer(wx.VERTICAL)

		# Input date range
		# This is messy.....
		sizerMain.AddSpacer(10)
		instruct_dates = wx.StaticText(self, label="Time frame to process", size=(self.parent.col1_width,-1))
		sizerMain.Add(instruct_dates)
		sizerDates = wx.FlexGridSizer(rows=2, cols=2, vgap=5, hgap=5)

		sizerDates.Add(wx.StaticText(self, label="Start date"))
		sizerDates.Add(wx.StaticText(self, label="End date"))

		self.date_min = wx.DatePickerCtrl(self, size=(200, -1) )
# Matt: Figure out how to get rid of the retarded US format
		sizerDates.Add(self.date_min)

		self.date_max = wx.DatePickerCtrl(self, size=(200,-1))
		sizerDates.Add(self.date_max)
		sizerMain.Add(sizerDates)

		self.SetSizer(sizerMain)

#	def updateDateRange(self, d1, d2):
#		""" Updates the available date ranges """
#
#		sdate=wx.DateTime.Now()
#		if d1 != None:
#			sdate.Set(d1.day, d1.month, d1.year)
#		edate=wx.DateTime.Now()
#		if d2 != None:
#			sdate.Set(d2.day, d2.month, d2.year)
#		self.date_min.SetRange(sdate, edate)
#		self.date_max.SetRange(sdate, edate)

	def updateDate(self, d, mm=0):
		""" Updates the date choosers

		Keyword Arguments:

			d:*datetime*
			  Datetime to set it to

			mm:*bool*
			  False for min date, true for max date

		"""
		sdate=wx.DateTime.Now()
		if d != None:
			sdate.Set(d.day, d.month-1, d.year)
		if mm:
			print "Received %s, Setting date_max to %s"%(d, sdate)
			self.date_max.SetValue(sdate)
		else:
			print "Received %s, Setting date_min to %s"%(d, sdate)
			self.date_min.SetValue(sdate)


class GeneralInputsPanel(wx.Panel):
	parent = None

	avgoption = None

	def __init__(self, parent, size = wx.DefaultSize, style=wx.SUNKEN_BORDER):
		wx.Panel.__init__(self, parent, size=size, style=style)
		self.parent = parent

		mySize=self.parent.GetSize()
		mySize[0]=mySize[0]*0.98

		sizerMain = wx.BoxSizer(wx.VERTICAL)
		sizerCombos = wx.FlexGridSizer(rows=2, cols=2, vgap=10, hgap=10)
		sizerTexts = wx.FlexGridSizer(rows=1, cols=2, vgap=10, hgap=5)
		sizerFormat = wx.FlexGridSizer(rows=1, cols=3, hgap=10)
		
		dline=18
		input_width=180

		sizerMain.AddSpacer(10)
		instruct1 = wx.StaticText(self, label="Choose the species you will input into the forcing function.", size=(self.parent.col1_width, -1))
		#instruct1.Wrap(mySize[0])
		sizerMain.Add(instruct1)
		sizerMain.AddSpacer(10)


		# Species
		lblspecies = wx.StaticText(self, label="Species:")
		if parent.validator != None:
			species_list = parent.validator.getSpecies();
		else:
			species_list = []
		self.species = wx.CheckListBox(self, size=(input_width, 4*dline), choices=species_list)
		self.Bind(wx.EVT_CHECKLISTBOX, self.choseSpecies)


		# Layer mask
		lbllayers = wx.StaticText(self, label="Use Layers:")
		if parent.validator != None:
			layers_list = parent.validator.getLayers();
		else:
			layers_list = []
		self.layers = wx.CheckListBox(self, size=(input_width, 4*dline), choices=layers_list)
		self.Bind(wx.EVT_CHECKLISTBOX, self.choseLayers, self.layers)

		# Add to sizer
		sizerCombos.Add(lblspecies)
		sizerCombos.Add(lbllayers)
		sizerCombos.Add(self.species)
		sizerCombos.Add(self.layers)



		# Add combos
		sizerMain.Add(sizerCombos)

		# Shape file masks
		spacialSizer = wx.FlexGridSizer(rows=2, cols=3, vgap=1, hgap=5)

		spacialSizer.Add(wx.StaticText(self, label="Spacial Mask:"))
		spacialSizer.Add(wx.StaticText(self, label="Variable"))
		spacialSizer.Add(wx.StaticText(self, label="Value"))

		self.spacialmask_fname = SingleFileChooser(self, label="Spacial Mask File", name="specialmask_fname", fname="Spacial Mask", fmessage="Choose gridded spacial mask NetCDF file")
		spacialSizer.Add(self.spacialmask_fname)

		self.spacialmask_var = wx.TextCtrl(self, value='USA', size=(50,-1))
		spacialSizer.Add(self.spacialmask_var)

		self.spacialmask_val = wx.TextCtrl(self, value='2', size=(30,-1))
		spacialSizer.Add(self.spacialmask_val)

		sizerMain.AddSpacer(10)
		sizerMain.Add(spacialSizer)

		# Timezone
		sizerTexts.Add(wx.StaticText(self, label="Timezones:"))
		self.timezone_fname = SingleFileChooser(self, label="Timezone File", name="timezone_fname", fname="Timezone", fmessage="Choose gridded timezone NetCDF file")
		sizerTexts.Add(self.timezone_fname)


		# Forcing Options
		sizerTexts.Add(wx.StaticText(self, label="Forcing Function:"))

		options = self.parent.fpm.getNames()
		self.forcing = wx.ComboBox(self, value="Choose", choices=options, size=(input_width, -1), style=wx.CB_READONLY)
		self.Bind(wx.EVT_COMBOBOX, self.chooseForce)

		sizerTexts.Add(self.forcing)

		## A button
		#self.button =wx.Button(self, label="Save", pos=(200, 325))
		#self.Bind(wx.EVT_BUTTON, self.OnClick,self.button)

		sizerMain.AddSpacer(15)
		sizerMain.Add(sizerTexts)
		self.SetSizer(sizerMain)


	def choseSpecies(self, event):
		self.parent.debug('Chose species: [%s]' % ', '.join(map(str, self.species.GetCheckedStrings())))

	def choseLayers(self, event):
		self.parent.debug('Chose layers: [%s]' % ', '.join(map(str, self.layers.GetCheckedStrings())))


	def chooseForce(self, event):
		item_id = event.GetSelection()
		item = self.forcing.GetValue()

		self.setForcingPanel(item)
		pass

	def setForcingPanel(self, forcing_name):
		""" This code was broken off of the above 'chooseForce' simply so I could set the panel
		without creating a fake event or anything.  This function removes the current forcing
		panel and replaces it with the one specified by forcing_name """

		# Get an object for this panel
		oldPanForce=self.parent.pan_force
		newPanForce=ForcingPanelManager.factory(forcing_name, self.parent)

		sizer=self.parent.forcingSizer
		panel_id=1

		# Replace this in the sizer
		res=sizer.Detach(panel_id)
		#self.parent.debug("Panel was detached? %r"%res)
		oldPanForce.Hide()
		res=oldPanForce.Destroy()
		#self.parent.debug("Panel (%s) was destroyed? %r"%(str(oldPanForce), res))

		sizer.Insert(panel_id, newPanForce, wx.EXPAND)

		self.parent.pan_force=newPanForce

		# Refresh..
		sizer.Layout()
		#self.parent.Fit()
		self.parent.Update()

		self.parent.debug('Chose forcing: [%s]' % forcing_name)

		# Enable run button
		self.parent.runbtn.Enable(True)

		return newPanForce

	def Enable(self, doEnable):
		""" When enabled, populate stuff that was waiting on a concentration file """
		wx.Panel.Enable(self, doEnable)

		#if self.IsEnabled is True:
		if doEnable is True:

			# Populate species
			if self.parent.validator != None:
				species_list = self.parent.validator.getSpecies();
				self.parent.debug("Received species list: " + '[%s]' % ', '.join(map(str, species_list)), 2)
			else:
				self.parent.warn("Cannot load species list!")
				species_list = []

			self.species.Clear()
			self.parent.debug("Setting species in combo box", 2)
			self.species.SetItems(species_list)

			# Populate layers
			if self.parent.validator != None:
				layers_list = self.parent.validator.getLayers();
				self.parent.debug("Received layers list: " + '[%s]' % ', '.join(map(str, layers_list)), 2)
			else:
				self.parent.warn("Cannot load layer list!")
				layers_list = []

			self.layers.Clear()
			self.parent.debug("Setting layers in combo box", 2)
			self.layers.SetItems(layers_list)
			self.layers.Check(0)

			# Populate times
			if self.parent.validator != None:
				times_list = self.parent.validator.getTimes()
				self.parent.debug("Received times list: " + '[%s]' % ', '.join(map(str, times_list)))
			else:
				self.parent.warn("Cannot load times!")
				times_list = []

			self.parent.valid_times = map(int, times_list)

			#self.times.Clear()
			#self.parent.debug("Setting times in combo box")
			#self.times.SetItems(times_list)
			#for i in range(0,len(times_list)):
			#	self.times.Check(i)

			# Enable run button
			#self.parent.runbtn.Enable(True)


