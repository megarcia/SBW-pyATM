#!/bin/bash
#
# $1 = sensitivity_11, etc.

cd "$1"_collected/summaries || exit 1
#
echo ""
echo "collecting $1 summary stats"
touch "$1"_collected_stats.csv
echo "simulation_number, n_total, n_female, n_male, n_nonfliers_total, n_nonfliers_female, n_nonfliers_male, n_fliers_total, n_fliers_female, n_fliers_male, sunset_min, sunset_mean, sunset_stdv, sunset_max, Tref_min, Tref_mean, Tref_stdv, Tref_max, flight_start_min, flight_start_mean, flight_start_stdv, flight_start_max, flight_start_female_min, flight_start_female_mean, flight_start_female_stdv, flight_start_female_max, flight_start_male_min, flight_start_male_mean, flight_start_male_stdv, flight_start_male_max, liftoff_vertical_v_mean, liftoff_vertical_v_stdv, liftoff_vertical_v_female_mean, liftoff_vertical_v_female_stdv, liftoff_vertical_v_male_mean, liftoff_vertical_v_male_stdv, liftoff_horizontal_v_mean, liftoff_horizontal_v_stdv, liftoff_horizontal_v_female_mean, liftoff_horizontal_v_female_stdv, liftoff_horizontal_v_male_mean, liftoff_horizontal_v_male_stdv, flight_duration_min, flight_duration_mean, flight_duration_stdv, flight_duration_max, flight_duration_female_min, flight_duration_female_mean, flight_duration_female_stdv, flight_duration_female_max, flight_duration_male_min, flight_duration_male_mean, flight_duration_male_stdv, flight_duration_male_max, flight_dist_min, flight_dist_mean, flight_dist_stdv, flight_dist_max, flight_dist_female_min, flight_dist_female_mean, flight_dist_female_stdv, flight_dist_female_max, flight_dist_male_min, flight_dist_male_mean, flight_dist_male_stdv, flight_dist_male_max, flight_speed_mean, flight_speed_stdv, flight_speed_female_mean, flight_speed_female_stdv, flight_speed_male_mean, flight_speed_male_stdv, flight_wind_speed_mean, flight_airspeed_mean, flight_airspeed_stdv, flight_airspeed_female_mean, flight_airspeed_female_stdv, flight_airspeed_male_mean, flight_airspeed_male_stdv, flight_meanAGL_mean, flight_meanAGL_stdv, flight_meanAGL_female_mean, flight_meanAGL_female_stdv, flight_meanAGL_male_mean, flight_meanAGL_male_stdv, flight_maxAGL_mean, flight_maxAGL_stdv, flight_maxAGL_female_mean, flight_maxAGL_female_stdv, flight_maxAGL_male_mean, flight_maxAGL_male_stdv, flight_maxAMSL_mean, flight_maxAMSL_stdv, flight_maxAMSL_female_mean, flight_maxAMSL_female_stdv, flight_maxAMSL_male_mean, flight_maxAMSL_male_stdv" >> "$1"_collected_stats.csv
for f in *_flights_summary.txt ; do
  echo "    $f"
  tail -n 37 "$f" | head -n 1 >> "$1"_collected_stats.csv
done
#
echo ""
echo "collecting $1 liftoff times"
touch "$1"_liftoff_times_histogram.csv
echo "5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150,155,160,165,170,175,180,185,190,195,200,205,210,215,220,225,230,235,240,245,250,255,260,265,270,275,280,285,290,295,300,305,310,315,320,325,330,335,340,345,350,355,360,365,370,375,380,385,390,395,400,405,410,415,420" >> "$1"_liftoff_times_histogram.csv
for f in *_flights_summary.txt ; do
  echo "    $f"
  tail -n 35 "$f" | head -n 1 >> "$1"_liftoff_times_histogram.csv
done
#
echo ""
echo "collecting $1 female liftoff times"
touch "$1"_liftoff_times_female_histogram.csv
echo "5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150,155,160,165,170,175,180,185,190,195,200,205,210,215,220,225,230,235,240,245,250,255,260,265,270,275,280,285,290,295,300,305,310,315,320,325,330,335,340,345,350,355,360,365,370,375,380,385,390,395,400,405,410,415,420" >> "$1"_liftoff_times_female_histogram.csv
for f in *_flights_summary.txt ; do
  echo "    $f"
  tail -n 33 "$f" | head -n 1 >> "$1"_liftoff_times_female_histogram.csv
done
#
echo ""
echo "collecting $1 male liftoff times"
touch "$1"_liftoff_times_male_histogram.csv
echo "5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150,155,160,165,170,175,180,185,190,195,200,205,210,215,220,225,230,235,240,245,250,255,260,265,270,275,280,285,290,295,300,305,310,315,320,325,330,335,340,345,350,355,360,365,370,375,380,385,390,395,400,405,410,415,420" >> "$1"_liftoff_times_male_histogram.csv
for f in *_flights_summary.txt ; do
  echo "    $f"
  tail -n 31 "$f" | head -n 1 >> "$1"_liftoff_times_male_histogram.csv
