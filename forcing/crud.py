#!/usr/bin/env python

""" http://visitusers.org/index.php?title=Writing_NETCDF_Using_Python """
from numpy import shape
from Scientific.IO.NetCDF import NetCDFFile
import numpy as np
 
# Write a variable with rectilinear coordinates to NETCDF.
def write_rectilinear(file, var, varname, x_coord, y_coord):
    nx = len(x_coord)
    ny = len(y_coord)
 
    # Reshape for 2D
    my_data = np.reshape(var,(ny,nx),'F')
 
    # Create dimensions:
    file.createDimension('nx', nx)
    file.createDimension('ny', ny)
 
    x = file.createVariable('nx', 'd', ('nx',))
    y = file.createVariable('ny', 'd', ('ny',))
 
    # transfer the coordinate variables:
    x[:] = x_coord
    y[:] = y_coord
 
    # Create data variable in NetCDF.
    data = file.createVariable(varname, 'd', ('ny','nx'))
 
    # transfer the data variables:
    data[:] = my_data
 
 
# coordinate information:
x_coord = [0,2,4,6,8,10,12] 
y_coord = [0, 5, 10]
 
# number of points:
nx = len(x_coord)
ny = len(y_coord)
 
# Create a nodal data variable
nodal = []
for i in range(nx):
    for j in range(ny):
        nodal = nodal + [j*nx + i]
 
# Write the file.
file = NetCDFFile('rectilinear.nc', 'w')
write_rectilinear(file, nodal, 'data', x_coord, y_coord)
file.close()
