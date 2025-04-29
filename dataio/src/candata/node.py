from message import Message
from signal import Values
from baseclasses import EntryBase
from collections import OrderedDict


class Node(EntryBase):
    def __init__(self):
        EntryBase.__init__(self)
        self._rx_messages = set()
        self._tx_messages = set()
        self._env_vars = OrderedDict()
        self._address = None

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, new_address):
        if new_address is None:
            return
        if 0 <= new_address < 255:
            self._address = new_address
        else:
            print new_address
            raise ValueError('address must be equal or greater than 0 and less then 255')

    @property
    def tx_messages(self):
        return self._tx_messages

    @tx_messages.setter
    def tx_messages(self, new_messages):
        if type(new_messages) is not set:
            raise TypeError("tx_messages must be 'set', not '{}'".format(type(new_messages)))
        for m in new_messages:
            if type(m) is not Message:
                raise TypeError("tx messages must be 'Message' instances, not '{}'".format(type(m)))
        self._tx_messages = new_messages

    @property
    def rx_messages(self):
        return self._rx_messages

    @rx_messages.setter
    def rx_messages(self, new_messsages):
        if type(new_messsages) is not set:
            raise TypeError("rx_messages must be 'set', not '{}'".format(type(new_messsages)))
        for m in new_messsages:
            if type(m) is not Message:
                raise TypeError("rx messages must be 'Message' instances, not '{}'".format(type(m)))
        self._rx_messages = new_messsages

    @property
    def env_vars(self):
        return self._env_vars

    @env_vars.setter
    def env_vars(self, new_env_vars):
        if type(new_env_vars) is not OrderedDict:
            raise TypeError("env_vars must be 'OrderedDict', not '{}'".format(type(new_env_vars)))
        for e in new_env_vars:
            if type(e) is not EnvVar:
                raise TypeError("env vars must be 'EnvVar', not '{}'".format(type(e)))
        self._env_vars = new_env_vars


class EnvVar(EntryBase):
    def __init__(self):
        EntryBase.__init__(self)
        self._dtype = 0
        self._min = 0
        self._max = 0
        self._unit = u''
        self._num1 = 0
        self._num2 = 0
        self._dummy_node = 'DUMMY_NODE_ETC'
        self._values = Values(OrderedDict())

    @property
    def dtype(self):
        return self._dtype

    @dtype.setter
    def dtype(self, new_dtype):
        if new_dtype not in (0,1):
            raise ValueError('allowed dtypes 0 (int) or 1 (float)')
        self._dtype = new_dtype

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
        if not isinstance(new_unit, basestring):  # allows both str and Unicode
            raise TypeError("Signal.unit must be 'str' or 'Unicode', not '{}'".format(type(new_unit)))
        self._unit = new_unit

    @property
    def num1(self):
        return self._num1

    @num1.setter
    def num1(self, new_num1):
        if type(new_num1) is not int:
            raise TypeError("Signal.num1 must be 'int', not '{}".format(type(new_num1)))
        self._num1 = new_num1

    @property
    def num2(self):
        return self._num2

    @num2.setter
    def num2(self, new_num2):
        if type(new_num2) is not int:
            raise TypeError("Signal.num2 must be 'int', not '{}".format(type(new_num2)))
        self._num2 = new_num2

    @property
    def dummy_node(self):
        return self._dummy_node

    @dummy_node.setter
    def dummy_node(self, new_dummy_node):
        if not isinstance(new_dummy_node, basestring):
            raise TypeError("Signal.dummy_node must be 'str' or 'Unicode', not '{}".format(type(new_dummy_node)))
        self._dummy_node = new_dummy_node


    @property
    def values(self):
        return self._values

    @values.setter
    def values(self, new_values):
        if type(new_values) is not Values:
            raise TypeError("EnvVar.values must be 'Values' instances, not '{}'".format(type(new_values)))
        self._values = new_values

