
__docformat__ = "restructuredtext en"

'''
Recording service for Navigators with graphical output.

Through this module, it's possible to save any sequence of frames shown in 
any navigator into a video file (for now, with avi extension only), as long 
as the navigator's output can be expressed in an ARGB string.

The module can start and save multiple "videos" during a single session, 
allowing the other navigators and the user to record as many parts as needed.

This module uses FFMPEG for encoding video. 

The service is supposed to work on the following way:

__init__: To be called on the constructor
   |
   V
record_start: After this, it's ready to receive frames.
   |
   V
update_record: Adds a new frame to the ongoing record
   |
   V
stop_record: Finishes recording, saves the file and stops service.
   |
   V
record_start: Would start a new record with a modified filename

:Pending:
TODO: Officially rig each UI, test with doublerunning recording.
TODO: Record remixing- use the 3 other filters OR:
TODO: A single filter using number of streams
TODO: Replace hardcoded temporary log files by using 'tempfile' module
TODO: Align file names and command line options with the image capture feature
'''

import pyglet_workaround  # necessary as early as possible (#164)

import os
import sys
import subprocess as sp
import logging

from measparser import ffmpeg

logger = logging.getLogger()

STDERR_OUT = "_record.log"
STDOUT_OUT = "_output.log"


class RecordingService(object):
  """
  Class for recording the sequence of any navigator that relies on dynamic
  image visualization
  """
  
  def __init__(self, filename, target_dir="recording"):
    """Constructor for RecordingService. Initializes the basic
    information needed to start a pipe to FFMPEG
    
    :Parameters:
    
    filename : str
      Base name for the output filename. The final file names will be on this
      format : [filename]_[number].[extension]

    target_dir : str, optional
      Folder to where the output files will be exported.
      If left by default, the output will be placed on a 'recording' folder where the 
      mass script is located
    """
    self.is_recording = False
    self.base_filename = filename
    # Multiple starts, multiple filenames:
    self.filename_template = "{0}_{1}.{2}"
    self.extension = 'avi'
    
    self.target_dir = os.path.abspath(target_dir)
    self.record_counter = 0
    self.cmd = None
    self.process = None
    return

  def set_target_path(self, path):
    """Sets target path for exported videos. Useful for setting paths after creating the 
    Navigator

    path : str
      New path for exported recordings. Can be absolute or relative
    """
    if os.path.isabs(path):
      self.target_dir = path
    else:
      self.target_dir = os.path.abspath(path)

  def record_start(self, video_size, fps=30, flipped=False, filename_extra=''):
    """Starts a new record under the known filename, using a 
    number extension.
    
    :Parameters:
    
    video_size : tuple 
      Tuple containing the frame's height and width. The method expects the tuple to
      have the following format : (WIDTH, HEIGHT)
      
    fps : int
      Frames per second of the video to be created. This determines the length (and 
      therefore playback speed) of the created video.
      
    flipped : boolean
      Indicates whether or not the navigator's RGBA output is flipped vertically.
      This happens with pyglet's output, but does not happen when the source is MPL.

    filename_extra : str
      Optional, extra prefix that can be added before the record's filename in order
      to recognize it better.

    """
    # FFMPEG likes WxH strings:
    self.video_size_str = "{0}x{1}".format(video_size[0], video_size[1])
    if not os.path.exists(self.target_dir):
      os.mkdir(self.target_dir)
    filename = self._format_filename(filename_extra)
    # If two parallel navigators start recording, they would write to the
    # same path/filename
    while os.path.exists(filename):
      self.record_counter += 1
    filename = self._format_filename(filename_extra)

    cmd = ([ffmpeg.executable, '-y',       # FFMPEG Binary, overwrite option
                '-s', self.video_size_str, # Set video size
                '-f', 'rawvideo',          # format - video codec
                '-pix_fmt', 'rgba',        # frame input format
                '-i', '-',                 # Force FFMPEG to expect Pipes
                '-vcodec', 'mpeg4',        # For output, use mpeg4 codec
                '-r', "%.02f"%fps,         # Expected FPS for the video
                '-b', '5000k']             # Use a 5000k bitrate for video
                + (['-vf', 'vflip']        # Flip vertically...
                   if flipped else [])     # ...if needed
                + [filename])              # Video ouput filename

    self.logfile = open(self.base_filename + STDERR_OUT + str(self.record_counter), 'w+')
    self.outputfile = open(self.base_filename + STDOUT_OUT + str(self.record_counter), 'w+')
    # stdout has to be piped out to a file in FFMPEG because the output can get long
    # and it can and WILL crash the pipe immediately.
    self.process = sp.Popen(cmd, stdout=self.outputfile, stdin=sp.PIPE, stderr=self.logfile)
    self.is_recording = True
    logger.info("Starting recording at '%s'..." % filename)
    return
  
  def update_current_record(self, frame):
    """Updates the existing record with a new frame. 
    If no record is active, the frame is discarded.
    
    :Parameters:
    
    frame : string (RGBA string)
      RGBA string containing the raw data from the navigator.
      If the frame does not follow the RGBA format, 
      the video will only contain random noise.
    """

    if self.is_recording and self.process is not None:
      try:
        self.process.stdin.write(frame)
      except IOError as err:
        error_str = str(err)+'\nFFMPEG Error: \n'
        encoder_error = self.process.stderr.read()
        if "Unknown encoder" in encoder_error:
          error_str += "FFMPEG did not find the video encoder"
        elif "incorrect codec parameters" in encoder_error:
          error_str += "The extension is not compatible with the codec."
        elif "encoder setup failed" in encoder_error:
          error_str += "The bitrate is too high or too low for the video codec."
        raise IOError(error_str)
    else:
      logger.warning("Can't record frame: FFMPEG is not engaged or " +
                     "Recorder is currently not expecting frames")
    return
  
  def stop_current_record(self):
    """Stop and closes the current record. 
    The recorded capture is saved to disk"""

    if self.process is not None:
      self.process.stdin.close()
      if self.process.stderr is not None:
        self.process.stderr.close()
      self.process.wait()
      del self.process
      self.record_counter += 1
      self.is_recording = False
      self.logfile.close()
      self.outputfile.close()
      logger.info("Stopped recording")
      # Cleanup of temporary pipe "valves", we don't need the output.
      path_stderr = os.path.join(os.path.dirname(sys.argv[0]),
                                 self.base_filename + STDERR_OUT + str(self.record_counter))
      path_stdout = os.path.join(os.path.dirname(sys.argv[0]),
                                 self.base_filename + STDOUT_OUT + str(self.record_counter))

      if os.path.exists(path_stderr):
        os.remove(path_stderr)
      if os.path.exists(path_stdout):
        os.remove(path_stdout)
    return

  def _format_filename(self, filename_extra):
    filename = self.filename_template.format(self.base_filename,
                                               self.record_counter,
                                               self.extension)
    filename = filename_extra + filename
    filename = os.path.join(self.target_dir, filename)
    return filename

