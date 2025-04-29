from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate
from reportlab.lib.pagesizes import A4, A3, landscape

def addPageTemplates(doc, event_detail_pagesize = None):
  x, y, width, height = doc.getGeom()
  ext_x, ext_y, ext_width, ext_height = doc.getExtGeom()
  #app_x, app_y, app_width, app_height = doc.getAppGeom()

  _showBoundary = 0

  portrait_frames = [
    Frame(ext_x, y, ext_width, height, id='FullPage'),
  ]

  landscape_frames = [
    Frame(ext_y,                  x + 0.9*width,     ext_height, 0.1*width, id='Title'),
    Frame(ext_y,                  x + 0.8*width,     ext_height, 0.1*width, id='Duartion'),
    Frame(ext_y,                  x + 0.5*width, 0.2*ext_height, 0.3*width, id='VideoNav'),
    Frame(ext_y,                  x,             0.2*ext_height, 0.5*width, id='TrackNav'),
    Frame(ext_y + 0.2*ext_height, x,             0.4*ext_height, 0.8*width, id='EgoPlot'),
    # Frame(ext_y + 1.6*ext_height, x,             0.4*ext_height, 0.8 * width, id='etrackchar'),
    Frame(ext_y + 0.6*ext_height, x,             0.4*ext_height, 0.8*width, id='TargetPlot'),
    Frame(ext_y + 1*ext_height,   x,             0.4*ext_height, 0.8*width, id='VehiclePlot'),
  ]

  comparing_frames = [
    Frame(ext_y,                  x + 0.9*width,     ext_height, 0.1*width, id='Title', showBoundary=_showBoundary),
    Frame(ext_y,                  x + 0.8*width, 0.6*ext_height, 0.1*width, id='Duartion', showBoundary=_showBoundary),
    Frame(ext_y,                  x + 0.5*width, 0.2*ext_height, 0.3*width, id='VideoNav', showBoundary=_showBoundary),
    Frame(ext_y,                  x,             0.2*ext_height, 0.5*width, id='TrackNav', showBoundary=_showBoundary),
    Frame(ext_y + 0.2*ext_height, x,             0.4*ext_height, 0.8*width, id='EgoPlot', showBoundary=_showBoundary),
    # Frame(ext_y + 1.6*ext_height,   x,             0.4*ext_height, 0.8*width, id='etrackchar', showBoundary=_showBoundary),
    Frame(ext_y + 0.6*ext_height, x,             0.4*ext_height, 0.9*width, id='TargetPlot', showBoundary=_showBoundary),
    Frame(ext_y + 1*ext_height,   x,             0.4*ext_height, 0.9*width, id='VehiclePlot', showBoundary=_showBoundary),
  ]

  landscape_table_frames = [
    Frame(y, x, height, width, id='FullPage'),
  ]
  if event_detail_pagesize == 'A3':
    doc.addPageTemplates([
      PageTemplate(id='Portrait', frames=portrait_frames,
                   onPage=doc.onPortraitPage, pagesize=A4),
      PageTemplate(id='Landscape', frames=landscape_frames,
                   onPage=doc.onLandscapePage, pagesize=landscape(A3)),
      PageTemplate(id='LandscapeTable', frames=landscape_table_frames,
                   onPage=doc.onLandscapePage, pagesize=landscape(A4)),
      PageTemplate(id='Comparing', frames=comparing_frames,
                   onPage=doc.onLandscapePage, pagesize=landscape(A4)),
    ])
  elif event_detail_pagesize == 'A3-TSR':
    landscape_frames = [
      Frame(ext_y, x + 0.9 * width, ext_height, 0.1 * width, id='Title'),
      Frame(ext_y, x + 0.8 * width, ext_height, 0.1 * width, id='Duartion'),
      Frame(ext_y + 20, x , 0.25 * ext_height, 0.8 * width, id='VideoNav'),
      Frame(ext_y + 0.39 * ext_height, x, 0.25 * ext_height, 0.8 * width, id='VideoNav'),

      Frame(ext_y + 0.66 * ext_height, x, 0.4 * ext_height, 0.8 * width, id='EgoPlot'),
      Frame(ext_y + 0.66 * ext_height, x - 0.4 * width, 0.4 * ext_height, 0.8 * width, id='etrackchar'),
      Frame(ext_y + 1.04 * ext_height, x, 0.4 * ext_height, 0.8 * width, id='TargetPlot'),
      Frame(ext_y + 1.04 * ext_height, x - 0.2 * width, 0.4 * ext_height, 0.8 * width, id='VehiclePlot'),
    ]

    comparing_frames = [
      Frame(ext_y, x + 0.9 * width, ext_height, 0.1 * width, id='Title', showBoundary=_showBoundary),
      Frame(ext_y, x + 0.8 * width, 0.6 * ext_height, 0.1 * width, id='Duartion', showBoundary=_showBoundary),
      Frame(ext_y+ 20, x , 0.25 * ext_height, 0.8 * width, id='VideoNav', showBoundary=_showBoundary),
      Frame(ext_y + 0.39 * ext_height, x, 0.25 * ext_height, 0.8 * width, id='VideoNav', showBoundary=_showBoundary),

      Frame(ext_y + 0.66 * ext_height, x, 0.4 * ext_height, 0.8 * width, id='EgoPlot', showBoundary=_showBoundary),
      Frame(ext_y + 0.66 * ext_height, x - 0.4 * width, 0.4 * ext_height, 0.9 * width, id='etrackchar', showBoundary=_showBoundary),
      Frame(ext_y + 1.04 * ext_height, x, 0.4 * ext_height, 0.9 * width, id='TargetPlot', showBoundary=_showBoundary),
      Frame(ext_y + 1.04 * ext_height, x - 0.2 * width, 0.4 * ext_height, 0.9 * width, id='VehiclePlot',
            showBoundary=_showBoundary),
    ]
    doc.addPageTemplates([
      PageTemplate(id = 'Portrait', frames = portrait_frames,
                   onPage = doc.onPortraitPage, pagesize = A4),
      PageTemplate(id = 'Landscape', frames = landscape_frames,
                   onPage = doc.onLandscapePage, pagesize = landscape(A3)),
      PageTemplate(id = 'LandscapeTable', frames = landscape_table_frames,
                   onPage = doc.onLandscapePage, pagesize = landscape(A4)),
      PageTemplate(id = 'Comparing', frames = comparing_frames,
                   onPage = doc.onLandscapePage, pagesize = landscape(A4)),
    ])
  else:
    doc.addPageTemplates([
      PageTemplate(id='Portrait', frames=portrait_frames,
                   onPage=doc.onPortraitPage, pagesize=A4),
      PageTemplate(id='Landscape', frames=landscape_frames,
                   onPage=doc.onLandscapePage, pagesize=landscape(A4)),
      PageTemplate(id='LandscapeTable', frames=landscape_table_frames,
                   onPage=doc.onLandscapePage, pagesize=landscape(A4)),
      PageTemplate(id='Comparing', frames=comparing_frames,
                   onPage=doc.onLandscapePage, pagesize=landscape(A4)),
    ])

  return
