## SBW-pyATM

This is the **Python-based Atmospheric Transport Model for Spruce Budworm** as published in January 2022:

Garcia, M., B.R. Sturtevant, R. Saint-Amant, J.J. Charney, J. Delisle, Y. Boulanger, P.A. Townsend, and J. Régnière, 2022: "Modeling weather-driven long-distance dispersal of spruce budworm moths (_Choristoneura fumiferana_). Part 1: Model description." _Agricultural and Forest Meteorology_, doi: [10.1016/j.agrformet.2022.108815](https://doi.org/10.1016/j.agrformet.2022.108815).

Contact: [matt.e.garcia@gmail.com](mailto://matt.e.garcia@gmail.com)

The paper is an Open-Access #OA publication that is free to everyone. Note that a link to Supplemental Information (PDF) is also provided on that publication page.

Additional information and materials for that paper are located at:
* Code supplement: [GitHub repository](https://github.com/megarcia/Garcia_etal_2022a)
* Sample datasets: [Dryad, doi: 10.5061/dryad.mpg4f4r19](https://doi.org/10.5061/dryad.mpg4f4r19)
* Supplemental Animations: [Zenodo, doi: 10.5281/zenodo.5534999](https://doi.org/10.5281/zenodo.5534999)

<hr>

### Repository contents:

LICENSE (text of GPLv3)

README.md (this file)

docs
* WRF simulations Technical Document (PDF)
* pyATM Technical Document (PDF)

source

tests
* Solar calculations (Solar_test.py)
* Circadian liftoff times (Circadian_test.py)

htcondor

preprocess
* htcondor

postprocess
* htcondor

<hr>

### Python requirements:

To use the SBW–pyATM code, you will need the following packages and libraries in your local python installation:

* python standard libraries: copy, datetime, warnings, os, sys
* basemap (a.k.a. mpl_toolkits.basemap)
* basemap-data-hires
* gdal (via osgeo)
* iso8601
* matplotlib
* netCDF4
* numpy
* pandas
* pyproj
* scipy.interpolate
* wrf-python (as wrf)

I recommend the [Anaconda](http://www.anaconda.com/products/individual) package installation for python, and then using the `conda` package manager, but the `pip` package manager works just as well.

The components of the pyATM software, including their external and inter-dependencies, are described in the pyATM Technical Document (see the docs folder, above).

<hr>

### Usage:

Details regarding model execution, including the use of HTCondor, are forthcoming.

Details regarding pre-processing operations and post-processing options are forthcoming.

<hr>

### Model Operation:

Flowcharts describing the order of operations during a model simulation are included in the pyATM Technical Document (see the docs folder, above).


