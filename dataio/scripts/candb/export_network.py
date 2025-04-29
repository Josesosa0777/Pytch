from candatabase.handler import CanDatabaseHandler
from argparse import ArgumentParser
import os


parser = ArgumentParser(description='Manage CAN database')
parser.add_argument('dbpath',
        help='path to the database')
parser.add_argument('name',
        help='name of network in database')
parser.add_argument('file',
        help='exported file path')
parser.add_argument('-m', '--merged',
        action='store_true',
        help='export merged network')


if __name__ == '__main__':
    args = parser.parse_args()
    dbh = CanDatabaseHandler(args.dbpath)
    path, ext = os.path.splitext(args.file)
    if ext.lower() == '.dbc':
        if args.merged:
            dbh.get_merged_dbc(args.name, args.file)
        else:
            dbh.get_dbc(args.name, args.file)
    elif ext.lower() == '.pdf':
        # TODO export pdf
        pass
