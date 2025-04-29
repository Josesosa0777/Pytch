"""
:Organization: Knorr-Bremse SfN GmbH T/DE Budapest Schwieberdingen T/HEE2
:Copyright: 
  Knorr-Bremse SfN GmbH reserves all rights even in the event of industrial 
  property. We reserve all rights of disposal such as copying and passing on to 
  third parties.
"""

'''The module provides OpenGL string rendering, shape building methods and shape definitions.
'''

__docformat__ = "restructuredtext en"

import math

import pyglet.gl
import OpenGL.GLUT  # requires pyopengl

import ShapeVertices

BUILDER = 'method'
""":type: str
Key of shape builder methods"""

KWARGS  = 'kwargs'
""":type: str
Key of keyword arguments for shape building"""

EDGE    = 'edge'
""":type: str
Key of edge/line OpenGL primitives:
  GL_POINTS,
  GL_LINES,
  GL_LINE_LOOP, 
  GL_LINE_STRIP"""

FACE    = 'face'
""":type: str
Key of surface OpenGL primitives:
  GL_TRIANGLES, 
  GL_TRIANGLE_STRIP, 
  GL_TRIANGLE_FAN,
  GL_QUADS,
  GL_QUAD_STRIP,
  GL_POLYGON"""

def drawString( text, 
                translate = None, 
                rotate    = None,
                scale     = (0.006,0.006,0),
                font      = OpenGL.GLUT.GLUT_STROKE_ROMAN,
                fontwidth = 1,
                color     = (255,255,255),
                alpha     = None ):
  """ Text rendering in an OpenGL context.
  :Parameters:
    text : str
      Text to render
    translate: tuple
      Additional text translation/offset: (x,y,z)
    rotate: tuple
      Additional text rotation: (angleDeg, Nx,Ny,Nz)
    scale: tuple
      Text scale factor: (xScale, yScale, zScale)
    font: int
      Text font (GLUT fonts are supported)
    fontwidth: int
      Text font width
    color: tuple
      Text color: (R,G,B) where color components are in range(0,255)
    alpha: int
      Text transparency level, in range(0,255)
  :Assumptions:
    OpenGL matrix mode is GL_MODELVIEW
    OpenGL blending (GL_BLEND) is enabled if alpha parameter is given
  :Warnings:
    If any other GL rendering is called after this method, matrix stack manipulation is needed (glPushMatrix, glPopMatrix)
  """

  # pyglet.gl.glPushMatrix()
  if translate is not None:
    pyglet.gl.glTranslatef(translate[0], translate[1], translate[2])
  if rotate is not None:
    pyglet.gl.glRotatef(rotate[0], rotate[1], rotate[2], rotate[3])
  if alpha is not None:
    pyglet.gl.glColor4ub(color[0], color[1], color[2], alpha)
  else:
    pyglet.gl.glColor3ub(color[0], color[1], color[2])
    
  pyglet.gl.glScalef(scale[0],scale[1],scale[2])
  pyglet.gl.glLineWidth(fontwidth)
  
  for c in text:
    OpenGL.GLUT.glutStrokeCharacter(font, ord(c))
  
  # pyglet.gl.glPopMatrix()
  return


def _buildDLvertexArray(listID, glPrimitive, vertices, indices=None, coordDim=3):
  """ Build the display list in vertex array mode. Applicable for static vertex data 
  with large number of vertices (more than a few hundreds).
  :Parameters:
    listID : int
      Identifier of the display list (covers the memory address)
    glPrimitive: int
      OpenGL primitive (GL_LINES, GL_LINE_LOOP, GL_POLYGON, etc.)
    vertices: iterable
      Container of the shape vertices
  """
  if indices is None:
    indices = range(len(vertices))
  c_verts = (pyglet.gl.GLfloat * len(vertices))(*vertices)
  c_indices = (pyglet.gl.GLuint * len(indices))(*indices)
  elementNum = len(c_indices)
    
  pyglet.gl.glEnableClientState(pyglet.gl.GL_VERTEX_ARRAY)
  pyglet.gl.glVertexPointer(coordDim, pyglet.gl.GL_FLOAT, 0, c_verts)
  
  pyglet.gl.glNewList(listID, pyglet.gl.GL_COMPILE)
  pyglet.gl.glDrawElements(glPrimitive, elementNum, pyglet.gl.GL_UNSIGNED_INT, c_indices)
  pyglet.gl.glEndList()
  # pyglet.gl.glDisableClientState(pyglet.gl.GL_VERTEX_ARRAY)
  
