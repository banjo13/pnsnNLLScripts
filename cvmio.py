#!/usr/bin/env python

"""cvmio.py: Input & output functions for CVM"""

__author__      = "Erin Wirth"

import pdb
import os
import numpy as np
import pandas as pd
import xarray as xr

def readBinary(zTop=0, zBot=1200,
               min_utme=None, max_utme=None,
               min_utmn=None, max_utmn=None,
               newModelName='subModel.nc',
               binModelName='',
               saveFull='N'):
    """
    Read in 3-D CVM from binary files.

    This function only works with one binary file at a time.
    Input parameters are used to specify bounds of a sub-model,
    if only a small chunk of the full CVM is needed.

    Offshore water is set to V=1e20 in binary files.

    All UTM coordinates are given for Zone 10T.

    For Puget Lowland: zTop=0, zBot=200,
               min_utme=446700, max_utme=567100,
               min_utmn=5194300, max_utmn=5316700,
               modelName='subModel_0_200m_PL.nc'

    Parameters:
    zTop: Top of sub-model [m]
    zBot: Bottom of sub-model [m]
    min_utme: Minimum easting [m]
    max_utme: Maximum easting [m]
    min_utmn: Minimum northing [m]
    max_utmn: Maximum northing [m]

    Returns:
    subModelxr: Sub-model in xarray format

    """

    # The following lines describe the size of the binary file values.
    #
    # Layer 1 0-1200m depth
    # 3271 in EW direction
    # 5367 in NS direction
    # 13 in z
    # dx=dy= 200m,  dz= 100m
    #
    if 'l1' in binModelName:
        nx = 3271; ny = 5367; nz = 13
        dx = 200;  dy = 200;  dz = 100
        zmin = 0; zmax = 1200
    #
    # Layer 2 1500-9900m depth
    # 2181 in EW
    # 3578 in NS
    # 29 in z
    # dx=dy=dz=300m
    #
    if 'l2' in binModelName:
        nx = 2181; ny = 3578; nz = 29
        dx = 300;  dy = 300;  dz = 300
        zmin = 1500; zmax = 9900
    #
    # Layer 3 10800-59400m depth
    # 727 in EW
    # 1193 NS
    # 55 in z
    # dx=dy=dz=900m
    #
    if 'l3' in binModelName:
        nx = 727; ny = 1193; nz = 55
        dx = 900; dy = 900;  dz = 900
        zmin = 10800; zmax = 59400
    #
    # The SW corner of the velocity model is -10800m East, 4467300m N Zone 10.
    SWcornerFull = [-10800, 4467300]
    #

    # Read in binary file
    v = np.fromfile(binModelName, dtype='<f4')

    # Generate arrays for x, y, & z locations
    z = np.linspace(zmin, zmax, nz)
    z = np.repeat(z, (np.ones(len(z))*nx*ny).astype(int))
    z = z[::-1]             # Reverse array

    y = np.linspace(SWcornerFull[1], SWcornerFull[1]+ny*dy, ny, endpoint=False)
    y = np.repeat(y, (np.ones(len(y))*nx).astype(int))
    y = np.tile(y, nz)     # Repeat array for each depth

    x = np.linspace(SWcornerFull[0], SWcornerFull[0]+nx*dx, nx, endpoint=False)
    x = np.tile(x, ny*nz)

    # Convert CVM to dataframe
    model = pd.DataFrame(np.column_stack((x,y,z,v)), columns=['utme','utmn','z',(binModelName.split('/'))[1].split('_16')[0]])

    if saveFull == 'N' or saveFull == 'n':
        # Subset model (speed things up)
        if min_utme==None:
            # Use full horizontal model extent
            subModel = model[(model["z"] >= zTop) & (model["z"] <= zBot)]
        else:
            subModel = model[(model["z"] >= zTop) & (model["z"] <= zBot)
                             & (model["utme"] >= min_utme) & (model["utme"] <= max_utme)
                             & (model["utmn"] >= min_utmn) & (model["utmn"] <= max_utmn)]
        subModel = subModel.set_index(['utme','utmn','z'])    # Set these parameters as coordinates

        # Convert to xarray (slow)
        subModelxr = subModel.to_xarray()

        # Save xarray for faster reload later
        subModelxr.to_netcdf('../output/' + newModelName)

        return subModelxr

    # This can be VERY slow (~ 1 hour)
    if saveFull == 'Y' or saveFull == 'y':
        model = model.set_index(['utme','utmn','z'])
        modelxr = model.to_xarray()
        modelxr.to_netcdf('../output/' + (binModelName.split('/'))[1].split('.bin')[0]+'.nc')

        return modelxr


def combineXarrays(vpXarray, vsXarray):
    """
    Combines Vp and Vs xarrays
    Confirms before deleting individual xarrays

    Parameters:
    vpXarray: Xarray contatining Vp (.nc)
    vsXarray: Xarray contatining Vp (.nc)

    Returns:
    None

    """
    mergedModel = xr.merge([vpXarray,vsXarray])
    mergedModel.to_netcdf('../output/vpvs_'+(vpXarray.split('vp_'))[1].split('.bin')[0]+'.nc')

    val = input('Delete individual Vp and Vs xarrays? (yes/no)')
    if val == 'yes':
        os.remove(vpXarray)
        os.remove(vsXarray)


def insertSubModel(subModelFile, fullModelFile):
    """
    Insert modified sub-model back into original model.
    Saves new, full model with a new name.

    Parameters:
    subModelFile: Filename of sub-model
    fullModelFile: Filename of original, full model

    Returns:
    None

    """

    # Former issues related to interpolating NaN or 1e20s
    # Strange behavior using xr functions for combining datasets
    print('This function is potentially unstable')

    subModel = xr.open_dataset(subModelFile)
    fullModel = xr.open_dataset(fullModelFile)

    # Mask offshore values (to NaNs)
    maskModel = fullModel.where(fullModel.vs < 1e19, np.nan)

    # Interpolate full model to same spacing
    if set(subModel.utme.values).issubset(set(fullModel.utme.values)) == False:
        maskModel = maskModel.interp(utme=subModel.utme.values)
    if set(subModel.utmn.values).issubset(set(fullModel.utmn.values)) == False:
        maskModel = maskModel.interp(utmn=subModel.utmn.values)
    if set(subModel.z.values).issubset(set(fullModel.z.values)) == False:
        maskModel = maskModel.interp(z=subModel.z.values)

    # Replace any values that were overwritten by interpolating NaNs
    tempModel = xr.merge([fullModel,maskModel])
    #pdb.set_trace()

    # Combine datasets
    nModel = subModel.combine_first(tempModel)
    # Re-mask
    nModel = nModel.where(nModel.vs < 1e19, np.nan)

    # Save full, modified model
    nModel.to_netcdf(fullModelFile[:-3]+'_modified.nc')


def makeSubModel(min_utme=477200, max_utme=643200,
                 min_utmn=5194100, max_utmn=5350100,
                 modelName='subModel.nc',
                 newModelName='newModel.nc'):
    """
    Cut larger .nc file into a submodel

    Parameters:

    Returns:
    None

    """
    model = xr.open_dataset(modelName)
    model = model.copy(deep=True)

    model = model.sel(utme=slice(min_utme,max_utme), utmn=slice(min_utmn,max_utmn))

    model.to_netcdf('../output/' + newModelName)


    return None
