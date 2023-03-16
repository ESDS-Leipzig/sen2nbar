import unittest

import cubo
import xarray as xr

from sen2nbar.nbar import nbar_cubo


class Test(unittest.TestCase):
    """Tests for the sen2nbar package."""

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


if __name__ == "__main__":
    unittest.main()