def mix_recorded_videos(target_path, filename_prefix):
  logger.info("Remixing videos...")
  initial_files = [os.path.join(target_path, x) for x in os.listdir(target_path)]
  # filter other filenames
  available_files = [path for path in initial_files if filename_prefix in path and "_allNavs.avi" not in path]
  num_streams = len(available_files)
  available_files = _get_suggested_layout(available_files)

  #

  if num_streams == 4:
    filter_ = "nullsrc=size=1200x1200 [background];"+\
     "[0:v] setpts=PTS-STARTPTS, scale=750x600[left];" +\
     "[1:v] setpts=PTS-STARTPTS, scale=450x600[right];"+\
     "[2:v] setpts=PTS-STARTPTS, scale=600x600[bleft];"+\
     "[3:v] setpts=PTS-STARTPTS, scale=600x600[bright];"+\
     "[background][left]       overlay=shortest=1       [background+left];"+\
     "[background+left][right] overlay=shortest=1:x=750 [left+right];"+\
     "[left+right][bleft] overlay=shortest=1:y=600 [top+left];"+\
     "[top+left][bright] overlay=shortest=1:y=600:x=600 [final]"
  elif num_streams == 3:
    filter_ = "nullsrc=size=1200x1200 [background];"+\
    "[0:v] setpts=PTS-STARTPTS, scale=600x600[left];" +\
    "[1:v] setpts=PTS-STARTPTS, scale=600x600[right];"+\
    "[2:v] setpts=PTS-STARTPTS, scale=600x600[bleft];"+\
    "[background][left]       overlay=shortest=1       [background+left];"+\
    "[background+left][right] overlay=shortest=1:x=600 [left+right];"+\
    "[left+right][bleft] overlay=shortest=1:y=600 [final]"
  elif num_streams == 2:
    filter_ = "nullsrc=size=1200x600 [background];"+\
    "[0:v] setpts=PTS-STARTPTS, scale=750x500[left];" +\
    "[1:v] setpts=PTS-STARTPTS, scale=450x500[right];"+\
    "[background][left]       overlay=shortest=1       [background+left];"+\
    "[background+left][right] overlay=shortest=1:x=750 [final]"
  elif num_streams == 1:
    filter_ = "nullsrc=size=600x600 [background];"+\
    "[0:v] setpts=PTS-STARTPTS, scale=500x500[left];" +\
    "[background][left]       overlay=shortest=1       [final]"
  else:
    raise ValueError("Select at least one module for recording")

  target_path = os.path.join(target_path, filename_prefix + "_allNavs.avi")
  cmd = [ffmpeg.executable, '-y', '-i', available_files[0]]
  cmd.extend(['-i', available_files[1]] if num_streams > 1 else [])
  cmd.extend(['-i', available_files[2]] if num_streams > 2 else [])
  cmd.extend(['-i', available_files[3]] if num_streams > 3 else [])
  cmd.extend(['-filter_complex', filter_])
  cmd.extend(['-map', "[final]"])
  cmd.extend(['-vcodec', 'mpeg4',
              '-r', "%.02f"%30,
              '-b:v', '5000k',
              target_path])

  errfile = open("mix"+STDERR_OUT, 'w+')
  outfile = open("mix"+STDOUT_OUT, 'w+')
  process = sp.Popen(cmd, stdout=outfile, stderr=errfile)
  process.wait()

  # Cleanup
  if os.path.exists(STDERR_OUT):
    os.remove(STDERR_OUT)
  if os.path.exists(STDOUT_OUT):
    os.remove(STDOUT_OUT)
  logger.info("Remixing finished.")
  return

def _get_suggested_layout(available_files):
  plots = []
  track = []
  video = []
  for path in available_files:
    if path.count('VideoRecord') > 0:
      video = [path]
    elif path.count('TrackRecord') > 0:
      track = [path]
    elif path.count('Record') > 0:
      plots.append(path)
  layout = video + track + plots
  return layout