done
#
echo ""
echo "collecting $1 liftoff vertical speed"
touch "$1"_liftoff_vertical_speed_histogram.csv
echo "0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0" >> "$1"_liftoff_vertical_speed_histogram.csv
for f in *_flights_summary.txt ; do
  echo "    $f"
  tail -n 29 "$f" | head -n 1 >> "$1"_liftoff_vertical_speed_histogram.csv
done
#
echo ""
echo "collecting $1 female liftoff vertical speed"
touch "$1"_liftoff_vertical_speed_female_histogram.csv
echo "0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0" >> "$1"_liftoff_vertical_speed_female_histogram.csv
for f in *_flights_summary.txt ; do
  echo "    $f"
  tail -n 27 "$f" | head -n 1 >> "$1"_liftoff_vertical_speed_female_histogram.csv
done
#
echo ""
echo "collecting $1 male liftoff vertical speed"
touch "$1"_liftoff_vertical_speed_male_histogram.csv
echo "0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0" >> "$1"_liftoff_vertical_speed_male_histogram.csv
for f in *_flights_summary.txt ; do
  echo "    $f"
  tail -n 25 "$f" | head -n 1 >> "$1"_liftoff_vertical_speed_male_histogram.csv
done
#
echo ""
echo "collecting $1 liftoff horizontal speed"
touch "$1"_liftoff_horizontal_speed_histogram.csv
echo "0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0" >> "$1"_liftoff_horizontal_speed_histogram.csv
for f in *_flights_summary.txt ; do
  echo "    $f"
  tail -n 23 "$f" | head -n 1 >> "$1"_liftoff_horizontal_speed_histogram.csv
done
#
echo ""
echo "collecting $1 female liftoff horizontal speed"
touch "$1"_liftoff_horizontal_speed_female_histogram.csv
echo "0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0" >> "$1"_liftoff_horizontal_speed_female_histogram.csv
for f in *_flights_summary.txt ; do
  echo "    $f"
  tail -n 21 "$f" | head -n 1 >> "$1"_liftoff_horizontal_speed_female_histogram.csv
done
#
echo ""
echo "collecting $1 male liftoff horizontal speed"
touch "$1"_liftoff_horizontal_speed_male_histogram.csv
echo "0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0" >> "$1"_liftoff_horizontal_speed_male_histogram.csv
for f in *_flights_summary.txt ; do
  echo "    $f"
  tail -n 19 "$f" | head -n 1 >> "$1"_liftoff_horizontal_speed_male_histogram.csv
done
#
echo ""
echo "collecting $1 flight distances"
touch "$1"_flight_dist_histogram.csv
echo "5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150,155,160,165,170,175,180,185,190,195,200,205,210,215,220,225,230,235,240,245,250,255,260,265,270,275,280,285,290,295,300,305,310,315,320,325,330,335,340,345,350,355,360,365,370,375,380,385,390,395,400,405,410,415,420,425,430,435,440,445,450,455,460,465,470,475,480,485,490,495,500,505,510,515,520,525,530,535,540,545,550,555,560,565,570,575,580,585,590,595,600" >> "$1"_flight_dist_histogram.csv
for f in *_flights_summary.txt ; do
  echo "    $f"
  tail -n 17 "$f" | head -n 1 >> "$1"_flight_dist_histogram.csv
done
#
echo ""
echo "collecting $1 female flight distances"
touch "$1"_flight_dist_female_histogram.csv
echo "5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150,155,160,165,170,175,180,185,190,195,200,205,210,215,220,225,230,235,240,245,250,255,260,265,270,275,280,285,290,295,300,305,310,315,320,325,330,335,340,345,350,355,360,365,370,375,380,385,390,395,400,405,410,415,420,425,430,435,440,445,450,455,460,465,470,475,480,485,490,495,500,505,510,515,520,525,530,535,540,545,550,555,560,565,570,575,580,585,590,595,600" >> "$1"_flight_dist_female_histogram.csv
for f in *_flights_summary.txt ; do
  echo "    $f"
  tail -n 15 "$f" | head -n 1 >> "$1"_flight_dist_female_histogram.csv
done
#
echo ""
echo "collecting $1 male flight distances"
touch "$1"_flight_dist_male_histogram.csv
echo "5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150,155,160,165,170,175,180,185,190,195,200,205,210,215,220,225,230,235,240,245,250,255,260,265,270,275,280,285,290,295,300,305,310,315,320,325,330,335,340,345,350,355,360,365,370,375,380,385,390,395,400,405,410,415,420,425,430,435,440,445,450,455,460,465,470,475,480,485,490,495,500,505,510,515,520,525,530,535,540,545,550,555,560,565,570,575,580,585,590,595,600" >> "$1"_flight_dist_male_histogram.csv
for f in *_flights_summary.txt ; do
  echo "    $f"
  tail -n 13 "$f" | head -n 1 >> "$1"_flight_dist_male_histogram.csv
