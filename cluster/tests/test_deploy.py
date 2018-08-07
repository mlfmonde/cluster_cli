import json

from unittest import mock

from cluster.client import main
from cluster import cluster
from cluster.tests.cluster_test_case import ClusterTestCase, Counter


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
                    'reponame',
                    'branch',
                    master=None,
                    slave=None,
                    wait=False,
                    timeout=cluster.DEFAULT_TIMEOUT
                )

    def test_command_line_new_service(self):
        with mock.patch(
                'sys.argv',
                [
                    'cluster',
                    'deploy',
                    '--master',
                    'master-node',
                    '--slave',
                    'slave-node',
                    '-w',
                    '-t',
                    '10',
                    'reponame',
                    'branch',
                ]
        ):
            with mock.patch('cluster.cluster.Cluster.deploy') as mo:
                main()
                mo.assert_called_once_with(
                    'reponame',
                    'branch',
                    master='master-node',
                    slave='slave-node',
                    wait=True,
                    timeout=10
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
                wait=False,
                timeout=cluster.DEFAULT_TIMEOUT
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
                wait=False,
                timeout=cluster.DEFAULT_TIMEOUT
            )

    def test_deploy_master_slave_force_master_on_same_node(self):
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
                wait=False,
                timeout=cluster.DEFAULT_TIMEOUT
            )

    def test_deploy_master_slave_force_master_on_current_slave(self):
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
                wait=False,
                timeout=cluster.DEFAULT_TIMEOUT
            )

    def test_deploy_master_slave_force_master_on_new_node(self):
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
                wait=False,
                timeout=cluster.DEFAULT_TIMEOUT
            )

    def test_deploy_master_slave_force_master_slave_new_nodes(self):
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
                wait=False,
                timeout=cluster.DEFAULT_TIMEOUT
            )

    def test_deploy_master_slave_force_master_slave_same_nodes(self):
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
                wait=False,
                timeout=cluster.DEFAULT_TIMEOUT
            )

    def test_deploy_master_slave_force_master_slave_switch_nodes(self):
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
                wait=False,
                timeout=cluster.DEFAULT_TIMEOUT
            )

    def test_deploy_master_slave_force_master_on_same_nodes_name(self):
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

    def test_deploy_master_only_force_master_same_master(self):
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
                wait=False,
                timeout=cluster.DEFAULT_TIMEOUT
            )

    def test_deploy_master_only_force_master_new_master(self):
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
                wait=False,
                timeout=cluster.DEFAULT_TIMEOUT
            )

    def test_deploy_master_only_force_slave_becomes_replicate(self):
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
                wait=False,
                timeout=cluster.DEFAULT_TIMEOUT
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

    def test_deploy_master_slave_force_slave_new_nodes(self):
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
                wait=False,
                timeout=cluster.DEFAULT_TIMEOUT
            )

    def test_deploy_master_slave_force_slave_same_node(self):
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
                wait=False,
                timeout=cluster.DEFAULT_TIMEOUT
            )

    def test_deploy_master_slave_force_slave_switch_nodes(self):
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
                wait=False,
                timeout=cluster.DEFAULT_TIMEOUT
            )

    def test_timeout(self):
        self.mocked_consul.configure_mock(**{
            'kv.find.return_value': {
                "app/repo-name_branch-name.12345": json.dumps(
                    self.get_mock_data()
                )
            }
        })

        def kv_get(key):
            return None

        self.mocked_consul.configure_mock(**{
            'kv.get.side_effect': kv_get
        })
        self.assertRaises(
            TimeoutError,
            self.cluster.deploy,
            'repo-name',
            'branch-name',
            wait=True,
            timeout=2
        )

    def test_wait(self):
        self.mocked_consul.configure_mock(**{
            'kv.find.return_value': {
                "app/repo-name_branch-name.12345": json.dumps(
                    self.get_mock_data()
                )
            }
        })

        def kv_get(key):
            if Counter.get('test_wait') > 2:
                return json.dumps(self.get_mock_data())
            return None

        self.mocked_consul.configure_mock(**{
            'kv.get.side_effect': kv_get
        })
        self.cluster.deploy(
            'repo-name', 'branch-name', wait=True
        )

    def test_wait_existing_app(self):
        self.mocked_consul.configure_mock(**{
            'kv.find.return_value': {
                "app/repo-name_branch-name.12345": json.dumps(
                    self.get_mock_data()
                )
            }
        })

        def kv_get(key):
            if Counter.get('test_wait_existing_app') > 2:
                return json.dumps(self.get_mock_data(
                    extra={'deploy_date': "2018-08-05T224230.000000"})
                )
            return json.dumps(self.get_mock_data())

        self.mocked_consul.configure_mock(**{
            'kv.get.side_effect': kv_get
        })
        self.cluster.deploy(
            'repo-name', 'branch-name', wait=True, timeout=6
        )

    def test_deploy_new_service(self):
        self.mocked_consul.configure_mock(**{
            'kv.find.return_value': {}
        })
        with mock.patch('cluster.cluster.Cluster._deploy') as mo:
            self.cluster.deploy(
                'ssh://git@git.example.org/namespace/project.git',
                'branch-name',
                master='node-1'
            )

            mo.assert_called_once_with(
                'app/project_branch-name.a02f7',
                "ssh://git@git.example.org/namespace/project",
                'branch-name',
                'node-1',
                slave=None,
                wait=False,
                timeout=cluster.DEFAULT_TIMEOUT
            )

    def test_deploy_new_service_no_nodes(self):
        self.mocked_consul.configure_mock(**{
            'kv.find.return_value': {}
        })
        self.assertRaises(
            RuntimeError,
            self.cluster.deploy,
            'repo-name',
            'branch-name'
        )

    def test_to_many_apps_found(self):
        value_branch = {
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
        value_branch2 = {
            "repo_url":
                "ssh://git@git.example.org:2222/services/repo-name",
            "branch": "branch-name2",
            "deploy_date": "2018-08-05T224229.591386",
            "deploy_id": "39c4807d-100f-5566-27e5-fbc65d5c5207",
            "previous_deploy_id":
                "d48ee41f-ded6-3db4-afb6-b160568f7bd7",
            "master": "node-1",
            "slave": "node-2"
        }
        self.mocked_consul.configure_mock(**{
            'kv.find.return_value': {
                "app/repo-name_branch-name.12345": json.dumps(value_branch),
                "app/repo-name_branch-name2.12345": json.dumps(value_branch2)
            }
        })
        self.assertRaises(
            RuntimeError,
            self.cluster.deploy,
            'repo-name',
            'branch-name'
        )
