"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""
__docformat__ = "restructuredtext en"

import subprocess
import os

ffmpeg = os.path.join(os.path.dirname(__file__), 'ffmpeg.exe')
""":type: str
Path of the ffmpeg"""
cutcmd = ffmpeg + ' -i %(Input)s -ss %(Start)f -t %(Duration)f -sameq -r 25 -y %(Output)s'
""":type: str
Command pattern to split video with ffmpeg"""

def splitVideo(Input, Output, Start, End):
  """
  Split the `Input` video with ffmpeg
  
  :Parameters:
    Input : str
      Path of the input video
    Output : str
      Path of the output video
    Start : float
      Start time of the video snippet
    End : float
      End time os the vieo snippet
  """
  Duration = End - Start
  subprocess.call(cutcmd %locals())
  pass
