from candatabase.handler import CanDatabaseHandler
from argparse import ArgumentParser


parser = ArgumentParser(description='lists available networks')
parser.add_argument('dbpath',
        help='path to the database')


if __name__ == '__main__':
    args = parser.parse_args()
    dbh = CanDatabaseHandler(args.dbpath)

    names = dbh.list_networks()
    network_names = names['networks']
    merged = names['networks']
    merged_names = []

    if len(merged) > 0:
        for m in merged:
            merged_names.append("'" + m[0] + "' ['" + "', '".join(m[1]) + "']")
    network_list = "\nNetworks:\n- '{}'\n\nMerged networks:\n- {}".format(
        "'\n- '".join(network_names), '\n- '.join(merged_names))

    print network_list
