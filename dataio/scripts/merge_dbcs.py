from argparse import ArgumentParser
from candatabase import CanDatabaseHandler
import os
import traceback


parser = ArgumentParser(description='creates a merged dbc from dbcs')
parser.add_argument('merged_path',
                     help='path to merged dbc')
parser.add_argument('dbc_paths',
                     nargs='+',
                     help='paths to dbcs to merge')


if __name__ == '__main__':
    args = parser.parse_args()

    dbh = CanDatabaseHandler()
    try:
        dbh.create('temp.db', connect=True)
        dbc_names = []
        for dbc_path in args.dbc_paths:
            name, ext = os.path.splitext(os.path.basename(dbc_path))
            dbh.add_dbc(dbc_path, name=name)
            dbc_names.append(name)
        merged_name, ext = os.path.splitext(os.path.basename(args.merged_path))
        dbh.create_merged(merged_name, dbc_names)
        dbh.get_merged_dbc(merged_name, args.merged_path)
    except Exception:
        print traceback.format_exc()
    finally:
        os.remove('temp.db')
