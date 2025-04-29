from sqlalchemy.orm.exc import NoResultFound
from collections import OrderedDict
import json
import tables as tbl
import candata


class CanDatabaseReader(object):
    definition_type_lut = {'STRING': (candata.StringAttributeDefinition, str),
                           'INT': (candata.IntAttributeDefinition, int),
                           'HEX': (candata.HexAttributeDefinition, int),
                           'FLOAT': (candata.FloatAttributeDefinition, float),
                           'ENUM ': (candata.EnumAttributeDefinition, int)}
    attribute_type_lut = {'STRING': (candata.StringAttribute, str),
                          'INT': (candata.IntAttribute, int),
                          'HEX': (candata.HexAttribute, int),
                          'FLOAT': (candata.FloatAttribute, float),
                          'ENUM ': (candata.EnumAttribute, int)}
    owner_type_lut = {tbl.Signal: (tbl.AttributeSignal, tbl.SignalAttribute),
                      tbl.Message: (tbl.AttributeMessage, tbl.MessageAttribute),
                      tbl.Node: (tbl.AttributeNode, tbl.NodeAttribute),
                      tbl.Network: (tbl.AttributeNetwork, tbl.NetworkAttribute)}

    def __init__(self, logger):
        self.logger = logger

    def get_network(self, session, network_name):
        # network
        self.logger.info("Reading network: '{}'...".format(network_name))
        try:
            network_row, network = self._get_network(session, network_name)
        except NoResultFound:
            self.logger.error("'{}' not found in database".format(network_name))
            return None
        # attribute definitions
        _, nw_defs = self._get_network_attribute_definitions(session, network_row.id)
        _, nd_defs = self._get_node_attribute_definitions(session, network_row.id)
        _, mg_defs = self._get_message_attribute_definitions(session, network_row.id)
        _, sg_defs = self._get_signal_attribute_definitions(session, network_row.id)
        network.attribute_definitions['network'] = nw_defs
        network.attribute_definitions['node'] = nd_defs
        network.attribute_definitions['message'] = mg_defs
        network.attribute_definitions['signal'] = sg_defs
        # real stuff
        node_rows, network.nodes = self._get_nodes(session, network_row)
        message_rows, network.messages = self._get_messages(session, network_row)
        self._pair_nodes_messages(session, node_rows, network)
        self.logger.debug("'{}' successfully read".format(network_name))
        return network

    def _get_network(self, session, network_name):
        n = candata.Network()
        network = session.query(tbl.Network).filter(
            tbl.Network.name == network_name).one()
        attribute_rows, n.attributes = self._get_attributes(session, network, network.id)
        n.name = str(network.name)
        n.protocol = str(network.protocol)
        n.version_string = network.version_string
        n.comment = network.comment
        return network, n

    def list_networks(self, session):
        self.logger.info('Reading available networks...')
        networks = session.query(tbl.Network).all()
        network_names = [n.name for n in networks]
        merged_networks = session.query(tbl.Merged).all()
        merged_names = []
        for m in merged_networks:
            ids = [r[0] for r in session.query(tbl.MergedNetwork.networkid).filter(
                    tbl.MergedNetwork.mergedid == m.id).all()]
            names = [r[0] for r in session.query(tbl.Network.name).filter(
                    tbl.Network.id.in_(ids)).all()]
            merged_names.append([m.name, names])

        network_list = OrderedDict()
        network_list['networks'] = network_names
        network_list['merged'] = merged_names
        return network_list

    def list_customers(self, session):
        self.logger.info('Reading available customers...')
        customers = session.query(tbl.Customer).all()
        customers_names = [c.name for c in customers]
        return customers_names

    def list_customer_networks(self, session, customer_name):
        self.logger.info('Reading available customer networks...')
        customer, c = self._get_customer(session, customer_name)
        network_ids = [r[0] for r in session.query(tbl.CustomerNetworkNodeMessageSignal.networkid).filter(
            tbl.CustomerNetworkNodeMessageSignal.customerid == customer.id).distinct().all()]
        networks = session.query(tbl.Network).filter(
            tbl.Node.id.in_(network_ids)).all()
        network_names = [n.name for n in networks]
        return network_names

    def _get_nodes(self, session, network):
        node_ids = [r[0] for r in session.query(tbl.NetworkMessageNode.nodeid).filter(
            tbl.NetworkMessageNode.networkid == network.id).distinct().all()]
        return self._get_nodes_by_ids(session, network, node_ids)

    def _get_nodes_by_ids(self, session, network, node_ids):
        nodes = session.query(tbl.Node).filter(
            tbl.Node.id.in_(node_ids)).all()
        ns = OrderedDict()
        nodes = [n for n in nodes if n.id != 1]  # exclude Vector__XXX
        for node in nodes:
            n = candata.Node()
            attribute_rows, n.attributes = self._get_attributes(session, node, network.id)
            n.name = str(node.name)
            n.address = node.address
            n.comment = node.comment
            n.pretty_name = node.pretty_name
            evs = session.query(tbl.EnvVar).filter(
                tbl.EnvVar.nodeid == node.id).all()
            for ev in evs:
                e = candata.EnvVar()
                e.name = ev.name
                e.dtype = 0 if ev.dtype == 'Integer' else 1
                e.min = ev.min
                e.max = ev.max
                e.unit = ev.unit
                e.num1 = ev.num1
                e.num2 = ev.num2
                e.dummy_node = ev.dummy_node
                # read values
                evval_rows = session.query(tbl.EnvVarVal).filter(
                    tbl.EnvVarVal.envvarid == ev.id).order_by(tbl.EnvVarVal.order).all()
                evvals_dict = OrderedDict()
                for r in evval_rows:
                    evvals_dict[int(r.val)] = r.description
                e.values = candata.Values(evvals_dict)
                n.env_vars[e.name] = e
            ns[n.name] = n
        return nodes, ns

    def _get_messages(self, session, network):
        message_ids = [r[0] for r in session.query(tbl.NetworkMessageNode.messageid).filter(
            tbl.NetworkMessageNode.networkid == network.id).distinct().all()]
        return self._get_messages_by_ids(session, network, message_ids)

    def _get_messages_by_ids(self, session, network, message_ids, signal_ids=None):
        ms = OrderedDict()
        messages = []
        for message_id in message_ids:
            message = session.query(tbl.Message).filter(tbl.Message.id == message_id).one()
            m = candata.Message()
            if signal_ids is None:
                signal_rows, signals = self._get_signals(session, message, network)
            else:
                # Filter message signals
                s_ids = [r[0] for r in session.query(tbl.Signal.id).filter(tbl.Signal.messageid == message_id).filter(
                    tbl.Signal.id.in_(signal_ids)).all()]
                signal_rows, signals = self._get_signals_by_ids(session, network, s_ids)

            attribute_rows, m.attributes = self._get_attributes(session, message, network.id)
            m.name = str(message.name)
            m.pretty_name = message.pretty_name
            m.short_name = message.short_name
            m.can_id = message.can_id
            m.dlc = message.dlc
            m.cycle_time = message.cycle_time
            m.cycle_time_fast = message.cycle_time_fast
            m.ct_note = message.ct_note
            m.signals = signals
            m.comment = message.comment
            m.note = message.note
            messages.append(message)
            ms[m.name] = m
        return messages, ms

    def _get_signals(self, session, message, network):
        signal_ids = [r[0] for r in session.query(tbl.Signal.id).filter(tbl.Signal.messageid == message.id).all()]
        return self._get_signals_by_ids(session, network, signal_ids)

    def _get_signals_by_ids(self, session, network, signal_ids):
        signals = session.query(tbl.Signal).filter(
            tbl.Signal.id.in_(signal_ids)).all()
        ss = OrderedDict()
        for signal in signals:
            s = candata.Signal()
            vals = self._get_vals(session, signal)
            notes = self._get_notes(session, signal)
            attribute_rows, s.attributes = self._get_attributes(session, signal, network.id)
            s.name = str(signal.name)
            s.pretty_name = signal.pretty_name
            s.comment = signal.comment
            s.mux = candata.Multiplexor(signal.mux)
            s.startbit = signal.startbit
            s.length = signal.length
            s.byteorder = str(signal.byteorder)
            s.type = str(signal.type)
            s.factor = signal.factor
            s.offset = signal.offset
            s.min = signal.min
            s.max = signal.max
            s.unit = signal.unit
            s.values = vals
            s.notes = notes
            ss[s.name] = s
        return signals, ss

    def _get_vals(self, session, signal):
        val_rows = session.query(tbl.Val).filter(tbl.Val.signalid == signal.id).order_by(tbl.Val.order).all()
        vals_dict = OrderedDict()
        for r in val_rows:
            vals_dict[int(r.val)] = r.description
        return candata.Values(vals_dict)

    def _get_notes(self, session, signal):
        notes = []
        # Get Default Notes assigned to this signal
        default_notes = session.query(tbl.DefaultNoteSignal).filter(
            tbl.DefaultNoteSignal.signalid == signal.id).all()
        for dn in default_notes:
            n = session.query(tbl.DefaultNote).filter(
                tbl.DefaultNote.id == dn.noteid).one()
            notes += [candata.Note(n.note, dn.val_index, n.key, True)]  # It is a default note, hence the True
        # Get Custom Notes assigned to this signal
        note_rows = session.query(tbl.CustomNote).filter(tbl.CustomNote.signalid == signal.id).all()
        for nr in note_rows:
            notes += [candata.Note(nr.note, nr.val_index, nr.key)]
        return notes

    def get_customer(self, session, customer_name):
        # get customer
        self.logger.info("Reading customer: '{}'...".format(customer_name))
        try:
            customer_row, customer = self._get_customer(session, customer_name)
        except NoResultFound:
            self.logger.error("'{}' not found in database".format(customer_name))
            return None

        networks = OrderedDict()

        # get networks
        network_ids = [r[0] for r in session.query(tbl.CustomerNetworkNodeMessageSignal.networkid).filter(
            tbl.CustomerNetworkNodeMessageSignal.customerid == customer_row.id).distinct().all()]
        for n in network_ids:
            network = session.query(tbl.Network).filter(tbl.Network.id == n).one()
            network_row, network = self._get_network(session, network.name)

            # attribute definitions
            _, nw_defs = self._get_network_attribute_definitions(session, network_row.id)
            _, nd_defs = self._get_node_attribute_definitions(session, network_row.id)
            _, mg_defs = self._get_message_attribute_definitions(session, network_row.id)
            _, sg_defs = self._get_signal_attribute_definitions(session, network_row.id)
            network.attribute_definitions['network'] = nw_defs
            network.attribute_definitions['node'] = nd_defs
            network.attribute_definitions['message'] = mg_defs
            network.attribute_definitions['signal'] = sg_defs

            # get nodes for network
            node_ids = [r[0] for r in session.query(tbl.CustomerNetworkNodeMessageSignal.nodeid).filter(
                tbl.CustomerNetworkNodeMessageSignal.customerid == customer_row.id).distinct().all()]
            node_rows, network.nodes = self._get_nodes_by_ids(session, network_row, node_ids)
            # get messages and signals for network
            message_ids = [r[0] for r in session.query(tbl.CustomerNetworkNodeMessageSignal.messageid).filter(
                tbl.CustomerNetworkNodeMessageSignal.customerid == customer_row.id).distinct().all()]
            signal_ids = [r[0] for r in session.query(tbl.CustomerNetworkNodeMessageSignal.signalid).filter(
                tbl.CustomerNetworkNodeMessageSignal.customerid == customer_row.id).distinct().all()]
            _, network.messages = self._get_messages_by_ids(session, network_row, message_ids, signal_ids)
            # Pair nodes and messages

            self._pair_nodes_messages(session, node_rows, network)
            networks[network.name] = network
        customer.networks = networks
        # Customer networks are created
        return customer

    def _get_customer(self, session, customer_name):
        c = candata.Customer()
        customer = session.query(tbl.Customer).filter(
            tbl.Customer.name == customer_name).one()
        c.name = str(customer.name)
        return customer, c

    def get_network_from_customer(self, session, customer_name, network_name):
        c = self.get_customer(session, customer_name)
        for ni, n in c.networks.iteritems():
            if ni == network_name:
                return n
        return None

    def _get_network_attribute_definitions(self, session, network_id):
        nw_def_rows = session.query(tbl.NetworkAttribute).filter(
            tbl.NetworkAttribute.networkid == network_id).all()
        defs = self._get_attr_definitions(nw_def_rows)
        return nw_def_rows, defs

    def _get_node_attribute_definitions(self, session, network_id):
        nd_def_rows = session.query(tbl.NodeAttribute).filter(
            tbl.NodeAttribute.networkid == network_id).all()
        defs = self._get_attr_definitions(nd_def_rows)
        return nd_def_rows, defs

    def _get_message_attribute_definitions(self, session, network_id):
        mg_def_rows = session.query(tbl.MessageAttribute).filter(
            tbl.MessageAttribute.networkid == network_id).all()
        defs = self._get_attr_definitions(mg_def_rows)
        return mg_def_rows, defs

    def _get_signal_attribute_definitions(self, session, network_id):
        sg_def_rows = session.query(tbl.SignalAttribute).filter(
            tbl.SignalAttribute.networkid == network_id).all()
        defs = self._get_attr_definitions(sg_def_rows)
        return sg_def_rows, defs

    def _get_attr_definitions(self, def_rows):
        defs = OrderedDict()
        for def_row in def_rows:
            DefClass, default_type = self.definition_type_lut[def_row.type]
            d = DefClass()
            d.name = str(def_row.name)
            d.default = default_type(def_row.default_)
            d.entries = json.loads(def_row.entries)
            defs[d.name] = d
        return defs

    def _get_attributes(self, session, owner, network_id):
        JunctionTable, DefinitionTable = self.owner_type_lut[type(owner)]
        attr_rows = session.query(JunctionTable).filter(
                JunctionTable.ownerid==owner.id, JunctionTable.networkid==network_id).all()
        ats = {}
        for attr_row in attr_rows:
            def_row = session.query(DefinitionTable).filter(
                    DefinitionTable.id==attr_row.attributeid).one()
            AttrClass, value_type = self.attribute_type_lut[def_row.type]
            a = AttrClass()
            a.name = str(def_row.name)
            a.value = value_type(attr_row.val)
            ats[a.name] = a
        return attr_rows, ats

    def _pair_nodes_messages(self, session, nodes, network):
        mgs = network.messages
        for node in nodes:
            txs = session.query(tbl.NetworkMessageNode).filter(
                tbl.NetworkMessageNode.nodeid == node.id,
                tbl.NetworkMessageNode.dir == tbl.TX).all()
            rxs = session.query(tbl.NetworkMessageNode).filter(
                tbl.NetworkMessageNode.nodeid == node.id,
                tbl.NetworkMessageNode.dir == tbl.RX).all()
            tx_messages = []
            for tx in txs:
                m = session.query(tbl.Message).filter(
                    tbl.Message.id == tx.messageid).one()
                tx_messages.append(m)
            rx_messages = []
            for rx in rxs:
                m = session.query(tbl.Message).filter(
                    tbl.Message.id == rx.messageid).one()
                rx_messages.append(m)
            tx_messages = set([m for nm, m in mgs.iteritems() if nm in [r.name for r in tx_messages]])
            rx_messages = set([m for nm, m in mgs.iteritems() if nm in [r.name for r in rx_messages]])
            network.nodes[node.name].tx_messages = tx_messages
            network.nodes[node.name].rx_messages = rx_messages


