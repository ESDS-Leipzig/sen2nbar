from typing import Any

import numpy as np
import xarray as xr

from .axioms import *
from .brdf import *
from .metadata import *


def c_factor(
    sun_zenith: xr.DataArray, view_zenith: xr.DataArray, relative_azimuth: xr.DataArray
) -> xr.DataArray:
    """Computes the c-factor.

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
    BANDS = list(fiso.keys())

    sun_view_angles = angles_from_metadata(metadata)

    theta = sun_view_angles.sel(angle="Zenith", band="Sun")
    vartheta = sun_view_angles.sel(angle="Zenith", band=BANDS)
    phi = sun_view_angles.sel(angle="Azimuth", band="Sun") - sun_view_angles.sel(
        angle="Azimuth", band=BANDS
    )

    return c_factor(theta, vartheta, phi)
