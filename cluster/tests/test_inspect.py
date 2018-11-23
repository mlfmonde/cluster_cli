from unittest import mock

from cluster.client import main
from cluster.tests.cluster_test_case import ClusterTestCase


class TestInspect(ClusterTestCase):

    def test_command_line(self):
        with mock.patch(
                'sys.argv',
                [
                    'cluster',
                    '-y',
                    'inspect',
                    'node-1',
                ]
        ):
            with mock.patch('cluster.cluster.Cluster.inspect_node') as mo:
                main()
                mo.assert_called_once_with('node-1')
