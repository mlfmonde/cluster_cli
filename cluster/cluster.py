import consulate
from urllib.parse import urlparse


class Cluster:

    def __init__(self, consul_url):
        consul_url = urlparse(consul_url)
        self.consul = consulate.Consul(
            scheme=consul_url.scheme,
            host=consul_url.hostname,
            port=consul_url.port,
            datacenter=None,
            token=None,
        )

    def checks(self, all=False):
        """Display failed checks per nodes

        :param all: if you want to see more
        :return: a dict of checks per node::

            {
                'node1': {
                    'service-id1': {
                        checks: [(check name, status, error message), ...],
                        name: "Service 1",
                    }
                    'service-id2': {
                        checks: [(check name, status, error message), ...],
                        ...
                    },
                },
                'node2': ...
            }
        """
        if all:
            warn_states = ["unknown", "passing", "warning", "critical"]
        else:
            warn_states = ["unknown", "warning", "critical"]
        checks = {}
        for warn_state in warn_states:
            for state in self.consul.health.state(warn_state):
                if not state['Node'] in checks:
                    checks[state['Node']] = dict()
                if not state['ServiceID'] in checks[state['Node']]:
                    checks[state['Node']][state['ServiceID']] = {
                        'checks': [],
                        'name': state['ServiceName']
                    }
                checks[state['Node']][state['ServiceID']]['checks'].append(
                    (state['Name'], state['Status'], state['Output'])
                )
        return checks
