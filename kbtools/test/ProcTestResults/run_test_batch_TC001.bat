REM Run Test Batch


echo Test Batch Start > results.txt
echo > results.txt


echo ======================================================= >> results.txt
echo tests for testsuite1 >> results.txt
cd testsuite1
python test_testsuite1.py 2>> ..\results.txt
cd..

echo ======================================================= >> results.txt
echo tests for testsuite2 >> results.txt
cd testsuite2
python test_testsuite2.py 2>> ..\results.txt
cd..


echo ======================================================= >> results.txt
echo Test Batch finished >> results.txt


python run_ProcTestResults.py