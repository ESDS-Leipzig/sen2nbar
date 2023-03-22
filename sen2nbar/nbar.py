import os
from glob import glob

import numpy as np
import planetary_computer as pc
import pystac_client
import rioxarray
import xarray as xr
from tqdm import tqdm

from .axioms import bands
from .c_factor import c_factor_from_item, c_factor_from_metadata
from .metadata import get_processing_baseline
from .utils import _extrapolate_c_factor


def nbar_SAFE(path: str, cog: bool = True, quiet: bool = False, toint: bool = False) -> None:
    """Computes the Nadir BRDF Adjusted Reflectance (NBAR) using the SAFE path.

    If the processing baseline is greater than 04.00, the DN values are automatically
    shifted before computing NBAR. All images are saved in the SAFE path inside the folder
    NBAR.

    Parameters
    ----------
    path : str
        SAFE path.
    cog : bool, default = True
        Whether to save the images as Cloud Optimized GeoTIFF (COG).
    quiet : bool, default = False
        Whether to show progress.
    toint : bool, default = False
        Whether to convert the NBAR output to integer.

    Returns
    -------
    None
    """
    # Whether to save as COG
    if cog:
        driver = "COG"
    else:
        driver = None

    # NBAR folder to store the images
    nbar_output_path = f"{path}/NBAR/"

    # Create folder inside the SAFE path
    if not os.path.exists(nbar_output_path):
        os.makedirs(nbar_output_path)

    # Metadata file
    metadata = glob(f"{path}/GRANULE/*/MTD_TL.xml")[0]

    # Processing baseline
    PROCESSING_BASELINE = get_processing_baseline(f"{path}/MTD_MSIL2A.xml")

    # Whether to shift the DN values
    # After 04.00 all DN values are shifted by 1000
    harmonize = PROCESSING_BASELINE >= 4.0

    # Compute c-factor
    c = c_factor_from_metadata(metadata)

    # Extrapolate c-factor
    c = _extrapolate_c_factor(c)

    # Initialize progress bar
    pbar = tqdm(bands.items(), disable=quiet)

    # Compute NBAR per band
    for band, resolution in pbar:
        pbar.set_description(f"Processing {band}")

        # Image file
        img_path = glob(f"{path}/GRANULE/*/IMG_DATA/*/*_{band}_{resolution}m.jp2")[0]

        # Rename filename to tif extension
        filename = img_path.split("/")[-1].replace("jp2", "tif")

        # Open image and convert zeros to nan
        img = rioxarray.open_rasterio(img_path)
        img = img.where(lambda x: x > 0, other=np.nan)

        # Harmonize
        if harmonize:
            img = img - 1000

        # Interpolate c-factor of the band to the resolution of the image
        interpolated = c.sel(band=band).interp(
            y=img.y, x=img.x, method="linear", kwargs={"fill_value": "extrapolate"}
        )

        # Compute the NBAR
        img = img * interpolated

        if toint:
            img = img.round().astype("int16")

        # Save the image
        img.rio.to_raster(f"{nbar_output_path}{filename}", driver=driver)

    pbar.set_description(f"Done")

    # Show the path where the images were saved
    if not quiet:
        print(f"Saved to {nbar_output_path}")


def nbar_stac(
    da: xr.DataArray, stac: str, collection: str, epsg: str, quiet: bool = False
) -> xr.DataArray:
    """Computes the Nadir BRDF Adjusted Reflectance (NBAR) for a :code:`xarray.DataArray`.

    If the processing baseline is greater than 04.00, the DN values are automatically
    shifted before computing NBAR.

    Parameters
    ----------
    da : xarray.DataArray
        Data array to use for the NBAR calculation.
    stac : str
        STAC Endpoint of the data array.
    collection : str
        Collection name of the data array.
    epsg : str
        EPSG code of the data array (e.g. "epsg:3115").
    quiet : bool, default = False
        Whether to show progress.

    Returns
    -------
    xarray.DataArray
        NBAR data array.
    """
    # Keep attributes xarray
    xr.set_options(keep_attrs=True)

    # Open catalogue
    CATALOG = pystac_client.Client.open(stac)

    # Do a search
    SEARCH = CATALOG.search(ids=da.id.values, collections=[collection])

    # Get the items
    items = SEARCH.get_all_items()

    # Sign the items if using PC
    if stac == "https://planetarycomputer.microsoft.com/api/stac/v1":
        items = pc.sign(items)

    # Order items
    items_ids = [item.id for item in items]
    original_order = np.array(
        [np.where(da.id.values == item) for item in items_ids]
    ).ravel()
    ordered_items = np.array(items)[original_order]

    # Compute the c-factor per item and extract the processing baseline
    c_array = []
    processing_baseline = []
    for item in tqdm(ordered_items, disable=quiet):
        c = c_factor_from_item(item, epsg)
        c = c.interp(
            y=da.y.values,
            x=da.x.values,
            method="linear",
            kwargs={"fill_value": "extrapolate"},
        )
        c_array.append(c)
        processing_baseline.append(item.properties["s2:processing_baseline"])

    # Processing baseline as data array
    processing_baseline = xr.DataArray(
        [float(x) for x in processing_baseline],
        dims="time",
        coords=dict(time=da.time.values),
    )

    # Whether to shift the DN values
    # After 04.00 all DN values are shifted by 1000
    harmonize = xr.where(processing_baseline >= 4.0, -1000, 0)

    # Zeros are NaN
    da = da.where(lambda x: x > 0, other=np.nan)

    # Harmonize (use processing baseline)
    da = da + harmonize

    # Concatenate c-factor
    c = xr.concat(c_array, dim="time")
    c["time"] = da.time.values

    # Compute NBAR
    da = da * c

    return da


def nbar_stackstac(
    da: xr.DataArray, stac: str, collection: str, quiet: bool = False
) -> xr.DataArray:
    """Computes the Nadir BRDF Adjusted Reflectance (NBAR) for a :code:`xarray.DataArray`
    obtained via :code:`stackstac`.

    If the processing baseline is greater than 04.00, the DN values are automatically
    shifted before computing NBAR.

    Parameters
    ----------
    da : xarray.DataArray
        Data array obtained via :code:`stackstac` to use for the NBAR calculation.
    stac : str
        STAC Endpoint of the data array.
    collection : str
        Collection name of the data array.
    quiet : bool, default = False
        Whether to show progress.

    Returns
    -------
    xarray.DataArray
        NBAR data array.
    """
    # Get info from the stackstac data array
    epsg = da.attrs["crs"]

    # Compute NBAR
    da = nbar_stac(da, stac, collection, epsg, quiet)

    return da


def nbar_cubo(da: xr.DataArray, quiet: bool = False) -> xr.DataArray:
    """Computes the Nadir BRDF Adjusted Reflectance (NBAR) for a :code:`xarray.DataArray`
    obtained via :code:`cubo`.

    If the processing baseline is greater than 04.00, the DN values are automatically
    shifted before computing NBAR.

    Parameters
    ----------
    da : xarray.DataArray
        Data array obtained via :code:`cubo` to use for the NBAR calculation.
    quiet : bool, default = False
        Whether to show progress.

    Returns
    -------
    xarray.DataArray
        NBAR data array.
    """
    # Get info from the cubo data array
    stac = da.attrs["stac"]
    collection = da.attrs["collection"]
    epsg = da.attrs["epsg"]

    # Compute NBAR
    da = nbar_stac(da, stac, collection, epsg, quiet)

    return da
