# pyIntertidalDEM

pyIntertidalDEM is a set of libraries and procedures written in python to extract shorelines from spectral images using
a sophisticated shoreline extraction algorithm. These modules are developed in Python v3 environment.

## Setup

Currently, the toolbox is only available as a git repository, and not published in any of the common python repository -
like pip or conda. Below is how you can install the package. It is highly recommended to use conda/miniconda
environment, and install other dependencies from conda-forge.

```shell
$ conda create -c conda-forge -n pyintdem python=3.11 numpy scipy pandas xarray dask netCDF4 rasterio rioxarray matplotlib cartopy cmocean gdal libgdal-jp2openjpeg shapely geopandas ipykernel notebook tqdm utide
$ conda activate pyintdem
$ git clone https://github.com/jamal919/pyIntertidalDEM
$ pip install -e . # -e allows for linking
```

## Processing

As explained in the associated [publication](#publications), the toolbox was developed to analyze Sentinel-2 imageries.
However, it is generic enough (e.g., Band class) to use with other image sets.

In the `examples` folder, there are several step-by-step notebooks to run the whole processing chain. Here is a general
description of these notebooks - 

- `01_download_dataset.ipynb`: Shows example of how to download cloud-free/filtered dataset from Theia or Copernicus.
- `02_generate_mask.ipynb`: Shows example of how to generate water masks for using in the processing stage.
- `03_extract_shoreline.ipynb`: Shows processing of Sentinel-2 imagery using Khan et al. (2019) pyIntertidal method.
- `04_reference.ipynb`: Shows vertical referencing using waterlevel dataset.

## Publications

Khan, M. J. U., Ansary, M. N., Durand, F., Testut, L., Ishaque, M., Calmant, S., Krien, Y., Islam, A. S. & Papa,
F. [High-Resolution Intertidal Topography from Sentinel-2 Multi-Spectral Imagery: Synergy between Remote Sensing and Numerical Modeling](https://doi.org/10.3390/rs11242888),
Remote Sensing, MDPI AG, 2019, 11, 2888, doi:[10.3390/rs11242888](https://doi.org/10.3390/rs11242888)

## Documentation

The package is documented enough at source level and strongly believed that the use of the program falls on the left
side of the xkcd documentation spectrum!

![XKCD MANUAL](https://imgs.xkcd.com/comics/manuals.png)
