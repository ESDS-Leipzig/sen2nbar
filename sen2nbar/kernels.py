from typing import Any, Union

import numpy as np
import xarray as xr


def kgeo(
    sun_zenith: Any,
    view_zenith: Any,
    relative_azimuth: Any,
    br: Union[float, int] = 1.0,
    hb: Union[float, int] = 2.0,
) -> Any:
    """Computes the Geometric Kernel (Kgeo).

    The mathematical formulation of Kgeo, also known as LiSparse-R Kernel (KLSR), can be
    found in Equation 39 of Lucht et al., 2000 [1]_.

    Parameters
    ----------
    sun_zenith : Any
        Sun Zenith angles in degrees.
    view_zenith : Any
        Sensor Zenith angles in degrees.
    relative_azimuth : Any
        Relative Azimuth angles in degrees.
    br : float | int, default = 1.0
        Crown relative height (Br) parameter.
    hb : float | int, default = 2.0
        Shape (Hb) parameter.

    Returns
    -------
    Any
        Geometric Kernel (Kgeo).

    References
    ----------
    .. [1] https://doi.org/10.1109/36.841980
    """
    # Convert to radians
    theta_i = np.deg2rad(sun_zenith)
    theta_v = np.deg2rad(view_zenith)
    phi = np.deg2rad(relative_azimuth)

    # Equation 44 in Lucht et al., 2000
    theta_i_dev = np.arctan(br * np.tan(theta_i))
    theta_v_dev = np.arctan(br * np.tan(theta_v))

    # Equation 43 in Lucht et al., 2000
    cos_xi_dev = np.cos(theta_i_dev) * np.cos(theta_v_dev) + np.sin(
        theta_i_dev
    ) * np.sin(theta_v_dev) * np.cos(phi)

    # Equation 42 in Lucht et al., 2000
    D = np.sqrt(
        (np.tan(theta_i_dev) ** 2.0)
        + (np.tan(theta_v_dev) ** 2.0)
        - (2.0 * np.tan(theta_i_dev) * np.tan(theta_v_dev) * np.cos(phi))
    )

    # Compute the cost term cos(t)
    # Equation 41 in Lucht et al., 2000
    cos_t = (
        hb
        * np.sqrt(
            (D ** 2.0)
            + ((np.tan(theta_i_dev) * np.tan(theta_v_dev) * np.sin(phi)) ** 2.0)
        )
        / ((1.0 / np.cos(theta_i_dev)) + (1.0 / np.cos(theta_v_dev)))
    )

    # cos(t) should be constrained to [-1,1]
    # Page 981 in Lucht et al., 2000
    cos_t = cos_t.where(lambda x: x <= 1.0, other=1.0)
    cos_t = cos_t.where(lambda x: x >= -1.0, other=-1.0)

    t = np.arccos(cos_t)

    # Compute the overlap area between the view and solar shadows (O)
    # Equation 40 in Lucht et al., 2000
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


def kvol(sun_zenith: Any, view_zenith: Any, relative_azimuth: Any) -> Any:
    """Computes the Volumetric Kernel (Kvol).

    The mathematical formulation of Kvol, also known as RossThick Kernel (KRT), can be
    found in Equation 38 of Lucht et al., 2000 [1]_.

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
        Volumeric Kernel (Kvol).

    References
    ----------
    .. [1] https://doi.org/10.1109/36.841980
    """
    # Convert to radians
    theta_i = np.deg2rad(sun_zenith)
    theta_v = np.deg2rad(view_zenith)
    phi = np.deg2rad(relative_azimuth)

    # Compute the phase angle
    cos_xi = np.cos(theta_i) * np.cos(theta_v) + np.sin(theta_i) * np.sin(
        theta_v
    ) * np.cos(phi)

    xi = np.arccos(cos_xi)

    return (
        (((np.pi / 2.0) - xi) * cos_xi + np.sin(xi))
        / (np.cos(theta_i) + np.cos(theta_v))
    ) - (np.pi / 4.0)
