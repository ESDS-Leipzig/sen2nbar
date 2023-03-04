from typing import Any

import numpy as np
import pystac
import rioxarray
import xarray as xr

from .axioms import *
from .brdf import *
from .metadata import *
from .utils import _extrapolate_c_factor


def c_factor(
    sun_zenith: xr.DataArray, view_zenith: xr.DataArray, relative_azimuth: xr.DataArray
) -> xr.DataArray:
    """Computes the c-factor.

    The mathematical formulation of the c-factor can be found in Equation 4 of Roy et al.,
    2008 [1]_ and Equation 7 of Roy et al., 2016 [2]_.

    Parameters
    ----------
    sun_zenith : xarray.DataArray
        Sun Zenith angles in degrees.
    view_zenith : xarray.DataArray
        Sensor Zenith angles in degrees.
    relative_azimuth : xarray.DataArray
        Relative Azimuth angles in degrees.

    Returns
    -------
    xarray.DataArray
        c-factor.

    References
    ----------
    .. [1] http://dx.doi.org/10.1016/j.rse.2008.03.009
    .. [2] http://dx.doi.org/10.1016/j.rse.2016.01.023
    """
    return brdf(sun_zenith, view_zenith * 0, relative_azimuth) / brdf(
        sun_zenith, view_zenith, relative_azimuth
    )


def c_factor_from_metadata(metadata: str) -> xr.DataArray:
    """Gets the c-factor per band from Sentinel-2 granule metadata.

    Parameters
    ----------
    metadata : str
        Path to the metadata file. An URL can also be used.

    Returns
    -------
    xarray.DataArray
        c-factor.
    """
    # Get the available band names
    BANDS = list(fiso.keys())

    # Get the Sun and View angles
    sun_view_angles = angles_from_metadata(metadata)

    # Get the Sun Zenith
    theta = sun_view_angles.sel(angle="Zenith", band="Sun")

    # Get the View Zenith
    vartheta = sun_view_angles.sel(angle="Zenith", band=BANDS)

    # Compute the relative azimuth per band
    phi = sun_view_angles.sel(angle="Azimuth", band="Sun") - sun_view_angles.sel(
        angle="Azimuth", band=BANDS
    )

    return c_factor(theta, vartheta, phi)


def c_factor_from_item(item: pystac.item.Item, to_epsg: str) -> xr.DataArray:
    """Gets the c-factor per band from a Sentinel-2 :code:`pystac.Item`.

    Parameters
    ----------
    item : pystac.item.Item
        Item to get the c-factor from.
    to_epsg : str
        EPSG code to reproject the c-factor to (e.g. "epsg:3115")

    Returns
    -------
    xarray.DataArray
        c-factor.
    """
    # Retrieve the EPSG from the item
    SOURCE_EPSG = item.properties["proj:epsg"]

    # Get the EPSG from the string
    TO_EPSG = float(to_epsg.split(":")[-1])

    # Get the granule metadata URL from the item
    metadata = item.assets["granule-metadata"].href

    # Compute the c-factor and extrapolate
    c = c_factor_from_metadata(metadata)
    c = _extrapolate_c_factor(c)

    # If the CRSs are different: reproject
    if SOURCE_EPSG != TO_EPSG:
        c = c.rio.write_crs(f"epsg:{SOURCE_EPSG}")
        c = c.rio.reproject(f"epsg:{TO_EPSG}")

    return c
