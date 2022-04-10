# pyIntertidalDEM
pyIntertidalDEM is a set of libraries and procedures written in python to extract shorelines from spectral images using a ophisticated shoreline extraction algorithm. These modules are developed in Python v3 environment.

## Setup
Currently the toolbox is only available as a git repository, and not published in any of the common python repository - like pip or conda. Below is how you can install the package. It is highly recommended to use conda/miniconda environment. 

* Step 0: Download the source-code in a directory. For that use either the download button or `git clone` command.
* Step 1: Create a conda environment from environment.yml file `conda env create -n pyintdem -f environment.yml`. It will create a new environment in your computer and install the pyintdem library.
* Step 3: Activate conda environment `conda activate pyIntertidalDEM`. Remember to use this environment each time you work with the toolbox.

## Processing
As explained in the associated [publication](#publications), the toolbox was developed to analyze Sentinel-2 imageries. However, it is generic enough (e.g., Band class) to use with other image sets.

Example scripts are provided showing various steps of the processing.

* `examples/step_1_extract.py`: This is a small script for extracting .zip archives of Sentinel-2 Images and nicely organize them tile-by-tile.
* `examples/step_2_create_mask.py`: This example illustrates how to create a mask from a set of images in a tile. This gross water mask is then used in the next step for final analysis. To be noted that, this mask generation procedure needs to be done only once, or can be fully skipped if you already have a gross mask of the land-water body.
* `examples/step_3_analysis.py`: This scripts implements the Sentinel-2 processing methodology shown in Khan et al. 2019. Various classes (e.g., Band, RGB) from the toolbox is used for the analysis, and the script can be modified as required by the end-user to test or to implement their own method. 

## Publications
Khan, M. J. U., Ansary, M. N., Durand, F., Testut, L., Ishaque, M., Calmant, S., Krien, Y., Islam, A. S. & Papa, F. [High-Resolution Intertidal Topography from Sentinel-2 Multi-Spectral Imagery: Synergy between Remote Sensing and Numerical Modeling](https://doi.org/10.3390/rs11242888), Remote Sensing, MDPI AG, 2019, 11, 2888, doi:[10.3390/rs11242888](https://doi.org/10.3390/rs11242888)

## Documentation
Currently the program is documented at source level and strongly believed that the use of the program falls on the left side of the xkcd documentation spectram!

![XKCD MANUAL](https://imgs.xkcd.com/comics/manuals.png)
