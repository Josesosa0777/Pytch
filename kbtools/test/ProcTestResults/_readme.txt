Testsuite for ProcTestResults
=============================

ProcTestResults : Processing of Test Results

The testsuite for ProcTestResults is implemented in test_ProcTestResults.py.
Currently it contains two testcases:
  Testcase 1 (TC001)
   This testcase run \testsuite1 and \testsuite2 which only include testcases that will pass
   The Excel Table shall report that all testcases have passed.
  Testcase 2 (TC002)
   This testcase run also \testsuite3 which include some testcases that will fail
   The Excel Table shall report the number of passed and failed testcases.


Currently there are 3 testsuites
   \testsuite1 and \testsuite2 only include testcases that will pass
   \testsuite3 includes some testcases that fill fail by intention.

The MS-DOS batch file run_test_batch_TC001.bat and run_test_batch_TC002.bat run the unittests of testcase 1 
and testcase 2 respectively. 

The python script run_ProcTestResults.py is called to post process the results and create the Excel table.

The files created during the tests are stored in the folder \results separately for each testcase.