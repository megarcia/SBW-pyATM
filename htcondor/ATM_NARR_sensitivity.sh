#!/bin/bash
#
# $(name) $(exp_num) $(variable) $(value) $(Process)
# $1 = simulation name
# $2 = experiment number
# $3 = variable name
# $4 = variable value
# $5 = simulation number
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
ln -s libtinfo.so.6 miniconda/lib/libtinfo.so.5

echo "------------------------------"
date
export PYTHONPATH=$(pwd)/miniconda:$(pwd)/miniconda/lib/python3.7:$(pwd)/miniconda/lib/python3.7/lib-dynload:$(pwd)/miniconda/lib/python3.7/site-packages
echo "PYTHONPATH = $PYTHONPATH"
echo ""
export PYTHONHOME=$PYTHONPATH
echo "PYTHONHOME = $PYTHONHOME"
echo ""
export PROJ_LIB=$(pwd)/miniconda/share/proj
echo "PROJ_LIB = $PROJ_LIB"
echo ""

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
mkdir "$1"_simulation_$(printf %02d "$2")_$(printf %05d "$5")_output
mkdir "$1"_simulation_$(printf %02d "$2")_$(printf %05d "$5")_summary

echo "------------------------------"
date
echo "starting model"
mv Simulation_specifications_"$1".py Simulation_specifications.py
python Model_control.py "$2" "$3" "$4" "$5"

echo ""
echo "------------------------------"
date
echo "model finished execution"
echo ""

echo "------------------------------"
date
echo "copying model and runtime files to output directories"
echo ""
cp *.py "$1"_simulation_$(printf %02d "$2")_$(printf %05d "$5")_output/
cp _condor_std* "$1"_simulation_$(printf %02d "$2")_$(printf %05d "$5")_output/
cp *.py "$1"_simulation_$(printf %02d "$2")_$(printf %05d "$5")_summary/
cp _condor_std* "$1"_simulation_$(printf %02d "$2")_$(printf %05d "$5")_summary/

echo "------------------------------"
date
echo "compressing output directories"
echo ""
tar -czf "$1"_simulation_$(printf %02d "$2")_$(printf %05d "$5")_output.tar.gz "$1"_simulation_$(printf %02d "$2")_$(printf %05d "$5")_output
tar -czf "$1"_simulation_$(printf %02d "$2")_$(printf %05d "$5")_summary.tar.gz "$1"_simulation_$(printf %02d "$2")_$(printf %05d "$5")_summary

echo "------------------------------"
date
echo "all done!"
echo ""