def _buildDLimmediate(listID, glPrimitive, vertices, rot=None, offset=None):
  """ Build the display list in immediate mode. Applicable for static vertex data
  with small number of vertices (less than a few hundred).
  :Parameters:
    listID : int
      Identifier of the display list (covers the memory address)
    glPrimitive: int
      OpenGL primitive (GL_LINES, GL_LINE_LOOP, GL_POLYGON, etc.)
    vertices: tuple
      Container of the shape vertices: (x1,y1,z1, ...., xN,yN,zN)
    rot: tuple
      Shape rotation definition: (angleDeg, Nx, Ny, Nz). Rotation is applied 
      first on the shape vertices, before translation (in case 'offset' parameter was given).
    offset: tuple
      Shape offset/translation definition: (x,y,z). Translation is applied 
      second on the shape vertices, after rotation (in case 'rot' parameter was given).
  """
  doStackOperation = rot is not None or offset is not None
  pyglet.gl.glNewList(listID, pyglet.gl.GL_COMPILE)
  if doStackOperation:
    pyglet.gl.glPushMatrix()
  if offset is not None:
    pyglet.gl.glTranslatef(offset[0], offset[1], offset[2])
  if rot is not None:
    pyglet.gl.glRotatef(rot[0], rot[1], rot[2], rot[3])
    
  pyglet.gl.glBegin(glPrimitive)
  for i in range(0, len(vertices), 3):
    x,y,z = vertices[i:i+3]
    pyglet.gl.glVertex3f(x,y,z)
  pyglet.gl.glEnd()
  
  if doStackOperation:
    pyglet.gl.glPopMatrix()
  pyglet.gl.glEndList()
  return

def calculateFOV(distances, anglesDeg):
  """ Calculates field of view shape coordinates
  """
  xLast = 0.0
  yLast = 0.0
  xData = []
  yData = distances
  xDataNeg = []
  yDataNeg = []
  for y, angle in zip(yData, anglesDeg):
    angle = math.radians(angle)
    x = xLast + (y-yLast)*math.tan(angle)
    xData.append(x)
    xDataNeg.append(-x)
    yDataNeg.append(y)
    xLast = x
    yLast = y
  
  xDataNeg.reverse()
  yDataNeg.reverse()
  xDataNeg.append(0.0)
  yDataNeg.append(0.0)
  xDataNeg.extend(xData)
  yDataNeg.extend(yData)
  
  return zip(xDataNeg, yDataNeg)
  
def _buildFieldOfView(listID, glPrimitive, distances, anglesDeg):
  """ Builds the field of view display list in immediate mode.
  """
  xyData = calculateFOV(distances, anglesDeg)
  
  pyglet.gl.glNewList(listID, pyglet.gl.GL_COMPILE)
  pyglet.gl.glBegin(glPrimitive)
  for x,y in xyData:
    pyglet.gl.glVertex3f( x, 0.0, -y)
    pyglet.gl.glVertex3f( x, 2.0, -y)
    pyglet.gl.glVertex3f( x, 0.0, -y)
    pyglet.gl.glVertex3f(-x, 0.0, -y)
    pyglet.gl.glVertex3f( x, 0.0, -y)
  pyglet.gl.glEnd()
  pyglet.gl.glEndList()
  return
  
