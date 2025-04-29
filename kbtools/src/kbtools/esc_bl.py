"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

''' function esc_bl - clone of esc_bl.m '''

''' only to be downward compatible '''


''' 
function [s_out] = esc_bl(s_in)
% [s] = esc_bl(s)
% convert understore '_' into  backslash understore '\_'
% e.g. esc_bl('delta_h') -> 'delta\_h'

%   $Revision: 1.6 $
%   (c) KNORR-BREMSE
%   Schwiederdingen
%   T/ESS3.1 - Guecker
%   2006-04-07

if isempty(s_in)
  s_in = '';
end
s_out = strrep(s_in,'_','\_');


%s_out='';
%for k = 1:length(s_in)
%   if s_in(k) == '_'
%      s_out = [s_out,'\'];
%   end
%   s_out = [s_out,s_in(k)];
%end
%return
'''

import string

def esc_bl(s_in):
  return string.replace(s_in,'_','\_')
  
  
if __name__ == '__main__':
  s_out = esc_bl('delta_h')
  print s_out
  


