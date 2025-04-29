"""
Simple way to execute multiple process in parallel (Python recipe)
http://code.activestate.com/recipes/577376-simple-way-to-execute-multiple-process-in-parallel
"""

import sys, os, time
from subprocess import Popen, list2cmdline

def cpu_count():
    ''' Returns the number of CPUs in the system
    '''
    num = 1
    if sys.platform == 'win32':
        try:
            num = int(os.environ['NUMBER_OF_PROCESSORS'])
        except (ValueError, KeyError):
            pass
    elif sys.platform == 'darwin':
        try:
            num = int(os.popen('sysctl -n hw.ncpu').read())
        except ValueError:
            pass
    else:
        try:
            num = os.sysconf('SC_NPROCESSORS_ONLN')
        except (ValueError, OSError, AttributeError):
            pass

    return num

def exec_commands(cmds, sleep=0.05, max_task=None, exit_on_fail=False):
    ''' Exec commands in parallel in multiple process 
    (as much as we have CPU)
    '''
    if not cmds: return # empty list

    def done(p):
        return p.poll() is not None
    def success(p):
        return p.returncode == 0

    max_task = max_task or cpu_count()
    processes = []
    while True:
        while cmds and len(processes) < max_task:
            task = cmds.pop()
            print list2cmdline(task)
            processes.append(Popen(task))

        for p in processes:
            if done(p):
                if success(p) or not exit_on_fail:
                    processes.remove(p)
                else:
                    sys.exit(p.returncode)

        if not processes and not cmds:
            break
        else:
            time.sleep(sleep)


if __name__ == '__main__':
    commands = [
        ['ping', 'www.reddit.com'],
        ['ping', 'en.wikipedia.org'],
        ['ping', 'www.google.com'],
        ['ping', 'www.yahoo.com'],
        ['ping', 'news.ycombinator.com']
    ]
    exec_commands(commands, max_task=4)
