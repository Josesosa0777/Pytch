"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

'''Slider for video play control.
'''

__docformat__ = "restructuredtext en"

import pyglet_workaround  # necessary as early as possible (#164)

import pyglet

def draw_rect(x, y, width, height, color=[255,255,255]):
  pyglet.gl.glLineWidth(1)
  pyglet.gl.glBegin(pyglet.gl.GL_LINE_LOOP)
  pyglet.gl.glColor3ub(color[0],color[1],color[2])
  pyglet.gl.glVertex2f(x, y)
  pyglet.gl.glVertex2f(x + width, y)
  pyglet.gl.glVertex2f(x + width, y + height)
  pyglet.gl.glVertex2f(x, y + height)
  pyglet.gl.glEnd()
  pass

class Control(pyglet.event.EventDispatcher):
  x = y = 0
  width = height = 10

  def __init__(self, parent):
    super(Control, self).__init__()
    self.parent = parent
    pass
  
  def hit_test(self, x, y):
    return (self.x < x < self.x + self.width and  
            self.y < y < self.y + self.height)

  def capture_events(self):
    self.parent.push_handlers(self)
    pass

  def release_events(self):
    self.parent.remove_handlers(self)
    pass

class Slider(Control):
  THUMB_WIDTH = 6
  THUMB_HEIGHT = 10
  GROOVE_HEIGHT = 2

  def draw(self):
    center_y = self.y + self.height / 2
    draw_rect(self.x, center_y - self.GROOVE_HEIGHT / 2, 
              self.width, self.GROOVE_HEIGHT)
    pos = self.x + self.value * self.width / (self.max - self.min)
    draw_rect(pos - self.THUMB_WIDTH / 2, center_y - self.THUMB_HEIGHT / 2, 
              self.THUMB_WIDTH, self.THUMB_HEIGHT,[255,255,0])
    pass

  def coordinate_to_value(self, x):
    return float(x - self.x) / self.width * (self.max - self.min) + self.min
    pass

  def on_mouse_press(self, x, y, button, modifiers):
    self.capture_events()
    value = self.coordinate_to_value(x)
    self.dispatch_event('on_begin_scroll', value)
    pass

  def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
    value = min(max(self.coordinate_to_value(x), self.min), self.max)
    self.dispatch_event('on_change', value)
    pass
  
  def on_mouse_release(self, x, y, button, modifiers):
    self.release_events()
    value = self.coordinate_to_value(x)
    self.dispatch_event('on_end_scroll', value)
    pass

Slider.register_event_type('on_begin_scroll')
Slider.register_event_type('on_end_scroll')
Slider.register_event_type('on_change')

