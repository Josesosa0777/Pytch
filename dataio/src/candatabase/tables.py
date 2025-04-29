import sqlalchemy.exc
import warnings
from sqlalchemy import Column, ForeignKey, UniqueConstraint, Integer, String, Float, Unicode
from sqlalchemy.ext.declarative import declarative_base, declared_attr


Base = declarative_base()
warnings.simplefilter('ignore', sqlalchemy.exc.SAWarning)
TX = 0
RX = 1


# data tables -----------------------------------------------------------------
class Merged(Base):
    __tablename__ = 'merged'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    protocol = Column(String, nullable=False, default='ExtendedCAN')
    version_string = Column(Unicode)
    comment = Column(Unicode)


class Network(Base):
    __tablename__ = 'networks'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    protocol = Column(String, nullable=False, default='ExtendedCAN')
    version_string = Column(Unicode)
    comment = Column(Unicode)


class Node(Base):
    __tablename__ = 'nodes'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    pretty_name = Column(String)  # pretty name
    address = Column(Integer)
    comment = Column(Unicode)
    __table_args__ = (UniqueConstraint('name', 'address'),)


class EnvVar(Base):
    __tablename__ = 'envvars'
    id = Column(Integer, primary_key=True)
    nodeid = Column(Integer, ForeignKey('nodes.id'))
    name = Column(String, nullable=False)
    dtype = Column(String)
    min = Column(Float)
    max = Column(Float)
    unit = Column(Unicode)
    num1 = Column(Integer)
    num2 = Column(Integer)
    dummy_node = Column(String)


class EnvVarVal(Base):
    __tablename__ = 'envvarvals'
    envvarid = Column(Integer, ForeignKey('envvars.id'), primary_key=True)
    val = Column(Integer, primary_key=True)
    order = Column(Integer, nullable=False)
    description = Column(Unicode, nullable=False)


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    can_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    short_name = Column(String)  # short name
    pretty_name = Column(String)  # pretty name
    dlc = Column(Integer, nullable=False, default=8)
    cycle_time = Column(Integer)
    cycle_time_fast = Column(Integer)
    ct_note = Column(Unicode)  # cycle time note
    comment = Column(Unicode)
    note = Column(Unicode)
    __table_args__ = (UniqueConstraint('can_id', 'name'),)


class Signal(Base):
    __tablename__ = 'signals'
    id = Column(Integer, primary_key=True)
    messageid = Column(Integer, ForeignKey('messages.id'))
    name = Column(String, nullable=False)
    pretty_name = Column(String)
    mux = Column(String)
    startbit = Column(Integer, nullable=False)
    length = Column(Integer, nullable=False)
    byteorder = Column(String, nullable=False, default='intel')
    type = Column(String, nullable=False, default='unsigned')
    factor = Column(Float, nullable=False, default=1)
    offset = Column(Float, nullable=False, default=0)
    min = Column(Float, nullable=False, default=0)
    max = Column(Float, nullable=False, default=0)
    unit = Column(Unicode, nullable=False, default='')
    comment = Column(Unicode)


class Val(Base):
    __tablename__ = 'vals'
    signalid = Column(Integer, ForeignKey('signals.id'), primary_key=True)
    val = Column(Integer, primary_key=True)
    order = Column(Integer, nullable=False)
    description = Column(Unicode, nullable=False)


class CustomNote(Base):
    __tablename__ = 'customnotes'
    signalid = Column(Integer, ForeignKey('signals.id'), primary_key=True)
    key = Column(Unicode)
    val_index = Column(Integer, primary_key=True, default=0)
    note = Column(Unicode, primary_key=True)


class DefaultNote(Base):
    __tablename__ = 'defaultnotes'
    id = Column(Integer, primary_key=True)
    key = Column(Unicode, primary_key=True)
    note = Column(Unicode, nullable=False)


class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode, nullable=False)
    # TODO add more property


