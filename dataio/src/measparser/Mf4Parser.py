import os
import sys
import mmap
import fnmatch
import datetime

import numpy

import mdf
import mf4
import iParser
import MdfParser
import subprocess
import numpy as np


class ChannelTypeError(BaseException):
  pass

def checkParser(FileName):
  """
  True if the `FileName` is a mdf 4 measurement.

  :Parameters:
    FileName : str
  :ReturnType: bool
  """
  File, Version = mdf.getVersion(FileName)
  return     File == 'MDF'\
         and Version >= '4.00'

ccs_def = {0: {'cc_type': 0, 'cc_val': tuple(), 'cc_unit': '', 'cc_ref':tuple()}}
""":type: dict
initial value for procCC"""

def procCC(ccs, f, cn_cc_conversion):
  """
  :Parameters:
    ccs : dict
      {cn_cc_conversion: {'cc_type': int, 'cc_val': tuple, 'cc_unit': str, 'cc_ref': tuple}}
    f : file
    cn_cc_conversion : int

  :ReturnType: dict
  :Return: {'cc_type': int, 'cc_val': tuple, 'cc_unit': str, 'cc_ref': tuple}
  """
  if cn_cc_conversion not in ccs:
    cc_type,\
    cc_val,\
    cc_ref,\
    unit = mf4.procCC(f, cn_cc_conversion)
    ccs[cn_cc_conversion] = dict(cc_type=cc_type,
                                 cc_val=cc_val,
                                 cc_ref=cc_ref,
                                 cc_unit=unit)
  return ccs[cn_cc_conversion]


def proc_cc7_cc_ref(ccs, f, link):
  """
  Create a string representation from the cc_ref elem `link`.

  :Parameters:
    ccs : dict
      {cn_cc_conversion: {'cc_type': int, 'cc_val': tuple, 'cc_unit': str, 'cc_ref': tuple}}
    f : file
    link : int
      cc_ref element

  :ReturnType: str
  """
  f.seek(link)
  link_id = f.read(4)
  if link_id == '##TX':
    return mf4.extractTX(f, link)
  elif link_id == '##CC':
    cc = procCC(ccs, f, link)
    return 'cc:cc_type=%(cc_type)d,cc_val=%(cc_val)s,cc_ref=%(cc_ref)s' %cc
  else:
    return 'unknown'

def str_cc7(f, ccs, cc_val, cc_ref):
  """
  Create a string representation from the `cc_val` and `cc_ref` of a conversion
  block with cc_type 7.


  :Parameters:
    f : file
    ccs : dict
      {cn_cc_conversion: {'cc_type': int, 'cc_val': tuple, 'cc_unit': str, 'cc_ref': tuple}}
    cc_val : tuple
    cc_ref : tuple

  :ReturnType: str
  """
  lines = []
  for value, text in get_cc7_rule(f, ccs, cc_val, cc_ref):
    if isinstance(value, float):
      value = '%.2f' % value
    line = '%s: %s' % (value, text)
    lines.append(line)
  return '\n'.join(lines)

def get_cc7_rule(f, ccs, cc_val, cc_ref):
  """
  Create a list representation from the `cc_val` and `cc_ref` of a conversion
  block with cc_type 7.


  :Parameters:
    f : file
    ccs : dict
      {cn_cc_conversion:
      {'cc_type': int, 'cc_val': tuple, 'cc_unit': str, 'cc_ref': tuple}}
    cc_val : tuple
    cc_ref : tuple

  :ReturnType: list
  """
  rule = []
  for link, value in zip(cc_ref, cc_val):
    text = proc_cc7_cc_ref(ccs, f, link)
    int_v = int(value)
    value = int_v if value == int_v else value
    rule.append((value, text))
  if cc_ref:
    text = proc_cc7_cc_ref(ccs, f, cc_ref[-1])
    rule.append(('default', text))
  return rule

sis_def = {0: ('NULL', 'NULL', 0)}
""":type: dict
Initial value for procSI"""

def procSI(sis, f, cn_si_source):
  """
  :Parameters:
    sis : dict
      {cn_si_source: (name<str>, path<str>, type<int>)}
    f : file
    cn_si_source : int

  :ReturnType: str, str, int
  :Return: name, path, type
  """
  if cn_si_source not in sis:
    sis[cn_si_source] = mf4.procSI(f, cn_si_source)
  return sis[cn_si_source]


