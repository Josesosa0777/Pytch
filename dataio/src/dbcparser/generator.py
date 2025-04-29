from candata import Network
import utils
import templates
from os import path
import codecs


class DbcGenerator(object):
    def __init__(self, logger):
        self.logger = logger
        self._dbc_lines = []
        self._filepath = ''

    @property
    def filename(self):
        return path.basename(self._filepath)

    def write(self, network, filepath):
        self._filepath = filepath
        self.logger.info("Generating dbc: '{}'...".format(self.filename))
        self._write_lines(network)
        self._write_file()
        self.logger.debug("'{}' successfully written".format(self.filename))

    def _write_lines(self, network):
        if type(network) is not Network:
            raise TypeError('network is error parameter not Network type')
        message_signal_lines = []
        message_tx_lines = []
        comment_lines = []
        env_var_lines = []
        definition_lines = []
        default_lines = []
        nw_attribute_lines = []
        nd_attribute_lines = []
        mg_attribute_lines = []
        sg_attribute_lines = []
        val_lines = []
        evval_lines = []
        sigtype_lines = []

        # network stuff
        version_line = templates.version.format(version=network.version_string)
        if network.comment:
            nw_comment_line = templates.network_comment.format(comment=network.comment)
            comment_lines.append(nw_comment_line)
        for a_name, a in network.attributes.iteritems():
            a_line = templates.network_attribute.format(name=a_name, value=a.value_str)
            nw_attribute_lines.append(a_line)
        a_line = templates.network_attribute.format(name='DBName', value='"'+network.name+'"')
        nw_attribute_lines.append(a_line)  # dbc stores name as an attribute
        a_line = templates.network_attribute.format(name='ProtocolType', value='"'+network.protocol+'"')
        nw_attribute_lines.append(a_line)  # dbc stores protocol as an attribute
        # attributes stuff
        for a_name, d in network.attribute_definitions['network'].iteritems():
            d_line = templates.network_attribute_definition.format(
                    name=a_name, type=d.type, entries=d.entries_str)
            dd_line = templates.attribute_default.format(name=a_name, value=d.default_str)
            definition_lines.append(d_line)
            default_lines.append(dd_line)
        d_line = templates.network_attribute_definition.format(
                name='DBName', type='STRING', entries='')
        dd_line = templates.attribute_default.format(name='DBName', value='""')
        definition_lines.append(d_line)
        default_lines.append(dd_line)
        d_line = templates.network_attribute_definition.format(
                name='ProtocolType', type='STRING', entries='')
        dd_line = templates.attribute_default.format(name='ProtocolType', value='"ExtendedCan"')
        definition_lines.append(d_line)
        default_lines.append(dd_line)
        for a_name, d in network.attribute_definitions['node'].iteritems():
            d_line = templates.node_attribute_definition.format(
                    name=a_name, type=d.type, entries=d.entries_str)
            dd_line = templates.attribute_default.format(name=a_name, value=d.default_str)
            definition_lines.append(d_line)
            default_lines.append(dd_line)
        d_line = templates.node_attribute_definition.format(
                name='NmStationAddress', type='INT', entries='0 255')
        dd_line = templates.attribute_default.format(name='NmStationAddress', value='254')
        definition_lines.append(d_line)
        default_lines.append(dd_line)
        for a_name, d in network.attribute_definitions['message'].iteritems():
            d_line = templates.message_attribute_definition.format(
                    name=a_name, type=d.type, entries=d.entries_str)
            dd_line = templates.attribute_default.format(name=a_name, value=d.default_str)
            definition_lines.append(d_line)
            default_lines.append(dd_line)
        for a_name, d in network.attribute_definitions['signal'].iteritems():
            d_line = templates.signal_attribute_definition.format(
                    name=a_name, type=d.type, entries=d.entries_str)
            dd_line = templates.attribute_default.format(name=a_name, value=d.default_str)
            definition_lines.append(d_line)
            default_lines.append(dd_line)
        # nodes
        node_names = []
        for n_name, n in network.nodes.iteritems():
            node_names.append(n_name)
            # node attributes
            for a_name, a in n.attributes.iteritems():
                a_line = templates.node_attribute.format(
                        name=a_name, node_name=n_name, value=a.value_str)
                nd_attribute_lines.append(a_line)
            if n.address is not None:
                a_line = templates.node_attribute.format(name='NmStationAddress', node_name=n_name,
                                                         value=n.address)
                nd_attribute_lines.append(a_line)  # dbc stores name as an attribute
            # node comment
            if n.comment:
                comment_lines.append(templates.node_comment.format(name=n_name, comment=n.comment))
            # environment variables
            for ev in n.env_vars.itervalues():
                ev_line = templates.env_var.format(name=ev.name, dtype=ev.dtype, min=ev.min,
                                                   max=ev.max, unit=ev.unit, num1=ev.num1,
                                                   num2=ev.num2, dummy_node=ev.dummy_node,
                                                   node=n.name)
                env_var_lines.append(ev_line)
                # values
                evval_entries = []
                for v, d in ev.values.iteritems():
                    evval_entries.append(u'{value} "{description}"'.format(value=v, description=d))
                if len(evval_entries) > 0:
                    entries = ' '.join(evval_entries)
                    evv_line = templates.envvar_values.format(
                            name=ev.name, values=entries)
                    evval_lines.append(evv_line)

        nodes_line = templates.nodes.format(nodes=' '.join(node_names))
        # message and signal stuff
        for m_name, m in network.messages.iteritems():
            transmitters = self._get_message_tranmitters(network.nodes, m.can_id)
            receivers = self._get_message_receivers(network.nodes, m.can_id)
            if len(transmitters) < 1:
                transmitters = ['Vector__XXX']
            if len(receivers) < 1:
                receivers = ['Vector__XXX']
            # message
            m_line = templates.message.format(
                    id=m.can_id, name=m.name, dlc=m.dlc, transmitter=transmitters[0])
            message_signal_lines.append(m_line)
            for s_name, s in m.signals.iteritems():
                # signal
                byteorder_char = utils.byteorder_py2dbc(s.byteorder)
                sigtype = utils.sigtype_py2dbc(s.type)
                if type(sigtype) is int:
                    st_line = templates.sigtype.format(id=m.can_id, name=s_name, sigtype=sigtype)
                    sigtype_lines.append(st_line)
                    sigtype = '-'
                s_line = templates.signal.format(
                        name=s_name, mux=s.mux.dbc_format, startbit=s.startbit, length=s.length,
                        byteorder=byteorder_char, sigtype=sigtype, factor=s.factor, offset=s.offset,
                        min=s.min, max=s.max, unit=s.unit, receivers=','.join(receivers))
                message_signal_lines.append(s_line)
                # signal values
                val_entries = []
                for v, d in s.values.iteritems():
                    val_entries.append(u'{value} "{description}"'.format(value=v, description=d))
                if len(val_entries) > 0:
                    entries = ' '.join(val_entries)
                    v_line = templates.signal_values.format(
                            id=m.can_id, name=s_name, values=entries)
                    val_lines.append(v_line)
                # signal attributes
                for a_name, a in s.attributes.iteritems():
                    a_line = templates.signal_attribute.format(
                            name=a_name, id=m.can_id, signal_name=s_name, value=a.value_str)
                    sg_attribute_lines.append(a_line)
                # signal comment
                if s.comment:
                    comment_lines.append(templates.signal_comment.format(
                            id=m.can_id, name=s_name, comment=s.comment))
            # message attributes
            for a_name, a in m.attributes.iteritems():
                a_line = templates.message_attribute.format(
                        name=a_name, id=m.can_id, value=a.value_str)
                sg_attribute_lines.append(a_line)
            if m.cycle_time is not None:
                a_line = templates.message_attribute.format(name='GenMsgCycleTime', id=m.can_id,
                                                         value=m.cycle_time)
                mg_attribute_lines.append(a_line)  # dbc stores name as an attribute
            if m.cycle_time_fast is not None:
                a_line = templates.message_attribute.format(name='GenMsgCycleTimeFast', id=m.can_id,
                                                         value=m.cycle_time_fast)
                mg_attribute_lines.append(a_line)  # dbc stores name as an attribute
            # message comment
            if m.comment:
                comment_lines.append(templates.message_comment.format(
                        id=m.can_id, comment=m.comment))
            if len(transmitters) > 1:
                tx_line = templates.message_transmitters.format(
                        id=m.can_id, nodes=','.join(transmitters))
                message_tx_lines.append(tx_line)
            message_signal_lines.append('\n')
        self._dbc_lines = (
            [version_line] +
            [templates.other_lines] +
            [nodes_line] +
            ['\n\n'] +
            message_signal_lines +
            message_tx_lines +
            ['\n\n'] +
            env_var_lines +
            ['\n'] +
            comment_lines +
            definition_lines +
            default_lines +
            nw_attribute_lines +
            nd_attribute_lines +
            mg_attribute_lines +
            sg_attribute_lines +
            val_lines +
            evval_lines +
            sigtype_lines
        )
        return True

    def _write_file(self):
        with codecs.open(self._filepath, 'w', encoding='dbcs') as f:
            f.writelines(self._dbc_lines)

    def _get_message_tranmitters(self, nodes, message_id):
        transmitters = []
        for name, node in nodes.iteritems():
            tx_ids = [m.can_id for m in node.tx_messages]
            if message_id in tx_ids:
                transmitters.append(name)
        return transmitters

    def _get_message_receivers(self, nodes, message_id):
        receivers = []
        for name, node in nodes.iteritems():
            rx_ids = [m.can_id for m in node.rx_messages]
            if message_id in rx_ids:
                receivers.append(name)
        return receivers