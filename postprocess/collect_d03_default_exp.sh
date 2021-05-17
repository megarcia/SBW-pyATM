#!/bin/bash
#
# $1 = date
#

tar -xzf miniconda3.tar.gz
export PATH=~/miniconda3/bin:$PATH
cwd=$(pwd)
cd /home/megarcia || exit 1
rm -r *
ln -Ffs "$cwd"/miniconda3 miniconda3
cd "$cwd" || exit 1
tar -xf "$1"_default_summaries.tar
rm "$1"_default_summaries.tar

cd default || exit 1
for d in WRF-NARR_d03_"$1"_default_simulation_000??_summary.tar.gz ; do
  echo "expanding $d"
  tar -xzf "$d"
done
cd ../

mkdir default_collected

# mkdir default_collected/dens_grids
# python combine_dens_grids.py "$1" default

# mkdir default_collected/dvel_grids
# python combine_dvel_grids.py "$1" default

mkdir default_collected/summaries
cp default/WRF-NARR_d03_"$1"_simulation_000??_summary/*_flights_summary.txt default_collected/summaries/
bash collect_experiment_stats.sh default
python plot_liftoff_time_histograms.py "$1" default
python plot_flight_distance_histograms.py "$1" default
python plot_flight_altitude_histograms.py "$1" default

mkdir default_collected/topo_maps
cp default/WRF-NARR_d03_"$1"_simulation_000??_summary/*_flights_topo_map.png default_collected/topo_maps/

mkdir default_collected/flier_locs
cp default/WRF-NARR_d03_"$1"_simulation_000??_summary/locs_*.csv default_collected/flier_locs/

mkdir default_collected/liftoff_locs
# cp default/WRF-NARR_d03_"$1"_simulation_000??_summary/liftoff_*.npy default_collected/liftoff_locs/
cp default/WRF-NARR_d03_"$1"_simulation_000??_summary/liftoff_*.csv default_collected/liftoff_locs/

mkdir default_collected/landing_locs
# cp default/WRF-NARR_d03_"$1"_simulation_000??_summary/landing_*.npy default_collected/landing_locs/
cp default/WRF-NARR_d03_"$1"_simulation_000??_summary/landing_*.csv default_collected/landing_locs/

mkdir default_collected/egg_deposition
# cp default/WRF-NARR_d03_"$1"_simulation_000??_summary/egg_deposition_*.npy default_collected/egg_deposition/
cp default/WRF-NARR_d03_"$1"_simulation_000??_summary/egg_deposition_*.csv default_collected/egg_deposition/

tar -czf "$1"_default_collected.tar.gz default_collected
