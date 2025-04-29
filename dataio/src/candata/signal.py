import re

import collections
from baseclasses import EntryBase
from collections import OrderedDict


class Signal(EntryBase):
    def __init__(self):
        EntryBase.__init__(self)
        self._mux = None
        self._startbit = 0
        self._length = 0
        self._byteorder = 0
        self._signed = False
        self._factor = 1
        self._offset = 0
        self._min = 0
        self._max = 0
        self._unit = u''
        self._values = Values(OrderedDict())
        self._notes = []

    @property
    def mux(self):
        return self._mux

    @mux.setter
    def mux(self, new_mux):
        # TODO check
        self._mux = new_mux

    @property
    def startbit(self):
        return self._startbit

    @startbit.setter
    def startbit(self, new_startbit):
        if new_startbit < 0:
            return
        self._startbit = new_startbit

    @property
    def length(self):
        return self._length

    @length.setter
    def length(self, new_length):
        if new_length < 0:
            return
        self._length = new_length

    @property
    def byteorder(self):
        return self._byteorder

    @byteorder.setter
    def byteorder(self, new_byteorder):
        if new_byteorder.lower() not in ('intel', 'motorola'):
            return
        self._byteorder = new_byteorder.lower()

    @property
    def type(self):
        return self._signed

    @type.setter
    def type(self, new_type):
        if new_type not in ('unsigned', 'signed', 'float', 'double'):
            raise ValueError("sigtype string must be one of ['unsigned','signed','float','double']"
                             ", not '{}'".format(new_type))
        self._signed = new_type

    @property
    def factor(self):
        return self._factor

    @factor.setter
    def factor(self, new_factor):
        self._factor = int(new_factor) if new_factor.is_integer() else new_factor

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, new_offset):
        self._offset = int(new_offset) if new_offset.is_integer() else new_offset

    @property
    def min(self):
        return self._min

    @min.setter
    def min(self, new_min):
        self._min = int(new_min) if new_min.is_integer() else new_min

    @property
    def max(self):
        return self._max

    @max.setter
    def max(self, new_max):
        self._max = int(new_max) if new_max.is_integer() else new_max

    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self, new_unit):
        if not isinstance(new_unit, basestring):
            raise TypeError("Signal.unit must be 'str' or 'Unicode', not '{}'".format(type(new_unit)))
        self._unit = new_unit

    @property
    def values(self):
        return self._values

    @values.setter
    def values(self, new_values):
        if type(new_values) is not Values:
            raise TypeError("Signal.values must a 'Values' instance, not '{}'".format(type(new_values)))
        self._values = new_values

    @property
    def notes(self):
        return self._notes

    @notes.setter
    def notes(self, new_notes):
        if not isinstance(new_notes, collections.Iterable):
            raise TypeError("notes must be an tuple of Notes, not '{}".format(type(new_notes)))
        for note in new_notes:
            if not isinstance(note, Note):
                raise TypeError("note must be an instance of Note, not '{}".format(type(note)))
            self._notes += [note]


class Values(OrderedDict):
    def __init__(self, dictionary):
        OrderedDict.__init__(self)
        if type(dictionary) is not OrderedDict:
            raise TypeError("dictionary must be 'OrderedDict', not '{}'".format(type(dictionary)))
        for key, value in dictionary.iteritems():
            if type(key) is not int or not isinstance(value, basestring):
                raise TypeError("Values must have key-value pairs of 'int':'str'/'unicode', "
                                "not '{}'-'{}'".format(type(key), type(value)))
            self[key] = value


class Note(object):
    def __init__(self, note, index=0, key=None, default=False):
        self._note = note  # The actual text
        self._index = index  # 0 means it is for the signal otherwise it is for a value
        self._key = key if key is not None else ''  # tag character
        self._default = default  # for writing database, default or custom note
        # During 'docx writing' it might receive a temporary key, but it should not be saved later on
        self._default_key = False if key == '' or key is None else True

    @property
    def note(self):
        return self._note

    @note.setter
    def note(self, note):
        self._note = note

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, index):
        self._index = index

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, key):
        self._key = key

    @property
    def default(self):
        return self._default

    @property
    def default_key(self):
        return self._default_key


class Multiplexor(object):
    multiplexor = 0
    multiplexed = 1
    mux_pattern_db = re.compile(r'multiplexed\s(?P<count>\d+)')
    mux_pattern_dbc = re.compile(r'm(?P<count>\d+)')

    def __init__(self, mux):
        self._type = -1
        self._count = -1
        if mux is None:
            return
        mux_str = str(mux)
        mux_str = mux_str.strip()
        # from dbc format
        if mux_str == 'M':
            self._type = self.multiplexor
            return
        mux_mo = self.mux_pattern_dbc.match(mux_str)
        if mux_mo is not None:
            self._type = self.multiplexed
            self._count = int(mux_mo.group('count'))
            return
        # from human fromat
        if mux_str == 'multiplexor':
            self._type = self.multiplexor
            return
        mux_mo = self.mux_pattern_db.match(mux_str)
        if mux_mo is not None:
            self._type = self.multiplexed
            self._count = int(mux_mo.group('count'))
            return
        raise ValueError('invalid Multiplexor initializer: "{}"'.format(mux_str))

    @property
    def human_format(self):
        if self._type == self.multiplexor:
            return 'multiplexor'
        if self._type == self.multiplexed:
            return 'multiplexed ' + str(self._count)
        return None

    @property
    def dbc_format(self):
        if self._type == self.multiplexor:
            return 'M '
        if self._type == self.multiplexed:
            return 'm' + str(self._count) + ' '
        return ''
