import io
import os
import re

from setuptools import find_packages, setup


def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    text_type = type(u"")
    with io.open(filename, mode="r", encoding="utf-8") as fd:
        return re.sub(text_type(r":[a-z]+:`~?(.*?)`"), text_type(r"``\1``"), fd.read())


setup(
    name="sen2nbar",
    version="2023.7.2",
    url="https://github.com/ESDS-Leipzig/sen2nbar",
    license="MIT",
    author="David Montero Loaiza",
    author_email="dml.mont@gmail.com",
    description="Nadir BRDF Adjusted Reflectance (NBAR) for Sentinel-2 in Python",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=("tests",)),
    package_data={"sen2nbar": ["data/*.json"]},
    install_requires=[
        "cubo>=2023.7.2",
        "pystac",
        "rasterio>=1.3.6",
        "requests",
        "rioxarray>=0.13.4",
        "scipy>=1.10.1",
        "tqdm",
        "xmltodict",
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
    ],
)
