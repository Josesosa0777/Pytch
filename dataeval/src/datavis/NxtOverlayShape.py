from OpenGL import GL

import NxtOpenGLutil
  
class Shapes(object):
  """ Manages the lifecycle of the OpenGL shapes
  """

  def __init__(self, shapeBuildProps):
    self._firstList = None
    """:type: int
    The place of the first shape display list"""
    self._dispLists = {}
    """:type: dict
    Container of the shape display lists: {shapeName<string> : {drawType<str> : listID<int>, }, }"""
    
    self._firstList, self._dispLists = self._createDispLists(shapeBuildProps)
    pass
  
  def draw(self, shapeName, shapeType):
    """ Prepares the specified shape for OpenGL rendering
    :Parameters:
      shapeName : str
        Shape name
      shapeType : str
        Shape type
    """
    listID = self._dispLists[shapeName][shapeType]
    GL.glCallList(listID)
    
  def has_shape(self, shapeName):
    """ Checks if the specified shape name exists
    :Parameters:
      shapeName : str
        Shape name
    :Return: 
      True if the shape name in parameter exists, otherwise False
    """
    return shapeName in self._dispLists
      
  def closeResources(self):
    """ Cleans up OpenGL resources
    """
    self._deleteDispLists()
    pass
    
  def _createDispLists(self, buildProps):
    """Initialize OpenGL display lists for efficient shape storage
    :Parameters:
      buildProps : dict
        Container of properties necessary for shape building
    :ReturnType: (int, dict)
    :Return: 
      firstList: int
        ID of the first display list
      displayLists: dict
        Container of the built display lists: {shapeName<string> : {drawType<str> : listID<int>, }, }
    """
    DISP_LISTS_LEN = len(buildProps)
    firstList = GL.glGenLists(DISP_LISTS_LEN)
    currentList = firstList    
    displayLists = {}
    
    for shapeName, shapeProps in buildProps.iteritems():
      displayLists[shapeName] = {}
      primitives  = {}
      kwargs      = {}
      buildMethod = None
      for propName, value in shapeProps.iteritems():
        if NxtOpenGLutil.BUILDER == propName:
          buildMethod = value
        elif NxtOpenGLutil.KWARGS == propName:
          kwargs = value
        else:
          primitives[propName] = value
          
      for drawType, value in primitives.iteritems():
        buildMethod(currentList, value, **kwargs)
        displayLists[shapeName][drawType] = currentList
        currentList += 1
      
    return firstList, displayLists
  
  
  def _deleteDispLists(self):
    """Free memory allocated for OpenGL display lists
    """
    if self._firstList is not None:
      # print 'DELETE DISP LISTS'
      GL.glDeleteLists(self._firstList, len(self._dispLists))
      self._firstList = None
      self._dispLists = {}
    pass
