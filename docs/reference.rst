API Reference
=============

Here you will find all :code:`sen2nbar` methods:

sen2nbar.nbar
-------------

Core module of :code:`sen2nbar`. Computes NBAR:

.. currentmodule:: sen2nbar.nbar

.. autosummary::
   :toctree: stubs

   nbar_SAFE
   nbar_stac
   nbar_stackstac
   nbar_cubo


sen2nbar.metadata
-----------------

Extracts information from Sentinel-2 metadata:

.. currentmodule:: sen2nbar.metadata

.. autosummary::
   :toctree: stubs

   angles_from_metadata
   get_processing_baseline


sen2nbar.kernels
----------------

Computes the required kernels for BRDF:

.. currentmodule:: sen2nbar.kernels

.. autosummary::
   :toctree: stubs

   kgeo
   kvol


sen2nbar.brdf
-------------

Computes the BRDF:

.. currentmodule:: sen2nbar.brdf

.. autosummary::
   :toctree: stubs

   brdf


sen2nbar.c_factor
-----------------

Computes the c-factor:

.. currentmodule:: sen2nbar.c_factor

.. autosummary::
   :toctree: stubs

   c_factor
   c_factor_from_metadata
   c_factor_from_item
   