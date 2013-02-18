from DoForce import *

name=r'CCTM_fwdFRC.20070503'
f=DataFile(name, file_format="*YYYYMMDD")
print name, f.date

name=r'CCTM_fwdFRC.3-05-2007'
f=DataFile(name, file_format="*DD-MM-YYY")
print "\n", name, f.date

name=r'CCTM_fwdFRC.2007-May-3'
f=DataFile(name, file_format="*YYYY-MMM-DD")
print "\n", name, f.date

name=r'CCTM_fwdFRC.2007123'
f=DataFile(name, file_format="*YYYY-JJJ")
print "\n", name, f.date
