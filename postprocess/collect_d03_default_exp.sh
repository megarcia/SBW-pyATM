#!/bin/bash
#
# $1 = date (e.g. 20130715)
#

date=$1

tar -xzf miniconda3.tar.gz
export PATH=~/miniconda3/bin:$PATH
export PROJ_LIB=~/miniconda3/share/proj
cwd=$(pwd)
cd /home/megarcia || exit 1
rm -r ./*
ln -Ffs "$cwd"/miniconda3 miniconda3
cd "$cwd" || exit 1

echo "extracting summary directories"
tar -xf "$date"_default_summaries.tar
rm "$date"_default_summaries.tar

cd default || exit 1
echo "expanding summary directories"
for dir in WRF-NARR_d03_"$date"_default_simulation_*_summary.tar.gz ; do
  echo "    $dir"
  tar -xzf "$dir"
  rm "$dir"
done
cd ../

target_dir="default_collected"
mkdir $target_dir
for dir in summaries topo_maps liftoff_locs landing_locs egg_deposition ; do
  mkdir "$target_dir"/"$dir"
done

echo "collecting flight summary files"
for source_dir in default/WRF-NARR_d03_"$date"_simulation_*_summary ; do
  mv "$source_dir"/*_flights_summary.txt "$target_dir"/summaries/
done
bash collect_experiment_stats.sh default
python summarize_experiment_stats.py "$date" default
python plot_liftoff_time_histograms.py "$date" default
python plot_flight_distance_histograms.py "$date" default
python plot_flight_altitude_histograms.py "$date" default

echo "collecting trajectory maps"
for source_dir in default/WRF-NARR_d03_"$date"_simulation_*_summary ; do
  mv "$source_dir"/*_flights_topo_map.png "$target_dir"/topo_maps/
done

echo "collecting liftoff files"
for source_dir in default/WRF-NARR_d03_"$date"_simulation_*_summary ; do
  mv "$source_dir"/liftoff_*.csv "$target_dir"/liftoff_locs/
done
for sex in male female ; do
  python map_locations_hexbin.py "$date" default "$sex" liftoff
done

echo "collecting landing files"
for source_dir in default/WRF-NARR_d03_"$date"_simulation_*_summary ; do
  mv "$source_dir"/landing_*.csv "$target_dir"/landing_locs/
done
for sex in male female ; do
  python map_locations_hexbin.py "$date" default "$sex" landing
done

echo "collecting egg deposition files"
for source_dir in default/WRF-NARR_d03_"$date"_simulation_*_summary ; do
  mv "$source_dir"/egg_deposition_*.csv "$target_dir"/egg_deposition/
done
python map_oviposition_hexbin.py "$date" default

echo "compressing directories and files"
cd $target_dir || exit 1
tar -czf csv_files.tar.gz ./*.csv
rm ./*.csv
tar -czf png_files.tar.gz ./*.png
rm ./*.png
for dir in summaries topo_maps liftoff_locs landing_locs egg_deposition ; do
  tar -czf "$dir".tar.gz "$dir"
  rm -r $dir
done
cd ../

echo "collecting flier location files"
mkdir "$target_dir"/flier_locs
yy=${date:0:4}
mm=${date:4:2}
dd=${date:6:2}
for hh in {21..23} ; do
  for mn in {0..59} ; do 
    time_dir="$yy"$(printf %02d "$mm")$(printf %02d "$dd")_$(printf %02d "$hh")$(printf %02d "$mn")
    echo "    $time_dir"
    mkdir "$target_dir"/flier_locs/"$time_dir"
    for source_dir in default/WRF-NARR_d03_"$date"_simulation_*_summary ; do
      # locs_2013-07-15T23:59:00+00:00_00999.csv
      time_fnames=locs_"$yy"-$(printf %02d "$mm")-$(printf %02d "$dd")T$(printf %02d "$hh"):$(printf %02d "$mn")
      mv "$source_dir"/"$time_fnames"*.csv "$target_dir"/flier_locs/"$time_dir"/
    done
    cd "$target_dir"/flier_locs || exit 1
    tar -czf "$time_dir".tar.gz "$time_dir"
    rm -r "$time_dir"
    cd ../../ 
  done
done
(( dd++ ))
if [ "$dd" -gt 31 ] ; then
  (( mm++ ))
  (( dd = 1 ))
fi
for hh in {0..8} ; do
  for mn in {0..59} ; do 
    time_dir="$yy"$(printf %02d "$mm")$(printf %02d "$dd")_$(printf %02d "$hh")$(printf %02d "$mn")
    echo "    $time_dir"
    mkdir "$target_dir"/flier_locs/"$time_dir"
    for source_dir in default/WRF-NARR_d03_"$date"_simulation_*_summary ; do
      # locs_2013-07-16T00:09:00+00:00_00999.csv
      time_fnames=locs_"$yy"-$(printf %02d "$mm")-$(printf %02d "$dd")T$(printf %02d "$hh"):$(printf %02d "$mn")
      mv "$source_dir"/"$time_fnames"*.csv "$target_dir"/flier_locs/"$time_dir"/
    done
    cd "$target_dir"/flier_locs || exit 1
    tar -czf "$time_dir".tar.gz "$time_dir"
    rm -r "$time_dir"
    cd ../../ 
  done
done

tar -cf "$date"_default_collected.tar default_collected

