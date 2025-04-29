import re


multiline_string_start = re.compile(r'^[^"]*"[^"]*$')
multiline_string_end = re.compile(r'^[^"]*"')
blank_line = re.compile(r'^$')
version = re.compile(r'VERSION\s+"(?P<version>.*)"', re.DOTALL)

bs = re.compile(r'BS_\s*:')

nodes = re.compile(r'BU_\s*:(?P<nodes>.+)?$')
val_table = re.compile(r'VAL_TABLE_\s+(?P<valt_name>[a-zA-Z0-9_]+)\s+(?P<vals>[^;]+);')
val_table_entry = re.compile('(?P<val>\d+)\s+"(?P<desc>[^"]*)"\s+')

msg = re.compile(r'BO_\s+(?P<id>\d+)\s+(?P<msg_name>[a-zA-Z0-9_]+)'
                 r':\s+(?P<dlc>\d+)\s+(?P<transmitter>[a-zA-Z0-9_]+)')

sgn = re.compile(r'\sSG_\s+(?P<sgn_name>[a-zA-Z0-9_]+)\s+(?P<mux>(M|m\d{0,3})\s+)?:\s+'
                 r'(?P<startbit>\d+)\|(?P<len>\d+)@(?P<endian>\d)(?P<signed>[+-])\s+'
                 r'\((?P<factor>[-0-9.+eE]+),(?P<offset>[-0-9.+eE]+)\)\s+'
                 r'\[(?P<min>[-0-9.+eE]+)\|(?P<max>[-0-9.+eE]+)\]\s+'
                 r'"(?P<unit>.*)"\s+(?P<receivers>.+)')

msg_transmitters = re.compile(r'BO_TX_BU_\s+(?P<id>\d+)\s+:\s+(?P<nodes>[a-zA-Z0-9_,]+);')

env_var = re.compile(r'EV_\s(?P<var_name>[a-zA-Z0-9_]+):\s(?P<dtype>\d+)\s'
                     r'\[(?P<min>[-0-9.+eE]+)\|(?P<max>[-0-9.+eE]+)\]\s'
                     r'"(?P<unit>.*)"\s(?P<num1>\d+)\s(?P<num2>\d+)\s'
                     r'(?P<dummy_node>[a-zA-Z0-9_]+)\s+(?P<node>[a-zA-Z0-9_]+);')
env_var_dtype_lut = {0: 'Integer',
                     1: 'Float'}

network_comment = re.compile(r'CM_\s+'
                             r'"(?P<comment>[^"]*)";')
node_comment = re.compile(r'CM_\s+BU_\s+(?P<node_name>[a-zA-Z0-9_]+)\s+'
                         r'"(?P<comment>[^"]*)";')
msg_comment = re.compile(r'CM_\s+BO_\s+(?P<id>\d+)\s+'
                         r'"(?P<comment>[^"]*)";')
sgn_comment = re.compile(r'CM_\s+SG_\s+(?P<id>\d+)\s+(?P<sgn_name>[a-zA-Z0-9_]+)\s+'
                         r'"(?P<comment>[^"]*)";')

network_attr = re.compile(r'BA_\s+"(?P<attr_name>[a-zA-Z0-9_-]+)"\s+'
                          r'"?(?P<attr_val>[a-zA-Z0-9_.-]+)"?;')
node_attr = re.compile(r'BA_\s+"(?P<attr_name>[a-zA-Z0-9_-]+)"\s+'
                       r'BU_\s+(?P<node_name>[a-zA-Z0-9_]+)\s+'
                       r'"?(?P<attr_val>[a-zA-Z0-9_.-]+)"?;')
msg_attr = re.compile(r'BA_\s+"(?P<attr_name>[a-zA-Z0-9_-]+)"\s+'
                      r'BO_\s+(?P<id>\d+)\s+'
                      r'"?(?P<attr_val>[a-zA-Z0-9_.-]+)"?;')
sgn_attr = re.compile(r'BA_\s+"(?P<attr_name>[a-zA-Z0-9_-]+)"\s+'
                      r'SG_\s+(?P<id>\d+)\s+(?P<sgn_name>[a-zA-Z0-9_]+)\s+'
                      r'"?(?P<attr_val>[a-zA-Z0-9_.-]+)"?;')

gen_attr_def = re.compile(r'BA_DEF_\s+(?P<attr_mode>(BO_)|(BU_)|(SG_))?\s*"'
                          r'(?P<attr_name>[a-zA-Z0-9_<>-]+)"\s+'
                          r'(?P<attr_type>[A-Z]+)\s+(?P<attr_def>.+)?;')
attr_mode_lut = {None : 'network',
                 'BU_': 'node',
                 'BO_': 'message',
                 'SG_': 'signal'}
attr_type_numeric = re.compile(r'(?P<min>[-0-9.+eE]+)\s+(?P<max>[-0-9.+eE]+)')

attr_default = re.compile(r'BA_DEF_DEF_\s+"(?P<attr_name>[a-zA-Z0-9_<>-]+)"\s+'
                          r'"?(?P<attr_val>[\s\(\)a-zA-Z0-9_@./]*)"?;')

val = re.compile(r'VAL_\s+(?P<id>\d+)?\s*(?P<sgn_name>[a-zA-Z0-9_]+)\s+(?P<vals>[^;]+);')
val_entry = re.compile(r'(?P<val>\d+)\s+"(?P<desc>[^"]*)"\s+')

signal_type = re.compile(r'SIG_VALTYPE_\s+(?P<id>\d+)\s+(?P<sgn_name>[a-zA-Z0-9_]+)\s+:\s+'
                         r'(?P<type>[1|2]);')
