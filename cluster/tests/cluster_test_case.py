from unittest import mock, TestCase

from cluster.cluster import Cluster


class ClusterTestCase(TestCase):

    def setUp(self):
        self.mocked_consul = mock.MagicMock()
        self.cluster_patch = mock.patch(
            'cluster.cluster.Cluster.consul',
            new_callable=mock.PropertyMock(return_value=self.mocked_consul)
        )
        self.cluster_patch.start()
        self.cluster = Cluster('http://fake.host')

    def tearDown(self):
        self.cluster_patch.stop()
