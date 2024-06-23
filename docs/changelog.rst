Changelog
=========

v2024.6.0
---------

- Pinned: :code:`cubo>=2024.6.0`. This avoids :code:`numpy>=2.0.0` since :code:`stackstac` breaks.

v2023.8.1
---------

- Fixed the occurrence of infinite values.

v2023.8.0
---------

- Fixed concatenation error when c-factor had been reprojected.

v2023.7.2
---------

- Raise :code:`ValueError` events when not all bands include angle values.
- Exclude timesteps in :code:`nbar_stac` when not all bands include angle values.

v2023.7.1
---------

- Catch RuntimeWarning events when doing :code:`np.nanmean` of detector angles.
- Added description to :code:`tqdm` progress bar and set :code:`leave=False`.
- Replaced :code:`get_all_items()` by :code:`item_collection()`.

v2023.7.0
---------

- Fixed path separators by os `(#4) <https://github.com/ESDS-Leipzig/sen2nbar/issues/4>`_.
- Pinned latest versions: :code:`cubo>=2023.7.0`.
- Fixed the required datatype of the EPSG code for stackstac `(#5) <https://github.com/ESDS-Leipzig/cubo/issues/5>`_.

v2023.3.0
---------

- First release of :code:`sen2nbar`!