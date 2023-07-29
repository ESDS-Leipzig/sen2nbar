import os
import warnings

import numpy as np
import requests
import xarray as xr
import xmltodict


def _get_angle_values(values_list: dict, angle: str) -> np.ndarray:
    """Gets the angle values per detector in Sentinel-2 granule metadata.

    Parameters
    ----------
    values_list : dict
        Dictionary of angle values in the metadata.
    angle : str
        Angle to retrieve. Either 'Zenith' oder 'Azimuth'.

    Returns
    -------
    numpy.ndarray
        Angle values per detector.
    """
    values = values_list[angle]["Values_List"]["VALUES"]
    array = np.array([row.split(" ") for row in values]).astype(float)

    return array


def angles_from_metadata(metadata: str) -> xr.DataArray:
    """Gets the angle values per band (and Sun) in Sentinel-2 granule metadata.

    The angle values are retrieved for the Sun and View modes as a
    :code:`xarray.DataArray` with a shape (band, angle, y, x).

    Parameters
    ----------
    metadata : str
        Path to the metadata file. An URL can also be used.

    Returns
    -------
    xarray.DataArray
        Angle values per band and Sun.
    """
    # Convert the xml into a dict
    if os.path.exists(metadata):
        data = xmltodict.parse(open(metadata, "r").read())
    else:
        data = xmltodict.parse(requests.get(metadata).content)

    # Extract the geocoding and angles, all the stuff we need is here
    Tile_Geocoding = data["n1:Level-2A_Tile_ID"]["n1:Geometric_Info"]["Tile_Geocoding"]
    Tile_Angles = data["n1:Level-2A_Tile_ID"]["n1:Geometric_Info"]["Tile_Angles"]

    # Save the upper left corner for the array
    ULX = float(Tile_Geocoding["Geoposition"][0]["ULX"])
    ULY = float(Tile_Geocoding["Geoposition"][0]["ULY"])

    # Band names
    band_names = ["B" + f"0{x}"[-2:] for x in np.arange(1, 13)]
    band_names.insert(8, "B8A")

    # Angles to work with
    ANGLES = ["Zenith", "Azimuth"]

    # Create a dictionary to store the angles per band (and the Sun)
    bands_dict = dict()
    for key in ["Sun"] + band_names:
        bands_dict[key] = dict(Zenith=list(), Azimuth=list())

    # Each band has multiple detectors, so we have to go through all of them
    # and save them in a list to later do a nanmean
    for single_angle_detector in Tile_Angles["Viewing_Incidence_Angles_Grids"]:
        band_id = int(single_angle_detector["@bandId"])
        band_name = band_names[band_id]
        for angle in ANGLES:
            bands_dict[band_name][angle].append(
                _get_angle_values(single_angle_detector, angle)
            )

    # Do the same for the Sun, but there is just one, of course, duh
    for angle in ANGLES:
        bands_dict["Sun"][angle].append(
            _get_angle_values(Tile_Angles["Sun_Angles_Grid"], angle)
        )

    # Do the nanmean of the detectors angles per band
    for key, value in bands_dict.items():
        for angle in ANGLES:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                bands_dict[key][angle] = np.nanmean(
                    np.array(bands_dict[key][angle]), axis=0
                )
        bands_dict[key] = np.array(
            [bands_dict[key]["Zenith"], bands_dict[key]["Azimuth"]]
        )

    # x and y coordinates of the array to create
    y = np.arange(ULY, ULY - 5000 * 23, -5000) - 2500
    x = np.arange(ULX, ULX + 5000 * 23, 5000) + 2500

    # Create the array
    try:
        da = xr.DataArray(
            list(bands_dict.values()),
            dims=["band", "angle", "y", "x"],
            coords=dict(band=list(bands_dict.keys()), angle=ANGLES, x=x, y=y),
        )
    except ValueError:
        raise ValueError("Not all bands include angles values.")

    # Add attributes
    da.attrs["epsg"] = Tile_Geocoding["HORIZONTAL_CS_CODE"]

    return da


def get_processing_baseline(metadata: str) -> float:
    """Gets the processing baseline in Sentinel-2 user metadata.

    The processing baseline is retrieved as a float.

    Parameters
    ----------
    metadata : str
        Path to the metadata file. An URL can also be used.

    Returns
    -------
    float
        Processing baseline.
    """
    # Convert the xml into a dict
    if os.path.exists(metadata):
        data = xmltodict.parse(open(metadata, "r").read())
    else:
        data = xmltodict.parse(requests.get(metadata).content)

    # Get the processing baseline
    PROCESSING_BASELINE = data["n1:Level-2A_User_Product"]["n1:General_Info"][
        "Product_Info"
    ]["PROCESSING_BASELINE"]

    return float(PROCESSING_BASELINE)
