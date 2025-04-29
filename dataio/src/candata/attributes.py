from baseclasses import AttributeBase, AttributeDefinitionBase


class StringAttribute(AttributeBase):
    def __init__(self):
        AttributeBase.__init__(self, str)


class IntAttribute(AttributeBase):
    def __init__(self):
        AttributeBase.__init__(self, int)


class HexAttribute(AttributeBase):
    def __init__(self):
        AttributeBase.__init__(self, int)


class FloatAttribute(AttributeBase):
    def __init__(self):
        AttributeBase.__init__(self, float)


class EnumAttribute(AttributeBase):
    def __init__(self):
        AttributeBase.__init__(self, int)


class StringAttributeDefinition(AttributeDefinitionBase):
    def __init__(self):
        AttributeDefinitionBase.__init__(self, str)
        self._default = ''

    @property
    def attr_class(self):
        return StringAttribute

    @property
    def type(self):
        return 'STRING'

    @property
    def entries_str(self):
        return ''

    @property
    def entries_json(self):
        return '""'


class NumericAttributeDefinition(AttributeDefinitionBase):
    def __init__(self, dtype):
        AttributeDefinitionBase.__init__(self, int)
        self._default = 0
        self._min = 0
        self._max = 0
        if dtype not in (int, float):
            raise TypeError(
                "NumericAttributeDefinition dtype must be 'int' or 'float', not '{}'".format(dtype))
        self._dtype = dtype

    @property
    def entries_str(self):
        return '{min} {max}'.format(min=self._min, max=self._max)

    @property
    def entries_json(self):
        return '{"min": ' + str(self._min) + ', "max": ' + str(self._max) + '}'

    @property
    def min(self):
        return self._min

    @min.setter
    def min(self, new_min):
        self._min = self._dtype(new_min)

    @property
    def max(self):
        return self._max

    @max.setter
    def max(self, new_max):
        self._max = self._dtype(new_max)


class IntAttributeDefinition(NumericAttributeDefinition):
    def __init__(self):
        NumericAttributeDefinition.__init__(self, int)

    @property
    def attr_class(self):
        return IntAttribute

    @property
    def type(self):
        return 'INT'


class HexAttributeDefinition(NumericAttributeDefinition):
    def __init__(self):
        NumericAttributeDefinition.__init__(self, int)

    @property
    def attr_class(self):
        return HexAttribute

    @property
    def type(self):
        return 'HEX'


class FloatAttributeDefinition(NumericAttributeDefinition):
    def __init__(self):
        NumericAttributeDefinition.__init__(self, float)

    @property
    def attr_class(self):
        return FloatAttribute

    @property
    def type(self):
        return 'FLOAT'


class EnumAttributeDefinition(AttributeDefinitionBase):
    def __init__(self):
        AttributeDefinitionBase.__init__(self, int)
        self._default = 0
        self._entries = []

    @property
    def attr_class(self):
        return EnumAttribute

    @property
    def type(self):
        return 'ENUM '

    @property
    def entries_str(self):
        return ','.join(['"' + v + '"' for v in self.entries])

    @property
    def entries_json(self):
        return '[{values}]'.format(values=self.entries_str)

    @property
    def entries(self):
        return self._entries

    @entries.setter
    def entries(self, new_entries):
        new_entries = [v.strip().strip('"') for v in new_entries]
        self._entries = new_entries

    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, new_default):
        if type(new_default) is int:
            self._default = new_default
        elif type(new_default) is str:
            self._default = self._entries.index(new_default)
        else:
            raise TypeError("default must be 'int' or 'str', not '{}'".format(type(new_default)))

    @property
    def default_str(self):
        return '"' + self._entries[self._default] + '"'
