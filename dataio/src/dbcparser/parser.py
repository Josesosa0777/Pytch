import patterns
from utils import byteorder_dbc2py, sigtype_dbc2py, merge_multiline_strings, remove_blank_lines
from candata import (Network, Node, EnvVar, Message, Signal, Values, Multiplexor,
                     StringAttributeDefinition, EnumAttributeDefinition,
                     IntAttributeDefinition, HexAttributeDefinition, FloatAttributeDefinition)
from os import path
from collections import OrderedDict


class DbcParser(object):
    def __init__(self, logger):
        self.logger = logger
        self._filepath = ''

    @property
    def filename(self):
        return path.basename(self._filepath)

    def parse(self, filepath):
        self._filepath = filepath
        self.logger.info("Parsing dbc: '{}'...".format(self.filename))
        with open(filepath, 'r') as fdbc:
            raw_lines = fdbc.readlines()

        # preprocess lines
        merged_lines = merge_multiline_strings(raw_lines)
        dbc_lines = remove_blank_lines(merged_lines)

        network = Network()
        filename, ext = path.splitext(path.basename(self._filepath))
        network.name = filename  # default name
        network.protocol = 'ExtendedCan'

        # parse version
        line = dbc_lines.pop(0)
        version_mo = patterns.version.match(line)
        if version_mo is None:
            self.logger.error('Invalid dbc file - version line:\n\t{}'.format(line))
            return None
        network.version_string = version_mo.group('version')
        # parse other stuff
        other_lines = []
        otherstuff_processed = False
        while not otherstuff_processed:
            line = dbc_lines.pop(0)
            bs_mo = patterns.bs.match(line)
            if bs_mo is not None:
                otherstuff_processed = True
            other_lines.append(line)  # TODO do sg with these lines
        # parse nodes
        line = dbc_lines.pop(0)
        nodes_mo = patterns.nodes.match(line)
        if nodes_mo is None:
            self.logger.error('Invalid dbc file - nodes:\n\t{}'.format(line))
            return None
        elif nodes_mo.group('nodes') is None:
            nodes_lst = []
        else:
            nodes_str = nodes_mo.group('nodes').strip()
            nodes_lst = nodes_str.split(' ')
        nodes_lst.append('Vector__XXX')
        for node in nodes_lst:
            n = Node()
            n.name = node
            network.nodes[node] = n
        # parse rest of dbc line by line
        curr_id = 0  # for binding signals to messages
        for dbc_line in dbc_lines:
            sgn_mo = patterns.sgn.match(dbc_line)
            if sgn_mo is not None:
                signal = Signal()
                signal.name = sgn_mo.group('sgn_name')
                signal.mux = Multiplexor(sgn_mo.group('mux'))
                signal.startbit = int(sgn_mo.group('startbit'))
                signal.length = int(sgn_mo.group('len'))
                signal.byteorder = byteorder_dbc2py(int(sgn_mo.group('endian')))
                signal.type = sigtype_dbc2py(sgn_mo.group('signed'))
                signal.factor = float(sgn_mo.group('factor'))
                signal.offset = float(sgn_mo.group('offset'))
                signal.min = float(sgn_mo.group('min'))
                signal.max = float(sgn_mo.group('max'))
                try:
                    signal.unit = sgn_mo.group('unit').decode('dbcs')
                except UnicodeDecodeError:
                    self.logger.error("could not decode unit of signal '{sg}': {unit}".format(
                            sg=signal.name, unit=sgn_mo.group('unit')))
                    signal.unit = sgn_mo.group('unit').decode('latin-1', 'replace')  # TODO encoding
                for node_name in sgn_mo.group('receivers').split(','):
                    network.nodes[node_name].rx_messages.add(curr_id)
                network.messages[curr_id].signals[signal.name] = signal
                continue
            msg_mo = patterns.msg.match(dbc_line)
            if msg_mo is not None:
                curr_id = int(msg_mo.group('id'))
                message = Message()
                message.name = msg_mo.group('msg_name')
                message.can_id = curr_id
                message.dlc = int(msg_mo.group('dlc'))
                network.messages[curr_id] = message
                network.nodes[msg_mo.group('transmitter')].tx_messages.add(curr_id)
                continue
            sgn_comment_mo = patterns.sgn_comment.match(dbc_line)
            if sgn_comment_mo is not None:
                msg_id = int(sgn_comment_mo.group('id'))
                sgn_name = sgn_comment_mo.group('sgn_name')
                network.messages[msg_id].signals[sgn_name].comment = sgn_comment_mo.group('comment').decode('dbcs')
                continue
            msg_comment_mo = patterns.msg_comment.match(dbc_line)
            if msg_comment_mo is not None:
                msg_id = int(msg_comment_mo.group('id'))
                network.messages[msg_id].comment = msg_comment_mo.group('comment').decode('dbcs')
                continue
            network_comment_mo = patterns.network_comment.match(dbc_line)
            if network_comment_mo is not None:
                network.comment = network_comment_mo.group('comment').decode('dbcs')
                continue
            node_comment_mo = patterns.node_comment.match(dbc_line)
            if node_comment_mo is not None:
                node_name = node_comment_mo.group('node_name')
                network.nodes[node_name].comment = node_comment_mo.group('comment').decode('dbcs')
                continue
            val_mo = patterns.val.match(dbc_line)
            if val_mo is not None:
                if val_mo.group('id') is None:
                    ev_name = val_mo.group('sgn_name')
                    node_name = None
                    for node in network.nodes.itervalues():
                        if ev_name in node.env_vars.keys():
                            node_name = node.name
                            break
                    if node_name is None:
                        # TODO handle error
                        pass
                    vals_str = val_mo.group('vals')
                    val_entries = patterns.val_entry.findall(vals_str)
                    vals_dict = OrderedDict()
                    for val_entry in val_entries:
                        vals_dict[int(val_entry[0])] = val_entry[1].decode('dbcs')
                    network.nodes[node_name].env_vars[ev_name].values = Values(vals_dict)
                else:
                    msg_id = int(val_mo.group('id'))
                    sgn_name = val_mo.group('sgn_name')
                    vals_str = val_mo.group('vals')
                    val_entries = patterns.val_entry.findall(vals_str)
                    vals_dict = OrderedDict()
                    for val_entry in val_entries:
                        vals_dict[int(val_entry[0])] = val_entry[1].decode('dbcs')
                    network.messages[msg_id].signals[sgn_name].values = Values(vals_dict)
                continue
            val_table_mo = patterns.val_table.match(dbc_line)
            if val_table_mo is not None:
                # not storing value tables
                continue
            gen_attr_def_mo = patterns.gen_attr_def.match(dbc_line)
            if gen_attr_def_mo is not None:
                if gen_attr_def_mo.group('attr_name') in ('DBName', 'ProtocolType', 'NmStationAddress'):
                    continue
                attr_type = gen_attr_def_mo.group('attr_type')
                if attr_type == 'ENUM':
                    attr = EnumAttributeDefinition()
                    attr.entries = gen_attr_def_mo.group('attr_def').split(',')
                elif attr_type == 'INT':
                    attr = IntAttributeDefinition()
                    attr_int_mo = patterns.attr_type_numeric.match(gen_attr_def_mo.group('attr_def'))
                    attr.min = int(attr_int_mo.group('min'))
                    attr.max = int(attr_int_mo.group('max'))
                elif attr_type == 'HEX':
                    attr = HexAttributeDefinition()
                    attr_int_mo = patterns.attr_type_numeric.match(gen_attr_def_mo.group('attr_def'))
                    attr.min = int(attr_int_mo.group('min'))
                    attr.max = int(attr_int_mo.group('max'))
                elif attr_type == 'FLOAT':
                    attr = FloatAttributeDefinition()
                    attr_int_mo = patterns.attr_type_numeric.match(gen_attr_def_mo.group('attr_def'))
                    attr.min = float(attr_int_mo.group('min'))
                    attr.max = float(attr_int_mo.group('max'))
                elif attr_type == 'STRING':
                    attr = StringAttributeDefinition()
                else:
                    self.logger.warning('Could not parse attribute definition:\n\t{}'.format(dbc_line))
                    continue
                attr.name = gen_attr_def_mo.group('attr_name')
                attr_mode = gen_attr_def_mo.group('attr_mode')
                network.attribute_definitions[patterns.attr_mode_lut[attr_mode]][attr.name] = attr
                continue
            attr_default_mo = patterns.attr_default.match(dbc_line)
            if attr_default_mo is not None:
                attr_name = attr_default_mo.group('attr_name')
                if attr_name in ('DBName', 'ProtocolType', 'NmStationAddress'):
                    continue
                default_val = attr_default_mo.group('attr_val')
                if default_val.isdigit():  # TODO float
                    default_val = int(default_val)
                try:
                    if attr_name in network.attribute_definitions['network'].viewkeys():
                        network.attribute_definitions['network'][attr_name].default = default_val
                    elif attr_name in network.attribute_definitions['node'].viewkeys():
                        network.attribute_definitions['node'][attr_name].default = default_val
                    elif attr_name in network.attribute_definitions['message'].viewkeys():
                        network.attribute_definitions['message'][attr_name].default = default_val
                    elif attr_name in network.attribute_definitions['signal'].viewkeys():
                        network.attribute_definitions['signal'][attr_name].default = default_val
                    else:
                        self.logger.warning("No definition found for attribute '{}'".format(attr_name))
                except ValueError:
                    if attr_name in network.attribute_definitions['network'].viewkeys():
                        network.attribute_definitions['network'][attr_name].default = 0
                        new_def = network.attribute_definitions['network'][attr_name].entries[0]
                    elif attr_name in network.attribute_definitions['node'].viewkeys():
                        network.attribute_definitions['node'][attr_name].default = 0
                        new_def = network.attribute_definitions['node'][attr_name].entries[0]
                    elif attr_name in network.attribute_definitions['message'].viewkeys():
                        network.attribute_definitions['message'][attr_name].default = 0
                        new_def = network.attribute_definitions['message'][attr_name].entries[0]
                    elif attr_name in network.attribute_definitions['signal'].viewkeys():
                        network.attribute_definitions['signal'][attr_name].default = 0
                        new_def = network.attribute_definitions['signal'][attr_name].entries[0]
                    else:
                        new_def = 'baj van'
                    self.logger.warning("Invalid default value for attribute '{}': '{}'\n\t"
                                        "using '{}' instead".format(attr_name, default_val, new_def))
                continue
            node_attr_mo = patterns.node_attr.match(dbc_line)
            if node_attr_mo is not None:
                node_name = node_attr_mo.group('node_name')
                attr_name = node_attr_mo.group('attr_name')
                attr_val = node_attr_mo.group('attr_val')
                if attr_name == 'NmStationAddress':
                    network.nodes[node_name].address = int(attr_val)
                    continue
                AttrClass = network.attribute_definitions['node'][attr_name].attr_class
                attr = AttrClass()
                attr.name = attr_name
                attr.value = attr_val
                network.nodes[node_name].attributes[attr_name] = attr
                continue
            msg_attr_mo = patterns.msg_attr.match(dbc_line)
            if msg_attr_mo is not None:
                msg_id = int(msg_attr_mo.group('id'))
                attr_name = msg_attr_mo.group('attr_name')
                attr_val = msg_attr_mo.group('attr_val')
                if attr_name == 'GenMsgCycleTime':
                    network.messages[msg_id].cycle_time = int(attr_val)
                    continue
                if attr_name == 'GenMsgCycleTimeFast':
                    network.messages[msg_id].cycle_time_fast = int(attr_val)
                    continue
                AttrClass = network.attribute_definitions['message'][attr_name].attr_class
                attr = AttrClass()
                attr.name = attr_name
                attr.value = attr_val
                network.messages[msg_id].attributes[attr_name] = attr
                continue
            sgn_attr_mo = patterns.sgn_attr.match(dbc_line)
            if sgn_attr_mo is not None:
                attr_name = sgn_attr_mo.group('attr_name')
                attr_val = sgn_attr_mo.group('attr_val')
                sgn_name = sgn_attr_mo.group('sgn_name')
                msg_id = int(sgn_attr_mo.group('id'))
                AttrClass = network.attribute_definitions['signal'][attr_name].attr_class
                attr = AttrClass()
                attr.name = attr_name
                attr.value = attr_val
                network.messages[msg_id].signals[sgn_name].attributes[attr_name] = attr
                continue
            network_attr_mo = patterns.network_attr.match(dbc_line)
            if network_attr_mo is not None:
                if network_attr_mo.group('attr_name') == 'DBName':
                    network.name = network_attr_mo.group('attr_val')
                    continue
                if network_attr_mo.group('attr_name') == 'ProtocolType':
                    network.protocol = network_attr_mo.group('attr_val')
                    continue
                attr_name = network_attr_mo.group('attr_name')
                attr_val = network_attr_mo.group('attr_val')
                AttrClass = network.attribute_definitions['network'][attr_name].attr_class
                attr = AttrClass()
                attr.name = attr_name
                attr.value = attr_val
                network.attributes[attr_name] = attr
                continue
            signal_type_mo = patterns.signal_type.match(dbc_line)
            if signal_type_mo is not None:
                msg_id = int(signal_type_mo.group('id'))
                sgn_name = signal_type_mo.group('sgn_name')
                sgn_type = sigtype_dbc2py(int(signal_type_mo.group('type')))
                network.messages[msg_id].signals[sgn_name].type = sgn_type
                continue
            msg_transmitters_mo = patterns.msg_transmitters.match(dbc_line)
            if msg_transmitters_mo is not None:
                tx_nodes_str = msg_transmitters_mo.group('nodes').strip()
                tx_nodes = tx_nodes_str.split(',')
                msg_id = int(msg_transmitters_mo.group('id'))
                for node_name in tx_nodes:
                    network.nodes[node_name].tx_messages.add(msg_id)
                continue
            env_var_mo = patterns.env_var.match(dbc_line)
            if env_var_mo is not None:
                ev = EnvVar()
                ev.name = env_var_mo.group('var_name')
                ev.dtype = int(env_var_mo.group('dtype'))
                ev.min = float(env_var_mo.group('min'))
                ev.max = float(env_var_mo.group('max'))
                ev.unit = env_var_mo.group('unit').decode('dbcs')
                ev.num1 = int(env_var_mo.group('num1'))
                ev.num2 = int(env_var_mo.group('num2'))
                ev.dummy_node = env_var_mo.group('dummy_node')
                node_name = env_var_mo.group('node')
                network.nodes[node_name].env_vars[ev.name] = ev
                continue
            self.logger.warning('line did not match any patterns: {}'.format(dbc_line))
        self.logger.debug("'{}' successfully parsed".format(self.filename))
        return network
