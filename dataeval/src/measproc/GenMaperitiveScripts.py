import os
import tempfile

OSM_API_TEMPLATES =\
    {'overpass-api.de':
     ('http://overpass-api.de/api/interpreter?'
      'data=(node(%(min_lat)f,%(min_lon)f,%(max_lat)f,%(max_lon)f);'
      'rel(bn)->.x;way(%(min_lat)f,%(min_lon)f,%(max_lat)f,%(max_lon)f);'
      'node(w)->.x;rel(bw););out;'),
     'overpass.osm.rambler.ru':
     ('http://overpass.osm.rambler.ru/cgi/interpreter?'
      'data=(node(%(min_lat)f,%(min_lon)f,%(max_lat)f,%(max_lon)f);'
      'rel(bn)->.x;way(%(min_lat)f,%(min_lon)f,%(max_lat)f,%(max_lon)f);'
      'node(w)->.x;rel(bw););out;'),
     'open.mapquestapi.com':
     ('http://open.mapquestapi.com/xapi/api/0.6/*'
      '[bbox=%(min_lon)f,%(min_lat)f,%(max_lon)f,%(max_lat)f]')}
# NOTE: Overpass API does not save the map bounding box to OSM XML files.


def createMaperitiveScript4OSM(osm_dir, map_bbox,
                               url_select='open.mapquestapi.com',
                               osm_name_template='map_osm_data'):
  """
  Creates script file to be run with Maperitive to download OSM XML datafile
  for a specific region form the URL specified in `url_select`. The output is
  the location of this script file.
  """
  osm_name = map_bbox.to_file_name(prefix=osm_name_template, suffix='.osm')
  osm_loc = os.path.join(osm_dir, osm_name)
  scripts_dir = tempfile.mkdtemp(prefix='Temp_OSM_Scripts_', dir=osm_dir)
  fd, download_script_path = tempfile.mkstemp(suffix='.mrc',
                                              prefix='temp_osm_script_',
                                              dir=scripts_dir,
                                              text=True)
  script = os.fdopen(fd, 'w')
  script_line = "clear-map\n"
  script.write(script_line)
  selected_url = OSM_API_TEMPLATES[url_select]
  osm_query = map_bbox.to_osm_mrc_line(selected_url)
  script_line = "download-file url=\"%s\" file=%s\n"
  script_line = script_line % (osm_query, osm_loc)
  script.write(script_line)
  script.close()
  return download_script_path

def createMaperitiveScript4MapDb(temp_dir, map_bbox,
                                 min_zoom_level=7, max_zoom_level=16,
                                 osm_2_use=None,
                                 mbtiles_name_template='tmp_map_db'):
  """
  Creates script file to be run with Maperitive to download map tile database
  for a specific region and zoom level range. The output is the location of
  this script file.
  """
  mbtiles_name = map_bbox.to_file_name(prefix=mbtiles_name_template,
                                       suffix='.mbtiles')
  mbtiles_loc = os.path.join(temp_dir, mbtiles_name)
  fd, download_script_path = tempfile.mkstemp(suffix='.mrc',
                                              prefix='temp_mbtiles_script_',
                                              dir=temp_dir,
                                              text=True)
  script = os.fdopen(fd, 'w')
  script_line = "clear-map\n"
  script.write(script_line)
  if osm_2_use:
    script_line = "load-source file=%s\n" % osm_2_use
    script.write(script_line)
  else:
    script_line = "add-web-map\n"
    script.write(script_line)
  script_line = "generate-mbtiles bounds=%s" % map_bbox.to_mbtiles_mrc_line()
  script_line += " minzoom=%d maxzoom=%d file=%s\n" % (min_zoom_level,
                                                       max_zoom_level,
                                                       mbtiles_loc)
  script.write(script_line)
  script.close()
  return download_script_path

def createMaperitiveExitScript(temp_dir):
  fd, exit_script_path = tempfile.mkstemp(suffix='.mrc',
                                          prefix='temp_exit_script_',
                                          dir=temp_dir,
                                          text=True)
  script = os.fdopen(fd, 'w')
  script_line = "exit"
  script.write(script_line)
  script.close()
  return exit_script_path
