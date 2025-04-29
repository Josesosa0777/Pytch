from candata import Customer
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from writer import CanDatabaseWriter
from reader import CanDatabaseReader
from deleter import CanDatabaseDeleter
from merger import CanDatabaseMerger
from candata import Network
from dbcparser import DbcGenerator, DbcParser
from datetime import datetime
import logging
import tables as tbl
import os


class NotConnectedError(Exception):
    pass


class CanDatabaseHandler(object):
    def __init__(self, path_to_db=None):
        logger = logging.getLogger('candatabase')
        logger.setLevel(logging.DEBUG)
        sh = logging.StreamHandler()
        sh.setLevel(logging.INFO)
        sh_formatter = logging.Formatter('[%(levelname)s] %(message)s')
        sh.setFormatter(sh_formatter)
        log_dir = os.path.expanduser(os.path.join(
                '~',
                '.{}'.format(os.getenv('DATAEVAL_NAME', 'dataeval')),
                'candatabase_logs'))
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_file = 'candatabase_{}.log'.format(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
        fh = logging.FileHandler(os.path.join(log_dir, log_file))
        fh.setLevel(logging.DEBUG)
        fh_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        fh.setFormatter(fh_formatter)
        logger.addHandler(sh)
        logger.addHandler(fh)
        # create stuff
        self._reader = CanDatabaseReader(logger)
        self._writer = CanDatabaseWriter(logger)
        self._deleter = CanDatabaseDeleter(logger)
        self._merger = CanDatabaseMerger(logger)
        self._parser = DbcParser(logger)
        self._generator = DbcGenerator(logger)
        self.logger = logger
        # administrative stuff
        self._connected = False
        self.Session = None
        if path_to_db is not None:
            self.connect(path_to_db)
            self.logger.debug('Database handler initialized for: {}'.format(path_to_db))
        else:
            self.logger.debug('Database handler initialized without db connection')

    @property
    def connected(self):
        return self._connected

    def connect(self, path_to_db):
        self.logger.info("Connecting to database: '{}'...".format(path_to_db))
        if not os.path.exists(path_to_db):
            self.logger.error('Could not find database')
            return
        db_url = 'sqlite:///' + path_to_db
        db_engine = create_engine(db_url)
        self.Session = sessionmaker(bind=db_engine)
        self._connected = True
        self.logger.info('Connected')

    def disconnect(self):
        self.Session = None
        self._connected = False
        self.logger.info('Disconnected from database')

    def create(self, path_to_db, connect=True):
        self.logger.info("Creating new database: '{}'...".format(path_to_db))
        db_ext = os.path.splitext(path_to_db)[1]
        if db_ext.lower() != '.db':
            self.logger.error("Invalid database extension: '{}'".format(db_ext))
            return
        if os.path.exists(path_to_db):
            self.logger.error('Database already exists, delete or rename it')
            return
        # create empty database
        engine = create_engine('sqlite:///' + path_to_db, case_sensitive=False)
        tbl.Base.metadata.create_all(engine)
        vector__xxx = tbl.Node()
        vector__xxx.name = 'Vector__XXX'
        vector__xxx.comment = 'Default node for all networks'
        vector__xxx.id = 1
        Session = sessionmaker(bind=engine)
        session = Session()
        session.add(vector__xxx)
        session.commit()
        session.close()
        if connect:
            self.connect(path_to_db)

    def get_network(self, network_name):
        self._check_connection()
        session = self.Session()
        network = self._reader.get_network(session, network_name)
        session.close()
        return network

    def add_network(self, network, customer_name=None):
        self._check_connection()
        if type(network) is not Network:
            raise TypeError("network should be an instance of 'Network', not '{}'".format(type(network)))
        session = self.Session()
        self._writer.add_network(session, network)
        if customer_name is not None:
            self.add_network_to_customer(network, customer_name)
        session.close()
        return network.name

    def delete_network(self, network_name):
        self._check_connection()
        session = self.Session()
        self._deleter.delete_network(session, network_name)
        session.close()

    def delete_merged(self, merged_name):
        self._check_connection()
        session = self.Session()
        self._deleter.delete_merged(session, merged_name)
        session.close()

    def get_customer(self, customer_name):
        self._check_connection()
        session = self.Session()
        customer = self._reader.get_customer(session, customer_name)
        session.close()
        return customer

    def add_customer(self, customer):
        self._check_connection()
        if type(customer) is not Customer:
            raise TypeError("customer should be an instance of 'Customer', not '{}'".format(type(customer)))
        session = self.Session()
        self._writer.add_customer(session, customer)
        session.close()
        return customer.name

    def delete_customer(self, customer_name):
        self._check_connection()
        session = self.Session()
        self._deleter.delete_customer(session, customer_name)
        session.close()

    def get_network_from_customer(self, network_name, customer_name):
        self._check_connection()
        session = self.Session()
        network = self._reader.get_network_from_customer(session, customer_name, network_name)
        session.close()
        return network

    def add_network_to_customer(self, network, customer_name):
        self._check_connection()
        if type(network) is not Network:
            raise TypeError("network should be an instance of 'Network', not '{}'".format(type(network)))
        session = self.Session()
        self._writer.add_network_to_customer(session, network, customer_name)
        session.close()
        return network.name

    def delete_network_from_customer(self, network_name, customer_name):
        self._check_connection()
        session = self.Session()
        self._deleter.delete_network_from_customer(session, network_name, customer_name)
        session.close()

    def get_dbc(self, network_name, path_to_dbc):
        network = self.get_network(network_name)
        if network is None:
            return
        self._generator.write(network, path_to_dbc)

    def get_customer_dbc(self, customer_name, network_name, path_to_dbc):
        self._check_connection()
        session = self.Session()
        network = self._reader.get_network_from_customer(session, customer_name, network_name)
        self._generator.write(network, path_to_dbc)
        session.close()

    def add_dbc(self, path_to_dbc, name=None):
        network = self._parser.parse(path_to_dbc)
        if name is not None:
            network.name = name
        self.add_network(network)
        return network.name

    def update_dbc(self, network_name, path_to_dbc):
        # TODO remove this! If problem occurs during parsing dbc then deleted network won't be rollbacked!
        self._check_connection()
        session = self.Session()
        # Customers provided
        deleted_id, customer_names = self._deleter.delete_network(session, network_name, remove_from_merged=False)
        if deleted_id == 0:
            return
        network = self._parser.parse(path_to_dbc)
        network.name = network_name
        self._writer.add_network(session, network, deleted_id)
        for customer_name in customer_names:
            self._writer.add_network_to_customer(session, self._reader.get_network(session, network_name), customer_name)
        session.close()

    def create_merged(self, merged_name, names_to_merge, append=False):
        self._check_connection()
        session = self.Session()
        self._merger.create(session, merged_name, names_to_merge, append=append)
        session.close()

    def remove_from_merged(self, merged_name, names_to_remove):
        self._check_connection()
        session = self.Session()
        self._merger.remove(session, merged_name, names_to_remove)
        session.close()

    def get_merged_network(self, merged_name):
        self._check_connection()
        session = self.Session()
        merged_network = self._merger.get(session, merged_name)
        session.close()
        return merged_network

    def get_merged_dbc(self, merged_name, path_to_dbc):
        network = self.get_merged_network(merged_name)
        self._generator.write(network, path_to_dbc)

    def list_networks(self):
        self._check_connection()
        session = self.Session()
        list_ = self._reader.list_networks(session)
        session.close()
        return list_

    def list_customers(self):
        self._check_connection()
        session = self.Session()
        list_ = self._reader.list_customers(session)
        session.close()
        return list_

    def list_customer_networks(self, customer_name):
        self._check_connection()
        session = self.Session()
        list_ = self._reader.list_customer_networks(session, customer_name)
        session.close()
        return list_

    def _check_connection(self):
        if not self.connected:
            self.logger.error('Not connected to a database!')
            raise NotConnectedError('Not connected to a database')


if __name__ == '__main__':
    cdb = CanDatabaseHandler()
    cdb.connect('sample.db')
    dbcs = [os.path.splitext(f)[0]
            for f in os.listdir('dbc/')
            if os.path.splitext(f)[1].lower() == '.dbc'
           and f != 'AC100_SMess_P2.dbc']
    for dbc in dbcs:
        nwn = cdb.add_dbc('dbc/' + dbc + '.dbc')
        cdb.get_dbc(nwn,  'gen/' + dbc + '.dbc')
    fusion_dbcs = ['A087MB_V3.2_MH11_truck_30obj_2',
                   'AC100_SMess_P0',
                   'Video_Fusion_Protocol',
                   'Bendix_Info2',
                   'Bendix_Info3']
    cdb.create_merged('fusion_can', fusion_dbcs)
    cdb.get_merged_dbc('fusion_can', 'gen/fusion_can_old.dbc')
    cdb.update_dbc('AC100_SMess_P0', 'dbc/AC100_SMess_P2.dbc')
    cdb.get_merged_dbc('fusion_can', 'gen/fusion_can_new.dbc')
    # cdb = CanDatabaseHandler('sample.db')