class AttributeBase(object):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
    entries = Column(Unicode)  # INT: min/max, ENUM: array of values, STRING: empty array
    default_ = Column(Unicode)  # as string for all types
    __table_args__ = (UniqueConstraint('name', 'networkid'),)

    @declared_attr
    def networkid(self):
        return Column(Integer, ForeignKey('networks.id'))


class NetworkAttribute(AttributeBase, Base):
    __tablename__ = 'networkattributes'


class NodeAttribute(AttributeBase, Base):
    __tablename__ = 'nodeattributes'


class MessageAttribute(AttributeBase, Base):
    __tablename__ = 'messageattributes'


class SignalAttribute(AttributeBase, Base):
    __tablename__ = 'signalattributes'


# junction tables -------------------------------------------------------------
class MergedNetwork(Base):
    __tablename__ = 'merged_network'
    mergedid = Column(Integer, ForeignKey('merged.id'), primary_key=True)
    networkid = Column(Integer, ForeignKey('networks.id'), primary_key=True)


class NetworkMessageNode(Base):
    __tablename__ = 'network_message_node'
    networkid = Column(Integer, ForeignKey('networks.id'), primary_key=True)
    messageid = Column(Integer, ForeignKey('messages.id'), primary_key=True)
    nodeid = Column(Integer, ForeignKey('nodes.id'), primary_key=True)
    dir = Column(Integer, primary_key=True)


class AttributeNetwork(Base):
    __tablename__ = 'attribute_network'
    ownerid = Column(Integer, ForeignKey('networks.id'), primary_key=True)
    attributeid = Column(Integer, ForeignKey('networkattributes.id') , primary_key=True)
    val = Column(Unicode, nullable=False)  # networks not specified here have the default value
    networkid = Column(Integer, ForeignKey('networks.id'), primary_key=True)


class AttributeNode(Base):
    __tablename__ = 'attribute_node'
    ownerid = Column(Integer, ForeignKey('nodes.id'), primary_key=True)
    attributeid = Column(Integer, ForeignKey('nodeattributes.id'), primary_key=True)
    val = Column(Unicode, nullable=False)  # nodes not specified here have the default value
    networkid = Column(Integer, ForeignKey('networks.id'), primary_key=True)


class AttributeMessage(Base):
    __tablename__ = 'attribute_message'
    ownerid = Column(Integer, ForeignKey('messages.id'), primary_key=True)
    attributeid = Column(Integer, ForeignKey('messageattributes.id'), primary_key=True)
    val = Column(Unicode, nullable=False)  # messages not specified here have the default value
    networkid = Column(Integer, ForeignKey('networks.id'), primary_key=True)


class AttributeSignal(Base):
    __tablename__ = 'attribute_signal'
    ownerid = Column(Integer, ForeignKey('signals.id'), primary_key=True)
    attributeid = Column(Integer, ForeignKey('signalattributes.id'), primary_key=True)
    val = Column(Unicode, nullable=False)  # signals not specified here have the default value
    networkid = Column(Integer, ForeignKey('networks.id'), primary_key=True)


class CustomerNetworkNodeMessageSignal(Base):
    __tablename__ = 'customer_network_node_message_signal'
    customerid = Column(Integer, ForeignKey('customers.id'), primary_key=True)
    networkid = Column(Integer, ForeignKey('networks.id'), primary_key=True)
    nodeid = Column(Integer, ForeignKey('nodes.id'), primary_key=True)
    messageid = Column(Integer, ForeignKey('messages.id'), primary_key=True)
    signalid = Column(Integer, ForeignKey('signals.id'), primary_key=True)


class DefaultNoteSignal(Base):
    __tablename__ = 'defaultnote_signal'
    noteid = Column(Integer, ForeignKey('defaultnotes.id'), primary_key=True)
    signalid = Column(Integer, ForeignKey('signals.id'), primary_key=True)
    val_index = Column(Integer, primary_key=True, default=0)
