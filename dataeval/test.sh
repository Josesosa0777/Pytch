#!/usr/bin/bash

PYTHON_PATH=/cygdrive/c/Python27

PATH=$PYTHON_PATH:$PATH
export testmeas=`findmeas CVR3_B1_2011-02-10_16-53_020.mdf`

python test/testCreateStatistic.py -m c:/KBData/measurement/test/CVR3_B1_2011-02-10_16-53_020.mdf\
                                   -u c:/KBData/measurement/test/backup\
                                   -d c:/KBData/measurement/test\
                                   -c c:/KBData/measurement/test/E_CreateStatistic.npy
python test/test_batchsqlite.py
python test/test_batchsqlite_entries.py
python test/test_batchsqlite_report2.py
python test/test_batchsqlite_quantity.py
python test/test_report.py
python test/test_report2.py
python test/test_IntervalList.py
python test/test_batchsqlite_merge.py
python test/test_batch_xml2sqlite.py $verbose
python test/test_batchsqlite_versioncheck.py
python test/interface/grouptypes/main.py
python test/interface/Intrfaces/channels.py
python test/interface/manager/params.py
python test/interface/manager/clone.py
python test/interface/manager/close.py
python test/interface/manager/build.py
python test/interface/module/main.py
python test/interface/module/without_param.py
python test/interface/modules/main.py
python test/interface/modules/calc.py
python test/interface/modules/get_name.py
python test/interface/scan/scanInterfaceModule.py
python test/config/Config/scan.py
python test/config/Config/load_namespace.py
python test/config/Config/tempparam.py
python test/config/Config/scan_multiple_channels.py
python test/config/Config/unselected_parameter.py
python test/config/Config/file_check.py
python test/config/Config/load.py
python test/config/Search/arg_parse.py
python test/config/modules/scan.py
python test/config/parameter/build.py
python test/config/parameter/filter.py
python test/config/parameter/test_copy.py
python test/config/logger/no_file_logger.py
python test/config/logger/file_logger.py
python test/dmw/ViewText/main.py
python test/measproc/quantity/main.py
python test/measproc/quantity/separate_intervallist.py
python test/measproc/batchsqlite/replace_measurement.py
python test/measproc/batchsqlite/interval_queries.py
python test/measproc/batchsqlite/label_interval.py
python test/measproc/batchsqlite/unlabel_interval.py
python test/measproc/batchsqlite/label_exclusive_group.py
python test/measproc/batchsqlite/get_table.py
python test/measproc/batchsqlite/tablequery.py
python test/measproc/batchsqlite/set_qua_interval.py
batch=`findmeas batch.db`
repdir=`dirname $batch`/files
python test/measproc/batchsqlite/update.py -b $batch --repdir $repdir
python test/measproc/batchsqlite/create_view_from_last_start.py
export testmeas=c:/KBData/measurement/test/merge_crash_sample_time.npy
python test/measproc/IntervalList/index_out_of_bound.py
python test/measproc/IntervalList/findlongestintervals.py
python test/measproc/IntervalList/rescale.py
python -m doctest src/measproc/IntervalList.py
python test/measproc/IntervalList/findIntervalIdsWithin.py
python test/measproc/report2/rescale.py
python test/measproc/MapTileCalculation/coord_calc.py
python test/measproc/MapTileCalculation/pixel_calc.py
python test/measproc/MapTileCalculation/tile_calc.py
python test/measproc/mapbbox/mapbbox_handling.py
python test/measproc/mapmanager/map_manager_tester.py --maperitive 'C:\Maperitive\Maperitive.exe'

python src/datavis/ListNavigator.py
python src/datavis/OpenGLutil.py
python src/datavis/PlotNavigator.py
python src/datavis/Synchronizer.py
python src/datavis/TrackNavigator.py
python src/datavis/VideoNavigator.py -v c:/KBData/measurement/test/CVR3_B1_2011-02-10_16-53_020.avi
python src/measproc/EventFinder.py -m c:/KBData/measurement/test/CVR3_B1_2011-02-10_16-53_020.mdf\
                                   -u c:/KBData/measurement/test/backup
python src/measproc/IntervalList.py
python src/measproc/batchsqlite.py
python test/datavis/Synchronizer/test_navigator_function.py
python test/datavis/Synchronizer/test_navigators.py
python test/datavis/Synchronizer/test_window_id.py
python test/datavis/PlotNavigator/test_plot_navigator.py
python test/datavis/PlotNavigator/test_plot_navigator_subplot.py
python test/datavis/Synchronizer/test_cnavigator.py
python test/datavis/GroupNavigator/test_group_navigator.py
python test/datavis/ListNavigator/test_list_navigator.py
python test/datavis/StatisticNavigator/test_statistic_navigator.py
python test/datavis/TrackNavigator/test_track_navigator.py
python test/datavis/ReportNavigator/test_report_navigator.py
python test/datavis/Report2Navigator/test_report2_navigator.py
python test/datavis/VideoNavigator/test_video_navigator.py
python test/datavis/BatchFrame/test_batch_frame.py
python test/datavis/MatplotlibNavigator/test_matplotlib_navigator.py
python test/datavis/ConcurrenceNavigator/test_concurrence_navigator.py
python test/datavis/SituationNavigator/test_situation_navigator.py
python test/datavis/BatchNavigator/test_batch_navigator.py
python test/datavis/MapNavigator/test_map_navigator.py --mapdb '\\file\Messdat\DAS\Evaluation\Map_Database\meas_map.mapdb'
python test/datavis/MapNavigator/test_static_map_navigator.py --mapdb '\\file\Messdat\DAS\Evaluation\Map_Database\meas_map.mapdb'
python test/datavis/backend_map/test_degree_formatter.py
python test/datavis/backend_map/test_navigation_tools.py --mapdb '\\file\Messdat\DAS\Evaluation\Map_Database\meas_map.mapdb'

python test/datalab/story/main.py

python test/primitives/aebs/merge.py
python -m doctest src/primitives/aebs.py

