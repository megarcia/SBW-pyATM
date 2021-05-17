#!/bin/bash
cp Simulation_specifications_$1_$2.py Simulation_specifications.py
python map_wrf_io_T_wind_sfc.py WRF-$1 WRF_$1/$2_reduced
python map_wrf_io_T_wind_upa.py WRF-$1 WRF_$1/$2_reduced
