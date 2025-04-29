# -*- coding: utf-8 -*-

import sys
import getopt
import re

from measparser.Mf4Parser import proc_answer, cMf4Parser 
from measparser.SignalSource import findParser
from measparser.iParser import iParser, CommandError, Quit


opts, args = getopt.getopt(sys.argv[1:], 'hic:p:s:t:')
optdict = dict(opts)
status = 0

prompt = optdict.get('-p', '\n>>> ')
sep = optdict.get('-s', '\n')
tab = optdict.get('-t')  

if '-h' in sys.argv:
  gen_cmd = iParser.cmd_h()
  gen_cmd_dict = dict(gen_cmd)
  mf4_cmd = [(cmd, doc) 
             for cmd, doc in cMf4Parser.cmd_h() 
             if cmd not in gen_cmd_dict]

  sys.stdout.write('python -m measparser [options] measurement-file\n\n'
                   '*options*\n\n'
                   '  -h print help\n'
                   '  -c command to execute\n'
                   '  -i switch to interactive mode\n'
                   '  -p prompt alternate\n'
                   '  -s answer line separator\n'
                   '  -t answer line inner tab\n\n'
                   '*general commands*\n\n'
                   '%s\n'
                   '*mdf 4 specific commands*\n\n'
                   '%s' %(proc_answer(gen_cmd, tab, sep), proc_answer(mf4_cmd, tab, sep)))
  sys.stdout.flush()
  exit(status)


measurement = args.pop(0)
Parser = findParser(measurement)
parser = Parser(measurement)

if '-c' in optdict:
  knowledge = []
  for line in optdict['-c'].split(';'):
    try:
      answer = parser.communicate(line)
    except CommandError:
      sys.stderr.write('Invalid command: %s\n' %line)
      sys.stderr.flush()
      status = 1
    else:
      knowledge.extend(answer)
  knowledge = proc_answer(knowledge, tab, sep)
  sys.stdout.write(knowledge.encode('utf-8'))
  sys.stdout.flush()


if '-i' in optdict:
  sys.stdout.write(prompt)
  sys.stdout.flush()
else:
  exit()

line = 'foo'
while line:
  line = sys.stdin.readline()
  try:
    answer = parser.communicate(line)
  except CommandError, error:
    sys.stderr.write(error.message)
    sys.stderr.flush()
    status = 1
  except Quit:
    break
  else:
    answer = proc_answer(answer, tab, sep)
    sys.stdout.write(answer.encode('utf-8'))
  sys.stdout.write(prompt)
  sys.stdout.flush()

parser.close()
exit(status)
