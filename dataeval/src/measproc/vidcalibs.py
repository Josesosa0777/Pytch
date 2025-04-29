import os
import stat
import logging

from sqlalchemy import (ForeignKey, Column, String, Integer,
                        create_engine, Float)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker

from datavis.calibration_data import cCalibrationData
from measparser.filenameparser import FileNameParser


Base = declarative_base()

class CalibData(Base):
  __tablename__ = 'calibdata'
  __table_args__ = {'sqlite_autoincrement': True}
  id = Column(Integer, primary_key=True)
  camerax = Column(Float)
  cameray = Column(Float)
  cameraz = Column(Float)
  caliwidth = Column(Integer)
  caliheight = Column(Integer)
  fov = Column(Float)
  looktox = Column(Float)
  looktoy = Column(Float)
  upx = Column(Float)

class Vehicles(Base):
  __tablename__ = 'vehicles'
  __table_args__ = {'sqlite_autoincrement': True}
  id = Column(Integer, primary_key=True)
  short_name = Column(String)

class Cameras(Base):
  __tablename__ = 'cameras'
  __table_args__ = {'sqlite_autoincrement': True}
  id = Column(Integer, primary_key=True)
  short_name = Column(String)

class Starts(Base):
  __tablename__ = 'starts'
  __table_args__ = {'sqlite_autoincrement': True}
  id = Column(Integer, primary_key=True)
  time = Column(String)

class Calibs(Base):
  __tablename__ = 'calibs'
  __table_args__ = {'sqlite_autoincrement': True}
  id = Column(Integer, primary_key=True)
  vehicle_id = Column(Integer, ForeignKey('vehicles.id'))
  start_id = Column(Integer, ForeignKey('starts.id'))
  camera_id = Column(Integer, ForeignKey('cameras.id'))
  calibdata_id = Column(Integer, ForeignKey('calibdata.id'))

  vehicle = relationship('Vehicles', backref=backref('calibs'))
  start = relationship('Starts', backref=backref('calibs'))
  camera = relationship('Cameras', backref=backref('calibs'))
  calibdata = relationship('CalibData', backref=backref('calibs'))

class Video2Calib(Base):
  __tablename__ = 'video2calib'
  __table_args__ = {'sqlite_autoincrement': True}
  id = Column(Integer, primary_key=True)
  basename = Column(String)
  origin = Column(String)
  video_start_time = Column(Float)
  calib_id = Column(Integer, ForeignKey('calibs.id'))

  calibs = relationship('Calibs', backref=backref('video2calib'))


