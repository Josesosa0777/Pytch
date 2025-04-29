from candatabase.tables import Customer
from message import Message
from node import Node
from baseclasses import EntryBase, AttributeDefinitionBase
from collections import OrderedDict


class Network(EntryBase):
    def __init__(self):
        EntryBase.__init__(self)
        self._attribute_definitions = {'network': OrderedDict(),
                                       'node': OrderedDict(),
                                       'message': OrderedDict(),
                                       'signal': OrderedDict()}
        self._messages = OrderedDict()
        self._nodes = OrderedDict()
        self._version = ''

    @property
    def attribute_definitions(self):
        return self._attribute_definitions

    @attribute_definitions.setter
    def attribute_definitions(self, new_defs):
        for name, d in new_defs.iteritems():
            if not isinstance(d, AttributeDefinitionBase):
                raise TypeError("attribute definitions must be 'AttributeDefinitionBase' "
                                "instances, not '{}'".format(type(d)))
        self._attribute_definitions = new_defs

    @property
    def messages(self):
        return self._messages

    @messages.setter
    def messages(self, new_messages):
        if type(new_messages) is not OrderedDict:
            raise TypeError("Network.messages must be 'OrderedDict', not '{}'".format(
                    type(new_messages)))
        for n, m in new_messages.iteritems():
            if type(m) is not Message:
                raise TypeError("messages must be 'Message' instances, not '{}'".format(type(m)))
        self._messages = new_messages

    @property
    def nodes(self):
        return self._nodes

    @nodes.setter
    def nodes(self, new_nodes):
        if type(new_nodes) is not OrderedDict:
            raise TypeError("Network.nodes must be 'OrderedDict', not '{}'".format(type(new_nodes)))
        for _, a in new_nodes.iteritems():
            if type(a) is not Node:
                raise TypeError("nodes must be 'Node' instances, not '{}'".format(type(a)))
        self._nodes = new_nodes

    @property
    def version_string(self):
        return self._version

    @version_string.setter
    def version_string(self, new_string):
        self._version = str(new_string)

    def _dump_json(self):
        # TODO recursively call json.dumps, then return json string
        return 'printing of Network objects not supported yet'

    def __str__(self):
        return self._dump_json()
