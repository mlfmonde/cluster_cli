from cluster.cluster import Cluster
from cluster.tests.cluster_test_case import ClusterTestCase


class TestDeploy(ClusterTestCase):

    def test_nodes(self):
        self.cluster = Cluster()
        self.assertEqual(
            self.cluster.nodes,
            ['node-1', 'node-2', 'node-3', 'node-4']
        )
