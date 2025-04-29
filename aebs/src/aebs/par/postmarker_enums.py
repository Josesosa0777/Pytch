from pyutils.enum import enum


TIME_VALS = ('UNKNOWN','Day',	'Twilight',	'Night')

ROAD_TYPE_VALS = ('UNKNOWN','City',	'Country Road',	'Motorway')

VEHICLE_HEADLAMP_VALS =	('UNKNOWN','Halogen',	'LED',	'Xenon',	'Laser')

WEATHER_CONDITIONS_VALS = ('UNKNOWN','Clear',	'Cloudy',	'Rain',	'Snow fall',	'Fog',	'Hail',	'Heavy Sun Glaring')

ROAD_EDGE_VALS = ('UNKNOWN','Flat', 'Continuous Elevated', 'Discrete Elevated', 'Trench or Cliff', 'Curbstone')

STREET_OBJECTS_VALS = ('UNKNOWN','Bad road conditions', 'Fishbone lane marker', 'Zigzag lane  marker', 'Street island')

OBJECT_ON_SIDE_OF_ROAD_VALS = ('UNKNOWN','Tunnel', 'Under Bridge')

TRAFFIC_EVENT_VALS = ('UNKNOWN','Construction', 'Traffic jam', 'Country Border', 'Overtaking scenario', 'Roundabout',
         'Interesting traffic situation')

MOVING_OBJECTS_VALS = ('UNKNOWN','Crossing scenarios', 'Children', 'Unusual shaped vehicle', 'Vehicle transport', 'Tram', 'Unusual taillights',
         'Hazard lights', 'Animals', 'Motorbike', 'Bicycle')

COUNTRY_CODE_VALS = ('UNKNOWN','DEU', 'AUT', 'BEL', 'HUN', 'LUX', 'NLD', 'USA', 'CAN', 'KOR', 'CHN', 'JPN', 'GBR', 'IRL', 'FRA', 'ITA', 'ESP',
         'PRT', 'MLT', 'CYP', 'CZE', 'POL', 'ROU', 'BGR', 'SWE')


TIME = dict((name, n) for n, name in enumerate(TIME_VALS))
ROAD_TYPE = dict((name, n) for n, name in enumerate(ROAD_TYPE_VALS))
VEHICLE_HEADLAMP = dict((name, n) for n, name in enumerate(VEHICLE_HEADLAMP_VALS))
WEATHER_CONDITIONS = dict((name, n) for n, name in enumerate(WEATHER_CONDITIONS_VALS))
ROAD_EDGE = dict((name, n) for n, name in enumerate(ROAD_EDGE_VALS))
STREET_OBJECTS = dict((name, n) for n, name in enumerate(STREET_OBJECTS_VALS))
OBJECT_ON_SIDE_OF_ROAD = dict((name, n) for n, name in enumerate(OBJECT_ON_SIDE_OF_ROAD_VALS))
TRAFFIC_EVENT = dict((name, n) for n, name in enumerate(TRAFFIC_EVENT_VALS))
MOVING_OBJECTS = dict((name, n) for n, name in enumerate(MOVING_OBJECTS_VALS))
COUNTRY_CODE = dict((name, n) for n, name in enumerate(COUNTRY_CODE_VALS))