shapeBuildProps = {'rectangle'          : {BUILDER   : _buildDLimmediate,
                                           EDGE      :  pyglet.gl.GL_LINE_LOOP,
                                           FACE      :  pyglet.gl.GL_QUADS,
                                           KWARGS    :  dict(vertices=ShapeVertices.rectangeVerts)},
                   'triangle'           : {BUILDER   : _buildDLimmediate,
                                           EDGE      :  pyglet.gl.GL_LINE_LOOP,
                                           FACE      :  pyglet.gl.GL_TRIANGLES,
                                           KWARGS    :  dict(vertices=ShapeVertices.triangleVerts)},
                   'triangleUpsideDown' : {BUILDER   : _buildDLimmediate,
                                           EDGE      :  pyglet.gl.GL_LINE_LOOP,
                                           FACE      :  pyglet.gl.GL_TRIANGLES,
                                           KWARGS    :  dict(vertices=ShapeVertices.triangleVerts, offset=(0., 1., 0.), rot=(180.0, 1.0, 0.0, 0.0))},
                   'aimingSign'         : {BUILDER   : _buildDLimmediate,
                                           EDGE      :  pyglet.gl.GL_LINES,
                                           KWARGS    :  dict(vertices=ShapeVertices.aimingsignVerts)},
                   'diamond'            : {BUILDER   : _buildDLimmediate,
                                           EDGE      :  pyglet.gl.GL_LINE_LOOP,
                                           FACE      :  pyglet.gl.GL_QUADS,
                                           KWARGS    :  dict(vertices=ShapeVertices.diamondVerts)},
                   'soundLines'         : {BUILDER   : _buildDLimmediate,
                                           EDGE      :  pyglet.gl.GL_LINES,
                                           KWARGS    :  dict(vertices=ShapeVertices.soundlinesVerts)},
                   'greaterLessThanSign': {BUILDER   : _buildDLimmediate,
                                           EDGE      :  pyglet.gl.GL_LINES,
                                           KWARGS    :  dict(vertices=ShapeVertices.greaterLessThanSignVerts)},
                   'X'                  : {BUILDER   : _buildDLimmediate,
                                           EDGE      :  pyglet.gl.GL_LINES,
                                           KWARGS    :  dict(vertices=ShapeVertices.xsignVerts)},
                   '+'                  : {BUILDER   : _buildDLimmediate,
                                           EDGE      :  pyglet.gl.GL_LINES,
                                           KWARGS    :  dict(vertices=ShapeVertices.plussignVerts)},
                   'hexagon'            : {BUILDER   : _buildDLimmediate,
                                           EDGE      :  pyglet.gl.GL_LINE_LOOP,
                                           FACE      :  pyglet.gl.GL_POLYGON,
                                           KWARGS    :  dict(vertices=ShapeVertices.hexagonVerts)},
                   'upsideDownT'        : {BUILDER   : _buildDLimmediate,
                                           EDGE      :  pyglet.gl.GL_LINES,
                                           KWARGS    :  dict(vertices=ShapeVertices.upsidedowntVerts)},
                   'v'                  : {BUILDER   : _buildDLimmediate,
                                           EDGE      :  pyglet.gl.GL_LINES,
                                           KWARGS    :  dict(vertices=ShapeVertices.smallvVerts)},
                   'rectNoCorn'         : {BUILDER   : _buildDLimmediate,
                                           EDGE      :  pyglet.gl.GL_LINES,
                                           KWARGS    :  dict(vertices=ShapeVertices.rectnocornersVerts)},
                   'eye'                : {BUILDER   : _buildDLimmediate,
                                           EDGE      :  pyglet.gl.GL_LINE_LOOP,
                                           FACE      :  pyglet.gl.GL_POLYGON,
                                           KWARGS    :  dict(vertices=ShapeVertices.eyeVerts)},
                   'eyeRot'             : {BUILDER   : _buildDLimmediate,
                                           EDGE      :  pyglet.gl.GL_LINE_LOOP,
                                           FACE      :  pyglet.gl.GL_POLYGON,
                                           KWARGS    :  dict(vertices=ShapeVertices.eyeVerts, offset=(0.6, 0.7, 0.), rot=(90.0, 0.0, 0.0, 1.0))},
                   'smallBow'           : {BUILDER   : _buildDLimmediate,
                                           EDGE      :  pyglet.gl.GL_LINES,
                                           KWARGS    :  dict(vertices=ShapeVertices.smallbowVerts)},
                   'pedestrian'         : {BUILDER   : _buildDLimmediate,
                                           EDGE      :  pyglet.gl.GL_LINES,
                                           KWARGS    :  dict(vertices=ShapeVertices.pedestrianVerts)},
                   'circle'             : {BUILDER   : _buildDLimmediate,
                                           EDGE      :  pyglet.gl.GL_LINE_LOOP,
                                           FACE      :  pyglet.gl.GL_POLYGON,
                                           KWARGS    :  dict(vertices=ShapeVertices.circleVerts)},
                   'trapezoid'          : {BUILDER   : _buildDLimmediate,
                                           EDGE      :  pyglet.gl.GL_LINE_LOOP,
                                           FACE      :  pyglet.gl.GL_QUADS,
                                           KWARGS    :  dict(vertices=ShapeVertices.trapezoidVerts)},
                   'flippedN'           : {BUILDER   : _buildDLimmediate,
                                           EDGE      :  pyglet.gl.GL_LINES,
                                           KWARGS    :  dict(vertices=ShapeVertices.flippednVerts)},
                   'Y'                  : {BUILDER   : _buildDLimmediate,
                                           EDGE      :  pyglet.gl.GL_LINES,
                                           KWARGS    :  dict(vertices=ShapeVertices.ysignVerts)},
                   'YupsideDown'        : {BUILDER   : _buildDLimmediate,
                                           EDGE      :  pyglet.gl.GL_LINES,
                                           KWARGS    :  dict(vertices=ShapeVertices.ysignVerts, offset=(0., 1.2, 0.), rot=(180.0, 1.0, 0.0, 0.0))},
                   'car'                : {BUILDER   : _buildDLimmediate,
                                           EDGE      :  pyglet.gl.GL_LINE_LOOP,
                                           FACE      :  pyglet.gl.GL_POLYGON,
                                           KWARGS    :  dict(vertices=ShapeVertices.carshapeVerts)},
                   'stop'               : {BUILDER   : _buildDLimmediate,
                                           EDGE      :  pyglet.gl.GL_LINE_LOOP,
                                           FACE      :  pyglet.gl.GL_POLYGON,
                                           KWARGS    :  dict(vertices=ShapeVertices.stopsignVerts)},  
                   'pentagon'           : {BUILDER   : _buildDLimmediate,
                                           EDGE      :  pyglet.gl.GL_LINE_LOOP,
                                           FACE      :  pyglet.gl.GL_POLYGON,
                                           KWARGS    :  dict(vertices=ShapeVertices.pentagonVerts)},
                   '?'                  : {BUILDER   : _buildDLimmediate,
                                           EDGE      :  pyglet.gl.GL_LINES,
                                           KWARGS    :  dict(vertices=ShapeVertices.questionmarkVerts)},
                   'intro'              : {BUILDER   : _buildDLimmediate,
                                           EDGE      :  pyglet.gl.GL_LINES,
                                           KWARGS    :  dict(vertices=ShapeVertices.introVerts)},
                   'debug'              : {BUILDER   : _buildDLimmediate,
                                           EDGE      :  pyglet.gl.GL_LINES,
                                           KWARGS    :  dict(vertices=ShapeVertices.debugVerts)},
                  }
