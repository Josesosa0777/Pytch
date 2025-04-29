# -*- dataeval: init -*-

import os
import sys
import subprocess
from datetime import datetime

from scipy.io import loadmat

from measparser.signalgroup import SignalGroupError
import calc_flr20_aebs_phases

SIM_DIR = r"C:\Users\str-clarax\aebs_c_1-15\test\data"

class Calc(calc_flr20_aebs_phases.Calc):
  def check(self):
    assert os.path.isdir(SIM_DIR), "No AEBS_C sandbox found (required: %s)" % SIM_DIR
    mat = simulate(self.source.FileName)
    time = mat['t'][0]
    status = mat['AEBS1_SystemState'][0]
    level = mat['AEBS1_WarningLevel'][0]
    return time, status, level

def simulate(measfullname):
  simoutfullname = ""
  try:
    simoutfullname = run_simulation(measfullname)
    mat = get_results(simoutfullname)
  finally:
    if os.path.isfile(simoutfullname):
      os.remove(simoutfullname)  # TODO: for all generated files
  return mat

def run_simulation(measfullname):
  xlim = None
  gate = None
  Description = ""
  SimOutput_as_ExpectedResult = False
  
  # find unique file name for simulation output
  cnt = 0
  while True:
    VariationName = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_%d" % cnt
    simoutfullname = os.path.join(
      SIM_DIR, "TD_aebs_01_var_%s_output.mat" % VariationName)
    if not os.path.isfile(simoutfullname):
      break
    cnt += 1
  
  cwd = os.getcwd()
  try:
    # prepare simulation (generate MATs: _input, _expected_results, _parameters)
    os.chdir(SIM_DIR)
    sys.path.insert(0, SIM_DIR)  # to find gen_test_data
    import gen_test_data
    with open("tc_aebs_01.txt", "w") as Handle_ContentsFile:
      gen_test_data.one_measurement(Handle_ContentsFile, measfullname,
        VariationName, xlim, gate, Description, SimOutput_as_ExpectedResult)
    
    # run simulation (generate MAT: _output)
    os.chdir(r"..\release")
    subprocess.call("CUnit_main.exe")
  except:
    import traceback
    traceback.print_exc()
    if os.path.isfile(simoutfullname):
      os.remove(simoutfullname)  # TODO: for all generated files
    raise SignalGroupError("Error while running gen_test_data")
  finally:
    if sys.path[0] == SIM_DIR:
      sys.path.pop(0)
    os.chdir(cwd)
  return simoutfullname

def get_results(simoutfullname):
  try:
    mat = loadmat(simoutfullname)
  except:
    raise SignalGroupError("MAT file cannot be loaded (%s)" % simoutfullname)
  return mat
