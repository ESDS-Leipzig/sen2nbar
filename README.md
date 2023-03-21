<p align="center">
  <a href="https://github.com/ESDS-Leipzig/sen2nbar"><img src="https://github.com/ESDS-Leipzig/sen2nbar/raw/main/docs/_static/logo.png" alt="cubo"></a>
</p>
<p align="center">
    <em>Nadir BRDF Adjusted Reflectance (NBAR) for Sentinel-2 in Python</em>
</p>
<p align="center">
<a href='https://pypi.python.org/pypi/sen2nbar'>
    <img src='https://img.shields.io/pypi/v/sen2nbar.svg' alt='PyPI' />
</a>
<a href='https://anaconda.org/conda-forge/sen2nbar'>
    <img src='https://img.shields.io/conda/vn/conda-forge/sen2nbar.svg' alt='conda-forge' />
</a>
<a href='https://sen2nbar.readthedocs.io/en/latest/?badge=latest'>
    <img src='https://readthedocs.org/projects/sen2nbar/badge/?version=latest' alt='Documentation Status' />
</a>
<a href="https://github.com/ESDS-Leipzig/sen2nbar/actions/workflows/tests.yml" target="_blank">
    <img src="https://github.com/ESDS-Leipzig/sen2nbar/actions/workflows/tests.yml/badge.svg" alt="Tests">
</a>
<a href="https://opensource.org/licenses/MIT" target="_blank">
    <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License">
</a>
<a href="https://github.com/sponsors/davemlz" target="_blank">
    <img src="https://img.shields.io/badge/GitHub%20Sponsors-Donate-ff69b4.svg" alt="GitHub Sponsors">
</a>
<a href="https://www.buymeacoffee.com/davemlz" target="_blank">
    <img src="https://img.shields.io/badge/Buy%20me%20a%20coffee-Donate-ff69b4.svg" alt="Buy me a coffee">
</a>
<a href="https://ko-fi.com/davemlz" target="_blank">
    <img src="https://img.shields.io/badge/kofi-Donate-ff69b4.svg" alt="Ko-fi">
</a>
<a href="https://twitter.com/dmlmont" target="_blank">
    <img src="https://img.shields.io/twitter/follow/dmlmont?style=social" alt="Twitter">
</a>
<a href="https://github.com/psf/black" target="_blank">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Black">
</a>
<a href="https://pycqa.github.io/isort/" target="_blank">
    <img src="https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336" alt="isort">
</a>
</p>

---

