import subprocess

def executeCmd(cmdLine):
    process = subprocess.Popen(cmdLine, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result  = process.communicate()
    return str(result[0]+result[1])
