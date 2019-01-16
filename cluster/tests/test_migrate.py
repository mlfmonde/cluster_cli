import json

from testfixtures import OutputCapture
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
                    '-y',
                    'migrate',
                    'reponame',
                    'source-branch',
                    'target-branch',
                    '--target-repo',
                    'reponame2',
                    '--no-wait',
                    '-t',
                    '5',
                ]
        ):
            with mock.patch('cluster.cluster.Cluster.migrate') as mo:
                main()
                mo.assert_called_once_with(
                    'reponame',
                    'source-branch',
                    'target-branch',
                    target_repo='reponame2',
                    no_wait=True,
                    timeout=5,
                    ask_user=False,
                    no_update=False
                )

    def test_command_line_no_update(self):
        with mock.patch(
                'sys.argv',
                [
                    'cluster',
                    '-y',
                    'migrate',
                    'reponame',
                    'source-branch',
                    'target-branch',
                    '--target-repo',
                    'reponame2',
                    '--no-wait',
                    '-t',
                    '5',
                    '-n',
                ]
        ):
            with mock.patch('cluster.cluster.Cluster.migrate') as mo:
                main()
                mo.assert_called_once_with(
                    'reponame',
                    'source-branch',
                    'target-branch',
                    target_repo='reponame2',
                    no_wait=True,
                    timeout=5,
                    ask_user=False,
                    no_update=True
                )

        with mock.patch(
                'sys.argv',
                [
                    'cluster',
                    '-y',
                    'migrate',
                    'reponame',
                    'source-branch',
                    'target-branch',
                    '--target-repo',
                    'reponame2',
                    '--no-wait',
                    '-t',
                    '5',
                    '--no-update',
                ]
        ):
            with mock.patch('cluster.cluster.Cluster.migrate') as mo:
                main()
                mo.assert_called_once_with(
                    'reponame',
                    'source-branch',
                    'target-branch',
                    target_repo='reponame2',
                    no_wait=True,
                    timeout=5,
                    ask_user=False,
                    no_update=True
                )

    @mock.patch('cluster.util.get_input', return_value='yes')
    def test_migrate_default(self, _):
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
                        },
                        'update': True
                    }
                ),
                False,
                cluster.Cluster.migrate_finished,
                cluster.DEFAULT_TIMEOUT
            )

    @mock.patch('cluster.util.get_input', return_value='yes')
    def test_migrate_no_update(self, _):
        self.init_mocks(extra={
            "repo_url": "ssh://git@git.example.org:2222/services/migrate-repo"}
        )
        with mock.patch('cluster.cluster.Cluster._fire_event') as mo:
            self.cluster.migrate('migrate-repo', 'prod', 'qualif',
                                 no_update=True)
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
                        },
                        'update': False
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
            no_wait=False,
            ask_user=False
        )

    @mock.patch('cluster.util.get_input', return_value='no')
    def test_migrate_says_no(self, _):
        self.init_mocks(extra={
            "repo_url": "ssh://git@git.example.org:2222/services/migrate-repo"}
        )
        with OutputCapture() as output:
            # code under test
            self.cluster.migrate('migrate-repo', 'prod', 'qualif')
        self.assertTrue(
            "Not confirmed, Aborting" in output.captured
        )
