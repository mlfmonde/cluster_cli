import json

from unittest import mock

from cluster.client import main
from cluster.tests.cluster_test_case import ClusterTestCase


class TestDeploy(ClusterTestCase):

    def init_mocks(self, extra=None):
        value = self.get_mock_data(extra=extra)
        self.init_mock_kv_find(data=value)
        self.init_mock_kv_get(data=value)

    def get_mock_data(self, extra=None):
        if not extra:
            extra = {}
        value = {
            "repo_url":
                "ssh://git@git.example.org:2222/services/repo-name",
            "branch": "branch-name",
            "deploy_date": "2018-08-05T224229.591386",
            "deploy_id": "39c4807d-100f-5566-27e5-fbc65d5c5207",
            "previous_deploy_id":
                "d48ee41f-ded6-3db4-afb6-b160568f7bd7",
            "master": "node-1",
            "slave": "node-2"
        }
        value.update(extra)
        return value

    def init_mock_kv_find(self, data):
        self.mocked_consul.configure_mock(**{
            'kv.find.return_value': {
                "app/repo-name_branch-name.12345": json.dumps(data)
            }
        })

    def init_mock_kv_get(self, data):
        self.mocked_consul.configure_mock(**{
            'kv.get.return_value': json.dumps(data)
        })

    def test_command_line(self):
        with mock.patch(
                'sys.argv',
                ['cluster', 'deploy', 'reponame', 'branch', ]
        ):
            with mock.patch('cluster.cluster.Cluster.deploy') as mo:
                main()
                mo.assert_called_once_with(
                    'reponame', 'branch', master=None, slave=None
                )

    def test_command_line_new_service(self):
        with mock.patch(
                'sys.argv',
                [
                    'cluster',
                    'deploy',
                    'reponame',
                    'branch',
                    '--master',
                    'master-node',
                    '--slave',
                    'slave-node'
                ]
        ):
            with mock.patch('cluster.cluster.Cluster.deploy') as mo:
                main()
                mo.assert_called_once_with(
                    'reponame',
                    'branch',
                    master='master-node',
                    slave='slave-node'
                )

    def test_deploy(self):
        self.init_mocks()
        self.cluster.deploy('repo-name', 'branch-name')

    def test_deploy_switch(self):
        self.init_mocks()
        with mock.patch('cluster.cluster.Cluster._deploy') as mo:
            self.cluster.deploy('repo-name', 'branch-name')
            mo.assert_called_once_with(
                'app/repo-name_branch-name.12345',
                "ssh://git@git.example.org:2222/services/repo-name",
                'branch-name',
                'node-2',
                slave='node-1',
            )

    def test_deploy_switch_master_only(self):
        self.init_mocks({"slave": None})
        with mock.patch('cluster.cluster.Cluster._deploy') as mo:
            self.cluster.deploy('repo-name', 'branch-name')
            mo.assert_called_once_with(
                'app/repo-name_branch-name.12345',
                "ssh://git@git.example.org:2222/services/repo-name",
                'branch-name',
                'node-1',
                slave=None,
            )

    def test_deploy_master_slave_foce_master_on_same_node(self):
        self.init_mocks()
        with mock.patch('cluster.cluster.Cluster._deploy') as mo:
            self.cluster.deploy(
                'repo-name', 'branch-name', master='node-1'
            )
            mo.assert_called_once_with(
                'app/repo-name_branch-name.12345',
                "ssh://git@git.example.org:2222/services/repo-name",
                'branch-name',
                'node-1',
                slave='node-2',
            )

    def test_deploy_master_slave_foce_master_on_current_slave(self):
        self.init_mocks()
        with mock.patch('cluster.cluster.Cluster._deploy') as mo:
            self.cluster.deploy(
                'repo-name', 'branch-name', master='node-2'
            )
            mo.assert_called_once_with(
                'app/repo-name_branch-name.12345',
                "ssh://git@git.example.org:2222/services/repo-name",
                'branch-name',
                'node-2',
                slave='node-1',
            )

    def test_deploy_master_slave_foce_master_on_new_node(self):
        self.init_mocks()
        with mock.patch('cluster.cluster.Cluster._deploy') as mo:
            self.cluster.deploy(
                'repo-name', 'branch-name', master='node-3'
            )
            mo.assert_called_once_with(
                'app/repo-name_branch-name.12345',
                "ssh://git@git.example.org:2222/services/repo-name",
                'branch-name',
                'node-3',
                slave='node-1',
            )

    def test_deploy_master_slave_foce_master_slave_new_nodes(self):
        self.init_mocks()
        with mock.patch('cluster.cluster.Cluster._deploy') as mo:
            self.cluster.deploy(
                'repo-name', 'branch-name', master='node-3', slave='node-4'
            )
            mo.assert_called_once_with(
                'app/repo-name_branch-name.12345',
                "ssh://git@git.example.org:2222/services/repo-name",
                'branch-name',
                'node-3',
                slave='node-4',
            )

    def test_deploy_master_slave_foce_master_slave_same_nodes(self):
        self.init_mocks()
        with mock.patch('cluster.cluster.Cluster._deploy') as mo:
            self.cluster.deploy(
                'repo-name', 'branch-name', master='node-1', slave='node-2'
            )
            mo.assert_called_once_with(
                'app/repo-name_branch-name.12345',
                "ssh://git@git.example.org:2222/services/repo-name",
                'branch-name',
                'node-1',
                slave='node-2',
            )

    def test_deploy_master_slave_foce_master_slave_switch_nodes(self):
        self.init_mocks()
        with mock.patch('cluster.cluster.Cluster._deploy') as mo:
            self.cluster.deploy(
                'repo-name', 'branch-name', master='node-2', slave='node-1'
            )
            mo.assert_called_once_with(
                'app/repo-name_branch-name.12345',
                "ssh://git@git.example.org:2222/services/repo-name",
                'branch-name',
                'node-2',
                slave='node-1',
            )

    def test_deploy_master_slave_foce_master_on_same_nodes_name(self):
        self.init_mocks()
        self.assertRaises(
            RuntimeError,
            self.cluster.deploy,
            'repo-name',
            'branch-name',
            master='node-1',
            slave='node-1'
        )

    def test_deploy_unknown_master(self):
        self.init_mocks()
        self.assertRaises(
            RuntimeError,
            self.cluster.deploy,
            'repo-name',
            'branch-name',
            master='node-5',
        )

    def test_deploy_unknown_slave(self):
        self.init_mocks()
        self.assertRaises(
            RuntimeError,
            self.cluster.deploy,
            'repo-name',
            'branch-name',
            slave='node-5',
        )

    def test_deploy_master_only_foce_master_same_master(self):
        self.init_mocks({"slave": None})
        with mock.patch('cluster.cluster.Cluster._deploy') as mo:
            self.cluster.deploy(
                'repo-name', 'branch-name', master='node-1'
            )
            mo.assert_called_once_with(
                'app/repo-name_branch-name.12345',
                "ssh://git@git.example.org:2222/services/repo-name",
                'branch-name',
                'node-1',
                slave=None,
            )

    def test_deploy_master_only_foce_master_new_master(self):
        self.init_mocks({"slave": None})
        with mock.patch('cluster.cluster.Cluster._deploy') as mo:
            self.cluster.deploy(
                'repo-name', 'branch-name', master='node-2'
            )
            mo.assert_called_once_with(
                'app/repo-name_branch-name.12345',
                "ssh://git@git.example.org:2222/services/repo-name",
                'branch-name',
                'node-2',
                slave=None,
            )

    def test_deploy_master_only_foce_slave_becomes_replicate(self):
        self.init_mocks({"slave": None})
        with mock.patch('cluster.cluster.Cluster._deploy') as mo:
            self.cluster.deploy(
                'repo-name', 'branch-name', slave='node-2'
            )

            mo.assert_called_once_with(
                'app/repo-name_branch-name.12345',
                "ssh://git@git.example.org:2222/services/repo-name",
                'branch-name',
                'node-1',
                slave='node-2',
            )

    def test_deploy_master_only_becomes_replicate_force_slave_conflict_master(
            self
    ):
        self.init_mocks({"slave": None})
        self.assertRaises(
            RuntimeError,
            self.cluster.deploy,
            'repo-name',
            'branch-name',
            slave='node-1'
        )

    def test_deploy_master_slave_foce_slave_new_nodes(self):
        self.init_mocks()
        with mock.patch('cluster.cluster.Cluster._deploy') as mo:
            self.cluster.deploy(
                'repo-name', 'branch-name', slave='node-4'
            )
            mo.assert_called_once_with(
                'app/repo-name_branch-name.12345',
                "ssh://git@git.example.org:2222/services/repo-name",
                'branch-name',
                'node-2',
                slave='node-4',
            )

    def test_deploy_master_slave_foce_slave_same_node(self):
        self.init_mocks()
        with mock.patch('cluster.cluster.Cluster._deploy') as mo:
            self.cluster.deploy(
                'repo-name', 'branch-name', slave='node-2'
            )
            mo.assert_called_once_with(
                'app/repo-name_branch-name.12345',
                "ssh://git@git.example.org:2222/services/repo-name",
                'branch-name',
                'node-1',
                slave='node-2',
            )

    def test_deploy_master_slave_foce_slave_switch_nodes(self):
        self.init_mocks()
        with mock.patch('cluster.cluster.Cluster._deploy') as mo:
            self.cluster.deploy(
                'repo-name', 'branch-name', slave='node-1'
            )
            mo.assert_called_once_with(
                'app/repo-name_branch-name.12345',
                "ssh://git@git.example.org:2222/services/repo-name",
                'branch-name',
                'node-2',
                slave='node-1',
            )
