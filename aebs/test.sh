#!/usr/bin/sh
PYTHON_PATH=/cygdrive/c/Python27

function usage {
  cat <<END
usage: ./test.sh option...

*required options*

  -d <measurement-directory> 
    directory where the test measurements are stored in cygwin style

*optional options*

  -p <python-path>
    directory of python exe in cygwin style
END
  exit 0
}

function findmeas {
  m=`find $1 -name $2 -type f`
  echo `cygpath -ma $m`
}

while getopts "hd:" opt; do
  case $opt in
    h) usage;;
    d) MEAS_DIR=$OPTARG;;
    p) PYTHON_PATH=$OPTARG;;
  esac
done


PATH=$PYTHON_PATH:$PATH

m1=`findmeas $MEAS_DIR comparison_all_sensors_2012-08-01_17-39-00.h5`
m2=`findmeas $MEAS_DIR comparison_all_sensors_2012-08-16_10-46-11.MF4`
m3=`findmeas $MEAS_DIR comparison_all_sensors_2012-09-03_14-14-46.MF4`
m4=`findmeas $MEAS_DIR H566_2013-04-09_06-52-13.mf4`
m5=`findmeas $MEAS_DIR H566_2013-03-20_18-02-39.mf4`

python src/aebs/sdf/assoOHL.py              $m1
python src/aebs/sdf/fuseOHL.py              $m1
python src/aebs/sdf/asso_cvr3_ac100.py      $m2
python src/aebs/sdf/asso_cvr3_sCam_cipv.py  $m1
python src/aebs/sdf/asso_cvr3_sCam.py       $m1
python src/aebs/sdf/asso_cvr3_fus_result.py $m1
python src/aebs/sdf/asso_cvr3_fus_recalc.py $m1

python test/test_asso_cvr3_fus_modules.py -m $m3

python test/fill/test_fill_flr20_flc20_raw.py -m $m4
python test/fill/test_fill_flr20_aeb_track.py -m $m4
python test/fill/test_fill_flr20_acc_track.py -m $m4
python test/fill/test_calc_flr20_egomotion.py -m $m4
python test/sdf/test_asso_flr20_fus_result.py -m $m4
python test/sdf/test_asso_flr20_fus_result.py -m $m5
