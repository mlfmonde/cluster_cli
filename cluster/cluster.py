import consulate
import hashlib
import json
import logging
import os
import time

from datetime import datetime
from urllib import parse

from cluster import util

DEFAULT_TIMEOUT = 300
logger = logging.getLogger(__name__)


class Cluster:

    _consul_url = None
    _consul = None
    _nodes = None

    def __init__(self, consul_url='http://localhost:8500'):
        self._consul_url = parse.urlparse(consul_url)

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

    @property
    def nodes(self):
        if not self._nodes:
            self._nodes = [
                node['Node'] for node in self.consul.catalog.nodes()
            ]
        return self._nodes

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

    def deploy(
            self,
            repo_name,
            branch,
            master=None,
            slave=None,
            wait=False,
            timeout=DEFAULT_TIMEOUT,
            ask_user=True
    ):
        key, app = self.get_kv_application(repo_name, branch)
        if master and slave and master == slave:
            raise RuntimeError("Master and slave must be different")
        new_master = master
        new_slave = slave
        if not app:
            if not master:
                raise RuntimeError(
                    "Deploying a new service require a master"
                )
            repo_url, branch = repo_name.strip(), branch.strip()
            if repo_url.endswith('.git'):
                repo_url = repo_url[:-4]
            md5 = hashlib.md5(
                parse.urlparse(repo_url.lower()).path.encode('utf-8')
            ).hexdigest()
            repo_name = os.path.basename(repo_url.strip('/').lower())
            key = 'app/' + repo_name + (
                '_' + branch if branch else ''
            ) + '.' + md5[:5]  # don't need full md5
        else:
            if app.slave:
                # taht was a replicated service => that will carry on to be a
                # replicate service because the auto detect switch guess the
                # slave
                if not new_master:
                    new_master = app.slave
                if not new_slave:
                    new_slave = app.master
                if new_master == new_slave:
                    if master:
                        new_slave = app.slave
                    if slave:
                        new_master = app.master
            else:
                # was a master only service
                if not new_master:
                    new_master = app.master
            repo_url = app.repo_url
            branch = app.branch

        if new_master == new_slave:
            raise RuntimeError("Master and slave must be different")
        if new_master not in self.nodes:
            raise RuntimeError(
                "Can't deploy to unknown master (node host: {})".format(
                    new_master
                )
            )
        if new_slave is not None and new_slave not in self.nodes:
            raise RuntimeError(
                "Can't deploy using unknown slave (node host: {}) ".format(
                    new_slave
                )
            )
        if ask_user:
            print(
                "You are going to move following app {} from "
                "[master: {} - replicate: {}] to "
                "[master: {} - replicate: {}]".format(
                    key,
                    app.master if app else None,
                    app.slave if app else None,
                    new_master,
                    new_slave
                )
            )
            answer = util.get_input("Please confim by entering 'yes': ")
            if answer.strip().lower() != 'yes':
                print("Not confirmed, Aborting")
                logging.critical("Not confirmed. Aborting")
                return

        self._deploy(
            key,
            repo_url,
            branch,
            new_master,
            slave=new_slave,
            wait=wait,
            timeout=timeout
        )

    def move_masters_from(
        self,
        node,
        master=None,
        wait=False,
        timeout=DEFAULT_TIMEOUT,
        ask_user=True
    ):
        move_apps = []
        for key, value in self.consul.kv.find('app/').items():
            app = util.json2obj(value)
            if app.master == node:
                mstr = app.slave
                if not mstr:
                    if not master:
                        raise RuntimeError(
                            "You must define a default master (--master) as "
                            "there are some services (at least {}) without "
                            "replicate (slave)".format(key)
                        )
                    if master not in self.nodes:
                        raise RuntimeError(
                            "The given default master hostname: {} is "
                            "unknown. Available nodes: {}".format(
                                master, self.nodes
                            )
                        )
                    if master == node:
                        raise RuntimeError(
                            "You must provide a different default master: {} "
                            "it must be different to the node that you want"
                            "clear: {}".format(
                                master, node
                            )
                        )

                    mstr = master
                move_apps.append(
                    (
                        key,
                        app,
                        mstr,
                        app.master if app.slave else None,
                    )
                )

        if ask_user:
            print("You are going to move following apps:")
            for key, app, mstr, _ in move_apps:
                print(" - from {} to {}, project: {}".format(
                    app.master,
                    mstr,
                    key
                ))
            answer = util.get_input("Please confim by entering 'yes': ")
            if answer.strip().lower() != 'yes':
                print("Not confirmed, Aborting")
                logging.critical("Not confirmed. Aborting")
                return
        for key, app, mstr, slave in move_apps:
            self._deploy(
                key,
                app.repo_url,
                app.branch,
                mstr,
                slave=slave,
                wait=wait,
                timeout=timeout
            )

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

    # move as classmethod to easly reuse it in unittest
    @classmethod
    def migrate_finished(
            cls, kv_app_before, kv_app_after, maintenance=None, self=None,
            **kwargs
    ):
        if maintenance:
            self.was_maintenance = True
        if self.was_maintenance and not maintenance:
            return True
        return False

    def migrate(
            self,
            source_repo,
            source_branch,
            target_branch,
            target_repo=None,
            wait=False,
            timeout=DEFAULT_TIMEOUT,
            ask_user=True
    ):

        if not target_repo:
            target_repo = source_repo

        if target_branch in ['prod', 'production']:
            raise RuntimeError(
                "You can't migrate data to production branch using this script"
            )

        source_key, source_app = self.get_kv_application(
            source_repo, source_branch
        )
        if not source_app:
            raise RuntimeError(
                "Source service (repo: {}, branch: {}) not found".format(
                    source_repo,
                    source_branch
                )
            )
        target_key, target_app = self.get_kv_application(
            target_repo, target_branch
        )
        if not target_app:
            raise RuntimeError(
                "Target service (repo: {}, branch: {}) not found".format(
                    target_repo,
                    target_branch
                )
            )
        self.was_maintenance = False

        if ask_user:
            print(
                "You are on the way to replace common docker volumes on "
                " service {} by data from {}".format(
                    target_key, source_key
                )
            )
            answer = util.get_input("Please confim by entering 'yes': ")
            if answer.strip().lower() != 'yes':
                print("Not confirmed, Aborting")
                logging.critical("Not confirmed. Aborting")
                return
        self._fire_event(
            target_key,
            'migrate',
            json.dumps(
                {
                    'repo': source_app.repo_url,
                    'branch': source_app.branch,
                    'target': {
                        'repo': target_app.repo_url,
                        'branch': target_app.branch
                    }
                }
            ),
            wait,
            Cluster.migrate_finished,
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
