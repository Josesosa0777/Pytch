version = u'VERSION "{version}"\n'

nodes = 'BU_: {nodes}\n'

message = 'BO_ {id} {name}: {dlc} {transmitter}\n'

signal = u' SG_ {name} {mux}: {startbit}|{length}@{byteorder}{sigtype} ({factor},{offset}) [{min}|{max}] "{unit}" {receivers}\n'

message_transmitters = 'BO_TX_BU_ {id} : {nodes};\n'

env_var = u'EV_ {name}: {dtype} [{min}|{max}] "{unit}" {num1} {num2} {dummy_node}  {node};\n'

network_comment = u'CM_ "{comment}";\n'
node_comment = u'CM_ BU_ {name} "{comment}";\n'
message_comment = u'CM_ BO_ {id} "{comment}";\n'
signal_comment = u'CM_ SG_ {id} {name} "{comment}";\n'

network_attribute_definition = 'BA_DEF_  "{name}" {type} {entries};\n'
node_attribute_definition = 'BA_DEF_ BU_  "{name}" {type} {entries};\n'
message_attribute_definition = 'BA_DEF_ BO_  "{name}" {type} {entries};\n'
signal_attribute_definition = 'BA_DEF_ SG_  "{name}" {type} {entries};\n'

attribute_default = 'BA_DEF_DEF_  "{name}" {value};\n'

network_attribute = 'BA_ "{name}" {value};\n'
node_attribute = 'BA_ "{name}" BU_ {node_name} {value};\n'
message_attribute = 'BA_ "{name}" BO_ {id} {value};\n'
signal_attribute = 'BA_ "{name}" SG_ {id} {signal_name} {value};\n'

signal_values = u'VAL_ {id} {name} {values} ;\n'
envvar_values = u'VAL_ {name} {values} ;\n'

sigtype = 'SIG_VALTYPE_ {id} {name} : {sigtype};\n'

other_lines = '''

NS_ : 
\tNS_DESC_
\tCM_
\tBA_DEF_
\tBA_
\tVAL_
\tCAT_DEF_
\tCAT_
\tFILTER
\tBA_DEF_DEF_
\tEV_DATA_
\tENVVAR_DATA_
\tSGTYPE_
\tSGTYPE_VAL_
\tBA_DEF_SGTYPE_
\tBA_SGTYPE_
\tSIG_TYPE_REF_
\tVAL_TABLE_
\tSIG_GROUP_
\tSIG_VALTYPE_
\tSIGTYPE_VALTYPE_
\tBO_TX_BU_
\tBA_DEF_REL_
\tBA_REL_
\tBA_DEF_DEF_REL_
\tBU_SG_REL_
\tBU_EV_REL_
\tBU_BO_REL_
\tSG_MUL_VAL_

BS_:

'''
