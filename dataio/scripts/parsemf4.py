#!/usr/bin/env python
"""
python -m parsemf4 [option...] measurementfile

*options*

-f  format:        hdf5
                   if it is not selected no file will be created
                   if no -o option is added the ouput file name is generated
                   based on format
                     hdf5 : .h5

-c  compression:   lzo, zlib (default), bzip2, blosc
                   hdf5 channel compression

-l  comp-level:    0-9
                   compression level 0 (default) means no compression

-o  file-name:     output file name

-r  con-cycle:     int, defualt=-1 means no extra concatenation
                   concatenate the values in case of datablock list after
                   con-cycle

-v  verboselevel:  0,1,2
"""


import sys
import os
import getopt

import numpy

from measparser import mdf, mf4, Mf4Parser, Hdf5Parser, NameDump


if '-h' in sys.argv:
  print __doc__
  exit(0)

exts = {None:   '.foo',
        'hdf5': '.h5'}

union_type = '<u1'

opts, args = getopt.getopt(sys.argv[1:], 'hf:c:v:l:r:')
optdict = dict(opts)
status = 0

verbose   = optdict.get('-v', 0)
conv      = optdict.get('-f')
comp      = optdict.get('-c', 'zlib')
complevel = optdict.get('-l', 0)
complevel = int(complevel)
flush_lim = optdict.get('-r', -1)
flush_lim = int(flush_lim)

if args:
  filename = args[0]
else:
  sys.stderr.write('No filename was given\n')
  exit(1)

if '-o' in optdict:
  convname = optdict['-o']
else:
  _name, _ext = os.path.splitext(filename)
  convname = _name + exts.get(conv, '.foo')
  namedumpname = _name + '.db'

if not Mf4Parser.checkParser(filename):
  sys.stderr.write('%s is not an mdf 4 file!\n' %filename)
  sys.stderr.flush()
  status = 1
elif not mf4.isMdfSorted(filename):
  sys.stderr.write('%s is unsorted!\n' %filename)
  sys.stderr.flush()
  status = 2

if status:
  exit(status)

if conv == 'hdf5':
  comp = Hdf5Parser.getCompression(comp, complevel)
  h, devices, times = Hdf5Parser.init(convname)

f = open(filename, 'rb')
sis = Mf4Parser.sis_def.copy()
ccs = Mf4Parser.ccs_def.copy()

dg_link,\
hd_fh_first,\
hd_ch_first,\
hd_at_first,\
hd_ev_first,\
hd_md_comment,\
hd_start_time_ns,\
hd_tz_offset_min,\
hd_dst_offset_min,\
hd_time_flags,\
hd_time_class,\
hd_flags,\
hs_start_angle_rad,\
hd_start_distance_m = mf4.extractHD(f)

filecomment = mf4.extractTX(f, hd_md_comment)
filecomment = mf4.parseFileComment(filecomment)
filecomment = str(filecomment)

if conv == 'hdf5':
  Hdf5Parser.setHeader(h, hd_start_time_ns, filecomment)

