# -*- coding: utf-8 -*-
from base import BaseTopology


class BaseMongoDB(BaseTopology):
    def deploy_first_steps(self):
        return (
            'workflow.steps.util.deploy.build_databaseinfra.BuildDatabaseInfra',
            'workflow.steps.mongodb.deploy.create_virtualmachines.CreateVirtualMachine',
            'workflow.steps.util.deploy.create_dns.CreateDns',
            'workflow.steps.util.deploy.create_nfs.CreateNfs',
            'workflow.steps.mongodb.deploy.init_database.InitDatabaseMongoDB',
            'workflow.steps.util.deploy.config_backup_log.ConfigBackupLog',
            'workflow.steps.util.deploy.check_database_connection.CheckDatabaseConnection',
            'workflow.steps.util.deploy.check_dns.CheckDns',
            'workflow.steps.util.deploy.start_monit.StartMonit',
        )

    def deploy_last_steps(self):
        return (
            'workflow.steps.util.deploy.build_database.BuildDatabase',
            'workflow.steps.util.deploy.check_database_binds.CheckDatabaseBinds',
        )

    def get_clone_steps(self):
        return self.deploy_first_steps() + self.deploy_last_steps() + (
            'workflow.steps.util.clone.clone_database.CloneDatabase',
        ) + self.monitoring_steps()


class MongoDBSingle(BaseMongoDB):

    def get_upgrade_steps_extra(self):
        return ('workflow.steps.mongodb.upgrade.vm.ChangeBinaryTo32',) + \
            super(MongoDBSingle, self).get_upgrade_steps_extra() + (
            'workflow.steps.util.database.Start',
            'workflow.steps.util.database.CheckIsUp',
            'workflow.steps.util.database.Stop',
            'workflow.steps.util.database.CheckIsDown',
            'workflow.steps.mongodb.upgrade.vm.ChangeBinaryTo34',
        )

    def get_upgrade_steps_final(self):
        return [{
            'Setting feature compatibility version 3.4': (
                'workflow.steps.mongodb.upgrade.database.SetFeatureCompatibilityVersion34',
            ),
        }] + super(MongoDBSingle, self).get_upgrade_steps_final()

    @property
    def driver_name(self):
        return 'mongodb_single'


class MongoDBReplicaset(BaseMongoDB):

    def get_upgrade_steps_description(self):
        return 'Upgrading to MongoDB 3.2'

    def get_upgrade_steps_extra(self):
        return (
            'workflow.steps.mongodb.upgrade.vm.ChangeBinaryTo32',
            'workflow.steps.util.plan.InitializationForUpgrade',
            'workflow.steps.util.plan.ConfigureForUpgrade',
            'workflow.steps.util.pack.Configure',
        )

    def get_upgrade_steps_final(self):
        return [{
            'Upgrading to MongoDB 3.4': (
                'workflow.steps.util.vm.ChangeMaster',
                'workflow.steps.util.database.Stop',
                'workflow.steps.util.database.CheckIsDown',
                'workflow.steps.mongodb.upgrade.vm.ChangeBinaryTo34',
                'workflow.steps.util.database.Start',
                'workflow.steps.util.database.CheckIsUp',
            ),
        }] + [{
            'Setting feature compatibility version 3.4': (
                'workflow.steps.mongodb.upgrade.database.SetFeatureCompatibilityVersion34',
            ),
        }] + super(MongoDBReplicaset, self).get_upgrade_steps_final()

    def get_add_database_instances_middle_steps(self):
        return (
            'workflow.steps.util.plan.Initialization',
            'workflow.steps.util.plan.Configure',
            'workflow.steps.util.pack.Configure',
            'workflow.steps.mongodb.horizontal_elasticity.database.CreateDataDir',
            'workflow.steps.util.database.Start',
            'workflow.steps.mongodb.horizontal_elasticity.database.AddInstanceToReplicaSet',
        )

    def get_resize_oplog_steps(self):
        return [{
            'Resize oplog': (
                'workflow.steps.util.database.ValidateOplogSizeValue',
                'workflow.steps.util.zabbix.DisableAlarms',
                'workflow.steps.util.db_monitor.DisableMonitoring',
                'workflow.steps.util.vm.ChangeMaster',
                'workflow.steps.util.database.CheckIfSwitchMaster',
                'workflow.steps.util.database.Stop',
                'workflow.steps.util.database.CheckIsDown',
                'workflow.steps.util.plan.ConfigureForResizeLog',
                'workflow.steps.util.database.StartForResizeLog',
                'workflow.steps.util.database.CheckIsUpForResizeLog',
                'workflow.steps.util.database.ResizeOpLogSize',
                'workflow.steps.util.database.Stop',
                'workflow.steps.util.database.CheckIsDown',
                'workflow.steps.util.plan.Configure',
                'workflow.steps.util.database.Start',
                'workflow.steps.util.database.CheckIsUp',
                'workflow.steps.util.db_monitor.EnableMonitoring',
                'workflow.steps.util.zabbix.EnableAlarms',
            )
        }] + self.get_change_parameter_steps_final()

    def get_resize_oplog_steps_and_retry_steps_back(self):
        return self.get_resize_oplog_steps(), 0

    @property
    def driver_name(self):
        return 'mongodb_replica_set'
