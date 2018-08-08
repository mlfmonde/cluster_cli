import json

from unittest import mock

from cluster.client import main
from cluster import cluster
from cluster.tests.cluster_test_case import ClusterTestCase, Counter


class TestMoveMastersFrom(ClusterTestCase):

    def test_command_line(self):
        with mock.patch(
                'sys.argv',
                [
                    'cluster',
                    'move-masters-from',
                    'node-1',
                    '--master',
                    'node-2',
                    '--wait',
                    '-t',
                    '5'
                ]
        ):
            with mock.patch('cluster.cluster.Cluster.move_masters_from') as mo:
                main()
                mo.assert_called_once_with(
                    'node-1',
                    master='node-2',
                    wait=True,
                    timeout=5
                )

    def test_move_masters_from(self):
        self.init_mocks(extra={
            "master": 'node-1',
            "slave": 'node-2',
        })
        with mock.patch('cluster.cluster.Cluster._deploy') as mo:
            self.cluster.move_masters_from('node-1', master='node-3')
            mo.assert_has_calls(
                [
                    mock.call(
                        'app/repo-name_branch-name.739a5',
                        'ssh://git@git.example.org:2222/services/repo-name',
                        'branch-name',
                        'node-2',
                        slave='node-1',
                        wait=False,
                        timeout=cluster.DEFAULT_TIMEOUT,
                    ),
                    mock.call(
                        'app/migrate-repo_qualif.12345',
                        'ssh://git@git.example.org:2222/services/repo-name',
                        'qualif',
                        'node-2',
                        slave='node-1',
                        wait=False,
                        timeout=cluster.DEFAULT_TIMEOUT,
                    ),
                    mock.call(
                        'app/migrate-repo_prod.12345',
                        'ssh://git@git.example.org:2222/services/repo-name',
                        'prod',
                        'node-2',
                        slave='node-1',
                        wait=False,
                        timeout=cluster.DEFAULT_TIMEOUT,
                    ),
                ],
                any_order=True
            )

    def test_move_masters_from_with_no_slave(self):
        self.init_mocks(extra={
            "master": 'node-1',
            "slave": None,
        })
        with mock.patch('cluster.cluster.Cluster._deploy') as mo:
            self.cluster.move_masters_from('node-1', master='node-3')
            mo.assert_has_calls(
                [
                    mock.call(
                        'app/repo-name_branch-name.739a5',
                        'ssh://git@git.example.org:2222/services/repo-name',
                        'branch-name',
                        'node-3',
                        slave=None,
                        wait=False,
                        timeout=cluster.DEFAULT_TIMEOUT,
                    ),
                    mock.call(
                        'app/migrate-repo_qualif.12345',
                        'ssh://git@git.example.org:2222/services/repo-name',
                        'qualif',
                        'node-3',
                        slave=None,
                        wait=False,
                        timeout=cluster.DEFAULT_TIMEOUT,
                    ),
                    mock.call(
                        'app/migrate-repo_prod.12345',
                        'ssh://git@git.example.org:2222/services/repo-name',
                        'prod',
                        'node-3',
                        slave=None,
                        wait=False,
                        timeout=cluster.DEFAULT_TIMEOUT,
                    ),
                ],
                any_order=True
            )

    def test_move_masters_from_with_unkwonw_node(self):
        self.init_mocks(extra={
            "master": 'node-1',
            "slave": None,
        })
        self.assertRaises(
            RuntimeError,
            self.cluster.move_masters_from,
            'node-1',
            master='node-10'
        )

    def test_move_masters_from_with_wrong_master(self):
        self.init_mocks(extra={
            "master": 'node-1',
            "slave": None,
        })
        self.assertRaises(
            RuntimeError,
            self.cluster.move_masters_from,
            'node-1',
            master='node-1'
        )

    def test_move_masters_from_slaveless_service_without_default_master(self):
        self.init_mocks(extra={
            "master": 'node-1',
            "slave": None,
        })
        self.assertRaises(
            RuntimeError,
            self.cluster.move_masters_from,
            'node-1',
        )