""":type: dict
Container of general shape building properties {ShapeName<str> : {Builder<str>        : BuildMethod<function>,
                                                                  PrimitiveType<str>  : OpenGLprimitive<int>,
                                                                    ...,
                                                                  Keyword<str>        : Kwargs<dict>}, }"""
                                                                  
fovBuildProps = {'CVR3_FOV'     : {BUILDER   : _buildFieldOfView,
                                   EDGE      :  pyglet.gl.GL_LINE_STRIP,
                                   KWARGS    :  dict( distances=(30.0, 100.0, 160.0),
                                                      anglesDeg=(22  ,  10  ,   7  ))},
                 'LRR3_FOV'     : {BUILDER   : _buildFieldOfView,
                                   EDGE      :  pyglet.gl.GL_LINE_STRIP,
                                   KWARGS    :  dict( distances=(30.0, 100.0, 250.0),
                                                      anglesDeg=(15  ,  10  ,   8  ))},
                }
""":type: dict
Container of field of view shape building properties {ShapeName<str> : {Builder<str>        : BuildMethod<function>,
                                                                        PrimitiveType<str>  : OpenGLprimitive<int>,
                                                                          ...,
                                                                        Keyword<str>        : Kwargs<dict>}, }"""

allShapeBuildProps = dict(shapeBuildProps)
allShapeBuildProps.update(fovBuildProps)

OpenGL.GLUT.glutInit()  # required!

if '__main__' == __name__:
  """Module test
  """
  edgeGLprimitives = (pyglet.gl.GL_POINTS,
                      pyglet.gl.GL_LINES,
                      pyglet.gl.GL_LINE_LOOP, 
                      pyglet.gl.GL_LINE_STRIP)
                      
  faceGLprimitives = (pyglet.gl.GL_TRIANGLES, 
                      pyglet.gl.GL_TRIANGLE_STRIP, 
                      pyglet.gl.GL_TRIANGLE_FAN,
                      pyglet.gl.GL_QUADS,
                      pyglet.gl.GL_QUAD_STRIP,
                      pyglet.gl.GL_POLYGON)
                      
  for shape, props in shapeBuildProps.iteritems():
    assert callable(props[BUILDER])
    if props.has_key(EDGE):
      assert props[EDGE] in edgeGLprimitives
    if props.has_key(FACE):
      assert props[FACE] in faceGLprimitives
    if props.has_key(KWARGS):
      assert isinstance(props[KWARGS], dict)
