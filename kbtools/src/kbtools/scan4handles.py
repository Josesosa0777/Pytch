"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

"""
function [list] = scan4handles(Handle)
% [list] = scan4handles(Handle)
% Find start and stop index of intervals when Handle is not zero
% 
% input:
%   Handle : sequence with default value 0
% return:
%   list   : list of start and stop index 
%            struct array with fields: start_idx and stop_idx
%
% example [list]=scan4handles([0,0,3,3,0,0,0,4,4,4,4,0])
%   list(1): start_idx: 3
%            stop_idx: 4
%   list(2): start_idx: 8
%            stop_idx: 11
"""
import numpy as np

#========================================================================================
def scan4handles(Handle, lowest_Handle_value = 1):

  ret = []

  idx_start_handle = np.diff(Handle).nonzero()[0]  # np.diff returns a tuple#

  start_idx = 0
  tmp_ret = [];
  for k in xrange(idx_start_handle.size):
    stop_idx = idx_start_handle[k]
    tmp_ret.append([Handle[start_idx], start_idx, stop_idx])
    start_idx = stop_idx+1
  tmp_ret.append([Handle[start_idx], start_idx, Handle.size-1])

  ret = []
  for k in xrange(len(tmp_ret)):
    if (tmp_ret[k][0]) >= lowest_Handle_value:
        ret.append(tmp_ret[k][1:])
 
  return ret

  
