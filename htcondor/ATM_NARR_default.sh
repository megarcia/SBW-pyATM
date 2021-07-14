#!/bin/bash
#
# $1 = $(grid)_$(date) = simulation name
# $2 = $(Process) = ensemble replicate number
#
echo ""
echo "------------------------------"
date
echo "installing python"
echo ""
bash miniconda.sh -b -p miniconda
echo ""
export PATH=$(pwd)/miniconda/bin:$PATH
echo "PATH = $PATH"
echo ""
eval "$(miniconda/bin/conda shell.bash hook)"
# conda init
# echo ""
conda update -y -n base -c defaults conda
conda install -y -c conda-forge iso8601 numpy scipy pandas matplotlib=3.2 basemap netcdf4 libiconv gdal basemap-data-hires wrf-python

echo "------------------------------"
date
export PYTHONPATH=$(pwd)/miniconda:$(pwd)/miniconda/lib/python3.8:$(pwd)/miniconda/lib/python3.8/lib-dynload:$(pwd)/miniconda/lib/python3.8/site-packages
echo "PYTHONPATH = $PYTHONPATH"
echo ""
export PYTHONHOME=$PYTHONPATH
echo "PYTHONHOME = $PYTHONHOME"
echo ""
export PROJ_LIB=$(pwd)/miniconda/share/proj
echo "PROJ_LIB = $PROJ_LIB"

echo "------------------------------"
date
echo "extracting WRF grids"
echo ""
tar -xzf "$1"_grids.tar.gz
rm "$1"_grids.tar.gz

echo "------------------------------"
date
echo "making model output directories"
echo ""
mkdir "$1"_simulation_$(printf %05d "$2")_output
mkdir "$1"_simulation_$(printf %05d "$2")_summary

echo "------------------------------"
date
echo "starting model"
mv Simulation_specifications_"$1".py Simulation_specifications.py
python Model_control.py "$2"

echo ""
echo "------------------------------"
date
echo "model finished execution"
echo ""

echo "------------------------------"
date
echo "copying model and runtime files to output directories"
echo ""
cp *.py "$1"_simulation_$(printf %05d "$2")_output/
cp _condor_std* "$1"_simulation_$(printf %05d "$2")_output/
cp *.py "$1"_simulation_$(printf %05d "$2")_summary/
cp _condor_std* "$1"_simulation_$(printf %05d "$2")_summary/

echo "------------------------------"
date
echo "compressing output directories"
echo ""
tar -czf "$1"_default_simulation_$(printf %05d "$2")_output.tar.gz "$1"_simulation_$(printf %05d "$2")_output
tar -czf "$1"_default_simulation_$(printf %05d "$2")_summary.tar.gz "$1"_simulation_$(printf %05d "$2")_summary

echo "------------------------------"
date
echo "all done!"
echo ""
