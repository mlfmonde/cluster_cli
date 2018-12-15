import json

from unittest import mock
from testfixtures import OutputCapture

from cluster.client import main
from cluster import cluster
from cluster.tests.cluster_test_case import ClusterTestCase, Counter


class TestDeploy(ClusterTestCase):

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
                    no_wait=False,
                    timeout=cluster.DEFAULT_TIMEOUT,
                    ask_user=True,
                    update=False
                )

    def test_command_line_new_service(self):
        with mock.patch(
                'sys.argv',
                [
                    'cluster',
                    '-y',
                    'deploy',
                    '--master',
                    'master-node',
                    '--slave',
                    'slave-node',
                    '-d',
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
                    no_wait=True,
                    timeout=10,
                    ask_user=False,
                    update=False
                )

    def test_command_line_update_short(self):
        with mock.patch(
                'sys.argv',
                [
                    'cluster',
                    '-y',
                    'deploy',
                    '--master',
                    'master-node',
                    '--slave',
                    'slave-node',
                    '-d',
                    '-t',
                    '10',
                    'reponame',
                    'branch',
                    '-u'
                ]
        ):
            with mock.patch('cluster.cluster.Cluster.deploy') as mo:
                main()
                mo.assert_called_once_with(
                    'reponame',
                    'branch',
                    master='master-node',
                    slave='slave-node',
                    no_wait=True,
                    timeout=10,
                    ask_user=False,
                    update=True
                )

    def test_command_line_update_long(self):
        with mock.patch(
                'sys.argv',
                [
                    'cluster',
                    '-y',
                    'deploy',
                    '--master',
                    'master-node',
                    '--slave',
                    'slave-node',
                    '-d',
                    '-t',
                    '10',
                    'reponame',
                    'branch',
                    '--update'
                ]
        ):
            with mock.patch('cluster.cluster.Cluster.deploy') as mo:
                main()
                mo.assert_called_once_with(
                    'reponame',
                    'branch',
                    master='master-node',
                    slave='slave-node',
                    no_wait=True,
                    timeout=10,
                    ask_user=False,
                    update=True
                )

    @mock.patch('cluster.util.get_input', return_value='Yes')
    def test_deploy_switch(self, _):
        self.init_mocks()
        with mock.patch('cluster.cluster.Cluster._deploy') as mo:
            self.cluster.deploy('repo-name', 'branch-name')
            mo.assert_called_once_with(
                'app/repo-name_branch-name.739a5',
                "ssh://git@git.example.org:2222/services/repo-name",
                'branch-name',
                'node-2',
                slave='node-1',
                no_wait=False,
                timeout=cluster.DEFAULT_TIMEOUT
            )

    @mock.patch('cluster.util.get_input', return_value='Yes')
    def test_deploy_switch_master_only(self, _):
        self.init_mocks({"slave": None})
        with mock.patch('cluster.cluster.Cluster._deploy') as mo:
            self.cluster.deploy('repo-name', 'branch-name')
            mo.assert_called_once_with(
                'app/repo-name_branch-name.739a5',
                "ssh://git@git.example.org:2222/services/repo-name",
                'branch-name',
                'node-1',
                slave=None,
                no_wait=False,
                timeout=cluster.DEFAULT_TIMEOUT
            )

    @mock.patch('cluster.util.get_input', return_value='Yes')
    def test_deploy_master_slave_force_master_on_same_node(self, _):
        self.init_mocks()
        with mock.patch('cluster.cluster.Cluster._deploy') as mo:
            self.cluster.deploy(
                'repo-name', 'branch-name', master='node-1'
            )
            mo.assert_called_once_with(
                'app/repo-name_branch-name.739a5',
                "ssh://git@git.example.org:2222/services/repo-name",
                'branch-name',
                'node-1',
                slave='node-2',
                no_wait=False,
                timeout=cluster.DEFAULT_TIMEOUT
            )

    @mock.patch('cluster.util.get_input', return_value='Yes')
    def test_deploy_master_slave_force_master_on_current_slave(self, _):
        self.init_mocks()
        with mock.patch('cluster.cluster.Cluster._deploy') as mo:
            self.cluster.deploy(
                'repo-name', 'branch-name', master='node-2'
            )
            mo.assert_called_once_with(
                'app/repo-name_branch-name.739a5',
                "ssh://git@git.example.org:2222/services/repo-name",
                'branch-name',
                'node-2',
                slave='node-1',
                no_wait=False,
                timeout=cluster.DEFAULT_TIMEOUT
            )

    @mock.patch('cluster.util.get_input', return_value='Yes')
    def test_deploy_master_slave_force_master_on_new_node(self, _):
        self.init_mocks()
        with mock.patch('cluster.cluster.Cluster._deploy') as mo:
            self.cluster.deploy(
                'repo-name', 'branch-name', master='node-3'
            )
            mo.assert_called_once_with(
                'app/repo-name_branch-name.739a5',
                "ssh://git@git.example.org:2222/services/repo-name",
                'branch-name',
                'node-3',
                slave='node-1',
                no_wait=False,
                timeout=cluster.DEFAULT_TIMEOUT
            )

    def test_deploy_master_slave_force_master_slave_new_nodes(self):
        self.init_mocks()
        with mock.patch('cluster.cluster.Cluster._deploy') as mo:
            self.cluster.deploy(
                'repo-name',
                'branch-name',
                master='node-3',
                slave='node-4',
                ask_user=False
            )
            mo.assert_called_once_with(
                'app/repo-name_branch-name.739a5',
                "ssh://git@git.example.org:2222/services/repo-name",
                'branch-name',
                'node-3',
                slave='node-4',
                no_wait=False,
                timeout=cluster.DEFAULT_TIMEOUT,
            )

    @mock.patch('cluster.util.get_input', return_value='Yes')
    def test_deploy_master_slave_force_master_slave_same_nodes(self, _):
        self.init_mocks()
        with mock.patch('cluster.cluster.Cluster._deploy') as mo:
            self.cluster.deploy(
                'repo-name', 'branch-name', master='node-1', slave='node-2'
            )
            mo.assert_called_once_with(
                'app/repo-name_branch-name.739a5',
                "ssh://git@git.example.org:2222/services/repo-name",
                'branch-name',
                'node-1',
                slave='node-2',
                no_wait=False,
                timeout=cluster.DEFAULT_TIMEOUT
            )

    @mock.patch('cluster.util.get_input', return_value='Yes')
    def test_deploy_master_slave_force_master_slave_switch_nodes(self, _):
        self.init_mocks()
        with mock.patch('cluster.cluster.Cluster._deploy') as mo:
            self.cluster.deploy(
                'repo-name', 'branch-name', master='node-2', slave='node-1'
            )
            mo.assert_called_once_with(
                'app/repo-name_branch-name.739a5',
                "ssh://git@git.example.org:2222/services/repo-name",
                'branch-name',
                'node-2',
                slave='node-1',
                no_wait=False,
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

    @mock.patch('cluster.util.get_input', return_value='Yes')
    def test_deploy_master_only_force_master_same_master(self, _):
        self.init_mocks({"slave": None})
        with mock.patch('cluster.cluster.Cluster._deploy') as mo:
            self.cluster.deploy(
                'repo-name', 'branch-name', master='node-1'
            )
            mo.assert_called_once_with(
                'app/repo-name_branch-name.739a5',
                "ssh://git@git.example.org:2222/services/repo-name",
                'branch-name',
                'node-1',
                slave=None,
                no_wait=False,
                timeout=cluster.DEFAULT_TIMEOUT
            )

    @mock.patch('cluster.util.get_input', return_value='Yes')
    def test_deploy_master_only_force_master_new_master(self, _):
        self.init_mocks({"slave": None})
        with mock.patch('cluster.cluster.Cluster._deploy') as mo:
            self.cluster.deploy(
                'repo-name', 'branch-name', master='node-2'
            )
            mo.assert_called_once_with(
                'app/repo-name_branch-name.739a5',
                "ssh://git@git.example.org:2222/services/repo-name",
                'branch-name',
                'node-2',
                slave=None,
                no_wait=False,
                timeout=cluster.DEFAULT_TIMEOUT
            )

    @mock.patch('cluster.util.get_input', return_value='Yes')
    def test_deploy_master_only_force_slave_becomes_replicate(self, _):
        self.init_mocks({"slave": None})
        with mock.patch('cluster.cluster.Cluster._deploy') as mo:
            self.cluster.deploy(
                'repo-name', 'branch-name', slave='node-2'
            )

            mo.assert_called_once_with(
                'app/repo-name_branch-name.739a5',
                "ssh://git@git.example.org:2222/services/repo-name",
                'branch-name',
                'node-1',
                slave='node-2',
                no_wait=False,
                timeout=cluster.DEFAULT_TIMEOUT
            )

    @mock.patch('cluster.util.get_input', return_value='Yes')
    def test_deploy_master_only_becomes_replicate_force_slave_conflict_master(
            self, _
    ):
        self.init_mocks({"slave": None})
        self.assertRaises(
            RuntimeError,
            self.cluster.deploy,
            'repo-name',
            'branch-name',
            slave='node-1'
        )

    @mock.patch('cluster.util.get_input', return_value='Yes')
    def test_deploy_master_slave_force_slave_new_nodes(self, _):
        self.init_mocks()
        with mock.patch('cluster.cluster.Cluster._deploy') as mo:
            self.cluster.deploy(
                'repo-name', 'branch-name', slave='node-4'
            )
            mo.assert_called_once_with(
                'app/repo-name_branch-name.739a5',
                "ssh://git@git.example.org:2222/services/repo-name",
                'branch-name',
                'node-2',
                slave='node-4',
                no_wait=False,
                timeout=cluster.DEFAULT_TIMEOUT
            )

    @mock.patch('cluster.util.get_input', return_value='Yes')
    def test_deploy_master_slave_force_slave_same_node(self, _):
        self.init_mocks()
        with mock.patch('cluster.cluster.Cluster._deploy') as mo:
            self.cluster.deploy(
                'repo-name', 'branch-name', slave='node-2'
            )
            mo.assert_called_once_with(
                'app/repo-name_branch-name.739a5',
                "ssh://git@git.example.org:2222/services/repo-name",
                'branch-name',
                'node-1',
                slave='node-2',
                no_wait=False,
                timeout=cluster.DEFAULT_TIMEOUT
            )

    @mock.patch('cluster.util.get_input', return_value='YeS')
    def test_deploy_master_slave_force_slave_switch_nodes(self, _):
        self.init_mocks()
        with mock.patch('cluster.cluster.Cluster._deploy') as mo:
            self.cluster.deploy(
                'repo-name', 'branch-name', slave='node-1'
            )
            mo.assert_called_once_with(
                'app/repo-name_branch-name.739a5',
                "ssh://git@git.example.org:2222/services/repo-name",
                'branch-name',
                'node-2',
                slave='node-1',
                no_wait=False,
                timeout=cluster.DEFAULT_TIMEOUT
            )

    @mock.patch('cluster.util.get_input', return_value='YEs')
    def test_timeout(self, _):
        self.mocked_consul.configure_mock(**{
            'kv.find.return_value': {
                "app/repo-name_branch-name.739a5": json.dumps(
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
            no_wait=False,
            timeout=2
        )

    @mock.patch('cluster.util.get_input', return_value='YEs')
    def test_wait(self, _):
        self.mocked_consul.configure_mock(**{
            'kv.find.return_value': {
                "app/repo-name_branch-name.739a5": json.dumps(
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
            'repo-name', 'branch-name', no_wait=False
        )

    @mock.patch('cluster.util.get_input', return_value='Yes')
    def test_wait_existing_app(self, _):
        self.mocked_consul.configure_mock(**{
            'kv.find.return_value': {
                "app/repo-name_branch-name.739a5": json.dumps(
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
            'repo-name', 'branch-name', no_wait=False, timeout=6
        )

    @mock.patch('cluster.util.get_input', return_value='Yes')
    def test_deploy_new_service(self, _):
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
                no_wait=False,
                timeout=cluster.DEFAULT_TIMEOUT
            )

    @mock.patch('cluster.util.get_input', return_value='no')
    def test_deploy_answer_no(self, _):
        self.init_mocks()
        self.cluster.deploy(
            'ssh://git@git.example.org/namespace/project.git',
            'branch-name',
            master='node-1'
        )
        with OutputCapture() as out:
            # code under test
            self.cluster.move_masters_from('node-1')
            self.assertTrue(
                "Not confirmed, Aborting" in out.captured
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
                "app/repo-name_branch-name.739a5": json.dumps(value_branch),
                "app/repo-name_branch-name2.12345": json.dumps(value_branch2)
            }
        })
        self.assertRaises(
            RuntimeError,
            self.cluster.deploy,
            'repo-name',
            'branch-name'
        )
