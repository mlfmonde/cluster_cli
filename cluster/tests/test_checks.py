from unittest import mock, TestCase
from cluster.cluster import Cluster


class TestChecks(TestCase):

    def setUp(self):
        self.cluster = Cluster('http://fake.host')
        self.cluster.consul = mock.MagicMock()

    def test_checks_empty_result(self):
        self.assertFalse(
            self.cluster.checks()
        )

    def fill_data(self):
        def consul_health_state(state):
            if state == 'passing':
                return [
                    {
                        'Node': 'node-1',
                        'ServiceID': 'service-1',
                        'ServiceName': 'Service 1',
                        'Status': state,
                        'Output': "check output",
                        'Name': "Check Service 1",
                    }, {
                        'Node': 'node-2',
                        'ServiceID': 'service-2',
                        'ServiceName': 'Service 2',
                        'Status': state,
                        'Output': "check output",
                        'Name': "Check Service 2",
                    }, {
                        'Node': 'node-2',
                        'ServiceID': 'service-2',
                        'ServiceName': 'Service 2',
                        'Status': state,
                        'Output': "check output 2",
                        'Name': "Check Service 2.2",
                    }
                ]
            elif state == 'critical':
                return [
                    {
                        'Node': 'node-2',
                        'ServiceID': 'service-3',
                        'ServiceName': 'Service 3',
                        'Status': state,
                        'Output': "check output error",
                        'Name': "Check Service 3",
                    }
                ]
            else:
                return []
        self.cluster.consul.configure_mock(**{
            'health.state.side_effect': consul_health_state,
        })

    def test_checks_all(self):
        self.fill_data()
        self.maxDiff = None
        self.assertEqual(
            self.cluster.checks(all=True),
            {
                'node-1': {
                    'service-1': {
                        'name': "Service 1",
                        'checks': [
                            ('Check Service 1', 'passing', 'check output', ),
                        ],
                    },
                },
                'node-2': {
                    'service-2': {
                        'name': "Service 2",
                        'checks': [
                            ('Check Service 2', 'passing', 'check output', ),
                            (
                                'Check Service 2.2',
                                'passing',
                                'check output 2',
                            ),
                        ],
                    },
                    'service-3': {
                        'name': "Service 3",
                        'checks': [
                            (
                                'Check Service 3',
                                'critical',
                                'check output error',
                            ),
                        ],
                    },
                },
            }
        )

    def test_checks_warn(self):
        self.fill_data()
        self.assertEqual(
            self.cluster.checks(all=False),
            {
                'node-2': {
                    'service-3': {
                        'name': "Service 3",
                        'checks': [
                            (
                                'Check Service 3',
                                'critical',
                                'check output error',
                            ),
                        ],
                    },
                },
            }
        )