done
#
echo ""
echo "collecting $1 flight horizontal airspeed"
touch "$1"_flight_horizontal_airspeed_histogram.csv
echo "0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,3.0,3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,4.0,4.1,4.2,4.3,4.4,4.5,4.6,4.7,4.8,4.9,5.0" >> "$1"_flight_horizontal_airspeed_histogram.csv
for f in *_flights_summary.txt ; do
  echo "    $f"
  tail -n 11 "$f" | head -n 1 >> "$1"_flight_horizontal_airspeed_histogram.csv
done
#
echo ""
echo "collecting $1 female flight horizontal airspeed"
touch "$1"_flight_horizontal_airspeed_female_histogram.csv
echo "0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,3.0,3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,4.0,4.1,4.2,4.3,4.4,4.5,4.6,4.7,4.8,4.9,5.0" >> "$1"_flight_horizontal_airspeed_female_histogram.csv
for f in *_flights_summary.txt ; do
  echo "    $f"
  tail -n 9 "$f" | head -n 1 >> "$1"_flight_horizontal_airspeed_female_histogram.csv
done
#
echo ""
echo "collecting $1 male flight horizontal airspeed"
touch "$1"_flight_horizontal_airspeed_male_histogram.csv
echo "0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4,2.5,2.6,2.7,2.8,2.9,3.0,3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,4.0,4.1,4.2,4.3,4.4,4.5,4.6,4.7,4.8,4.9,5.0" >> "$1"_flight_horizontal_airspeed_male_histogram.csv
for f in *_flights_summary.txt ; do
  echo "    $f"
  tail -n 7 "$f" | head -n 1 >> "$1"_flight_horizontal_airspeed_male_histogram.csv
done
#
echo ""
echo "collecting $1 flight altitudes"
touch "$1"_flight_alt_histogram.csv
echo "20,40,60,80,100,120,140,160,180,200,220,240,260,280,300,320,340,360,380,400,420,440,460,480,500,520,540,560,580,600,620,640,660,680,700,720,740,760,780,800,820,840,860,880,900,920,940,960,980,1000,1020,1040,1060,1080,1100,1120,1140,1160,1180,1200,1220,1240,1260,1280,1300,1320,1340,1360,1380,1400,1420,1440,1460,1480,1500,1520,1540,1560,1580,1600,1620,1640,1660,1680,1700,1720,1740,1760,1780,1800,1820,1840,1860,1880,1900,1920,1940,1960,1980,2000" >> "$1"_flight_alt_histogram.csv
for f in *_flights_summary.txt ; do
  echo "    $f"
  tail -n 5 "$f" | head -n 1 >> "$1"_flight_alt_histogram.csv
done
#
echo ""
echo "collecting $1 female flight altitudes"
touch "$1"_flight_alt_female_histogram.csv
echo "20,40,60,80,100,120,140,160,180,200,220,240,260,280,300,320,340,360,380,400,420,440,460,480,500,520,540,560,580,600,620,640,660,680,700,720,740,760,780,800,820,840,860,880,900,920,940,960,980,1000,1020,1040,1060,1080,1100,1120,1140,1160,1180,1200,1220,1240,1260,1280,1300,1320,1340,1360,1380,1400,1420,1440,1460,1480,1500,1520,1540,1560,1580,1600,1620,1640,1660,1680,1700,1720,1740,1760,1780,1800,1820,1840,1860,1880,1900,1920,1940,1960,1980,2000" >> "$1"_flight_alt_female_histogram.csv
for f in *_flights_summary.txt ; do
  echo "    $f"
  tail -n 3 "$f" | head -n 1 >> "$1"_flight_alt_female_histogram.csv
done
#
echo ""
echo "collecting $1 male flight altitudes"
touch "$1"_flight_alt_male_histogram.csv
echo "20,40,60,80,100,120,140,160,180,200,220,240,260,280,300,320,340,360,380,400,420,440,460,480,500,520,540,560,580,600,620,640,660,680,700,720,740,760,780,800,820,840,860,880,900,920,940,960,980,1000,1020,1040,1060,1080,1100,1120,1140,1160,1180,1200,1220,1240,1260,1280,1300,1320,1340,1360,1380,1400,1420,1440,1460,1480,1500,1520,1540,1560,1580,1600,1620,1640,1660,1680,1700,1720,1740,1760,1780,1800,1820,1840,1860,1880,1900,1920,1940,1960,1980,2000" >> "$1"_flight_alt_male_histogram.csv
for f in *_flights_summary.txt ; do
  echo "    $f"
  tail -n 1 "$f" >> "$1"_flight_alt_male_histogram.csv
done
#
mv *.csv ../
cd ../../
echo ""
