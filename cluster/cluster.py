import consulate
import logging
import json
import time

from datetime import datetime
from urllib.parse import urlparse

from cluster import util

DEFAULT_TIMEOUT = 600
logger = logging.getLogger(__name__)


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

    def get_kv_application(self, repo_name, branch):
        apps = self.consul.kv.find('app/{repo}_{branch}'.format(
            repo=repo_name, branch=branch)
        )
        if not apps:
            return None, None
        if len(apps) > 1:
            raise RuntimeError(
                "Repo / branch are ambiguous, multiple keys ({}) found for"
                "given repo: {}, branch: {}".format(
                    apps.keys(), repo_name, branch
                )
            )
        key, data = apps.popitem()
        return key, util.json2obj(data)

    def deploy(self, repo_name, branch, master=None, slave=None):
        key, app = self.get_kv_application(repo_name, branch)
        if not app:
            raise NotImplementedError(
                "Deploying a new service is not implemented"
            )
        if master or slave:
            raise NotImplementedError(
                "Forcing master or slave is not implemented"
            )
        if app.slave and app.master:
            self._deploy(
                key,
                app.repo_url,
                app.branch,
                app.slave,
                slave=app.master,
            )
            return
        raise NotImplementedError("This use case is not yet implemented")

    # communicate with consul
    def _deploy(
        self,
        kv_key,
        repo_url,
        branch,
        master,
        slave=None,
        wait=False,
        timeout=DEFAULT_TIMEOUT,
        event_consumed=None
    ):
        """Deploy a service waiting the end end of deployment before carry on
        """
        def deploy_finished(kv_app_before, kv_app_after, *args, **kwargs):
            if kv_app_before and kv_app_after:
                if kv_app_after.deploy_date > kv_app_before.deploy_date:
                    return True
                else:
                    return False
            else:
                if not kv_app_before:
                    if kv_app_after:
                        return True
                    else:
                        return False
                else:
                    return False

        if not event_consumed:
            event_consumed = deploy_finished

        self._fire_event(
            kv_key,
            'deploy',
            json.dumps(
                {
                    'repo': repo_url,
                    'branch': branch,
                    'master': master,
                    'slave': slave,
                }
            ),
            wait,
            event_consumed,
            timeout
        )

    def _fire_event(
        self,
        kv_key,
        event_name,
        payload,
        wait,
        event_consumed,
        timeout
    ):
        app_before = util.json2obj(self.consul.kv.get(kv_key))
        logger.info(
            "Emit %s event for kv key: %s with following payload: %r",
            event_name, kv_key, payload
        )
        event_id = self.consul.event.fire(
            event_name, payload
        )
        start_date = datetime.now()
        while wait and not event_consumed(
                app_before,
                util.json2obj(self.consul.kv.get(kv_key)),
                maintenance=self.consul.kv.get_record(
                    kv_key.replace("app/", "maintenance/")
                ),
                self=self
        ):
            time.sleep(1)
            if (datetime.now() - start_date).seconds > timeout:
                raise TimeoutError(
                    "Event (id: {}) was not processed in the expected time"
                    " ({}s),".format(event_id, timeout)
                )
        logger.info(
            "Event %s takes %ss to consume",
            event_name, (datetime.now() - start_date).seconds
        )
        return event_id
