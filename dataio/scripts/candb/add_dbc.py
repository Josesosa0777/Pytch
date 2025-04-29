from candatabase.handler import CanDatabaseHandler
from argparse import ArgumentParser


parser = ArgumentParser(description='adds the given dbc with the given name to the database')
parser.add_argument('dbpath',
        help='path to the database')
parser.add_argument('-n', '--name',
                           help='name of the network in database')
parser.add_argument('dbc',
                           help='dbc file path')


if __name__ == '__main__':
    args = parser.parse_args()
    dbh = CanDatabaseHandler(args.dbpath)
    dbh.add_dbc(args.dbc, name=args.name)
