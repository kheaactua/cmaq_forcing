# GUY Lib
import wx
import os

from ForcingValidator import *

class ForcingFrame(wx.Frame):
	LOG_ERROR = 1
	LOG_WARN  = 2
	LOG_INFO  = 3
	LOG_DEBUG = 4

	validator=None

	def __init__(self,parent, id=-1, title="Forcing File Generator", pos=wx.DefaultPosition, size=(500,400), style=wx.DEFAULT_FRAME_STYLE, name=wx.FrameNameStr):
		wx.Frame.__init__(self, parent, id=id, title=title, pos=pos, size=size, style=style, name=name)

		randomId = wx.NewId()
		self.Bind(wx.EVT_MENU, self.onKeyCombo, id=randomId)
		accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL,  ord('W'), randomId), (wx.ACCEL_CTRL,  ord('Q'), randomId)])
		self.SetAcceleratorTable(accel_tbl)

		# Events Panel
		self.pan_log = LoggingPanel(self)

		# Sample concentration Panel
		self.pan_sample_conc = SampleConcPanel(self)

		# Inputs Panel
		self.pan_inputs = InputsPanel(self)
		self.pan_inputs.Enable(False)

		# Add events
		panels = [self.pan_log, self.pan_sample_conc, self.pan_inputs];
		for p in panels:
			p.Bind(wx.EVT_MENU, self.onKeyCombo, id=randomId)

		#self.sizer = wx.FlexGridSizer(wx.VERTICAL)
		self.sizer = wx.FlexGridSizer(rows=3, cols=1)
		self.sizer.Add(self.pan_sample_conc, 1, wx.EXPAND)
		self.sizer.Add(self.pan_inputs, 2, wx.EXPAND)
		self.sizer.Add(self.pan_log, 3, wx.EXPAND)

		self.SetSizer(self.sizer)
		self.Fit()

	def onKeyCombo(self, event):
		self.Close()

	""" Logging Methods """
	def log(self, msg, level):
		if level == self.LOG_ERROR:
			prefix='E'
		elif level == self.LOG_WARN:
			prefix='W'
		elif level == self.LOG_INFO:
			prefix='I'
		elif level == self.LOG_DEBUG:
			prefix = 'D'
		else:
			prefix='U'

		full_msg = "[%s] %s"%(prefix, msg)
		self.pan_log.logger.AppendText(full_msg + "\n")
		print full_msg
	def info(self, msg):
		self.log(msg,self.LOG_INFO)
	def error(self, msg):
		self.log(msg,self.LOG_ERROR)
	def warn(self, msg):
		self.log(msg,self.LOG_WARN)
	def debug(self, msg):
		self.log(msg,self.LOG_DEBUG)

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
			self.conc_file.SetValue(path)
			if self.parent.validator == None:
				try:
					self.parent.validator = ForcingValidator(path)
					self.parent.pan_inputs.Enable(True)
				except IOError as e:
					self.parent.error("I/O error({0}): {1}".format(e.errno, e.strerror))
					self.parent.validator = None
					self.parent.pan_inputs.Enable(False)

class LoggingPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)

		fsize=parent.GetSize()

		# A multiline TextCtrl - This is here to show how the events work in this program, don't pay too much attention to it
		#self.logger = wx.TextCtrl(self, pos=(10,fsize[1]-200), size=(fsize[0]-20,190), style=wx.TE_MULTILINE | wx.TE_READONLY)
		self.logger = wx.TextCtrl(self, pos=(10,10), size=(fsize[0]-20,190), style=wx.TE_MULTILINE | wx.TE_READONLY)
		
class InputsPanel(wx.Panel):
	parent = None

	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		self.parent = parent

		dline=20

		line1=dline
		instruct1 = wx.StaticText(self, label="Second, choose the species you will input into the forcing function.", pos=(10,line1))

		# the combobox Control
		line2=line1+dline
		lblspecies = wx.StaticText(self, label="Species:", pos=(20, line2))
		if parent.validator != None:
			species_list = parent.validator.getSpecies();
		else:
			species_list = []
		#self.species = wx.ComboBox(self, pos=(150, line2), size=(95, -1), choices=species_list, style=wx.CB_DROPDOWN)
		self.species = wx.CheckListBox(self, pos=(150, line2), size=(150, 4*dline), choices=species_list)#, style=wx.LB_MULTILINE|wx.LB_EXTENDED|wx.LB_NEEDED_SB)
		self.Bind(wx.EVT_CHECKLISTBOX, self.choseSpecies, self.species)


		# the edit control - one line version.
		line3=line2+5*dline
		self.lblname = wx.StaticText(self, label="Mask File :", pos=(20,line3))
		self.editmask = wx.TextCtrl(self, value="Mask file", pos=(150, line3), size=(140,-1))
		self.Bind(wx.EVT_TEXT, self.EvtText, self.editmask)
		self.Bind(wx.EVT_CHAR, self.EvtChar, self.editmask)
		
		# Radio Boxes
		radioList = ['Species to Initial Conc', 'Morbidity to Species Conc', 'Morbidity to Species max 8 hour conc']
		rb = wx.RadioBox(self, label="Forcing Function?", pos=(20, 210), choices=radioList,  majorDimension=1,
						 style=wx.RA_SPECIFY_COLS)
		self.Bind(wx.EVT_RADIOBOX, self.EvtRadioBox, rb)

		# A button
		self.button =wx.Button(self, label="Save", pos=(200, 325))
		self.Bind(wx.EVT_BUTTON, self.OnClick,self.button)

	def choseSpecies(self, event):
		self.parent.debug('Chose species: [%s]' % ', '.join(map(str, self.species.GetCheckedStrings())))

	def EvtRadioBox(self, event):
		self.parent.debug('EvtRadioBox: %d' % event.GetInt())
	def EvtComboBox(self, event):
		self.parent.debug('EvtComboBox: %s' % event.GetString())
	def OnClick(self,event):
		self.parent.debug(" Click on object with Id %d" %event.GetId())
	def EvtText(self, event):
		self.parent.debug('EvtText: %s' % event.GetString())
	def EvtChar(self, event):
		self.parent.debug('EvtChar: %d' % event.GetKeyCode())
		event.Skip()
	def EvtCheckBox(self, event):
		self.parent.debug('EvtCheckBox: %d' % event.Checked())


	def Enable(self, doEnable):
		""" When enabled, populate stuff that was waiting on a concentration file """
		wx.Panel.Enable(self, doEnable)

		#if self.IsEnabled is True:
		if doEnable is True:
			if self.parent.validator != None:
				species_list = self.parent.validator.getSpecies();
				self.parent.debug("Received species list: " + '[%s]' % ', '.join(map(str, species_list)))
			else:
				self.parent.warn("Cannot load species list!")
				species_list = []

			self.species.Clear()
			self.parent.debug("Setting species in combo box")
			self.species.SetItems(species_list)
			#for s in species_list:
			#	self.species.Append(s) # might be SetItems