**GitHub**: [https://github.com/ESDS-Leipzig/sen2nbar](https://github.com/ESDS-Leipzig/sen2nbar)

**Documentation**: [https://sen2nbar.readthedocs.io/](https://sen2nbar.readthedocs.io/)

**PyPI**: [https://pypi.org/project/sen2nbar/](https://pypi.org/project/sen2nbar/)

**Conda-forge**: [https://anaconda.org/conda-forge/sen2nbar](https://anaconda.org/conda-forge/sen2nbar)

**Tutorials**: [https://sen2nbar.readthedocs.io/en/latest/tutorials.html](https://sen2nbar.readthedocs.io/en/latest/tutorials.html)

---

## Overview

First, a super small glossary:

- **BRDF**: Bidirectional Reflectance Distribution Function.
- **DN**: Digital Number.
- **NBAR**: Nadir BRDF Adjusted Reflectance.
- **SR**: Surface Reflectance.
- **STAC**: SpatioTemporal Assets Catalogs.

Second, the amazing bibliography by David P. Roy et al., used to create this package:

- [Multi-temporal MODIS-Landsat data fusion for relative radiometric normalization, gap filling, and prediction of Landsat data.](https://doi.org/10.1016/j.rse.2008.03.009)
- [A general method to normalize Landsat reflectance data to nadir BRDF adjusted reflectance.](https://doi.org/10.1016/j.rse.2016.01.023)
- [Examination of Sentinel-2A multi-spectral instrument (MSI) reflectance anisotropy and the suitability of a general method to normalize MSI reflectance to nadir BRDF adjusted reflectance.](https://doi.org/10.1016/j.rse.2017.06.019)
- [Adjustment of sentinel-2 multi-spectral instrument (MSI) red-edge band reflectance to nadir BRDF adjusted reflectance (NBAR) and quantification of red-edge band BRDF effects.](https://doi.org/10.3390/rs9121325)

Third, the super useful bibliography by Lucht et al.,:

- [An algorithm for the retrieval of albedo from space using semiempirical BRDF models.](https://doi.org/10.1109/36.841980)

Given this, and in a few words, `sen2nbar` converts the **Sentinel-2 SR** (i.e., L2A) to **Sentinel-2 NBAR** via the **_c_-factor** method.

### SAFE

You can use `sen2nbar` to convert complete images via SAFE:

```python
from sen2nbar.nbar import nbar_SAFE

# Converted images are saved inside the SAFE path
nbar_SAFE("S2A_MSIL2A_20230223T075931_N0509_R035_T35HLC_20230223T120656.SAFE")
```

> **Note**
>
> Note that `sen2nbar` automatically shifts the DN of images with a processing baseline >= 04.00. This includes data cubes obtained via `stackstac` or `cubo`.

### stackstac

Or, if you are using STAC and retrieving images via `stackstac`:

```python
import pystac_client
import stackstac
import planetary_computer as pc
from sen2nbar.nbar import nbar_stackstac

# Important infor for later
endpoint = "https://planetarycomputer.microsoft.com/api/stac/v1"
collection = "sentinel-2-l2a"
bounds = (-148.565368, 60.800723, -147.443389, 61.183638)

# Open the STAC
catalog = pystac_client.Client.open(endpoint, modifier=pc.sign_inplace)

# Define your area
area_of_interest = {
    "type": "Polygon",
    "coordinates": [
        [
            [bounds[0], bounds[1]],
            [bounds[2], bounds[1]],
            [bounds[2], bounds[3]],
            [bounds[0], bounds[3]],
            [bounds[0], bounds[1]],
        ]
    ],
}

# Search the items
items = catalog.search(
    collections=[collection],
    intersects=area_of_interest,
    datetime="2019-06-01/2019-08-01",
    query={"eo:cloud_cover": {"lt": 10}},
).get_all_items()

# Retrieve all items as a xr.DataArray
stack = stackstac.stack(
    items,
    assets=["B05","B06","B07"], # Red Edge here, but you can use more!
    bounds_latlon=bounds,
    resolution=20
)

# Convert it to NBAR!
da = nbar_stackstac(
    stack,
    stac=endpoint,
    collection=collection
)
```

> **Warning**
>
> These examples are done using `Planetary Computer`. If you are using data cubes retrieved via STAC (e.g., by using `stackstac` or `cubo`), we recommend you to use this provider. The provider `Element84` is not supported at the moment.

### cubo

And going deeper, if you are using `cubo`:

```python
import cubo
import xarray as xr
from sen2nbar.nbar import nbar_cubo

# Get your cube
da = cubo.create(
    lat=47.84815,
    lon=13.37949,
    collection="sentinel-2-l2a",
    bands=["B02","B03","B04"], # RGB here, but you can add more bands!
    start_date="2020-01-01",
    end_date="2021-01-01",
    edge_size=64,
    resolution=10,
    query={"eo:cloud_cover": {"lt": 3}}
)

# Convert it to NBAR (This a xr.DataArray)
da = nbar_cubo(da)
```

## Bands

`sen2nbar` converts the following bands (if available in the input data):

- **RGB Bands**: 02, 03, 04.
- **Red Edge Bands**: 05, 06, 07.
- **Broad NIR Band**: 08.
- **SWIR Bands**: 11, 12.


## Installation

Install the latest version from PyPI:

```
pip install sen2nbar
```

Upgrade `sen2nbar` by running:

```
pip install -U sen2nbar
```

Install the latest version from conda-forge:

```
conda install -c conda-forge sen2nbar
```

Install the latest dev version from GitHub by running:

```
pip install git+https://github.com/davemlz/sen2nbar
```

## License

The project is licensed under the MIT license.

[![RSC4Earth](https://github.com/davemlz/sen2nbar/raw/main/docs/_static/esds.png)](https://rsc4earth.de/authors/esds/)