from unittest import mock

from cluster.client import main
from cluster.tests.cluster_test_case import ClusterTestCase


class TestDeploy(ClusterTestCase):

    def init_mock_kv_find(self):
        self.mocked_consul.configure_mock(**{
            'kv.find.return_value': {
                "app/repo-name_branch-name.12345": """{
                    "repo_url":
                        "ssh://git@git.example.org:2222/services/repo-name",
                    "branch": "branch-name",
                    "deploy_date": "2018-08-05T224229.591386",
                    "deploy_id": "39c4807d-100f-5566-27e5-fbc65d5c5207",
                    "previous_deploy_id":
                        "d48ee41f-ded6-3db4-afb6-b160568f7bd7",
                    "master": "node-1",
                    "slave": "node-2"
                }"""
            }
        })

    def init_mock_kv_get(self):
        self.mocked_consul.configure_mock(**{
            'kv.get.return_value': """{
                "repo_url":
                    "ssh://git@git.example.org:2222/services/repo-name",
                "branch": "branch-name",
                "deploy_date": "2018-08-05T224229.591386",
                "deploy_id": "39c4807d-100f-5566-27e5-fbc65d5c5207",
                "previous_deploy_id":
                    "d48ee41f-ded6-3db4-afb6-b160568f7bd7",
                "master": "node-1",
                "slave": "node-2"
            }"""
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
        self.init_mock_kv_find()
        self.init_mock_kv_get()
        self.cluster.deploy('repo-name', 'branch-name')

    def test_deploy_switch(self):
        self.init_mock_kv_find()
        self.init_mock_kv_get()
        with mock.patch('cluster.cluster.Cluster._deploy') as mo:
            self.cluster.deploy('repo-name', 'branch-name')
            mo.assert_called_once_with(
                'app/repo-name_branch-name.12345',
                "ssh://git@git.example.org:2222/services/repo-name",
                'branch-name',
                'node-2',
                slave='node-1',
            )
