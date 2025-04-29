import os
import sys, getopt
import sqlite3
import logging
from measproc.batchsqlite import Batch, RESULTS, update

logger = logging.getLogger('derive_labels_db')

def derive_labels_from_db(labelled_database, unlabelled_database):
    con = sqlite3.connect(unlabelled_database)
    cur = con.cursor()

    mergescript = r"C:\KBApps\Bitbucket_Repo\pytch2.7\dataeval\src\measproc\batchsqlite\derive_labels.sql"

    mergescript = open(mergescript).read()
    mergescript = mergescript % labelled_database
    cur.executescript(mergescript)

    # logger.info("Labels derived successfully.")
    print "Labels derived successfully."

def main(argv):
    labelled_database = ""
    unlabelled_database = ""
    try:
        opts, args = getopt.getopt(argv, "l:u:")
    except getopt.GetoptError:
        print ('python -m derive_labels_db -l <labelled_database_name> -u <unlabelled_database_name>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h"):
            print("python -m derive_labels_db -l <labelled_database_name> -u <unlabelled_database_name>")
            sys.exit(0)
        if opt in ("-l", "--labelleddb"):
            labelled_database = arg
        elif opt in ("-u", "--unlabelleddb"):
            unlabelled_database = arg

    derive_labels_from_db(labelled_database, unlabelled_database)

if __name__ == "__main__":
    main(sys.argv[1:])
