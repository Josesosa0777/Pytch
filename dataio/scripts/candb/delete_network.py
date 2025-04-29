from candatabase.handler import CanDatabaseHandler
from argparse import ArgumentParser


parser = ArgumentParser(description='deletes the given networks from the database')
parser.add_argument('dbpath',
        help='path to the database')
parser.add_argument('-m', '--merged',
                              action='store_true',
                              help='delete merged network')
parser.add_argument('name',
                              help='name of network to delete')


if __name__ == '__main__':
    args = parser.parse_args()
    dbh = CanDatabaseHandler(args.dbpath)
    if args.merged:
        dbh.delete_merged(args.name)
    else:
        dbh.delete_network(args.name)
