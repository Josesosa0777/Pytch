"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
This module was initiated by:
http://www.mail-archive.com/pyglet-users@googlegroups.com/msg01914.html
"""

import pyglet_workaround  # necessary as early as possible (#164)

import pyglet
from pyglet import clock
import threading
import types
import collections
import time
import traceback

# This value is the minimum frequency with which the inter-thread message queue
# is checked by the _tend_queue function. If the queue starts piling up, 
# it will be checked more frequently, though.
min_queue_check_rate = 1/60.

_message_queue_lock = threading.Lock()
_message_queue = collections.deque()
_pyglet_thread = None

def _tend_queue(dt):
  # ONLY CALL THIS FROM WITHIN THE PYGLET EVENT LOOP
  if not _message_queue:
    # if the queue is empty, report that we can go a bit longer without checking
    # it in the future
    check_rate = dt * 1.5
  else:
    # if the queue has entries, choose a suitable check rate for the future
    # that would have kept these entries from piling up
    queue_len = len(_message_queue)
    check_rate = dt / (queue_len * 2.0)
    t = time.time()
    while _message_queue:
      # call functions from the queue, but for no longer than dt seconds
      # (otherwise, this function could stall a window while it services
      # a very full queue)
      _message_queue_lock.acquire()
      output_func, function, args, kwargs = _message_queue.popleft()
      _message_queue_lock.release()
      try:
        result = function(*args, **kwargs)
      except:
        print "Caught exception in background:"
        traceback.print_exc()
        result = None
      if output_func is not None:
        # If a function to call when the output is ready was specified, do so...
        output_func(result)
      if (time.time() - t) > dt:
        break
  return check_rate

class BackgroundEventLoop(pyglet.app.EventLoop):
  def idle(self):
    # Make a new idle loop that does NOT draw window contents each cycle.
    # If it did draw each loop through, then windows would get redrawn each
    # time the queue gets checked by _tend_queue, which is usually higher than
    # the needed frame rate. In this regime, windows are responsible for 
    # calling on_draw() as needed in response to clock ticks or GUI events.
    dt = clock.tick(True)  # MOD by BA
    # call _tend_queue, which returns the next time that the queue ought to 
    # be checked.
    desired_queue_check = _tend_queue(dt)
    desired_sleep_time = clock.get_sleep_time(True)  # MOD by BA
    if desired_sleep_time is None:
      return min(desired_queue_check, min_queue_check_rate)
    else:
      return min(desired_queue_check, desired_sleep_time, min_queue_check_rate)
      
  def on_window_close(self, window):
    # We don't care about closing windows because the pyglet app is just running
    # as a background thread
    pass

def _run_pyglet_thread():
  # ONLY CALL THIS FROM THE THREAD THAT WILL BE HANDLING PYGLET
  while True:
    try:
      reload(pyglet.app)  # need to reload pyglet.app to avoid RuntimeError
      event_loop = BackgroundEventLoop()
      event_loop.run()
    except:
      if traceback is not None:
        print "Caught exception in background:"
        traceback.print_exc()
        print "Restarting background event loop"

def start_pyglet():
  """Start pyglet in a background thread."""
  global _pyglet_thread
  if _pyglet_thread is None:
    _pyglet_thread = threading.Thread(target=_run_pyglet_thread)
    _pyglet_thread.setDaemon(True)
    _pyglet_thread.start()

class OutputContainer(object):
  def __init__(self):
    self.value = None
    self.filled = False
  def __call__(self, value):
    self.value = value
    self.filled = True

def _call_pyglet_function(function, args, kwargs, output_func):
  # basic core of calling a function
  if _pyglet_thread is None:
    start_pyglet()
  _message_queue_lock.acquire()
  _message_queue.append((output_func, function, args, kwargs))
  _message_queue_lock.release()

def call_pyglet_function(function, args=[], kwargs={}, return_result = True):
  """Call a function from within the pyglet background thread safely.
  If return_result is True, the output of the function will be returned,
  otherwise it will be discarded, which is slightly faster."""
  try:
    return_result = kwargs['return_result']
  except KeyError:
    pass
  if return_result:
    output = OutputContainer()
  else:
    output = None
  _call_pyglet_function(function, args, kwargs, output)
  if return_result:
    while not output.filled:
      # Just spin waiting for the result to be appended to the output list.
      pass
    return output.value

class PygletProxy(object):
  """Thread-safe proxy for a pyglet object. Pass the constructor a class object
   and provide the required arguments for initializing that class.
  The required instance will then be constructed in the pyglet background thread.
  The instance can be interacted with transparently through this proxy: getting
  and setting attributes and calling functions is done in a thread-safe manner
  by message passing. In addition, the object's dict is proxied, so dir()
  and friends works properly too.
  
  Example:
  win = PygletProxy(my_background_window, width=600, height=200)
  win.width = 500
  print dir(win)
  win.close()
  """
  class_names = set(['__init__', '__getattribute__', '__setattr__', '_proxy_object'])
  def __init__(self, object_class, *args, **kwargs):
    # ask the pyglet thread to make us the required object; however don't wait for it...
    # The thread could be blocked (e.g. if we try to construct such a proxy during
    # a module import), so we'll just let the proxy reference be filled in 
    # when it's ready.
    object.__setattr__(self, '_proxy_object', None)
    output_func = lambda result: object.__setattr__(self, '_proxy_object', result)
    _call_pyglet_function(object_class, args, kwargs, output_func)
      
  def __getattribute__(self, name):
    if name in PygletProxy.class_names:
      return object.__getattribute__(self, name)
    while self._proxy_object is None:
      pass  # wait for the object to be ready if not yet created
    value = getattr(self._proxy_object, name)
    if isinstance(value, types.MethodType):
      return ProxyFunction(value)
    else:
      return value
  
  def __setattr__(self, name, value):
    while self._proxy_object is None:
      pass  # wait for the object to be ready if not yet created
    if hasattr(self._proxy_object, name):
      call_pyglet_function(setattr, (self._proxy_object, name, value), {}, return_result=False)
    else:
      object.__setattr__(self, name, value)

class ProxyFunction(object):
  def __init__(self, function):
    self.function = function
  
  def __call__(self, *args, **kwargs):
    return call_pyglet_function(self.function, args, kwargs)
