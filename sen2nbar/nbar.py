import os
from glob import glob

import numpy as np
import rioxarray
import xarray as xr
from tqdm import tqdm

from .axioms import bands
from .c_factor import c_factor_from_metadata
from .metadata import get_processing_baseline
from .utils import _extrapolate_c_factor


def nbar_SAFE(path: str, cog: bool = True, quiet: bool = False) -> None:
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

        # Save the image
        img.rio.to_raster(f"{nbar_output_path}{filename}", driver=driver)

    pbar.set_description(f"Done")

    # Show the path where the images were saved
    if not quiet:
        print(f"Saved to {nbar_output_path}")
