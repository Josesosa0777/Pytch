REM Run Test Batch



echo kbtools - Test Batch Start > results.txt
echo >> results.txt

echo ======================================================= >> results.txt
echo call _clean.bat >> results.txt
call _clean.bat >> results.txt
echo _clean.bat ready >> results.txt

echo ======================================================= >> results.txt
echo tests for excel_io >> results.txt
cd excel_io
python test_excel_io.py 2>> ..\results.txt  1> test_excel_io.txt
cd..

echo ======================================================= >> results.txt
echo tests for hysteresis >> results.txt
cd hysteresis
python test_hysteresis.py 2>> ..\results.txt  1> test_hysteresis.txt
cd..

echo ======================================================= >> results.txt
echo tests for svf >> results.txt
cd svf
python test_svf.py 2>> ..\results.txt  1> test_svf.txt
cd..


echo ======================================================= >> results.txt
echo tests for dcnvt3 >> results.txt
cd dcnvt3
python test_dcnvt3.py 2>> ..\results.txt  1> test_dcnvt3.txt
cd..

echo ======================================================= >> results.txt
echo tests for getIntervalAroundEvent >> results.txt
cd getIntervalAroundEvent
python test_getIntervalAroundEvent.py 2>> ..\results.txt  1> test_getIntervalAroundEvent.txt
cd..

echo ======================================================= >> results.txt
echo tests for smooth_filter >> results.txt
cd smooth_filter
python test_smooth_filter.py 2>> ..\results.txt  1> test_smooth_filter.txt
cd..

echo ======================================================= >> results.txt
echo tests for MultiState >> results.txt
cd MultiState
python test_MultiState.py 2>> ..\results.txt  1> test_MultiState.txt
cd..

echo ======================================================= >> results.txt
echo tests for extract_values >> results.txt
cd extract_values
python test_extract_values.py 2>> ..\results.txt  1> test_extract_values.txt
cd..

echo ======================================================= >> results.txt
echo tests for kb_io >> results.txt
cd kb_io
python test_kb_io.py 2>> ..\results.txt  1> test_kb_io.txt
cd..


echo ======================================================= >> results.txt
echo tests for ugdiff >> results.txt
cd ugdiff
python test_ugdiff.py 2>> ..\results.txt  1> test_ugdiff.txt
cd..


echo ======================================================= >> results.txt
echo tests for resample >> results.txt
cd resample
python test_resample.py 2>> ..\results.txt  1> test_resample.txt
cd..


echo ======================================================= >> results.txt
echo tests for timer >> results.txt
cd timer
python test_timer.py 2>> ..\results.txt  1> test_timer.txt
cd..

echo ======================================================= >> results.txt
echo tests for IsActiveInInterval >> results.txt
cd IsActiveInInterval
python test_IsActiveInInterval.py 2>> ..\results.txt  1> test_IsActiveInInterval.txt
cd..


echo ======================================================= >> results.txt
echo tests for GetTRisingEdge >> results.txt
cd GetTRisingEdge
python test_GetTRisingEdge.py 2>> ..\results.txt  1> test_GetTRisingEdge.txt
cd..

echo ======================================================= >> results.txt
echo tests for LPF_butter >> results.txt
cd LPF_butter
python test_LPF_butter.py 2>> ..\results.txt  1> test_LPF_butter.txt
cd..


rem echo ======================================================= >> results.txt
rem echo tests for pt1_filter >> results.txt
rem cd pt1_filter
rem python test_pt1_filter.py 2>> ..\results.txt  1> test_pt1_filter.txt
rem cd..



echo ======================================================= >> results.txt
echo tests for cnvt_GPS >> results.txt
cd cnvt_GPS
python test_cnvt_GPS.py 2>> ..\results.txt  1> test_cnvt_GPS.txt
cd..


echo ======================================================= >> results.txt
echo tests for scan4handles >> results.txt
cd scan4handles
python test_scan4handles.py 2>> ..\results.txt  1> test_scan4handles.txt
cd..

echo ======================================================= >> results.txt
echo tests for hunt4event >> results.txt
cd hunt4event
python test_hunt4event.py 2>> ..\results.txt 1> test_hunt4event.txt
cd..


echo ======================================================= >> results.txt
echo tests for read_input_file >> results.txt
cd read_input_file
python test_read_input_file.py 2>> ..\results.txt 1> test_read_input_file.txt
cd..

echo ======================================================= >> results.txt
echo tests for kb_tex >> results.txt
cd kb_tex
python test_kb_tex.py 2>> ..\results.txt 1> test_kb_tex.txt
cd..


echo ======================================================= >> results.txt
echo tests for DAS_eval >> results.txt
cd DAS_eval
python test_DAS_eval.py 2>> ..\results.txt 1> test_DAS_eval.txt
cd..

echo ======================================================= >> results.txt
echo tests for BatchServer >> results.txt
cd BatchServer
python test_BatchServer.py 2>> ..\results.txt 1> test_BatchServer.txt
cd..

echo ======================================================= >> results.txt
echo tests for ProcTestResults >> results.txt
cd ProcTestResults
python test_ProcTestResults.py 2>> ..\results.txt 1> test_ProcTestResults.txt
cd..




echo ======================================================= >> results.txt
echo Test Batch finished >> results.txt


python run_ProcTestResults.py

pause