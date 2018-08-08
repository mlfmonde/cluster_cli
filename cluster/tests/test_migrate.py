import json

from unittest import mock

from cluster.client import main
from cluster import cluster
from cluster.tests.cluster_test_case import ClusterTestCase, Counter


class TestMigrate(ClusterTestCase):

    def test_command_line(self):
        with mock.patch(
                'sys.argv',
                [
                    'cluster',
                    'migrate',
                    'reponame',
                    'source-branch',
                    'target-branch',
                    '--target-repo',
                    'reponame2',
                    '--wait',
                    '-t',
                    '5'
                ]
        ):
            with mock.patch('cluster.cluster.Cluster.migrate') as mo:
                main()
                mo.assert_called_once_with(
                    'reponame',
                    'source-branch',
                    'target-branch',
                    target_repo='reponame2',
                    wait=True,
                    timeout=5
                )

    def test_migrate(self):
        self.init_mocks(extra={
            "repo_url": "ssh://git@git.example.org:2222/services/migrate-repo"}
        )
        with mock.patch('cluster.cluster.Cluster._fire_event') as mo:
            self.cluster.migrate('migrate-repo', 'prod', 'qualif')
            mo.assert_called_once_with(
                'app/migrate-repo_qualif.12345',
                'migrate',
                json.dumps(
                    {
                        'repo': 'ssh://git@git.example.org:2222/services/'
                                'migrate-repo',
                        'branch': 'prod',
                        'target': {
                            'repo': 'ssh://git@git.example.org:2222/services/'
                                    'migrate-repo',
                            'branch': 'qualif'
                        }
                    }
                ),
                False,
                cluster.Cluster.migrate_finished,
                cluster.DEFAULT_TIMEOUT
            )

    def test_source_app_not_found(self):
        self.init_mocks()
        self.assertRaises(
            RuntimeError,
            self.cluster.migrate,
            'migrate-repo',
            'other',
            'qualif'
        )

    def test_target_app_not_found(self):
        self.init_mocks()
        self.assertRaises(
            RuntimeError,
            self.cluster.migrate,
            'migrate-repo',
            'prod',
            'other'
        )

    def test_forbidden_target_branch_name(self):
        self.init_mocks()
        self.assertRaises(
            RuntimeError,
            self.cluster.migrate,
            'migrate-repo',
            'qualif',
            'prod'
        )
        self.assertRaises(
            RuntimeError,
            self.cluster.migrate,
            'migrate-repo',
            'qualif',
            'production'
        )

    def test_finished_migrate(self):
        self.init_mocks()

        def kv_get_record(_):
            call_number = Counter.get('test_finished_migrate')
            if call_number > 1 and call_number <= 3:
                return True
            return None

        self.mocked_consul.configure_mock(**{
            'kv.get_record.side_effect': kv_get_record
        })

        self.cluster.migrate(
            'migrate-repo',
            'prod',
            'branch-name',
            target_repo='repo-name',
            wait=True
        )
