import imp
import sys

import numpy as np
import scipy.io as scio

AEBS_C_wrapper = imp.load_dynamic('AEBS_C_wrapper', r'C:\KBData\sandbox\AEBS_C_AREL\cython\release\AEBS_C_wrapper.pyd')

def fill_float_arrs(arrs_fxp, **kwargs):
  "fill float arrays based on fixed-point data"
  arrs_float = dict(arrs_fxp)
  for name, data in arrs_fxp.iteritems():
    if not np.issubdtype(data.dtype, np.float) and name in AEBS_C_wrapper.signame2norm:
      # convert to float only if not already float and has a norming constant
      data = AEBS_C_wrapper.FixedPointArray(data, name, **kwargs).float_value
    arrs_float[name] = data
  return arrs_float

def sim_mat(filename, **kwargs):
  mat = scio.loadmat(filename)
  # remove extra dimensions from arrays
  mat = dict((k,np.ravel(v)) if isinstance(v, np.ndarray) else (k,v) for k,v in mat.iteritems())
  # remove "kbaebsXXX_" prefix from field names
  mat = dict((k,v) if not k.startswith('kbaebs') else (k.split('_',1)[1],v) for k,v in mat.iteritems())
  t = mat['t']
  # put real-valued data into float format
  inp = fill_float_arrs( dict( (name, mat[name]) for name in AEBS_C_wrapper.kbaebsInputSt_t_dtype.names if name in mat )  )
  out = fill_float_arrs( dict( (name, mat[name]) for name in AEBS_C_wrapper.kbaebsOutputSt_t_dtype.names if name in mat ) )
  par = fill_float_arrs( dict( (name, mat[name][-1]) for name in AEBS_C_wrapper.kbaebsParameterSt_t_dtype.names )         )
  par.update(kwargs)

  out_sim, internals = AEBS_C_wrapper.AEBSproc_float(t, inp, par, typecheck=False)

  return t, inp, out, par, out_sim, internals

if __name__ ==  '__main__':
  t, inp, out, par, out_sim, internals  = sim_mat(sys.argv[1], UseAccelerationInfo=False)
  print t[0], t[-1]
  # print internals['drv']
