import signal  # TODO
from baseclasses import EntryBase
from collections import OrderedDict


class Message(EntryBase):
    # Static default variables
    default_cycle_time = None

    def __init__(self):
        EntryBase.__init__(self)
        self._can_id = 0
        self._dlc = 0
        self._signals = OrderedDict()
        self._cycle_time = None
        self._cycle_time_fast = None
        self._ct_note = ''  # Note for the cycle time
        self._short_name = '_'  # Short name for docx generation
        self._note = ''  # Comment goes under the title and this will be printed under the table of signals

    @property
    def ct_note(self):
        return self._ct_note

    @ct_note.setter
    def ct_note(self, new_note):
        if new_note is None:
            return
        self._ct_note = new_note

    @property
    def note(self):
        return self._note

    @note.setter
    def note(self, new_note):
        if new_note is None:
            return
        self._note = new_note

    @property
    def short_name(self):
        return self._short_name

    @short_name.setter
    def short_name(self, new_short):
        name_valid = self.valid_name_pattern.match(new_short)
        if name_valid is None:
            raise ValueError("invalid short name: '{}'! Only [a-zA-Z0-9_<>-] is allowed".format(new_short))
        self._short_name = str(new_short)

    @property
    def cycle_time(self):
        return self._cycle_time

    @cycle_time.setter
    def cycle_time(self, new_cycle_time):
        if new_cycle_time is None:
            return
        if new_cycle_time >= 0:
            self._cycle_time = new_cycle_time
        else:
            raise ValueError('cycle_time must be greater than zero')

    @property
    def cycle_time_fast(self):
        return self._cycle_time_fast

    @cycle_time_fast.setter
    def cycle_time_fast(self, new_cycle_time_fast):
        if new_cycle_time_fast is None:
            return
        if new_cycle_time_fast > 0:
            self._cycle_time_fast = new_cycle_time_fast
        else:
            raise ValueError('cycle_time_fast must be greater than zero')

    @property
    def can_id(self):
        return self._can_id

    @can_id.setter
    def can_id(self, new_id):
        if new_id < 1:
            raise ValueError('id must be greater than zero')
        self._can_id = new_id

    @property
    def dlc(self):
        return self._dlc

    @dlc.setter
    def dlc(self, new_dlc):
        if not (0 <= new_dlc <= 320):  # TODO high limit
            raise ValueError('dlc must be between 1 and ??? - {}'.format(self.name))
        self._dlc = new_dlc

    @property
    def signals(self):
        return self._signals

    @signals.setter
    def signals(self, new_signals):
        if type(new_signals) is not OrderedDict:
            raise TypeError("signals must be 'OrderedDict', not '{}'".format(type(new_signals)))
        for n, s in new_signals.iteritems():
            if type(s) is not signal.Signal:
                raise TypeError("signals must be 'Signal' instances, not '{}'".format(type(s)))
        self._signals = new_signals
