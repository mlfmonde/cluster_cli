import json
from unittest import mock, TestCase

from cluster.cluster import Cluster


class ClusterTestCase(TestCase):

    def setUp(self):
        self.mocked_consul = mock.MagicMock()
        self.cluster_patch = mock.patch(
            'cluster.cluster.Cluster.consul',
            new_callable=mock.PropertyMock(return_value=self.mocked_consul)
        )

        self.mocked_consul.configure_mock(**{
            'catalog.nodes.return_value': [
                {'Node': 'node-1', },
                {'Node': 'node-2', },
                {'Node': 'node-3', },
                {'Node': 'node-4', },
            ]
        })
        self.cluster_patch.start()
        self.cluster = Cluster('http://fake.host')

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

        def kv_find(search_key):
            qualif_data = data.copy()
            qualif_data['branch'] = 'qualif'
            prod_data = data.copy()
            prod_data['branch'] = 'prod'
            cases = {
                'app/repo-name_branch-name': {
                    "app/repo-name_branch-name.12345": json.dumps(data)
                },
                'app/migrate-repo_qualif': {
                    "app/migrate-repo_qualif.12345": json.dumps(qualif_data)
                },
                'app/migrate-repo_prod': {
                    "app/migrate-repo_prod.12345": json.dumps(prod_data)
                },
            }
            return cases.get(search_key)

        self.mocked_consul.configure_mock(**{
            'kv.find.side_effect': kv_find
        })

    def init_mock_kv_get(self, data):
        self.mocked_consul.configure_mock(**{
            'kv.get.return_value': json.dumps(data)
        })

    def tearDown(self):
        self.cluster_patch.stop()


class Counter:

    _counter = {}

    @classmethod
    def get(cls, key):
        if key not in cls._counter.keys():
            cls._counter[key] = 0
        cls._counter[key] += 1
        return cls._counter[key]
