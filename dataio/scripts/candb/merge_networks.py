from candatabase.handler import CanDatabaseHandler
from argparse import ArgumentParser


parser = ArgumentParser(description='creates a merged network from NETWORKS')
parser.add_argument('dbpath',
        help='path to the database')
parser.add_argument('merged_name',
                             help='name of merged network')
parser.add_argument('networks',
                             nargs='+',
                             help='names of networks to merge')
group = parser.add_mutually_exclusive_group()
group.add_argument('-a', '--append',
                   action='store_true',
                   help='append networks to existing merged')
group.add_argument('-r', '--remove',
                   action='store_true',
                   help='removes the networks from existing merged')


if __name__ == '__main__':
    args = parser.parse_args()
    dbh = CanDatabaseHandler(args.dbpath)
    if args.remove:
        dbh.remove_from_merged(args.merged_name, args.networks)
    else:
        dbh.create_merged(args.merged_name, args.networks, append=args.append)
