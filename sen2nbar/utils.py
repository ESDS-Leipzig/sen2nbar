import numpy as np
import xarray as xr
from scipy.interpolate import NearestNDInterpolator


def _extrapolate_data_array(da: xr.DataArray) -> xr.DataArray:
    """Extrapolates a data array using Nearest Neighbor.

    Parameters
    ----------
    da : xr.DataArray
        Data array.

    Returns
    -------
    xr.DataArray
        Extrapolated data array.
    """
    # Flatten the data
    flattened = da.data.ravel()

    # Get all not nan data indices
    not_nan_idx = ~np.isnan(flattened)

    # Get the data from the flattened array
    flattened_not_nan = flattened[not_nan_idx]

    # Create a meshgrid with the coordinates values
    X, Y = np.meshgrid(da.x, da.y)

    # Flatten the meshgrid
    X = X.ravel()
    Y = Y.ravel()

    # Get the not nan coordinates
    X_not_nan = X[not_nan_idx]
    Y_not_nan = Y[not_nan_idx]

    # Initialize the interpolator
    interpolator = NearestNDInterpolator(
        list(zip(X_not_nan, Y_not_nan)), flattened_not_nan
    )

    # Do the interpolation
    Z = interpolator(X, Y)

    # Reshape the result and replace the original values
    da.values = Z.reshape(da.shape)

    return da


def _extrapolate_c_factor(da: xr.DataArray) -> xr.DataArray:
    """Extrapolates the c-factor data array.

    Parameters
    ----------
    da : xr.DataArray
        c-factor data array.

    Returns
    -------
    xr.DataArray
        Extrapolated c-factor data array.
    """

    return xr.concat(
        [_extrapolate_data_array(da.sel(band=band)) for band in da.band.values],
        dim="band",
    )
