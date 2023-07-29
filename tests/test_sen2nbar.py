import unittest

import cubo
import planetary_computer as pc
import pystac_client
import stackstac
import xarray as xr

from sen2nbar.nbar import nbar_cubo, nbar_stackstac


class Test(unittest.TestCase):
    """Tests for the sen2nbar package."""

    def test_stackstac(self):
        """Test the nbar_stackstac with Planetary Computer"""
        endpoint = "https://planetarycomputer.microsoft.com/api/stac/v1"
        collection = "sentinel-2-l2a"
        bounds = (-148.565368, 60.800723, -147.443389, 61.183638)

        catalog = pystac_client.Client.open(endpoint, modifier=pc.sign_inplace)

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

        items = catalog.search(
            collections=[collection],
            intersects=area_of_interest,
            datetime="2019-06-01/2019-08-01",
            query={"eo:cloud_cover": {"lt": 10}},
        ).get_all_items()

        stack = stackstac.stack(
            items, assets=["B05", "B06", "B07"], bounds_latlon=bounds, resolution=20
        )

        da = nbar_stackstac(stack, stac=endpoint, collection=collection)
        self.assertIsInstance(da, xr.DataArray)

    def test_cubo(self):
        """Test the nbar_cubo"""
        da = nbar_cubo(
            cubo.create(
                lat=50,
                lon=10,
                collection="sentinel-2-l2a",
                bands=["B02", "B03", "B04"],
                start_date="2021-06-01",
                end_date="2021-06-10",
                edge_size=32,
                resolution=10,
            )
        )
        self.assertIsInstance(da, xr.DataArray)

    def test_cubo_not_all_angles(self):
        """Test the nbar_cubo"""
        da = nbar_cubo(
            cubo.create(
                lat=64.25611,
                lon=19.7745,
                collection="sentinel-2-l2a",
                bands=["B02", "B03", "B04"],
                start_date="2016-01-01",
                end_date="2016-03-01",
                edge_size=512,
                resolution=10,
            )
        )
        self.assertIsInstance(da, xr.DataArray)


if __name__ == "__main__":
    unittest.main()
