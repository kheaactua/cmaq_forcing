# GUY Lib
import wx

class ForcingFrame(wx.Frame):
	def __init__(self,parent, id=-1, title="Forcing File Generator", pos=wx.DefaultPosition, size=(520,400), style=wx.DEFAULT_FRAME_STYLE, name=wx.FrameNameStr):
		wx.Frame.__init__(self, parent, id, title, pos, size, style, name)


		randomId = wx.NewId()
		self.Bind(wx.EVT_MENU, self.onKeyCombo, id=randomId)
		accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL,  ord('W'), randomId), (wx.ACCEL_CTRL,  ord('Q'), randomId)])
		self.SetAcceleratorTable(accel_tbl)

	def onKeyCombo(self, event):
		self.Close()

	def Close(self):
		print "calling local Close()"
		wx.Frame.Close(self)

class ForcingGUI(wx.Panel):
	 def __init__(self, parent):
			wx.Panel.__init__(self, parent)

			fsize=parent.GetSize()

			# A multiline TextCtrl - This is here to show how the events work in this program, don't pay too much attention to it
			self.logger = wx.TextCtrl(self, pos=(10,fsize[1]-200), size=(fsize[0]-20,190), style=wx.TE_MULTILINE | wx.TE_READONLY)

			# A button
			self.button =wx.Button(self, label="Save", pos=(200, 325))
			self.Bind(wx.EVT_BUTTON, self.OnClick,self.button)

			# the edit control - one line version.
			self.lblname = wx.StaticText(self, label="Concentration :", pos=(20,30))
			self.editname = wx.TextCtrl(self, value="Concentration file", pos=(150, 30), size=(140,-1))
			self.Bind(wx.EVT_TEXT, self.EvtText, self.editname)
			self.Bind(wx.EVT_CHAR, self.EvtChar, self.editname)

			# the edit control - one line version.
			self.lblname = wx.StaticText(self, label="Mask File :", pos=(20,60))
			self.editmask = wx.TextCtrl(self, value="Mask file", pos=(150, 60), size=(140,-1))
			self.Bind(wx.EVT_TEXT, self.EvtText, self.editmask)
			self.Bind(wx.EVT_CHAR, self.EvtChar, self.editmask)

			# the combobox Control
			self.sampleList = ['O3', 'NOx', 'VOCs']
			self.lblhear = wx.StaticText(self, label="Species", pos=(20, 90))
			self.edithear = wx.ComboBox(self, pos=(150, 90), size=(95, -1), choices=self.sampleList, style=wx.CB_DROPDOWN)
			self.Bind(wx.EVT_COMBOBOX, self.EvtComboBox, self.edithear)
			self.Bind(wx.EVT_TEXT, self.EvtText,self.edithear)

			# Radio Boxes
			radioList = ['Species to Initial Conc', 'Morbidity to Species Conc', 'Morbidity to Species max 8 hour conc']
			rb = wx.RadioBox(self, label="Forcing Function?", pos=(20, 210), choices=radioList,  majorDimension=1,
								 style=wx.RA_SPECIFY_COLS)
			self.Bind(wx.EVT_RADIOBOX, self.EvtRadioBox, rb)

	 def EvtRadioBox(self, event):
			self.logger.AppendText('EvtRadioBox: %d\n' % event.GetInt())
	 def EvtComboBox(self, event):
			self.logger.AppendText('EvtComboBox: %s\n' % event.GetString())
	 def OnClick(self,event):
			self.logger.AppendText(" Click on object with Id %d\n" %event.GetId())
	 def EvtText(self, event):
			self.logger.AppendText('EvtText: %s\n' % event.GetString())
	 def EvtChar(self, event):
			self.logger.AppendText('EvtChar: %d\n' % event.GetKeyCode())
			event.Skip()
	 def EvtCheckBox(self, event):
			self.logger.AppendText('EvtCheckBox: %d\n' % event.Checked())





