from sqlalchemy.orm.exc import NoResultFound
import tables as tbl
from utils import rollback_on_exception
from reader import CanDatabaseReader
from deleter import CanDatabaseDeleter


class CanDatabaseMerger(object):
    def __init__(self, logger):
        self.logger = logger

    @rollback_on_exception
    def create(self, session, name, network_names, append=False, protocol=None, version=None, comment=None):
        # fill default values
        if protocol is None:
            protocol = 'ExtendedCan'
        if version is None:
            version = '1.0'
        if comment is None:
            comment = "merged from '{}'".format("', '".join(network_names))
        # create merged row
        merged = session.query(tbl.Merged).filter(
                tbl.Merged.name==name).one_or_none()
        if merged is None:
            self.logger.info("Creating merged network: '{}'...".format(name))
            merged = tbl.Merged(name=name,
                            protocol=protocol,
                            version_string=version,
                            comment=comment)
            session.add(merged)
            session.flush()
            mode = 'Merging'
        elif not append:
            self.logger.error("Merged network '{}' already exists.\nConsider appending".format(name))
            return
        else:
            mode = 'Appending'
            self.logger.info("Merged network '{}' already exists".format(name))
        # create merged_network relations
        networks = session.query(tbl.Network).filter(
                tbl.Network.name.in_(network_names)).all()
        if len(networks) < 1:
            self.logger.error('None of the given networks found')
            return False
        if len(networks) < len(network_names):
            missing = [n for n in network_names if n not in [ne.name for ne in networks]]
            self.logger.warning("Missing networks: '{}'".format("', '".join(missing)))
        if len(networks) > len(network_names):
            duplicates = [n for n in network_names if network_names.count(n) > 1]
            self.logger.error("Duplicate network names: '{}'".format("', '".join(duplicates)))
            return
        for network in networks:
            mn = session.query(tbl.MergedNetwork).filter(
                    tbl.MergedNetwork.mergedid==merged.id,
                    tbl.MergedNetwork.networkid==network.id).one_or_none()
            if mn is None:
                self.logger.info(mode + " '" + network.name + "'...")
                session.add(tbl.MergedNetwork(mergedid=merged.id, networkid=network.id))
                session.flush()
            else:
                self.logger.info("'{}' already merged, skipping".format(network.name))
        session.commit()
        self.logger.debug("'{}' successfully created".format(name))
        return

    @rollback_on_exception
    def get(self, session, name):
        self.logger.info("Constructing temporary network: '{}'...".format(name))
        # get merged
        try:
            merged = session.query(tbl.Merged).filter(tbl.Merged.name == name).one()
        except NoResultFound:
            self.logger.error("No merged entry found for '{}'".format(name))
            return None
        self.logger.debug("Found merged: '{}'".format(name))
        # create temporary network for merged
        tmp_network = tbl.Network(name=name,
                                  protocol=merged.protocol,
                                  version_string=merged.version_string,
                                  comment=merged.comment)
        session.add(tmp_network)
        session.flush()
        self.logger.debug("Inserted temp network '{}' with id: {}".format(name, tmp_network.id))
        # create temporary network_message_node rows for merged
        network_ids = [r[0] for r in session.query(tbl.MergedNetwork.networkid).filter(
            tbl.MergedNetwork.mergedid == merged.id).all()]
        self.logger.debug('Merging networks: {}'.format(', '.join([str(i) for i in network_ids])))
        orig_rows = session.query(tbl.NetworkMessageNode).filter(
                tbl.NetworkMessageNode.networkid.in_(network_ids)).all()
        inserted = []
        message_data = []
        for row in orig_rows:
            if (tmp_network.id, row.messageid, row.nodeid, row.dir) in inserted:
                # already copied
                continue

            # Checking for same can id usages in different networks
            # Only check transmitting rows
            if row.dir == tbl.TX:
                temp_message_id, temp_name = session.query(tbl.Message.can_id, tbl.Message.name).filter(
                    tbl.Message.id == row.messageid).one()
                for m_id, n, net_id in message_data:
                    # Using the same id, having different name in different networks
                    # TODO look at this
                    if temp_message_id == m_id and temp_name != n and row.networkid != net_id:
                        self.logger.warning("Messages have the same id (0x{:08x}), {} <-> {}".format(
                            temp_message_id & 0x7fffffff, temp_name, n))
                        break
                message_data += [[temp_message_id, temp_name, row.networkid]]

            inserted.append((tmp_network.id, row.messageid, row.nodeid, row.dir))
            session.add(tbl.NetworkMessageNode(networkid=tmp_network.id,
                                               messageid=row.messageid,
                                               nodeid=row.nodeid,
                                               dir=row.dir))
        self.logger.debug('Added {} temporary NetworkMessageNode rows'.format(len(inserted)))
        session.flush()
        # create temporary attribute definitions
        self.logger.debug('Adding temporary attribute definitions...')
        for AttrDef in (tbl.NetworkAttribute, tbl.NodeAttribute,
                        tbl.MessageAttribute, tbl.SignalAttribute):
            orig_rows = session.query(AttrDef).filter(
                    AttrDef.networkid.in_(network_ids)).all()
            inserted = []
            for row in orig_rows:
                self.logger.debug('adding {}...'.format(row.name))
                if row.name in inserted:
                    # already copied
                    self.logger.debug('skipping {}, it\'s already added'.format(row.name))
                    continue
                inserted.append(row.name)
                session.add(AttrDef(name=row.name,
                              type=row.type,
                              entries=row.entries,
                              default_=row.default_,
                              networkid=tmp_network.id))
                self.logger.debug('added {}'.format(row.name))
            session.flush()
            self.logger.debug('Added {} temporary {} rows'.format(len(inserted), AttrDef.__name__))
        # create temporary network attributes
        orig_rows = session.query(tbl.AttributeNetwork).filter(
                tbl.AttributeNetwork.ownerid.in_(network_ids)).all()
        inserted = []
        for row in orig_rows:
            if (tmp_network.id, row.attributeid) in inserted:
                # already copied
                # NOTE Since only the name and the value are checked, attributes, which are defined
                # in more than one network will be copied with the value in the first network in
                # the list.
                continue
            inserted.append((tmp_network.id, row.attributeid))
            session.add(tbl.AttributeNetwork(ownerid=tmp_network.id,
                                             attributeid=row.attributeid,
                                             val=row.val,
                                             networkid=tmp_network.id))
        session.commit()
        # get temporary merged network
        rd = CanDatabaseReader(self.logger)
        merged_network = rd.get_network(session, name)
        # delete temporary network
        dl = CanDatabaseDeleter(self.logger)
        dl.delete_network(session, name)
        return merged_network

    @rollback_on_exception
    def remove(self, session, merged_name, network_names):
        self.logger.info("Removing the following networks from '{}': '{}'".format(
                merged_name, "', '".join(network_names)))
        merged = session.query(tbl.Merged).filter(
                tbl.Merged.name==merged_name).one()
        networks = session.query(tbl.Network).filter(
                tbl.Network.name.in_(network_names)).all()
        for network in networks:
            row = session.query(tbl.MergedNetwork).filter(
                    tbl.MergedNetwork.networkid==network.id,
                    tbl.MergedNetwork.mergedid==merged.id).one_or_none()
            if row is None:
                self.logger.warning("Network '{}' not found in merged".format(network.name))
                continue
            session.delete(row)
            self.logger.info("Removed '{}' from merged".format(network.name))
        session.commit()
