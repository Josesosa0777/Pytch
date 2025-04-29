REM run only interface tests with other libraries 
REM output of python unittest script are piped into files
REM   stdout 1>>  local text files e.g. test_SignalSource.txt
REM   stderr 2>>  gobal text file: results_interface_tests_only


REM create head of global 
echo Interface Test Only Start > results_interface_tests_only.txt
echo >> results_interface_tests_only.txt


echo ======================================================= >> results_interface_tests_only.txt
echo tests for lib_dataio\measparser\SignalSource >> results_interface_tests_only.txt
cd interface_lib_dataio
cd measparser
cd SignalSource
python test_SignalSource.py 2>> ..\..\..\results_interface_tests_only.txt 1> test_SignalSource.txt
cd..
cd..
cd..




echo ======================================================= >> results_interface_tests_only.txt
echo Interface Test Only finished >> results_interface_tests_only.txt

REM process test results using a python script
python run_ProcTestResults_interface_tests_only.py

