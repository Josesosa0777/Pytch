from candatabase.handler import CanDatabaseHandler
from argparse import ArgumentParser


parser = ArgumentParser(description='updates the given network with the given dbc in the database')
parser.add_argument('dbpath',
        help='path to the database')
parser.add_argument('name',
                              help='name of network to update')
parser.add_argument('dbc',
                              help='path to new dbc')


if __name__ == '__main__':
    args = parser.parse_args()
    dbh = CanDatabaseHandler(args.dbpath)
    dbh.update_dbc(args.name, args.dbc)
