import pytest
from testfixtures import OutputCapture
from unittest import mock

from cluster.client import main
from cluster.tests.cluster_test_case import ClusterTestCase


class TestInspect(ClusterTestCase):
    _command_line_args = [
        'sys.argv',
        [
            'cluster',
            '-y',
            'inspect',
            'node1',
        ],
    ]
    _app_kv = {
        "app1": '{"master": "node1", "slave": "node2"}',
        "app2": '{"master": "node2", "slave": "node1"}',
        "app3": '{"master": "node1", "slave": "node2"}',
        "app4": '{"master": "node2", "slave": "node1"}',
        "app5": '{"master": "node3", "slave": "node4"}',
    }

    def fixture_command_line(self, node):
        command_line_args = self._command_line_args
        command_line_args[1][-1] = node
        return command_line_args

    def test_command_line(self):
        node = 'node1'
        command_line_args = self.fixture_command_line(node)

        with mock.patch(*command_line_args):
            with mock.patch('cluster.cluster.Cluster.inspect_node') as mo:
                main()
                mo.assert_called_once_with(node)

    def test_command_output(self):
        node = 'node1'
        command_line_args = self.fixture_command_line(node)

        self.mocked_consul.configure_mock(**{
            'kv.find': lambda state: self._app_kv,
        })

        with OutputCapture() as output:
            with mock.patch(*command_line_args):
                main()
                output.compare("\n".join([
                        "Master apps of node {node}:".format(node=node),
                        "app1",
                        "app3",
                    ])
                )

    def test_command_output_empty_node(self):
        node = 'node5'
        command_line_args = self.fixture_command_line(node)

        self.mocked_consul.configure_mock(**{
            'kv.find': lambda state: self._app_kv,
        })

        with OutputCapture() as output:
            with mock.patch(*command_line_args):
                main()
                output.compare("\n".join([
                        "Master apps of node {node}:".format(node=node),
                    ])
                )
