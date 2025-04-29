from reportlab.platypus.flowables import Image

from datalab.tygra import Paragraph

class Client(object):
  def __init__(self, client_name, windgeom, width, height,
               unit, kind='direct', **kwargs):
    """
    Initializes Client (usually a wrapper around cNavigator instance).
    
    Interpretation of 'kind' parameter
    (code copied from reportlab.platypus.flowables):
    
    if kind in ['direct','absolute']:
      self.drawWidth = width or self.imageWidth
      self.drawHeight = height or self.imageHeight
    elif kind in ['percentage','%']:
      self.drawWidth = self.imageWidth*width*0.01
      self.drawHeight = self.imageHeight*height*0.01
    elif kind in ['bound','proportional']:
      factor = min(float(width)/self.imageWidth,float(height)/self.imageHeight)
      self.drawWidth = self.imageWidth*factor
      self.drawHeight = self.imageHeight*factor
    """
    self.client_name = client_name
    self.windgeom = windgeom
    conv_size = lambda size: size*unit if size is not None else None
    self.size = dict(width=conv_size(width), height=conv_size(height), kind=kind)
    self.mod_kwargs = kwargs
    return

  def __call__(self, sync, module_name):
    try:
      client = sync.getClient(module_name)
    except ValueError:
      data = Paragraph("('%s' not available)" %self.client_name)
    else:
      self.mod_client(client, **self.mod_kwargs)
      client.setWindowGeometry(self.windgeom)
      data = Image(client.copyContentToBuffer(), **self.size)
    return data

  def mod_client(self, client):
    return

class TrackNavigator(Client):
  def mod_client(self, client):
    #client.stateLabel = "NONE"
    client.showPosition = True
    for _, obj in client.iterActualObjects(client.Objects):
      if isinstance(obj.Label, basestring):
        obj.Label = obj.Label.replace("FLR20", "FLR21")
      else:  # label type can also be numpy.ndarray
        for i, l in enumerate(obj.Label):
          obj.Label[i] = l.replace("FLR20", "FLR21")
    return

class VideoNavigator(Client):
  pass


class TableNavigator(Client):
  pass

class PlotNavigator(Client):
  pass