dg_nr = 0
while dg_link:
  dg_link,\
  cg_link,\
  dg_data,\
  dg_md_comment,\
  dg_rec_id_size = mf4.extractDG(f, dg_link)

  timekey = str(dg_nr)
  while cg_link:
    cg_link,\
    cn_link,\
    cg_tx_acq_name,\
    cg_si_acq_source,\
    cg_sr_first,\
    cg_md_comment,\
    cg_record_id,\
    cg_cycle_count,\
    cg_flags,\
    cg_data_bytes,\
    cg_inval_bytes = mf4.extractCG(f, cg_link)

    acq_name = mf4.extractTX(f, cg_tx_acq_name)
    cg_acq_name,\
    cg_acq_path,\
    cg_acq_type = Mf4Parser.procSI(sis, f, cg_si_acq_source)

    signals = {}
    record = {}
    reserve = {}
    while cn_link:
      for cn in Mf4Parser.iterCnStruct(f, ccs, cn_link):
        if cn['cn_type'] == 2:
          cn_name = timekey
        else:
          cn_name = cn['cn_name']

        dtype,\
        byte_size,\
        dbyte_size,\
        byte_offset,\
        upshift,\
        downshift = mdf.calcReadAttrs(mf4.orders,
                                      mf4.formats,
                                      cn['cn_data_type'],
                                      cn['cn_bit_count'],
                                      cn['cn_bit_offset'],
                                      cn['cn_byte_offset'])
        cn_acq_name,\
        cn_acq_path,\
        cn_acq_type = Mf4Parser.procSI(sis, f, cn['cn_si_source'])

        dev_name,\
        dev_ext = mf4.createDevName(acq_name,
                                    cg_acq_name, cg_acq_path, cg_acq_type,
                                    cn_acq_name, cn_acq_path)

        byte_offsets = []
        signals[cn_name] = dict(ByteOffsets=byte_offsets,
                                CClink=cn['cn_cc_conversion'],
                                UpShift=upshift,
                                DownShift=downshift,
                                DType=dtype,
                                dev=(dev_name, dev_ext),
                                cn_composition=cn['cn_composition'],
                                unit=cn['unit'])

        if cn['cn_composition']:
          ca = mf4.extractCA(f, cn['cn_composition'])
          size = mdf.getTypeSize(dtype)
          ca_prod = mf4.calcCaDimProd(ca)
          byte_offsets.append(byte_offset)
          for i in xrange(ca_prod):
            offset = i*size
            mdf.calcRecord(record,
                           reserve,
                           signals,
                           [],
                           '%s-%d' %(cn_name, i),
                           byte_offset+offset,
                           byte_size,
                           dbyte_size,
                           dtype,
                           mf4.union_type)
        else:
          mdf.calcRecord(record,
                         reserve,
                         signals,
                         byte_offsets,
                         cn_name,
                         byte_offset,
                         byte_size,
                         dbyte_size,
                         dtype,
                         mf4.union_type)
        cn_link = cn['cn_link']
    if conv is not None and cg_cycle_count:
      mdf.patchRecord(record)
      dtypes = mdf.toDTypes(record)
      del record
      valuecon = []
      valueflush = []
      flush_cycle = 0
      for dt_data, dt_size in mf4.iterDT(f, dg_data):
        flush_cycle += 1
        dt_cycle_count = min(dt_size / cg_data_bytes, cg_cycle_count)
        values = mdf.getValues(f, dtypes, dt_data, dt_cycle_count)
        valuecon.append(values)
        if flush_cycle == flush_lim:
          flush_cycle = 0
          values = numpy.concatenate(valuecon)
          valuecon = []
          valueflush.append(values)
      del dtypes
      if flush_cycle > 0:
        values = numpy.concatenate(valuecon)
        valueflush.append(values)
        valuecon = valueflush
        del valueflush
      if len(valuecon) > 1:
        values = numpy.concatenate(valuecon)
      del valuecon
      for cn_name, signal in signals.iteritems():
        if signal['cn_composition']:
          ca = mf4.extractCA(f, signal['cn_composition'])
          size = mdf.getTypeSize(signal['DType'])
          ca_prod = mf4.calcCaDimProd(ca)
          value = numpy.zeros((cg_cycle_count, ca_prod), dtype=signal['DType'])
          for i in xrange(ca_prod):
            offset = i * size
            byte_offsets = [e + offset for e in signal['ByteOffsets']]
            value[:,i]= mdf.getValue(values,
                                     cg_cycle_count,
                                     byte_offsets,
                                     signal['DType'],
                                     signal['UpShift'],
                                     signal['DownShift'])
          shape = [cg_cycle_count]
          shape.extend(ca['ca_dim_size'])
          order = 'F' if ca['ca_flags'] & 64 else 'C'
          value = value.reshape(shape, order=order)
        else:
          value = mdf.getValue(values,
                               cg_cycle_count,
                               signal['ByteOffsets'],
                               signal['DType'],
                               signal['UpShift'],
                               signal['DownShift'])
        cn_cc_conversion = signal['CClink']
        cc = ccs[cn_cc_conversion]
        cc_type = cc['cc_type']
        cc_val = cc['cc_val']
        cc_ref = cc['cc_ref']
        if cc_type != 7:
          value = mf4.convRawPhy(value, cc_type, cc_val, cc_ref)
          comment = ''
        else:
          comment = Mf4Parser.str_cc7(f, ccs, cc_val, cc_ref)
        if conv == 'hdf5':
          dev_name, dev_ext = signal['dev']
          Hdf5Parser.addSignal(devices,
                               times,
                               dev_name,
                               dev_ext,
                               cn_name,
                               timekey,
                               value,
                               comp,
                               signal['unit'],
                               comment)
      del values
  dg_nr += 1

f.close()
if conv == 'hdf5':
  h.close()
  namedump = NameDump.fromMeasurement(filename, DbName=namedumpname)
  namedump.close()
exit(status)
