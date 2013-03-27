#from DataFile import DataFile
import datetime as dt
import wx, os


#class NetCDFValidator(wx.PyValidator):
#	""" I don't know how to use this, and it doesn't work yet."""
#
#	def __init__(self):
#		wx.PyValidator.__init__(self)
#
#	def Validate(self, win):
#		""" Validate the contents of the given control.  """
#		print "Called validator"
#		ctrl = self.GetWindow()
#		text = ctrl.GetValue()
#
#		if len(text) == 0:
#			wx.MessageBox("A text object must contain some text!", "Error")
#			ctrl.SetBackgroundColour("pink")
#			#ctrl.SetFocus()
#			#ctrl.Refresh()
#			return False
#		else:
#			ctrl.SetBackgroundColour(
#			   wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
#			ctrl.Refresh()
#			return True
#
#	def Clone ( Self ):
#		return NetCDFValidator()

class HelpLink(wx.StaticText):
	""" Creates a StaticText control with an onclick event """

	def __init__(self, parent, id=-1, label=wx.EmptyString, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, name=wx.StaticTextNameStr, onClick=None):
		wx.StaticText.__init__(self, parent, id, label, pos, size, style, name)

		self.SetForegroundColour((0,0,255))
		font=self.GetFont();
		font.SetUnderlined(True)
		self.SetFont(font)
		self.Bind(wx.EVT_LEFT_DOWN, onClick)

class SingleFileChooser(wx.Button):
	path = None
	fname = "File"

	def __init__(self, parent, id=-1, label=wx.EmptyString, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, validator=wx.DefaultValidator, name=wx.ButtonNameStr, fname="", fmessage="Choose File"):

		wx.Button.__init__(self, parent=parent, id=id, label=label, pos=pos, size=size, style=style, validator=validator, name=name)

		self.parent = parent
		self.fname=fname
		self.fmessage=fmessage

		self.Bind(wx.EVT_BUTTON, self.chooseFile)

	def chooseFile(self, event):
		""" Choose a file, and write it to button label """
		dlg = wx.FileDialog(self,
		   message=self.fmessage,
		   defaultDir=os.getcwd())

		if dlg.ShowModal() == wx.ID_OK:
			self.path = dlg.GetPaths()[0]
			self.parent.parent.info("Chose %s file: %s"%(self.fname, self.path))
			v = self.parent.parent.validator
			try:
				if v.ValidateDataFileSurface(self.path) == False:
					self.parent.parent.warn("File %s doesn't have the proper dimensions."%self.path)
					self.SetLabel(os.path.basename(self.path))
			except Exception as e:
				self.parent.parent.warn("Could not open %s.  %s"%(self.path, str(e)))

# This should also be moved into another file
class dateE(dt.date, object):
	""" Extends datetime.datetime by adding juldate operators """

	_julday = -1

	def __init__(self, year, month, day):
		""" Date function wrapper used for juldate stuff """

		super(dateE, self).__init__(year, month, day)
		self._SetJulDay(year, month, day)

	@property
	def julday(self):
		#date_s = datetime.datetime(self.year, 1, 1)
		#date_e = datetime.datetime(self.year, self.month, self.day)
		#delta = date_s - date_e
		#self.julday = delta.days
		return self._julday
	@julday.setter
	def julday(self, val):
		# Needs to know the year
		raise NotImplementedError( "Not yet implemented" )

	def _SetJulDay(self, year, month, day):
		date_s = dt.date(self.year, 1, 1)
		date_e = dt.date(self.year, self.month, self.day)
		delta = date_s - date_e
		self._julday = delta.days

	def __str__(self):
		return "%d-%0.2d-%0.2d"%(self.year,self.month,self.day)

	@staticmethod
	def fromJulDate(year, jday):
		date = dt.date(year, 1, 1)
		days = dt.timedelta(days=jday-1) # -1 because we started at day 1
		date=date+days
		return dateE(year, date.month, date.day)
