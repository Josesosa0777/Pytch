#!/usr/bin/env python
import measparser
import numpy

def colorByBitField(BitField, ValidColor, InvalidColor):
  valid = (BitField == 4095)
  valid = valid.reshape((valid.size, 1))
  valid = valid.repeat(3, axis = 1)
  Color = numpy.where(valid, ValidColor, InvalidColor)
  return Color

def colorByVelocity(EgoVelocity, RelativeVelocity, OngoingColor, StationaryColor,
                    OncomingColor, VelEps=1.0):
  """
  Ongoing:    ]-inf,    VelEps]
  Stationary: ]-VelEps, VelEps[
  Moving:     [ VelEps, inf[

  :Parameters:
    EgoVelocity : `numpy.ndarray`
    RelativeVelocity : `numpy.ndarray`
    OngoingColor : sequence
      [R, G, B]
    StationaryColor : sequence
      [R, G, B]
    OncomingColor : sequence
      [R, G, B]
  :KeyWords:
    VelEps : float
      Absolute velocity limit, which under the target is classified as
      stationary, default is 1.0
  :ReturnType: `numpy.ndarray`
  :Return: N by 3 matrix where N is the size of `EgoVelocity` and `TargetVelocity`
  """
  # numpy.reshape(A, (-1, 3)) was used earlier
  with numpy.errstate(invalid='ignore'):
    Stationary = numpy.abs(RelativeVelocity + EgoVelocity) < VelEps
  Stationary = Stationary.reshape((Stationary.size, 1))
  Stationary = Stationary.repeat(3, axis=1)
  Color = numpy.where(Stationary, StationaryColor, OngoingColor)
  with numpy.errstate(invalid='ignore'):
    Ongoing = RelativeVelocity <= -(EgoVelocity + VelEps)
  Ongoing = Ongoing.reshape((Ongoing.size, 1))
  Ongoing = Ongoing.repeat(3, axis=1)
  Color = numpy.where(Ongoing, OncomingColor, Color)
  return Color

def colorByMovingState(MovingState,OngoingColor, StationaryColor,OncomingColor):
  with numpy.errstate(invalid = 'ignore'):
    Stationary = ((MovingState == 0 ) | (MovingState==1))
  Stationary = Stationary.reshape((Stationary.size, 1))
  Stationary = Stationary.repeat(3, axis = 1)
  Color = numpy.where(Stationary, StationaryColor, OngoingColor)
  with numpy.errstate(invalid='ignore'):
    Ongoing = (MovingState == 7)
  Ongoing = Ongoing.reshape((Ongoing.size, 1))
  Ongoing = Ongoing.repeat(3, axis=1)
  Color = numpy.where(Ongoing, OncomingColor, Color)
  return Color

def initObject(Reference, Keys, **Values):
  """
  Init a  dictionary from the `Keys` of the `Reference`,
  and fill them with zero or value from `Values`,
  if the key from `Keys` is present in `Values`.
  
  :Parameters:
    Reference : dict
      {Key<str>: `numpy.ndarray`}
    Keys : list
      [Key<str>]
  :KeyValues:
    Values : dict
      {Key<str>: Value<int>}
  :ReturnType: dict
  :Return: {Key<str>: `numpy.ndarray`}
  """
  Object = {}
  for Key in Keys:
    try:
      Fill = Values[Key]
    except KeyError:
      Fill = 0
    Value = Reference[Key]
    Value = Value.copy()
    Value.fill(Fill)
    Object[Key] = Value
  return Object 


def initObjects(Names, Reference, Keys, **Values):
  """
  Init objects with initObject(`Reference`, `Keys`, `Values`)
  and collect them into a dictionary under the keys from `Names`.

  :Parameters:
    Names : list
      [Name<str>]
    Reference : dict
      {Key<str>: `numpy.ndarray`}
    Keys : list
      [Key<str>]
  :KeyValues:
    Values : dict
      {Key<str>: Value<int>}
  :ReturnType: dict
  :Return: {Name<str>: {Key<str>: `numpy.ndarray`}}
  """
  Objects = {}
  for Name in Names:
    Objects[Name] = initObject(Reference, Keys, **Values)
  return Objects


def listObjects(Objects):
  """
  Create a list from the dictionries of `Objects`,
  and add a 'label' key to that dictionaries 
  with their original keys in `Objects` as value.
  
  :Parameters:
    Objects : dict
      {label<str>: Object<dict>}
  :ReturnType: list
  :Return: [Object<dict>]
  """
  ReGrouped = []
  for Label, Object in Objects.iteritems():
    Object['label'] = Label
    ReGrouped.append(Object)
  return ReGrouped


def copyObject(Input, Output, Mask, Keys, **Values):
  """
  Copy the Key values from `Input` into `Output` along `Mask`.
  Value fom `Values` will be set into `Output` 
  if Key present in `Values`.
  If the value in `Input` is two dimensional, 
  than the mask will be repeated 3 times along the second axis.

  :Parameters:
    Input : dict
      {Key<str>: `numpy.ndarray`}
    Output : dict
      {Key<str>: `numpy.ndarray`}
    Mask : `numpy.ndarray`
    Keys : list
      [Key<str>]
  :KeyValues:
    Values : dict
      {Key<str>: Value<int>}
  """
  for Key in Keys:
    if len(Input[Key].shape) == 2:
      CopyMask = Mask.reshape(Mask.size, 1)
      CopyMask = CopyMask.repeat(3, axis=1)
    else:
      CopyMask = Mask
      
    try:
      Value = Values[Key]
    except KeyError:
      Value = Input[Key][CopyMask]

    Output[Key][CopyMask] = Value
  return


def _rescaleObject(Object, Index):
  Rescaled = {}
  for Key, Value in Object.iteritems():
    if isinstance(Value, numpy.ndarray):
      Value = Value[Index]
    Rescaled[Key] = Value
  return Rescaled


def rescaleObject(Object, Time, ScaleTime):
  if measparser.signalproc.isSameTime(Time, ScaleTime):
    return Object
  Index = measparser.signalproc.mapTimeToScaleTime(Time, ScaleTime)
  Object = _rescaleObject(Object, Index)
  return Object


def rescaleObjects(Objects, Time, ScaleTime):
  if measparser.signalproc.isSameTime(Time, ScaleTime):
    return Objects
  Index = measparser.signalproc.mapTimeToScaleTime(Time, ScaleTime)
  Rescaled = [_rescaleObject(Object, Index) for Object in Objects]
  return Rescaled

def getObjects(Objects, **Filters):
  Filtered = [Object for Object in Objects
              if all([Key in Object and Object[Key] == Value 
                      for Key, Value in Filters.iteritems()])]
  return Filtered