def procCN(f, ccs, cn_link):
  cn_link,\
  cn_composition,\
  cn_tx_name,\
  cn_si_source,\
  cn_cc_conversion,\
  cn_data,\
  cn_md_unit,\
  cn_md_comment,\
  cn_type,\
  cn_sync_type,\
  cn_data_type,\
  cn_bit_offset,\
  cn_byte_offset,\
  cn_bit_count,\
  cn_flags,\
  cn_inval_bit_pos,\
  cn_precision,\
  cn_val_range_min,\
  cn_val_range_max,\
  cn_limit_min,\
  cn_limit_max,\
  cn_limit_ext_min,\
  cn_limit_ext_max = mf4.extractCN(f, cn_link)

  cc = procCC(ccs, f, cn_cc_conversion)

  unit = mf4.extractTX(f, cn_md_unit)
  if not unit:
    unit = cc['cc_unit']

  cn_name = mf4.extractTX(f, cn_tx_name)
  return {'cn_link':          cn_link,
          'cn_composition':   cn_composition,
          'cn_si_source':     cn_si_source,
          'cn_cc_conversion': cn_cc_conversion,
          'cn_data':          cn_data,
          'cn_type':          cn_type,
          'cn_data_type':     cn_data_type,
          'cn_bit_offset':    cn_bit_offset,
          'cn_byte_offset':   cn_byte_offset,
          'cn_bit_count':     cn_bit_count,
          'cn_name':          cn_name,
          'unit':             unit}


def isCnStruct(f, cn):
  return    cn['cn_data_type'] == 10\
        and mf4.checkBlock(f, cn['cn_composition'], '##CN')


def _iterCnStruct(f, ccs, cn_link, cn_str_link):
  while cn_link:
    cn = procCN(f, ccs, cn_link)
    cn_link = cn['cn_link']
    if isCnStruct(f, cn):
      for sub_cn in _iterCnStruct(f, ccs, cn['cn_composition'], cn_link):
        if sub_cn['cn_link'] == 0:
          sub_cn['cn_link'] = cn_str_link
        yield sub_cn
    else:
      yield cn


def iterCnStruct(f, ccs, cn_link):
  cn = procCN(f, ccs, cn_link)
  if isCnStruct(f, cn):
    for sub_cn in _iterCnStruct(f, ccs, cn['cn_composition'], cn['cn_link']):
      sub_cn['cn_si_source'] = cn['cn_si_source']
      yield sub_cn
  else:
    yield cn


def splitDeviceName(dev_name):
  """
  Split the `dev_name` by the first -.
  It returns always with two string.

  :Parameters:
    dev_name : str

  :ReturnType: str, str
  :Return: dev_name, dev_ext
  """
  if dev_name.count(iParser.DEVICE_NAME_SEPARATOR):
    return dev_name.split(iParser.DEVICE_NAME_SEPARATOR, 1)
  else:
    return dev_name, ''


