import pytest
from testfixtures import OutputCapture
from unittest import mock

from cluster.client import main
from cluster.tests.cluster_test_case import ClusterTestCase


def fixture_get_command_line_args():
    return [
        'sys.argv',
        [
            'cluster',
            '-y',
            'inspect',
            'node1',
        ],
    ]


def fixture_consul_kv_find_payload():
    return {
       "app1": '{"master": "node1", "slave": "node2"}',
       "app2": '{"master": "node2", "slave": "node1"}',
       "app3": '{"master": "node1", "slave": "node2"}',
       "app4": '{"master": "node2", "slave": "node1"}',
    }


def fixture_expected_result():
    return "\n".join([
       "Master apps of node node1:",
       "app1",
       "app3",
    ])


class TestInspect(ClusterTestCase):

    def test_command_line(self):
        with mock.patch(*fixture_get_command_line_args()):
            with mock.patch('cluster.cluster.Cluster.inspect_node') as mo:
                main()
                mo.assert_called_once_with('node1')

    def test_command_output(self):
        self.mocked_consul.configure_mock(**{
            'kv.find': lambda state: fixture_consul_kv_find_payload(),
        })

        with OutputCapture() as output:
            with mock.patch(*fixture_get_command_line_args()):
                main()
                output.compare(fixture_expected_result())
