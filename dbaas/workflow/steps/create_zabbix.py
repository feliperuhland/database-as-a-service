# -*- coding: utf-8 -*-
import logging
from base import BaseStep
from dbaas_zabbix.provider import ZabbixProvider


LOG = logging.getLogger(__name__)


class CreateZabbix(BaseStep):

    def __unicode__(self):
        return "Creating zabbix monitoring..."

    def do(self, workflow_dict):
        try:

            if not 'databaseinfra' in workflow_dict:
                return False

            LOG.info("Creating zabbix monitoring...")

            ZabbixProvider().create_monitoring(dbinfra=workflow_dict['databaseinfra'])

            return True
        except Exception, e:
            print e
            return False

    def undo(self, workflow_dict):
        try:
            if not 'databaseinfra' in workflow_dict:
                return False

            LOG.info("Destroying zabbix monitoring...")

            ZabbixProvider().destroy_monitoring(dbinfra=workflow_dict['databaseinfra'])

            return True
        except Exception, e:
            print e
            return False
