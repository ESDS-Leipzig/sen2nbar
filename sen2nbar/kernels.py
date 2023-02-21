import numpy as np
import xarray as xr


def kgeo(sunZenith, viewZenith, relativeAzimuth, br=1.0, hb=2.0):
    """Computes the Geometric Kernel (Kgeo).

    Parameters
    ----------
    sunZenith : xarray.DataArray
        Sun Zenith angles in degrees.
    viewZenith : xarray.DataArray
        Sensor Zenith angles in degrees.
    relativeAzimuth : xarray.DataArray
        Relative Azimuth angles in degrees.
    br : float | int, default = 1.0
        Br factor.
    hb : float | int, default = 2.0
        Hb factor.

    Returns
    -------
    xarray.DataArray
        Geometric Kernel (Kgeo).
    """
    theta_i = np.deg2rad(sunZenith)
    theta_v = np.deg2rad(viewZenith)

    phi = np.deg2rad(relativeAzimuth)

    theta_i_dev = np.arctan(br * np.tan(theta_i))
    theta_v_dev = np.arctan(br * np.tan(theta_v))

    cos_xi_dev = np.cos(theta_i_dev) * np.cos(theta_v_dev) + np.sin(
        theta_i_dev
    ) * np.sin(theta_v_dev) * np.cos(phi)

    D = np.sqrt(
        (np.tan(theta_i_dev) ** 2.0)
        + (np.tan(theta_v_dev) ** 2.0)
        - (2.0 * np.tan(theta_i_dev) * np.tan(theta_v_dev) * np.cos(phi))
    )

    cos_t = (
        hb
        * np.sqrt(
            (D ** 2.0)
            + ((np.tan(theta_i_dev) * np.tan(theta_v_dev) * np.sin(phi)) ** 2.0)
        )
        / ((1.0 / np.cos(theta_i_dev)) + (1.0 / np.cos(theta_v_dev)))
    )

    # cos_t[cos_t > 1.0] = 1.0
    # cos_t[cos_t < -1.0] = -1.0

    cos_t = cos_t.where(lambda x: x <= 1.0, other=1.0)
    cos_t = cos_t.where(lambda x: x >= -1.0, other=-1.0)

    t = np.arccos(cos_t)

    O = (
        (1.0 / np.pi)
        * (t - np.sin(t) * cos_t)
        * ((1.0 / np.cos(theta_i_dev)) + (1.0 / np.cos(theta_v_dev)))
    )

    return (
        O
        - (1.0 / np.cos(theta_i_dev))
        - (1.0 / np.cos(theta_v_dev))
        + 0.5
        * (1.0 + cos_xi_dev)
        * (1.0 / np.cos(theta_i_dev))
        * (1.0 / np.cos(theta_v_dev))
    )


def kvol(sunZenith, viewZenith, relativeAzimuth):
    """Computes the Volumetric Kernel (Kvol).

    Parameters
    ----------
    sunZenith : xarray.DataArray
        Sun Zenith angles in degrees.
    viewZenith : xarray.DataArray
        Sensor Zenith angles in degrees.
    relativeAzimuth : xarray.DataArray
        Relative Azimuth angles in degrees.

    Returns
    -------
    xarray.DataArray
        Volumeric Kernel (Kvol).
    """
    theta_i = np.deg2rad(sunZenith)
    theta_v = np.deg2rad(viewZenith)

    phi = np.deg2rad(relativeAzimuth)

    cos_xi = np.cos(theta_i) * np.cos(theta_v) + np.sin(theta_i) * np.sin(
        theta_v
    ) * np.cos(phi)

    xi = np.arccos(cos_xi)

    return (
        (((np.pi / 2.0) - xi) * cos_xi + np.sin(xi))
        / (np.cos(theta_i) + np.cos(theta_v))
    ) - (np.pi / 4.0)
