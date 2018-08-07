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
