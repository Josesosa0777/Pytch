#!/usr/bin/python
"""
python purge_mf4.py options

  *options*

    [h]    print help and exit
    [t]    test the output file
    i      input measurement file
    o      output measurement file
    purge  purge the signals of `signal-file` from `input-file`
    keep   keep the signals of `signal-file` from `input-file`

  keep and purge options cannot be selected together.
  The single letter options start with one -.
  The multiple letter options start with double -.
"""

import getopt
import sys
import shutil

from measparser.Mf4Parser import cMf4Parser
from measparser import mf4

def correctLink(struct, rm, check, check_max, link, link_pos):
  while check in rm:
    link = mf4.extract(struct, f, link)[link_pos]
    check += 1
  else:
    check -= 1
  if check in rm and check == check_max:
    link = 0
  return link

def writeLink(struct, block, f, act, link, link_pos):
  block = list(block)
  block[link_pos] = link
  mf4.write(struct, f, act, block)
  return

empty_si = mf4.si_struct.pack('\x00\x00\x00\x00', 
                              '\x00\x00\x00\x00',
                              0, 0, 0, 0, 0,
                              0, 0, 0)

empty_dg = mf4.dg_struct.pack('\x00\x00\x00\x00', 
                              '\x00\x00\x00\x00', 
                              0, 0, 0, 0, 0, 
                              0, 0, 
                              '\x00\x00\x00\x00\x00\x00\x00')

empty_cg = mf4.cg_struct.pack('\x00\x00\x00\x00', 
                              '\x00\x00\x00\x00',
                              0, 0, 0, 0, 0,
                              0, 0, 0, 0, 0,
                              0,
                              '\x00\x00\x00\x00\x00\x00',
                              0, 0)

empty_cn = mf4.cn_struct.pack('\x00\x00\x00\x00', 
                              '\x00\x00\x00\x00',
                              0, 0, 0, 0, 0,
                              0, 0, 0, 0, 0,
                              0, 0, 0, 0, 0,
                              0, 0, 0, 0,
                              '\x00\x00\x00',
                              0, 0, 0, 0, 0,
                              0)

empty_cc = mf4.struct_head.pack('\x00\x00\x00\x00', 
                                '\x00\x00\x00\x00',
                                0, 0)


opts, args = getopt.getopt(sys.argv[1:], 'i:o:ht', ['purge=', 'keep='])
optdict = dict(opts)
status = 0

if '-h' in optdict:
  sys.stdout.write(__doc__)
  sys.stdout.flush()
  exit()

shutil.copyfile(optdict['-i'], optdict['-o'])

p = cMf4Parser(optdict['-i'])


if '--keep' in optdict:
  f = open(optdict['--keep'])
  keeps = {}
  signals = []
  for line in f:
    devname, signame = line.split()
    dev = keeps.setdefault(devname, [])
    dev.append(signame)
  f.close()
  for devname in p.iterDeviceNames():
    purgedev = devname not in keeps
    for signame in p.iterSignalNames(devname):
      if purgedev or signame not in keeps[devname]:
        signals.append((devname, signame))
elif '--purge' in optdict:
  f = open(optdict['--purge'])
  signals = [tuple(line.split()) for line in f]
  f.close()
else:
  sys.stderr.write('No signal-file is added!\n')
  sys.stderr.flush()
  p.close()
  exit(1)

rm_cns = {}

for devname, signame in signals:
  dg_nr, cg_nr, cn_nr = p.getNrs(devname, signame)
  rm_cns.setdefault(dg_nr, {}).setdefault(cg_nr, set()).add(cn_nr)

rm_dg = set()
rm_cgs = {}
for dg_nr, cgs in rm_cns.iteritems():
  rm_dg_cg = rm_cgs.setdefault(dg_nr, set())
  for cg_nr, cns in cgs.iteritems():
    allcn = set(xrange(len(p.cns[dg_nr][cg_nr])))
    remain = allcn.difference(cns)
    if not remain:
      rm_dg_cg.add(cg_nr)
    elif len(remain) == 1:
      cn_nr = remain.pop()
      if p.cns[dg_nr][cg_nr][cn_nr]['cn_type'] == 2:
        cns.add(cn_nr)
        rm_dg_cg.add(cg_nr)
  if rm_dg_cg == set(xrange(len(p.cgs[dg_nr]))):
    rm_dg.add(dg_nr)

dg_max = len(p.dgs)-1
cg_maxes = [len(cgs)-1 for cgs in p.cgs]
cn_maxes = [[len(cns)-1 for cns in cg_cns] for cg_cns in p.cns]

p.close()

f = open(optdict['-o'], 'r+b')
hd = mf4.extract(mf4.hd_struct, f, 64)
dg_next = hd[4]

dg_nr = 0
dg_dg_next = correctLink(mf4.dg_struct, rm_dg, dg_nr, dg_max, dg_next, 4)
if dg_dg_next != dg_next:
  writeLink(mf4.hd_struct, hd, f, 64, dg_dg_next, 4)

