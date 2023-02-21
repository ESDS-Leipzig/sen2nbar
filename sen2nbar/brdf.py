from typing import Any, List

import numpy as np
import xarray as xr

from .axioms import *
from .kernels import *


def _f_values_to_xarray(dict_values: dict) -> xr.DataArray:
    """Helper function to convert fiso, fvol, and fgeo to :code:`xarray.DataArray`.

    Parameters
    ----------
    dict_values : dict
        Dictiornay of parameters for each band.

    Returns
    -------
    xarray.DataArray
        Parameters as a data array.
    """
    return xr.DataArray(
        list(dict_values.values()),
        dims="band",
        coords=dict(band=list(dict_values.keys())),
    )


def brdf(sun_zenith: Any, view_zenith: Any, relative_azimuth: Any) -> Any:
    """Computes the Bidirectional Reflectance Distribution Function (BRDF).

    Parameters
    ----------
    sun_zenith : Any
        Sun Zenith angles in degrees.
    view_zenith : Any
        Sensor Zenith angles in degrees.
    relative_azimuth : Any
        Relative Azimuth angles in degrees.

    Returns
    -------
    Any
        BRDF.
    """
    fiso_ = _f_values_to_xarray(fiso)
    fvol_ = _f_values_to_xarray(fvol)
    fgeo_ = _f_values_to_xarray(fgeo)

    fvol_kvol = fvol_ * kvol(sun_zenith, view_zenith, relative_azimuth)
    fgeo_kgeo = fgeo_ * kgeo(sun_zenith, view_zenith, relative_azimuth)

    brdf_ = fiso_ + (fvol_kvol + fgeo_kgeo)

    return brdf_