class VidCalibs(object):
  DB_Path = r'sqlite:///'
  def __init__(self, DbName, SetWritable=True):
    self.logger = logging.getLogger()

    if SetWritable and not os.access(DbName, os.W_OK):
      os.chmod(DbName, stat.S_IWRITE)
      self.logger.warning('Calibration database set to writable (read-only flag cleared)')

    self.DbName = DbName
    Path = self.DB_Path + DbName
    self.engine = create_engine(Path, echo=False)
    session = sessionmaker(bind=self.engine)
    self.session = session()
    Base.metadata.create_all(self.engine)
    return

  def get_calib(self, path):
    filename = os.path.basename(path)

    selected = self.get_calib_by_file(filename)
    if selected is not None:
      self.logger.debug("Calibration found for the video file explicitly: %d" %
                        selected.id)
      return selected

    parsed_data = self.parse_measurement(filename)
    if parsed_data is not None:
      veh, cam, date = parsed_data
      selected = self.get_calib_by_prop(veh, cam, date)
      if selected is not None:
        self.logger.debug("Calibration found by file name parsing: %d" %
                          selected.id)
        return selected

    selected = self.get_calib_by_dir_struct(path)
    if selected is not None:
      self.logger.debug("Calibration found by directory structure: %d" %
                        selected.id)
      return selected

    selected = self.get_latest_calib()
    if selected is not None:
      self.logger.debug("No calibration found; loading latest: %d" %
                        selected.id)
      return selected

    self.logger.debug("No calibration found; loading default")
    return None

  def get_calibration(self, path):
    selected = self.get_calib(path)

    if selected is None: return None

    calibration_data = {}
    names = cCalibrationData.get_value_names()
    for name in names:
      calibration_data[name] = getattr(selected, name)
    calib = cCalibrationData(**calibration_data)
    return calib

  def get_calibdata_by_id(self, id):
    query = self.session.query(CalibData).filter(CalibData.id == id)
    return query.first()

  def get_all_calibdata(self):
    query = self.session.query(CalibData).\
                         join(CalibData.calibs).\
                         filter(Calibs.calibdata)
    return query.all()

  def get_calib_by_file(self, filename):
    query = self.session.query(CalibData).\
                       join(CalibData.calibs).\
                       join(Calibs.video2calib).\
                       filter(Video2Calib.basename == filename)
    return query.first()

  def get_calib_by_dir_struct(self, path):
    path = os.path.normpath(path)  # to handle mixed paths
    new_path = os.path.dirname(path)
    selected = None
    while new_path != path and selected == None:
      # TODO: normpath(Video2Calib.origin)
      query = self.session.query(CalibData).\
                 join(CalibData.calibs).\
                 join(Calibs.video2calib).\
                 join(Calibs.start).\
                 filter(Video2Calib.origin.startswith(path)).\
                 order_by(Starts.time.desc())
      selected = query.first()
      path = new_path
      new_path = os.path.dirname(path)
    return selected

  def get_calib_by_prop(self, vehicle, camera, date):
    query = self.session.query(CalibData).\
                join(CalibData.calibs).\
                join(Calibs.vehicle).\
                join(Calibs.camera).\
                join(Calibs.start).\
                filter(Vehicles.short_name == vehicle).\
                filter(Cameras.short_name == camera).\
                filter(Starts.time <= date).\
                order_by(Starts.time.desc())
    return query.first()

  def get_latest_calib(self):
    query = self.session.query(CalibData).\
                join(CalibData.calibs).\
                join(Calibs.start).\
                order_by(Starts.time.desc())
    return query.first()

  @staticmethod
  def parse_measurement(measurement):
    logger = logging.getLogger()
    fn = FileNameParser( os.path.basename(measurement) )
    if fn is None:
      logger.debug("File name parser raw result: None")
      return None
    logger.debug("File name parser raw result: " +
                 ", ".join("%s: '%s'" % (prop, fn.group(prop)) for prop in
                           ('vehicle', 'device', 'date', 'description')))
    vehicle = fn.vehicle
    date = fn.date_underscore
    camera = fn.device or ''
    if vehicle is None or date is None:
      return None
    logger.debug("File name parsing successful: "
      "vehicle: '%s', camera: '%s', date: '%s'" % (vehicle, camera, date))
    return vehicle, camera, date

  def add_calib(self, calib, path, vehicle=None, camera=None, date=None,
                videostarttime=0.0):
    basename = os.path.basename(path)
    parsed_data = self.parse_measurement(basename)
    if parsed_data is not None:
      vehicle = parsed_data[0] if vehicle is None else vehicle
      camera = parsed_data[1] if camera is None else camera
      date = parsed_data[2] if date is None else date

    assert vehicle is not None, "Vehicle wasn't set"
    assert camera is not None, "Camera wasn't set"
    assert date is not None, "Date wasn't set"

    calib_data = CalibData()

    names = calib.get_value_names()
    for name in names:
      value = getattr(calib, name)
      setattr(calib_data, name, value)

    self.session.add(calib_data)
    self.session.flush()

    query = self.session.query(Video2Calib).\
                         filter(Video2Calib.basename == basename)
    video2calib = query.first()
    if not video2calib:
      video2calib = Video2Calib()
      self.session.add(video2calib)

    dirname = os.path.dirname(path)
    video2calib.basename = basename
    video2calib.origin = dirname
    video2calib.video_start_time = videostarttime

    query = self.session.query(Vehicles).\
                       filter(Vehicles.short_name == vehicle)
    veh = query.first()
    if not veh:
      veh = Vehicles()
      self.session.add(veh)
    veh.short_name = vehicle
    self.session.flush()

    query = self.session.query(Cameras).filter(Cameras.short_name == camera)
    cam = query.first()
    if not cam:
      cam = Cameras()
      self.session.add(cam)
    cam.short_name = camera
    self.session.flush()

    query = self.session.query(Starts).filter(Starts.time == date)
    start = query.first()
    if not start:
      start = Starts()
      self.session.add(start)
    start.time = date
    self.session.flush()

    query = self.session.query(Calibs).filter(Calibs.vehicle_id == veh.id).\
                                       filter(Calibs.start_id == start.id).\
                                       filter(Calibs.camera_id == cam.id)
    calib = query.first()
    if not calib:
      calib = Calibs()
      calib.vehicle_id = veh.id
      calib.start_id = start.id
      calib.camera_id = cam.id
      self.session.add(calib)
    calib.calibdata_id = calib_data.id
    self.session.flush()
    video2calib.calib_id = calib.id

    self.session.commit()
    return

  def save(self):
    self.session.close()
    return

  def close(self):
    self.save()
    self.engine.dispose()
    return

  def get_vehicle_name(self, calibdata_id):
    query = self.session.query(Vehicles.short_name).\
                            join(Vehicles.calibs).\
                            filter(Calibs.calibdata_id == calibdata_id)
    return self.unpack_one_element_query(query)

  def get_camera_name(self, calibdata_id):
    query = self.session.query(Cameras.short_name).\
                            join(Cameras.calibs).\
                            filter(Calibs.calibdata_id == calibdata_id)
    return self.unpack_one_element_query(query)

  def get_start(self, calibdata_id):
    query = self.session.query(Starts.time).\
                            join(Starts.calibs).\
                            filter(Calibs.calibdata_id == calibdata_id)
    return self.unpack_one_element_query(query)

  def unpack_one_element_query(self, query):
    result = query.first()
    return None if result is None else result[0]

if __name__ == '__main__':
  from datavis.calibration_data import cCalibrationData as Calib

  from aebs.par.vidcalibs import default
  vidcalibs = VidCalibs('vidcalibs.db')
  dummy_avi = r'C:\foo\bar\dummy.avi'
  for prop, calib in default.iteritems():
    veh, date = prop
    try:
      int(date)
    except ValueError:
      date = '2010-01-01_04-00-00'
    else:
      date = '20%s-%s-%s_04-00-00' %(date[:2], date[2:4], date[4:])
    vidcalibs.add_calib(calib, dummy_avi, vehicle=veh, date=date, camera='')


  #calib = Calib( 0.24, 2.3,   0.0,  640, 480, 36.2,    0.249, -0.262,  0.0)
  #
  #vidcalibs.get_calib(r'C:\KBData\measurement\H566_2013-03-21_16-40-21')
  #vidcalibs.add_calib(calib, r'C:\KBData\measurement\2014-02-04-10-00-22.avi')
