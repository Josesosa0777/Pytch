#!/usr/bin/sh

PYTHON_PATH=/cygdrive/c/Python27

PATH=$PYTHON_PATH:$PATH

meas=`findmeas comparison_all_sensors_2012-07-03_11-31-25.MF4`
out=`echo $meas|sed -r 's,(.+)\.MF4,\1.h5,'`
python -m parsemf4 -fhdf5 -czlib -l1 $meas
python test/testParseMdf.py $meas $out 2> /dev/null

meas=MQB_MRR_2012-06-21_10-17_0004.MF4
rm -r `cygpath -ua $MEASBACKUP`/$meas
meas=`findmeas $meas`
python test/test_SignalGroupTimemonGap_334.py -m $meas -u $MEASBACKUP
python test/test_selectTimeScaleOmit_334.py   -m $meas

meas=`findmeas comparison_all_sensors_2012-07-31_23-11-33.MF4`
python test/test_corrupt_cg_cycle_count_379.py -m $meas
python test/test_hdf5_build.py
python test/test_Hdf5Parser.py
python test/test_switchable_backup_parser.py
meas=`findmeas comparison_all_sensors_2012-08-21_16-46-26.MF4`
python test/test_signalgroup_error.py -m $meas -u $MEASBACKUP
meas=`findmeas comparison_all_sensors_2012-10-10_13-47-25.MF4`
python test/test_mf4.py -m $meas
python test/test_mf4_parse_error.py -m $meas
python test/test_signalproc.py
python test/test_unicode_xml_parsing.py

for meas in MAN_AEBS_ACC_2012-11-06_14-07-46.MF4\
            MAN_AEBS_ACC_2012-11-14_16-15-12.MF4\
            H566_2014-02-27_17-39-29.mf4; do
  export TEST_MEAS=`findmeas $meas`
  python test/test_mf4_umlaut_comment.py
done

python test/test_selectTimeScale.py
python test/test_SignalSource_selectScaleTime.py
python test/test_calcXBurstTimeScale.py

measbase=CVR3_B1_2011-02-10_16-53_020.mdf
meas=`findmeas $measbase`
out=`echo meas|sed -r ',(.+)\.mdf,\1.mod.mdf,'`

rm -r `cygpath -ua $MEASBACKUP`/$measbase
python test/testSignalGroup.py -m $meas -u $MEASBACKUP

python src/measparser/MdfParser.py -m $meas -o $out

rm -r `cygpath -ua $MEASBACKUP`/$measbase
python src/measparser/SignalSource.py -m $meas -u $MEASBACKUP

python test/signalgroup/test_select_allvalid_sgs.py
python test/signalgroup/SignalGroup.py
python test/signalgroup/SignalGroupList.py

meas=`findmeas 2013-07-08-07-28-20.MF4`
python test/Mf4Parser/conversion_rule.py -m $meas
python test/Mf4Parser/change_conversion.py

python test/BackupParser/version_check.py

python test/iParser/getStartDate.py
python test/iParser/commonInterfaces.py
python test/MdfParser/getStartDate.py -m `findmeas VTC6200_022_2013-07-22_09-40-08.MDF`
python test/Mf4Parser/getStartDate.py -m `findmeas H566_2013-03-28_10-29-02.mf4`
python test/MdfParser/change_conversion.py

python test/namedump/main.py
python test/testNamedumpOnOff.py

python test/SignalSource/change_conversion.py



