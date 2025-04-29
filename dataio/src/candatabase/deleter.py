from sqlalchemy.orm.exc import NoResultFound
import tables as tbl
from utils import rollback_on_exception


class CanDatabaseDeleter(object):
    def __init__(self, logger):
        self.logger = logger

    @rollback_on_exception
    def delete_network(self, session, network_name, remove_from_merged=True):
        self.logger.info("Deleting network: '{}'...".format(network_name))
        # delete network
        try:
            invalid_network_id = session.query(tbl.Network.id).filter(
                tbl.Network.name == network_name).one()[0]
        except NoResultFound:
            self.logger.error('Network: {} not found in database'.format(network_name))
            return 0, []
        # get customer names before deleting
        customer_ids = [r[0] for r in session.query(tbl.CustomerNetworkNodeMessageSignal.customerid).filter(
            tbl.CustomerNetworkNodeMessageSignal.networkid == invalid_network_id).distinct().all()]
        customer_names = [r[0] for r in session.query(tbl.Customer.name).filter(
            tbl.Customer.id.in_(customer_ids)).all()]
        # start deleting
        c = session.query(tbl.Network).filter(
            tbl.Network.id == invalid_network_id).delete(synchronize_session=False)
        if c == 0:
            self.logger.error('Could not delete network: {}'.format(network_name))
            return 0, []
        self.logger.debug('Deleted network with id: {}'.format(invalid_network_id))
        # delete network from merged_network
        if remove_from_merged:
            merged_ids = [r.mergedid for r in session.query(tbl.MergedNetwork).filter(
                    tbl.MergedNetwork.networkid==invalid_network_id).all()]
            merged_names = [r.name for r in session.query(tbl.Merged).filter(
                    tbl.Merged.id.in_(merged_ids))]
            if len(merged_ids) > 0:
                self.logger.warning("Removing '{}' from merged networks: '{}'".format(
                        network_name, "', '".join(merged_names)))
            session.query(tbl.MergedNetwork).filter(
                    tbl.MergedNetwork.networkid==invalid_network_id).delete(synchronize_session=False)
        # get ids of other networks
        valid_network_ids = [r[0] for r in session.query(tbl.Network.id, tbl.Network.name)
                             if r[1] != network_name]
        ac = session.query(tbl.AttributeNetwork).filter(
                tbl.AttributeNetwork.ownerid.notin_(valid_network_ids)).delete(synchronize_session=False)
        self.logger.debug('Remaining networks: {}'.format(', '.join([str(i) for i in valid_network_ids])))
        # cleanup nodes
        valid_node_ids = [r[0] for r in session.query(tbl.NetworkMessageNode.nodeid).filter(
                tbl.NetworkMessageNode.networkid.in_(valid_network_ids)).distinct().all()]
        valid_node_ids += [1]  # Vector__XXX
        c = session.query(tbl.Node).filter(
                tbl.Node.id.notin_(valid_node_ids)).delete(synchronize_session=False)
        ac += session.query(tbl.AttributeNode).filter(
                tbl.AttributeNode.ownerid.notin_(valid_node_ids)).delete(synchronize_session=False)
        self.logger.debug('Deleted {} nodes'.format(c))
        # cleanup environment variables and vals
        valid_evv_ids = [r[0] for r in session.query(tbl.EnvVar.id).filter(
                tbl.EnvVar.nodeid.in_(valid_node_ids))]
        ec = session.query(tbl.EnvVar).filter(
                tbl.EnvVar.id.notin_(valid_evv_ids)).delete(synchronize_session=False)
        evc = session.query(tbl.EnvVarVal).filter(
                tbl.EnvVarVal.envvarid.notin_(valid_evv_ids)).delete(synchronize_session=False)
        self.logger.debug('Deleted {} environment variables and {} values'.format(ec, evc))
        # cleanup messages
        all_message_ids = [r.messageid for r in session.query(tbl.NetworkMessageNode)]
        valid_message_ids = [r.messageid for r in session.query(tbl.NetworkMessageNode).filter(
                tbl.NetworkMessageNode.networkid.in_(valid_network_ids)).distinct().all()]
        invalid_message_ids = [i for i in all_message_ids if i not in valid_message_ids]
        c = 0
        invalid_signal_ids = []
        for iid in invalid_message_ids:
            c += session.query(tbl.Message).filter(
                    tbl.Message.id == iid).delete(synchronize_session=False)
            ac += session.query(tbl.AttributeMessage).filter(
                    tbl.AttributeMessage.ownerid == iid).delete(synchronize_session=False)
            # signal stuff
            invalid_signals = session.query(tbl.Signal).filter(
                tbl.Signal.messageid == iid).distinct().all()
            invalid_signal_ids += [s.id for s in invalid_signals]
        self.logger.debug('Deleted {} messages'.format(c))
        # cleanup signals and vals
        sc, vc = 0, 0
        for sid in invalid_signal_ids:
            sc += session.query(tbl.Signal).filter(
                tbl.Signal.id == sid).delete(synchronize_session=False)
            vc += session.query(tbl.Val).filter(
                tbl.Val.signalid == sid).delete(synchronize_session=False)
            ac += session.query(tbl.AttributeSignal).filter(
                tbl.AttributeSignal.ownerid == sid).delete(synchronize_session=False)
        self.logger.debug('Deleted {} signals'.format(sc))
        self.logger.debug('Deleted {} vals of deleted signals'.format(vc))
        self.logger.debug('Deleted {} attributes'.format(ac))
        # cleanup networkmessagenodes
        c = session.query(tbl.NetworkMessageNode).filter(
                tbl.NetworkMessageNode.networkid.notin_(valid_network_ids)).delete(synchronize_session=False)
        self.logger.debug('Deleted {} NetworkMessageNode entries'.format(c))
        # cleanup attribute definitions
        c = 0
        for DefClass in (tbl.NetworkAttribute, tbl.NodeAttribute,
                         tbl.MessageAttribute, tbl.SignalAttribute):
            c += session.query(DefClass).filter(
                    DefClass.networkid.notin_(valid_network_ids)).delete(synchronize_session=False)
        self.logger.debug('Deleted {} attribute definitions'.format(c))
        # cleanup customernetworknodemessagesignals
        c = session.query(tbl.CustomerNetworkNodeMessageSignal).filter(
            tbl.CustomerNetworkNodeMessageSignal.networkid.notin_(valid_network_ids)).delete(synchronize_session=False)
        self.logger.debug('Deleted {} CustomerNetworkNodeMessageSignal entries'.format(c))
        # commit deletions
        session.commit()
        self.logger.debug("'{}' successfully deleted".format(network_name))
        return invalid_network_id, customer_names

    @rollback_on_exception
    def delete_merged(self, session, merged_name):
        self.logger.info("Deleting merged network '{}'...".format(merged_name))
        try:
            deleted_merged = session.query(tbl.Merged).filter(
                    tbl.Merged.name == merged_name).one()
        except NoResultFound:
            self.logger.error('Merged network: {} not found in database'.format(merged_name))
            return 0
        invalid_merged_id = deleted_merged.id
        session.delete(deleted_merged)
        if 0:  # TODO
            self.logger.error('Could not delete merged network: {}'.format(merged_name))
            return 0
        c = session.query(tbl.MergedNetwork).filter(
                tbl.MergedNetwork.mergedid==invalid_merged_id).delete(synchronize_session=False)
        self.logger.info('Deleted {} network links'.format(c))
        session.commit()
        return invalid_merged_id

    @rollback_on_exception
    def delete_customer(self, session, customer_name):
        self.logger.info("Deleting customer '{}'...".format(customer_name))
        try:
            deleted_customer = session.query(tbl.Customer).filter(
                tbl.Customer.name == customer_name).one()
        except NoResultFound:
            self.logger.error("Customer: '{}' not found in database".format(customer_name))
            return 0
        invalid_customer_id = deleted_customer.id
        session.delete(deleted_customer)
        if 0:  # TODO
            self.logger.error("Could not delete customer: {}".format(customer_name))
            return 0
        c = session.query(tbl.CustomerNetworkNodeMessageSignal).filter(
            tbl.CustomerNetworkNodeMessageSignal.customerid == invalid_customer_id).delete(synchronize_session=False)

        self.logger.info('Deleted {} customer links'.format(c))
        session.commit()
        return invalid_customer_id

    @rollback_on_exception
    def delete_network_from_customer(self, session, customer, network_name):
        self.logger.info("Deleting network: {} from customer '{}'...".format(network_name, customer.name))
        try:
            network = session.query(tbl.Network).filter(
                tbl.Network.name == network_name).one()
        except NoResultFound:
            self.logger.error('Network not found in database'.format(customer.name))
            return 0
        c = session.query(tbl.CustomerNetworkNodeMessageSignal).filter(
            tbl.CustomerNetworkNodeMessageSignal.customerid == customer.id,
            tbl.CustomerNetworkNodeMessageSignal.networkid == network.id).delete(synchronize_session=False)

        self.logger.info('Deleted {} customer-network links'.format(c))
        session.commit()
        return network.id