rm_ccs = set()
rm_sis = set()
rm_txs = set()

save_ccs = set()
save_txs = set()
save_sis = set()

while dg_next:
  dg = mf4.extract(mf4.dg_struct, f, dg_next)
  dg_act = dg_next
  dg_next = dg[4]
  cg_next = dg[5]

  dg_dg_next = correctLink(mf4.dg_struct, rm_dg, dg_nr+1, dg_max, dg_next, 4)
  if dg_dg_next != dg_next:
    writeLink(mf4.dg_struct, dg, f, dg_act, dg_dg_next, 4)

  if dg_nr in rm_dg and dg_act != 0:
    mf4.clean(f, dg_act, empty_dg)
  
  cg_nr = 0
  cg_max = cg_maxes[dg_nr]
  rm_cg = rm_cgs.get(dg_nr, set())
  while cg_next:
    cg = mf4.extract(mf4.cg_struct, f, cg_next)
    cg_act = cg_next
    cg_next = cg[4]
    cn_next = cg[5]
    cg_tx_acq_name = cg[6]
    cg_si_acq_source = cg[7]

    cn_nr = 0
    cn_max = cn_maxes[dg_nr][cg_nr]
    rm_cn = rm_cns.get(dg_nr, {}).get(cg_nr, set())

    cg_cg_next = correctLink(mf4.cg_struct, rm_cg, cg_nr+1, cg_max, cg_next, 4)
    if cg_cg_next != cg_next:
      writeLink(mf4.cg_struct, cg, f, cg_act, cg_cg_next, 4)

    if cg_nr in rm_cg and cg_act != 0:
      mf4.clean(f, cg_act, empty_cg)
      rm_sis.add(cg_si_acq_source)
      rm_txs.add(cg_tx_acq_name)
    else:
      cg_cn_next = correctLink(mf4.cn_struct, rm_cn, cn_nr, cn_max, cn_next, 4)
      if cg_cn_next != cn_next:
        writeLink(mf4.cg_struct, cg, f, cg_act, cg_cn_next, 5)
      save_sis.add(cg_si_acq_source)
      save_txs.add(cg_tx_acq_name)

    while cn_next:
      cn = mf4.extract(mf4.cn_struct, f, cn_next)
      cn_act = cn_next
      cn_next = cn[4]
      cn_tx_name = cn[6]
      cn_si_source = cn[7]
      cn_cc_conversion = cn[8]

      cn_cn_next = correctLink(mf4.cn_struct, rm_cn, cn_nr+1, cn_max, cn_next, 4)
      if cn_cn_next != cn_next:
        writeLink(mf4.cn_struct, cn, f, cn_act, cn_cn_next, 4)

      if cn_nr in rm_cn and cn_act != 0:
        mf4.clean(f, cn_act, empty_cn)
        rm_sis.add(cn_si_source)
        rm_txs.add(cn_tx_name)
        rm_ccs.add(cn_cc_conversion)
      else:
        save_sis.add(cn_si_source)
        save_txs.add(cn_tx_name)
        save_ccs.add(cn_cc_conversion)

      cn_nr += 1
    cg_nr += 1
  dg_nr += 1

0 in rm_sis and rm_sis.remove(0)
0 in rm_ccs and rm_ccs.remove(0)
0 in rm_txs and rm_txs.remove(0)

rm_ccs.difference_update(save_ccs)
rm_sis.difference_update(save_sis)
rm_txs.difference_update(save_txs)

for si in rm_sis:
  mf4.clean(f, si, empty_si)

for cc in rm_ccs:
  mf4.clean(f, cc, empty_cc)

for tx in rm_txs:
  mf4.clearTX(f, tx)
f.close()

if '-t' in optdict:
  remained = []
  namemax = 0
  p = cMf4Parser(optdict['-o'])
  for devname, signame in signals:
    if p.contains(devname, signame):
      namemax = max(namemax, len(devname))
      remained.append((devname, signame))
  if remained:
    status = 1
    pattern = '%-' + str(namemax) + 's %s\n'
    sys.stdout.write('[Remained signal names]\n')
    for devname, signame in remained:
      sys.stdout.write(pattern %(devname, signame))
    sys.stdout.flush()

  missed = []
  namemax = 0
  i = cMf4Parser(optdict['-i'])
  for devname in i.iterDeviceNames():
    for signame in i.iterSignalNames(devname):
      if    (devname, signame) not in signals\
        and not p.contains(devname, signame):
        missed.append((devname, signame))
        namemax = max(namemax, len(devname))
  if missed:
    status = 1
    pattern = '%-' + str(namemax) + 's %s\n'
    sys.stdout.write('[Missed signal names]\n')
    for devname, signame in missed:
      sys.stdout.write(pattern %(devname, signame))
    sys.stdout.flush()
  i.close()
  
  p.close()
exit(status)
