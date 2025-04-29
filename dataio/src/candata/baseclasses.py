import re


class Base(object):
    valid_name_pattern = re.compile(r'[a-zA-Z0-9_<>-]+')

    def __init__(self):
        self._name = '_'
        self._pretty_name = '_'

    @property
    def pretty_name(self):
        return self._pretty_name

    @pretty_name.setter
    def pretty_name(self, new_pretty_name):
        name_valid = self.valid_name_pattern.match(new_pretty_name)
        if name_valid is None:
            raise ValueError("invalid pretty name: '{}'! Only [a-zA-Z0-9_<>-] is allowed".format(new_pretty_name))
        self._pretty_name = str(new_pretty_name)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        name_valid = self.valid_name_pattern.match(new_name)
        if name_valid is None:
            raise ValueError("invalid name: '{}'! Only [a-zA-Z0-9_<>-] is allowed".format(new_name))
        self._name = str(new_name)


class AttributeBase(Base):
    def __init__(self, dtype):
        Base.__init__(self)
        if dtype not in (str, int, float):
            raise ValueError("Attribute type must be 'str', 'int' or 'float', not '{}'".format(dtype))
        self._dtype = dtype
        self._value = None

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, raw_value):
        new_value = self._dtype(raw_value)
        self._value = new_value

    @property
    def value_str(self):
        if self._dtype is str:
            return '"' + self._value + '"'
        return str(self._value)


class AttributeDefinitionBase(Base):
    def __init__(self, dtype):
        Base.__init__(self)
        self._default = None
        if dtype not in (str, int):
            raise ValueError("AttributeDefinition type must be 'str' or 'int', not '{}'".format(dtype))
        self._dtype = dtype

    @property
    def default(self):
        return self._default

    @default.setter
    def default(self, new_default):
        self._default = self._dtype(new_default)

    @property
    def default_str(self):
        if type(self._default) is str:
            return '"' + self._default + '"'
        return str(self._default)


class EntryBase(Base):
    def __init__(self):
        Base.__init__(self)
        self._attributes = {}
        self._comment = ''

    @property
    def attributes(self):
        return self._attributes

    @attributes.setter
    def attributes(self, new_attrs):
        for name, a in new_attrs.iteritems():
            if not isinstance(a, AttributeBase):
                raise TypeError("attribute must be 'AttributeBase' instance, not '{}'".format(type(a)))
        self._attributes = new_attrs

    @property
    def comment(self):
        return self._comment

    @comment.setter
    def comment(self, new_comment):
        if not isinstance(new_comment, basestring):
            raise TypeError("comment type must be 'str' or 'unicode, not '{}'".format(
                    type(new_comment)))
        self._comment = new_comment
