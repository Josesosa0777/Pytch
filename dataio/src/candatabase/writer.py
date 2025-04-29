from sqlalchemy.exc import IntegrityError
import tables as tbl
from sqlalchemy.orm.exc import NoResultFound
from utils import rollback_on_exception


class CanDatabaseWriter(object):
    attr_type_lut = {'network': tbl.NetworkAttribute,
                     'node': tbl.NodeAttribute,
                     'message': tbl.MessageAttribute,
                     'signal': tbl.SignalAttribute}
    owner_type_lut = {tbl.Network: ('network', tbl.AttributeNetwork),
                      tbl.Node: ('node', tbl.AttributeNode),
                      tbl.Message: ('message', tbl.AttributeMessage),
                      tbl.Signal: ('signal', tbl.AttributeSignal)}

    def __init__(self, logger):
        self._attribute_definitions = {'network': [], 'node': [], 'message': [], 'signal': []}
        self.logger = logger

    @rollback_on_exception
    def add_network(self, session, network, nid=None):
        self.logger.info("Writing network: '{}'...".format(network.name))
        try:
            self._add_network(session, network, nw_id=nid)
            self._add_attribute_definitions(session, network.attribute_definitions)
            self._add_attributes(session, network.attributes, self.network)
            self._add_nodes(session, network.nodes)
            self._add_messages(session, network.messages)
            self._build_relations(session, network.nodes)
            session.commit()
        except IntegrityError as e:
            self.logger.error("Adding '{}' to database failed: \n{}".format(network.name, e))
            session.rollback()
        self.logger.debug("'{}' successfully written to database".format(network.name))

    def _add_network(self, session, network, nw_id):
        nw_row = session.query(tbl.Network).filter(
            tbl.Network.name == network.name).one_or_none()
        if nw_row is None:
            nw_row = tbl.Network(name=network.name,
                                 protocol=network.protocol,
                                 version_string=network.version_string,
                                 comment=network.comment)
            if nw_id is not None:
                reserved = session.query(tbl.Network).all()
                if nw_id in [r.id for r in reserved]:
                    raise ValueError('The given network id "{}" is already reserved'.format(nw_id))
                nw_row.id = nw_id
            session.add(nw_row)
            session.flush()
        self.network = nw_row

    def add_customer(self, session, customer):
        self.logger.info("Writing customer: '{}'...".format(customer.name))
        try:
            self._add_customer(session, customer)
            session.commit()
        except IntegrityError as e:
            self.logger.error("Adding '{}' to database failed: \n{}".format(customer.name, e))
            session.rollback()
        self.logger.debug("'{}' successfully written to database".format(customer.name))

    def _add_customer(self, session, customer):
        c_row = session.query(tbl.Customer).filter(
            tbl.Customer.name == customer.name).one_or_none()
        if c_row is None:
            c_row = tbl.Customer(name=customer.name)
            session.add(c_row)
            session.flush()
        # Build Customer relations
        for nwi, nw in customer.networks.iteritems():  # Every network
            network = session.query(tbl.Network).filter(
                tbl.Network.name == nwi).one_or_none()
            self._add_network_to_customer(session, network, customer.name)

    @rollback_on_exception
    def add_network_to_customer(self, session, network, customer_name):
        self.logger.info("Adding network to customer: '{}'...".format(network.name))
        try:
            try:
                customer = session.query(tbl.Customer).filter(
                    tbl.Customer.name == customer_name).one()
            except NoResultFound:
                self.logger.error('Customer not found in database'.format(customer_name))
                return 0
            self._add_network_to_customer(session, network, customer)
            session.commit()
        except IntegrityError as e:
            self.logger.error("Adding '{}' to {} failed: \n{}".format(network.name, customer_name,e))
            session.rollback()
        self.logger.debug("'{}' successfully added to {}".format(network.name, customer_name))

    def _add_network_to_customer(self, session, network, customer):
        n_row = session.query(tbl.Network).filter(
            tbl.Network.name == network.name).one_or_none()
        for ni, n in network.nodes.iteritems():  # Every node
            node = session.query(tbl.Node).filter(
                tbl.Node.name == ni,
                tbl.Node.address == n.address).one_or_none()
            for m in n.tx_messages:  # Every message (TR)
                message = session.query(tbl.Message).filter(
                    tbl.Message.name == m.name).one_or_none()

                for si, s in m.signals.iteritems():  # Every signal
                    signal = session.query(tbl.Signal).filter(
                        tbl.Signal.name == si).one_or_none()
                    # Check if already present
                    row = session.query(tbl.CustomerNetworkNodeMessageSignal).filter(
                        tbl.CustomerNetworkNodeMessageSignal.customerid == customer.id,
                        tbl.CustomerNetworkNodeMessageSignal.networkid == n_row.id,
                        tbl.CustomerNetworkNodeMessageSignal.nodeid == node.id,
                        tbl.CustomerNetworkNodeMessageSignal.messageid == message.id,
                        tbl.CustomerNetworkNodeMessageSignal.signalid == signal.id).one_or_none()
                    if row is None:
                        row = tbl.CustomerNetworkNodeMessageSignal(customerid=customer.id, networkid=n_row.id,
                                                                   nodeid=node.id, messageid=message.id,
                                                                   signalid=signal.id)
                    session.add(row)
                    session.flush()
            for m in n.rx_messages:  # Every message (RX)
                message = session.query(tbl.Message).filter(
                    tbl.Message.name == m.name).one_or_none()

                for si, s in m.signals.iteritems():  # Every signal
                    signal = session.query(tbl.Signal).filter(
                        tbl.Signal.name == si).one_or_none()
                    # Check if already present
                    row = session.query(tbl.CustomerNetworkNodeMessageSignal).filter(
                        tbl.CustomerNetworkNodeMessageSignal.customerid == customer.id,
                        tbl.CustomerNetworkNodeMessageSignal.networkid == n_row.id,
                        tbl.CustomerNetworkNodeMessageSignal.nodeid == node.id,
                        tbl.CustomerNetworkNodeMessageSignal.messageid == message.id,
                        tbl.CustomerNetworkNodeMessageSignal.signalid == signal.id).one_or_none()
                    if row is None:
                        row = tbl.CustomerNetworkNodeMessageSignal(customerid=customer.id, networkid=n_row.id,
                                                                   nodeid=node.id, messageid=message.id,
                                                                   signalid=signal.id)
                    session.add(row)
                    session.flush()

    def _add_nodes(self, session, nodes):
        nd_rows = [session.query(tbl.Node).filter(tbl.Node.id == 1).one()]  # Vector__XXX node
        for node in nodes.itervalues():
            if node.name == 'Vector__XXX':
                continue
            nd_address = node.address
            nd_comment = node.comment
            nd_row = session.query(tbl.Node).filter(
                tbl.Node.name == node.name,
                tbl.Node.address == nd_address).one_or_none()
            if nd_row is None:
                nd_row = tbl.Node(name=node.name, address=nd_address, comment=nd_comment, pretty_name=node.pretty_name)
                session.add(nd_row)
                session.flush()
            self._add_attributes(session, node.attributes, nd_row)
            # add environment variables
            for ev in node.env_vars.itervalues():
                ev_row = session.query(tbl.EnvVar).filter(
                    tbl.EnvVar.name == ev.name,
                    tbl.EnvVar.nodeid == nd_row.id).one_or_none()
                if ev_row is None:
                    dtype = 'Integer' if ev.dtype == 0 else 'Float'
                    ev_row = tbl.EnvVar(nodeid=nd_row.id, name=ev.name, dtype=dtype, min=ev.min,
                                        max=ev.max, unit=ev.unit, num1=ev.num1, num2=ev.num2,
                                        dummy_node=ev.dummy_node)
                    session.add(ev_row)
                    session.flush()
                # add values
                order = 1
                for val, description in ev.values.iteritems():
                    envvarval_row = session.query(tbl.EnvVarVal).filter(
                        tbl.EnvVarVal.envvarid == ev_row.id,
                        tbl.EnvVarVal.val == val).one_or_none()
                    if envvarval_row is None:
                        envvarval_row = tbl.EnvVarVal(envvarid=ev_row.id, val=val, order=order,
                                          description=description)
                        session.add(envvarval_row)
                        session.flush()
                        order += 1
            nd_rows.append(nd_row)
        self.nodes = nd_rows

    def _add_messages(self, session, messages):
        mg_rows = []
        for message in messages.itervalues():
            mg_row = session.query(tbl.Message).filter(
                tbl.Message.can_id == message.can_id,
                tbl.Message.name == message.name).one_or_none()
            if mg_row is None:
                mg_row = tbl.Message(can_id=message.can_id, name=message.name,
                                     dlc=message.dlc, comment=message.comment, cycle_time=message.cycle_time,
                                     cycle_time_fast=message.cycle_time_fast, pretty_name=message.pretty_name,
                                     short_name=message.short_name, note=message.note,
                                     ct_note=message.ct_note)

                session.add(mg_row)
                session.flush()
            self._add_attributes(session, message.attributes, mg_row)
            self._add_signals(session, message.signals, mg_row.id)
            mg_rows.append(mg_row)
        self.messages = mg_rows

    def _add_signals(self, session, signals, message_id):
        sg_rows = []
        for signal in signals.itervalues():
            sg_row = session.query(tbl.Signal).filter(
                tbl.Signal.messageid == message_id,
                tbl.Signal.name == signal.name).one_or_none()
                    # tables.Signal.startbit==signal.startbit
                    # tables.Signal.lenght==signal.length
            if sg_row is None:
                sg_row = tbl.Signal(messageid=message_id, name=signal.name, startbit=signal.startbit,
                                    length=signal.length, factor=signal.factor, offset=signal.offset,
                                    byteorder=signal.byteorder, type=signal.type, min=signal.min,
                                    max=signal.max, unit=signal.unit, comment=signal.comment,
                                    mux=signal.mux.human_format, pretty_name=signal.pretty_name)
                session.add(sg_row)
                session.flush()
            self._add_vals(session, signal.values, sg_row.id)
            self._add_notes(session, signal.notes, sg_row.id)
            self._add_attributes(session, signal.attributes, sg_row)
            sg_rows.append(sg_row)
        self.signals = sg_rows

    def _add_vals(self, session, vals, signal_id):
        val_rows = []
        order = 1
        for val, description in vals.iteritems():
            val_row = session.query(tbl.Val).filter(
                tbl.Val.signalid == signal_id,
                tbl.Val.val == val).one_or_none()
            if val_row is None:
                val_row = tbl.Val(signalid=signal_id, val=val, order=order, description=description)
                session.add(val_row)
                session.flush()
                order += 1
            val_rows.append(val_row)
        self.vals = val_rows

    def _add_notes(self, session, notes, signal_id):
        def_note_rows = []  # default notes
        cust_note_rows = []  # custom notes

        for n in notes:
            # Add default notes
            if n.default:
                # Get note if exist already
                def_note_row = session.query(tbl.DefaultNote).filter(
                    tbl.DefaultNote.key == n.key).one_or_none()
                # Create default note if needed
                if def_note_row is None:
                    def_note_row = tbl.DefaultNote(key=n.key, note=n.note)
                    session.add(def_note_row)
                    session.flush()
                def_note_rows.append(def_note_row)
                # Create joint
                note_signal_row = tbl.DefaultNoteSignal(noteid=def_note_row.id, signalid=signal_id, val_index=n.index)
                session.add(note_signal_row)
                session.flush()
            # Add custom notes
            else:
                cust_note_row = session.query(tbl.CustomNote).filter(
                    tbl.CustomNote.signalid == signal_id,
                    tbl.CustomNote.note == n.note,
                    tbl.CustomNote.val_index == n.index).one_or_none()
                if cust_note_row is None:
                    key = '' if n.default_key else n.key  # only save it if it was already the note's key
                    cust_note_row = tbl.CustomNote(signalid=signal_id, key=key, val_index=n.index, note=n.note)
                    session.add(cust_note_row)
                    session.flush()
                cust_note_rows.append(cust_note_row)

        self.def_notes = def_note_rows
        self.cust_notes = cust_note_rows

    def _add_attribute_definitions(self, session, definitions):
        for attr_type, attr_defs in definitions.iteritems():  # for network, node, message signal
            AttributeClass = self.attr_type_lut[attr_type]
            ad_rows = []
            for definition in attr_defs.itervalues():
                ad_row = session.query(AttributeClass).filter(
                        AttributeClass.name==definition.name).filter(
                        AttributeClass.networkid==self.network.id).one_or_none()
                if ad_row is None:
                    ad_row = AttributeClass(name=definition.name, networkid=self.network.id,
                                            type=definition.type, entries=definition.entries_json,
                                            default_=definition.default)
                    session.add(ad_row)
                    session.flush()
                ad_rows.append(ad_row)
            self._attribute_definitions[attr_type] = ad_rows

    def _add_attributes(self, session, attributes, owner):
        type_, AttributeJunction = self.owner_type_lut[type(owner)]
        attribute_rows = self._attribute_definitions[type_]
        j_rows = []
        def_ids_names = [(d.id, d.name) for d in attribute_rows]
        for a in attributes.itervalues():
            attribute_ids = [b[0] for b in def_ids_names if b[1] == a.name]
            if len(attribute_ids) != 1:
                self.logger.warning("did not find '{}' in [{}]".format(
                        a.name, [b.name for b in attribute_rows]))
                return
            attribute_id = attribute_ids[0]
            j_row = session.query(AttributeJunction).filter(
                    AttributeJunction.ownerid==owner.id,
                    AttributeJunction.attributeid==attribute_id,
                    AttributeJunction.val==a.value,
                    AttributeJunction.networkid==self.network.id).one_or_none()
            if j_row is None:
                j_row = AttributeJunction(ownerid=owner.id,
                                          attributeid=attribute_id,
                                          val=a.value,
                                          networkid=self.network.id)
                session.add(j_row)
                session.flush()
            j_rows.append(j_row)
        return j_rows

    def _build_relations(self, session, nodes):
        for node in self.nodes:
            for message_canid in nodes[node.name].tx_messages:
                mg_ids = [m.id for m in self.messages if m.can_id == message_canid]
                if len(mg_ids) > 1:
                    self.logger.warning('Skipping message {}, more found'.format(message_canid))
                    continue
                if len(mg_ids) < 1:
                    self.logger.warning('Skipping message {}, none found'.format(message_canid))
                    continue
                mg_id = mg_ids[0]
                nmn_row = session.query(tbl.NetworkMessageNode).filter(
                    tbl.NetworkMessageNode.networkid == self.network.id,
                    tbl.NetworkMessageNode.messageid == mg_id,
                    tbl.NetworkMessageNode.nodeid == node.id,
                    tbl.NetworkMessageNode.dir == tbl.TX).one_or_none()
                if nmn_row is None:
                    nmn_row = tbl.NetworkMessageNode(networkid=self.network.id, messageid=mg_id,
                                                     nodeid=node.id, dir=tbl.TX)
                    session.add(nmn_row)
                    session.flush()
            for message_canid in nodes[node.name].rx_messages:
                mg_ids = [m.id for m in self.messages if m.can_id == message_canid]
                if len(mg_ids) > 1:
                    self.logger.warning('Skipping message {}, more found'.format(message_canid))
                    continue
                if len(mg_ids) < 1:
                    self.logger.warning('Skipping message {}, none found'.format(message_canid))
                    continue
                mg_id = mg_ids[0]
                nmn_row = session.query(tbl.NetworkMessageNode).filter(
                    tbl.NetworkMessageNode.networkid == self.network.id,
                    tbl.NetworkMessageNode.messageid == mg_id,
                    tbl.NetworkMessageNode.nodeid == node.id,
                    tbl.NetworkMessageNode.dir == tbl.RX).one_or_none()
                if nmn_row is None:
                    nmn_row = tbl.NetworkMessageNode(networkid=self.network.id, messageid=mg_id,
                                                     nodeid=node.id, dir=tbl.RX)
                    session.add(nmn_row)
                    session.flush()
