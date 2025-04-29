REM Run Test Batch


echo kbtoolsuser - Test Batch Start > results.txt
echo >> results.txt

echo call _clean.bat >> results.txt
call _clean.bat >> results.txt
echo _clean.bat ready >> results.txt

echo ======================================================= >> results.txt
echo tests for ProcFLC20 >> results.txt
cd ProcFLC20
python test_ProcFLC20.py 2>> ..\results.txt  1> test_ProcFLC20.txt
cd..


echo ======================================================= >> results.txt
echo tests for CalcAEBS >> results.txt
cd CalcAEBS
rem python -m unittest test_CalcAEBS.cTestCalcAEBS.test_TC003_cpr_CalcaAvoidance_SingleStep 2>> ..\results.txt  1> test_CalcAEBS.txt
rem python -m unittest test_CalcAEBS.cTestCalcAEBS.test_TC025_CalcPredictedObjectMotion 2>> ..\results.txt  1> test_CalcAEBS.txt
rem python -m unittest test_CalcAEBS.cTestCalcAEBS.test_TC026_cpr_CalcaAvoidancePredictedCascade_SingleStep 2>> ..\results.txt  1> test_CalcAEBS.txt
rem python -m unittest test_CalcAEBS.cTestCalcAEBS.test_TC027_cpr_CalcaAvoidancePredictedCascade 2>> ..\results.txt  1> test_CalcAEBS.txt
python test_CalcAEBS.py 2>> ..\results.txt  1> test_CalcAEBS.txt
cd..





echo ======================================================= >> results.txt
echo Test Batch finished >> results.txt


python run_ProcTestResults.py

