import sys

from config.Config import init_dataeval

config, manager, modules = init_dataeval(sys.argv[1:])
