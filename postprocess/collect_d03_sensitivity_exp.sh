#!/bin/bash
#
# $1 = date
# $2 = experiment number
#

tar -xzf miniconda3.tar.gz
export PATH=~/miniconda3/bin:$PATH
cwd=$(pwd)
cd /home/megarcia || exit 1
rm -r *
ln -Ffs "$cwd"/miniconda3 miniconda3
cd "$cwd" || exit 1
tar -xf "$1"_sensitivity_"$2"_summaries.tar
rm "$1"_sensitivity_"$2"_summaries.tar

cd sensitivity_"$(printf %02d "$2")" || exit 1
for d in WRF-NARR_d03_"$1"_simulation_"$(printf %02d "$2")"_000??_summary.tar.gz ; do
  echo "expanding $d"
  tar -xzf "$d"
done
cd ../

mkdir sensitivity_"$2"_collected

mkdir sensitivity_"$2"_collected/dens_grids
python combine_dens_grids.py "$1" "$2"

mkdir sensitivity_"$2"_collected/dvel_grids
python combine_dvel_grids.py "$1" "$2"

mkdir sensitivity_"$2"_collected/summaries
cp sensitivity_"$(printf %02d "$2")"/WRF-NARR_d03_"$1"_simulation_"$(printf %02d "$2")"_000??_summary/*_flights_summary.txt sensitivity_"$2"_collected/summaries/
bash collect_experiment_stats.sh sensitivity_"$2"
python plot_liftoff_time_histograms.py "$1" sensitivity_"$2"
python plot_flight_distance_histograms.py "$1" sensitivity_"$2"
python plot_flight_altitude_histograms.py "$1" sensitivity_"$2"

mkdir sensitivity_"$2"_collected/topo_maps
cp sensitivity_"$(printf %02d "$2")"/WRF-NARR_d03_"$1"_simulation_"$(printf %02d "$2")"_000??_summary/*_flights_topo_map.png sensitivity_"$2"_collected/topo_maps/

mkdir sensitivity_"$2"_collected/liftoff_grids
cp sensitivity_"$(printf %02d "$2")"/WRF-NARR_d03_"$1"_simulation_"$(printf %02d "$2")"_000??_summary/liftoff_*.npy sensitivity_"$2"_collected/liftoff_grids/
cp sensitivity_"$(printf %02d "$2")"/WRF-NARR_d03_"$1"_simulation_"$(printf %02d "$2")"_000??_summary/liftoff_*.csv sensitivity_"$2"_collected/liftoff_grids/

mkdir sensitivity_"$2"_collected/landing_grids
cp sensitivity_"$(printf %02d "$2")"/WRF-NARR_d03_"$1"_simulation_"$(printf %02d "$2")"_000??_summary/landing_*.npy sensitivity_"$2"_collected/landing_grids/
cp sensitivity_"$(printf %02d "$2")"/WRF-NARR_d03_"$1"_simulation_"$(printf %02d "$2")"_000??_summary/landing_*.csv sensitivity_"$2"_collected/landing_grids/

mkdir sensitivity_"$2"_collected/egg_deposition_grids
cp sensitivity_"$(printf %02d "$2")"/WRF-NARR_d03_"$1"_simulation_"$(printf %02d "$2")"_000??_summary/egg_deposition_*.npy sensitivity_"$2"_collected/egg_deposition_grids/
cp sensitivity_"$(printf %02d "$2")"/WRF-NARR_d03_"$1"_simulation_"$(printf %02d "$2")"_000??_summary/egg_deposition_*.csv sensitivity_"$2"_collected/egg_deposition_grids/

tar -czf "$1"_sensitivity_"$2"_collected.tar.gz sensitivity_"$2"_collected
