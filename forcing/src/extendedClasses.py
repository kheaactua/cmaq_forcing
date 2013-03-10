import dateutil.parser as dparser
from datetime import date
import wx

class HelpLink(wx.StaticText):
	""" Creates a StaticText control with an onclick event """

	def __init__(self, parent, id=-1, label=wx.EmptyString, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0, name=wx.StaticTextNameStr, onClick=None):
		wx.StaticText.__init__(self, parent, id, label, pos, size, style, name)

		self.SetForegroundColour((0,0,255))
		font=self.GetFont();
		font.SetUnderlined(True)
		self.SetFont(font)
		self.Bind(wx.EVT_LEFT_DOWN, onClick)


# This should be moved into another file
class DataFile(object):
	""" Used encase we want any more info on the input files.
	Currently, name, path and date are all we care about
	"""

	_date = None
	@property
	def date(self):
		return self._date
	@date.setter
	def date(self, dt):
		self._date=dateE(dt.year, dt.month, dt.day)

	# Simply the file name (basename)
	name = None

	# Full path and file name
	path = None

	def __init__(self, filename, path="./", file_format=""):
		self.name=filename
		self.path=path

		# Try to determine the date
		try:
			# Should check if day is first
			day_is_first=None
			try:
				day_is_first = file_format.index('MM') > file_format.index('DD')
			except ValueError:
				# Meh
				day_is_first=None

			#print "Day is first? ", day_is_first
			self.date=dparser.parse(filename, fuzzy=True, dayfirst=day_is_first)
		except ValueError as e:
			print "Manually interpreting %s"%filename

			# YYYYMMDD
			match = re.match(r'.*[^\d]\d{4}\d{2}\d{2}.*', filename)
			if match:
				datestr = re.search(r'[^\d](\d{4})(\d{2})(\d{2})', '\1-\2-\3', filename)
				self.date=dparser.parse(datestr, fuzzy=True, dayfirst=day_is_first)
				return

			# Is it a julian date?
			match = re.match('.*[^\d]\d{4}\d{3}.*', filename)
			print match
			if match:
				raise NotImplementedError( "[TODO] Interpreting Julian date is not yet implemented" )
				return

	def __str__(self):
		return self.name

	# Used for sorting
	def __cmp__(self, other):
		if self._date > other._date:
			return 1
		elif self._date < other._date:
			return -1
		else:
			return 0 

# This should also be moved into another file
class dateE(date, object):
	""" Extends datetime.datetime by adding juldate operators """

	_julday = -1

	def __init__(self, year, month, day):
		date.__init__(year, month, day)

		self.SetJulDay(year, month, day)

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

	def SetJulDay(self, year, month, day):
		date_s = date(self.year, 1, 1)
		date_e = date(self.year, self.month, self.day)
		delta = date_s - date_e
		self._julday = delta.days