class cMf4Parser(iParser.iParser):
  checkParser = staticmethod(checkParser)
  __version__ = '0.2.0'

  @classmethod
  def readStartDate(cls, filename):
    """
    Get the start of the measurement from the hd_start_time_ns, hd_tz_offset_min
    and hd_dst_offset_min attributes of the header block

    :Parameters:
      FileName : str

    :Exceptions:
      AssertionError

    :ReturnType: `datetime.datetime`
    """
    assert os.path.isfile(filename), '%s does not exists' % filename
    f = open(filename, 'rb')

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
    f.close()

    date = datetime.datetime.fromtimestamp(hd_start_time_ns * 1e-9)
    if hd_time_flags & 2:
      date += datetime.timedelta(minutes=hd_tz_offset_min+hd_dst_offset_min)

    return date

  def __init__(self, filename):
    """
    :Parameters:
      filename : str
    """
    self.file_name = filename
    self.result = None

    f = open(filename, 'rb')
    try:
      self.f = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_COPY)
    except WindowsError:
      self.f = f
      mmap_success = False
    else:
      mmap_success = True

    sis = sis_def.copy()
    self.ccs = ccs_def.copy()
    self.dgs = []
    self.cgs = []
    self.cns = []
    self.Devicess = {}
    self.Times = {}

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
    hd_start_distance_m = mf4.extractHD(self.f)

    FileComment = mf4.extractTX(self.f, hd_md_comment)
    # self.FileComment = mf4.parseFileComment(FileComment)
    while dg_link:
      dg_link,\
      cg_link,\
      dg_data,\
      dg_md_comment,\
      dg_rec_id_size = mf4.extractDG(self.f, dg_link)

      dg = dict(dg_data=dg_data, dg_rec_id_size=dg_rec_id_size)
      dg_nr = len(self.dgs)
      self.dgs.append(dg)

      cgs = []
      self.cgs.append(cgs)
      cg_cns = []
      self.cns.append(cg_cns)
      while cg_link:
        cg_nr = len(cgs)
        timekey = self.genTimekey(dg_nr, cg_nr)

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
        cg_inval_bytes = mf4.extractCG(self.f, cg_link)

        acq_name = mf4.extractTX(self.f, cg_tx_acq_name)
        cg_acq_name,\
        cg_acq_path,\
        cg_acq_type = procSI(sis, self.f, cg_si_acq_source)
        cg = dict(cg_cycle_count=cg_cycle_count,
                  cg_data_bytes=cg_data_bytes, cg_record_id=cg_record_id)
        cgs.append(cg)

        cns = []
        cg_cns.append(cns)
        while cn_link:
          for cn in iterCnStruct(self.f, self.ccs, cn_link):
            cn_nr = len(cns)

            cn_acq_name,\
            cn_acq_path,\
            cn_acq_type = procSI(sis, self.f, cn['cn_si_source'])

            cn_link = cn.pop('cn_link')
            cn_name = cn.pop('cn_name')

            dev_name,\
            dev_ext = mf4.createDevName(acq_name,
                                        cg_acq_name, cg_acq_path, cg_acq_type,
                                        cn_acq_name, cn_acq_path, cn_name)


            del cn['cn_si_source']
            cns.append(cn)

            if cn['cn_type'] == 2:
              self.Times[timekey] = dg_nr, cg_nr, cn_nr
            else:
              dev_group = self.Devicess.setdefault(str(dev_name), {})
              dev = dev_group.setdefault(str(dev_ext), {})
              # cn_name = cn_name.replace('.', '_')
              # cn_name = cn_name.replace(' ', '_')
              dev[str(cn_name)] = dg_nr, cg_nr, cn_nr
    if mmap_success:
      self.f.close()
      self.f = f
    return

  @staticmethod
  def genTimekey(dg_nr, cg_nr):
    timekey = '%d.%d' % (dg_nr, cg_nr)
    return timekey

  def close(self):
    self.f.close()
    return

  def getNrs(self, dev_name, sig_name):
    """
    Get the data group and channel group numbers of the selected signal.

    :Parameters:
      dev_name : str
      sig_name : str
    :ReturnType: int, int, int
    :Return: dg_nr, cg_nr, cn_nr
    """
    try:
      dev_group, dev_ext = dev_name.split(iParser.DEVICE_NAME_SEPARATOR, 1)
      return self.Devicess[dev_group][dev_ext][sig_name]
    except:
      dev_group= dev_name.split(iParser.DEVICE_NAME_SEPARATOR, 1)
      for item in dev_group:
        for keys in self.Devicess[item]:
          return self.Devicess[item][keys][sig_name]


  def getSignal(self, dev_name, sig_name, dtype=None, factor=None, offset=None):
    """
    :Parameters:
      dev_name : str
      sig_name : str
      dtype : str, optional
        Override the default interpretation of measured bit pattern
        Example: Use '<i1' to interpret as little endian 1-byte signed integer
      factor: float, optional
        Override the default factor of measured signal
      offset: float, optional
        Override the default offset of measured signal
    :ReturnType: `numpy.ndarray`, str
    :Return: value, timekey
    """

    dg_nr, cg_nr, cn_nr = self.getNrs(dev_name, sig_name)
    exe_path = os.path.dirname(__file__) + r'\bin\mf4parser_exe\mf4parser_exe.exe'
    command = ' '.join(
      [exe_path, '-f', self.file_name, '-s', '"'+(sig_name)+'"', '-g', str(dg_nr), '-c', str(cn_nr)])

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    self.result = process.communicate()
    phy = np.fromstring(str(self.result[0]).split('signal_value: ')[1].split('Signal time: ')[0].replace('[', ''),
                    dtype='float64', sep=', ')
    # cn_type = self.cns[dg_nr][cg_nr][cn_nr]['cn_type']
    # if cn_type == 1:
    #   print >> sys.stderr, 'ChannelTypeError: variable length signal data is not implemented'\
    #                        'for %s signal at %d data group' %(sig_name, dg_nr)
    #   sys.stderr.flush()
    #   phy = self.getVarLenData(dg_nr, cg_nr, cn_nr)
    # else:
    #   phy = self.getValue(dg_nr, cg_nr, cn_nr, dtype=dtype, factor=factor,
    #                       offset=offset, dev_name=dev_name, sig_name=sig_name)
    timekey = self.genTimekey(dg_nr, cg_nr)
    return phy, timekey

  def getTime(self, timekey):
    """
    :Parameters:
      timekey : str
    :ReturnType: `numpy.ndarray`
    """
    phy = np.fromstring(str(self.result[0]).split('Signal time: ')[1].split('Signal Unit:')[0].replace('[', ''),
                dtype='float64', sep=', ')
    return phy

  def getVarLenData(self, dg_nr, cg_nr, cn_nr):
    """
    It is a cheat.

    :ReturnType: `numpy.ndarray`
    """
    #TODO SDblock of signal and DTblock of datagroup parsing
    #dummy implemetation against crashes
    cg_cycle_count = self.cgs[dg_nr][cg_nr]['cg_cycle_count']
    return numpy.empty(cg_cycle_count, dtype=str)

  def getValue(self, dg_nr, cg_nr, cn_nr, dtype=None, factor=None, offset=None,
                dev_name=None, sig_name=None):
    """
    :ReturnType: `numpy.ndarray`
    """
    raw = self.readRaw(dg_nr, cg_nr, cn_nr, dtype=dtype)
    cn = self.cns[dg_nr][cg_nr][cn_nr]
    return self.convRawPhy(raw, cn['cn_cc_conversion'], factor=factor,
                          offset=offset, dev_name=dev_name, sig_name=sig_name)

  def readRaw(self, dg_nr, cg_nr, cn_nr, dtype=None):
    dg = self.dgs[dg_nr]
    cg = self.cgs[dg_nr][cg_nr]
    cn = self.cns[dg_nr][cg_nr][cn_nr]

    dtypes,\
    dtype_,\
    upshift,\
    downshift = MdfParser.calcReadAttrs(mf4.orders,
                                        mf4.formats,
                                        cn['cn_data_type'],
                                        cn['cn_bit_count'],
                                        cn['cn_bit_offset'],
                                        cn['cn_byte_offset'],
                                        cg['cg_data_bytes'])

    dtype = dtype_ if dtype is None else dtype

    splits, dg_data_extra = MdfParser.calcSplits(dtypes)

    if cn['cn_composition']:
      ca = mf4.extractCA(self.f, cn['cn_composition'])
      ca['ca_size'] = mdf.getTypeSize(dtype)
      ca['ca_prod'] = mf4.calcCaDimProd(ca)
    else:
      ca = {}

    record_sizes = self.getRecordSizes(dg_nr)

    raws = []
    for dt_data, dt_size in mf4.iterDT(self.f, dg['dg_data']):
      dt_cycle_count = min(dt_size / cg['cg_data_bytes'], cg['cg_cycle_count'])
      if ca:
        raw = numpy.zeros((dt_cycle_count, ca['ca_prod']), dtype=dtype)
        for i in xrange(ca['ca_prod']):
          offset = i * ca['ca_size']
          raw[:,i] = mdf.readData(self.f,
                                  dt_data+offset,
                                  dg_data_extra,
                                  record_sizes,
                                  dg['dg_rec_id_size'],
                                  cg['cg_record_id'],
                                  dt_cycle_count,
                                  dtype,
                                  upshift,
                                  downshift,
                                  splits)
        shape = [dt_cycle_count]
        shape.extend(ca['ca_dim_size'])
        order = 'F' if ca['ca_flags'] & 64 else 'C'
        raw = raw.reshape(shape, order=order)
      else:
        raw = mdf.readData(self.f,
                           dt_data,
                           dg_data_extra,
                           record_sizes,
                           dg['dg_rec_id_size'],
                           cg['cg_record_id'],
                           dt_cycle_count,
                           dtype,
                           upshift,
                           downshift,
                           splits)
      raws.append(raw)
    if len(raws) > 1:
      raw = numpy.concatenate(raws)
    return raw

  def getSignalShape(self, DevName, SigName):
    dg_nr, cg_nr, cn_nr = self.getNrs(DevName, SigName)
    cn = self.cns[dg_nr][cg_nr][cn_nr]

    #the first element in the list is the "time dimension" and is a don't care in this case
    if cn['cn_composition']:
      ca = mf4.extractCA(self.f, cn['cn_composition'])
      dims = list((0,) + ca['ca_dim_size'])
      return dims
    else:
      #signal is one dimensional
      return [0]

  def getRecordSizes(self, dg_nr):
    sizes = dict((cg['cg_record_id'], cg['cg_data_bytes'])
                 for cg in self.cgs[dg_nr])
    return sizes

  def convRawPhy(self, raw, cn_cc_conversion, factor=None, offset=None,
                  dev_name=None, sig_name=None):
    cc = procCC(self.ccs, self.f, cn_cc_conversion)
    cc_type = cc['cc_type']
    cc_val = cc['cc_val']
    cc_ref = cc['cc_ref']
    if cc_type == 7:
      if dev_name is not None and sig_name is not None:
        rule = self.getConversionRule(dev_name, sig_name)
        if 'default'  in rule and rule['default'] != 'unknown':
          default = rule['default']
          default = default.replace('cc:', '')
          rule = eval("dict(%s)" %default)
          cc_type = rule['cc_type']
          cc_val = rule['cc_val']
          cc_ref = rule['cc_ref']
    phy = mf4.convRawPhy(raw, cc_type, cc_val, cc_ref, factor=factor,
                         offset=offset)
    return phy

  def contains(self, dev_name, sig_name):
    dev_group, dev_ext = dev_name.split(iParser.DEVICE_NAME_SEPARATOR, 1)
    return     dev_group in self.Devicess\
           and dev_ext   in self.Devicess[dev_group]\
           and sig_name  in self.Devicess[dev_group][dev_ext]

  def getDeviceNames(self, sig_name):
    dev_names = []
    for dev_group, dev in self.Devicess.iteritems():
      for dev_ext, signals in dev.iteritems():
        if sig_name in signals:
          dev_name = dev_group, dev_ext
          dev_name = iParser.DEVICE_NAME_SEPARATOR.join(dev_name)
          dev_names.append(dev_name)
    return dev_names

  def getExtendedDeviceNames(self, dev_name, FavorMatch=False):
    dev_group, search = splitDeviceName(dev_name)
    if dev_group not in self.Devicess:
      return []

    sep = iParser.DEVICE_NAME_SEPARATOR
    dev_names = [dev_group + sep + dev_ext
                 for dev_ext in self.Devicess[dev_group]
                 if dev_ext.startswith(search)]
    if FavorMatch and dev_group + sep + search in dev_names:
      dev_names = [dev_group + sep + search]  # return only the matching device
    return dev_names

  def getNames(self, sig_name, pattern, FavorMatch=False):
    dev_group, search = splitDeviceName(pattern)
    if dev_group not in self.Devicess:
      return []

    sep = iParser.DEVICE_NAME_SEPARATOR
    dev = self.Devicess[dev_group]

    dev_names = [dev_group + sep + ext
                 for ext in dev
                 if    ext.startswith(search)
                   and sig_name in dev[ext]]
    if FavorMatch and dev_group + sep + search in dev_names:
      dev_names = [dev_group + sep + search]  # return only the matching device
    return dev_names

  def iterDeviceNames(self):
    for dev_group, dev in self.Devicess.iteritems():
      for dev_ext in dev:
        dev_name = dev_group, dev_ext
        yield iParser.DEVICE_NAME_SEPARATOR.join(dev_name)

  def iterTimeKeys(self):
    return self.Times.iterkeys()

  def iterSignalNames(self, dev_name):
    dev_group,\
    dev_ext = dev_name.split(iParser.DEVICE_NAME_SEPARATOR, 1)
    return self.Devicess[dev_group][dev_ext].iterkeys()

  def getSignalLength(self, dev_name, sig_name):
    timekey = self.getTimeKey(dev_name, sig_name)
    dg_nr, cg_nr, cn_nr = self.getNrs(dev_name, sig_name)
    if self.result is None:
      exe_path = os.path.dirname(__file__) + r'\bin\mf4parser_exe\mf4parser_exe.exe'
      command = ' '.join(
      [exe_path, '-f', self.file_name, '-s', '"'+(sig_name)+'"', '-g', str(dg_nr), '-c', str(cn_nr)])

      process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      self.result = process.communicate()
    time = self.getTime(timekey)
    return time.size

  def getMeasSignalLength(self, dev_name, sig_name):
    """"
    Get the registered signal length, that can differ from the read signal in
    case of corrupt measurement

    :Parameters:
      dev_name : str
        Name of device which contain the selected signal.
      sig_name : str
        Name of the selected signal.
    :ReturnType: int
    """
    dg_nr, cg_nr, cn_nr = self.getNrs(dev_name, sig_name)
    return self.cgs[dg_nr][cg_nr]['cg_cycle_count']

  def isSignalEmpty(self, DeviceName, SignalName):
    return self.getMeasSignalLength(DeviceName, SignalName) == 0

  def getPhysicalUnit(self, dev_name, sig_name):
    unit = str(self.result[0]).split('Signal time: ')[1].split('Signal Unit:')[1].strip()
    # dg_nr, cg_nr, cn_nr = self.getNrs(dev_name, sig_name)
    # return self.cns[dg_nr][cg_nr][cn_nr]['unit']
    return unit

  def getTimeKey(self, dev_name, sig_name):
    dg_nr, cg_nr, cn_nr = self.getNrs(dev_name, sig_name)
    return self.genTimekey(dg_nr, cg_nr), dg_nr, cg_nr, cn_nr

  def getConversionRule(self, dev_name, sig_name):
    dg_nr, cg_nr, cn_nr = self.getNrs(dev_name, sig_name)
    cn_cc_conversion = self.cns[dg_nr][cg_nr][cn_nr]['cn_cc_conversion']
    cc = self.ccs[cn_cc_conversion]
    rule = dict(get_cc7_rule(self.f, self.ccs, cc['cc_val'], cc['cc_ref']))
    return rule

  def cmd_s(self, dev_name, sig_name):
    """
    show signal attributes for parsing
    device-name signal-name
    """
    dg_nr, cg_nr, cn_nr = self.getNrs(dev_name, sig_name)
    return [('dg_nr',   str(dg_nr)),
            ('cg_nr',   str(cg_nr)),
            ('cn_nr',   str(cn_nr)),
            ('timekey', self.getTimeKey(dev_name, sig_name)),
            ('unit',    self.getPhysicalUnit(dev_name, sig_name)),
            ('length',  str(self.getSignalLength(dev_name, sig_name)))]

  def cmd_t(self, timekey):
    """
    show data group block
    cg_nr
    """
    dg_nr, cg_nr, cn_nr = self.Times[timekey]
    return [('dg_nr', str(cg_nr)),
            ('cg_nr', str(cg_nr)),
            ('cn_nr', str(cn_nr))]

  def cmd_dg(self, dg_nr):
    """
    show data group block
    dg_nr
    """
    dg_nr = int(dg_nr)
    dg = self.dgs[dg_nr]
    k = 'dg_data'
    return [(k, str(dg[k]))]

  def cmd_cg(self, dg_nr, cg_nr):
    """
    show channel group block
    dg_nr
    cg_nr
    """
    dg_nr = int(dg_nr)
    cg_nr = int(cg_nr)
    cg = self.cgs[dg_nr][cg_nr]
    return [(k, str(cg[k])) for k in 'cg_data_bytes',
                                     'cg_cycle_count']

  def cmd_cn(self, dg_nr, cg_nr, cn_nr):
    """
    show channel block
    cn_nr
    """
    dg_nr = int(dg_nr)
    cg_nr = int(cg_nr)
    cn_nr = int(cn_nr)
    cn = self.cns[dg_nr][cg_nr][cn_nr]
    return [(k, str(cn[k])) for k in 'cn_data_type',
                                     'cn_bit_offset',
                                     'cn_byte_offset',
                                     'cn_bit_count',
                                     'cn_cc_conversion',
                                     'cn_type',
                                     'cn_data']

  def cmd_cc(self, cc_link):
    """
    show channel conversion block
    cn_cc_conversion
    """
    cc_link = int(cc_link)
    cc = self.ccs[cc_link]
    cc_type = cc['cc_type']
    cc_val  = cc['cc_val']
    cc_ref  = cc['cc_ref']
    answer = [(k, str(cc[k])) for k in 'cc_type', 'cc_val', 'cc_ref']
    for value, text in get_cc7_rule(self.f, self.ccs, cc_val, cc_ref):
      if isinstance(value, float):
        value = '%.2f' % value
      else:
        value = str(value)
      answer.append((value, text))
    return answer


def proc_answer(answer, tab, sep):
  if not answer:
    return ''
  if tab is None:
    maxes = [len(word) for word in answer[0][:-1]]
    for line in answer[1:]:
      maxes = [max(m, len(word)) for word, m in zip(line[:-1], maxes)]
    pat = ['%-'+str(m)+'s' for m in maxes]
    pat.append('%s')
    pat = ' '.join(pat)
  else:
    pat = ['%s' for i in xrange(len(answer[0]))]
    pat = tab.join(pat)
  answer = [pat %line for line in answer]
  return sep.join(answer)

