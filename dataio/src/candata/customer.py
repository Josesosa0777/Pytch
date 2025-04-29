from collections import OrderedDict


from signal import Signal
from network import Network
from candata.baseclasses import EntryBase


class Customer(EntryBase):
    def __init__(self):
        EntryBase.__init__(self)
        self._networks = OrderedDict()  # custom network with only the required node,message,signal

    @property
    def networks(self):
        return self._networks

    @networks.setter
    def networks(self, new_networks):
        if type(new_networks) is not OrderedDict:
            raise TypeError("Customer.networks must be 'OrderedDict', not '{}'".format(type(new_networks)))
        for _, n in new_networks.iteritems():
            if type(n) is not Network:
                raise TypeError("networks must be 'Network' instances, not '{}'".format(type(n)))
        self._networks = new_networks
