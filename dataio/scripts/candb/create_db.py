from candatabase.handler import CanDatabaseHandler
from argparse import ArgumentParser


parser = ArgumentParser(description='creates an empty database')
parser.add_argument('dbpath',
        help='path to the database')


if __name__ == '__main__':
    args = parser.parse_args()
    dbh = CanDatabaseHandler()
    dbh.create(args.dbpath, connect=False)
