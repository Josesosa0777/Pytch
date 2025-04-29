import argparse
import re

parser = argparse.ArgumentParser(description="""
  Create measparser query from all the signals of the dbc
""")

parser.add_argument('dbc', nargs='+',)
parser.add_argument('--query-sep', default=';',)

msg_pattern = re.compile(r'BO_\s+\d+\s+([\w\d_]+):\s+\d+\s+([\w\d_]+)')
sgn_pattern = re.compile(r'^\s*SG_\s+([\w\d_]+)')

args = parser.parse_args()
queries = []
for dbc in args.dbc:
  with open(dbc) as f:
    tags = {}
    for line in f:
      msg_match = msg_pattern.search(line)
      if msg_match:
        tags['msg'], tags['src'] = msg_match.groups()
      sgn_match = sgn_pattern.search(line)
      if sgn_match and tags:
        tags['sgn'], = sgn_match.groups()
        query = 'f pdt %(msg)s pst %(sgn)s' % tags
        if tags['src'] != "Vector__XXX":  # CAN message source set
          query += ' pdt %(src)s' % tags
        queries.append(query)
      if not line.strip():
        tags = {}
print args.query_sep.join(queries)
