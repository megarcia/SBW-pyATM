#!/bin/bash
#
tar -xzf miniconda2.tar.gz
export PATH=miniconda2/bin:$PATH
cwd=$(pwd)
cd /home/megarcia
ln -Ffs $cwd/miniconda2 miniconda2
cd $cwd
python reduce_wrfout.py /mnt/gluster/megarcia/WRF/2013_case_study/$1 $2 $3
rm *.pyc
