import argparse

from xlrd import open_workbook

parser = argparse.ArgumentParser(description="""
  Convert input tab of health xls into fault labels
""")

parser.add_argument('xls', help='name of the health excel spreadsheet')
parser.add_argument('--sheet', default='Input', help='name of the error sheet')
parser.add_argument('--nrows', type=int, help='force the number of rows to process')
parser.add_argument('--name-col', type=int, default=1, help='column of the fault name')
parser.add_argument('--dtc-col', type=int, default=2, help='column of the dtc id')
parser.add_argument('--fault-name', default='dtc2label')

args = parser.parse_args()

xls = open_workbook(args.xls)
sheet = xls.sheet_by_name(args.sheet)
nrows = args.nrows or sheet.nrows

faults = dict((int(sheet.cell(row, args.dtc_col).value),
               sheet.cell(row, args.name_col).value.strip())
              for row in xrange(1, nrows))

print '%s = {' % args.fault_name
print '\n'.join(["  %3d: '%s'," % (dtc, label.replace("FAULT_", ""))
                 for (dtc, label) in faults.iteritems()])
print '}'
