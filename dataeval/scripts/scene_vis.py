import os
import subprocess

exe_path = os.path.dirname(__file__)
os.chdir(exe_path)

command = os.path.join(exe_path, "scenario_visualization/scenario_visualization.exe")

p = subprocess.Popen(command)

stdout, stderr = p.communicate()
return_code = p.returncode

