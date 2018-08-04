import consulate
from urllib.parse import urlparse


class Cluster:

    _consul_url = None
    _consul = None

    def __init__(self, consul_url):
        self._consul_url = urlparse(consul_url)

    @property
    def consul(self):
        if not self._consul:
            self._consul = consulate.Consul(
                scheme=self._consul_url.scheme,
                host=self._consul_url.hostname,
                port=self._consul_url.port,
                datacenter=None,
                token=None,
            )
        return self._consul

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
