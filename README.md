[![Build Status](https://travis-ci.org/mlfmonde/cluster_cli.svg?branch=master)](https://travis-ci.org/mlfmonde/cluster_cli)
[![Coverage Status](https://coveralls.io/repos/github/mlfmonde/cluster_cli/badge.svg?branch=master)](https://coveralls.io/github/mlfmonde/cluster_cli?branch=master)

# Cluster cli

This is a command line utility tool to helps administrator to manage their
[cluster](https://github.com/mlfmonde/cluster).

Features are:

* List consul health checks per nodes and service


## Commands

Use the embedded help command, to know the list of available commands:

```bash
$ cluster -h
usage: cluster [-h] [--consul CONSUL] {checks,deploy,migrate} ...

Command line utility to administrate cluster

positional arguments:
  {checks,deploy,migrate}
                        sub-commands
    checks              List consul health checks per nodes/service
    deploy              Deploy or re-deploy a service
    migrate             Migrate buttervolume (docker volume) data from a
                        service to another one. Only identical volume name
                        will be restored. ``source`` service is where to get
                        data to restore on the ``target`` service. Make sure
                        to snaphot or backup your data (ie: switch your app
                        before migrate) on the target, target data will be
                        lost.``prod`` branch name as a target is forbidden

optional arguments:
  -h, --help            show this help message and exit
  --consul CONSUL, -c CONSUL
                        consul api url
```


### checks

List [consul health checks](https://www.consul.io/api/health.html) per nodes
and service.

```bash
$ cluster checks -h
usage: cluster checks [-h] [-a]

optional arguments:
  -h, --help  show this help message and exit
  -a, --all   Display all checks (any states)
```

_Usage example:_
```bash
$ cluster checks
Node node-3
 - Service ABC
     - Cehck (critical): Service 'ABC' check
```

### deploy

Re-deploy a service.

if master / slave are not provided, system will choose for you. For replicate
service it will try to switch master/slave. You can force master or slave only.


```bash
$ cluster deploy -h
usage: cluster deploy [-h] [--master NODE] [--slave NODE] [-w] [-t TIMEOUT]
                      repo branch

positional arguments:
  repo                  The repo name or whole form
                        (ssh://git@git.example.com:22/project-slug/repo-name)
                        for new service.
  branch                The branch to deploy

optional arguments:
  -h, --help            show this help message and exit
  --master NODE         Node where to deploy the master (required for new
                        service)
  --slave NODE          Slave node
  -w, --wait            Wait the end of deployment before stop the script.
                        Raise anexception if deployment failed in the given
                        time
  -t TIMEOUT, --timeout TIMEOUT
                        Time in second to let a chance to deploy the service
                        beforeraising an exception (ignored without ``--wait``
                        option)
```
### migrate

Migrate buttervolume (docker volume) data from a service to another one. 
 
Only identical volume name will be restored.

``source`` service is where to get data to restore on the ``target`` service.
 
Make sure to have a recent snaphot or backup of your target data (ie: switch
your app before migrate) target data will be lost.

``prod`` branch name as a target is forbidden.


```bash
$ cluster migrate -h
usage: cluster migrate [-h] [--target-repo TARGET_REPO] [-w] [-t TIMEOUT]
                       source_repo source_branch target_branch

positional arguments:
  source_repo           The source repo where to get data that will be
                        restored on the target service
  source_branch         The source branch where to get data that will be
                        restored on the target service
  target_branch         The target branch where data will be restored

optional arguments:
  -h, --help            show this help message and exit
  --target-repo TARGET_REPO
                        The target repo if different to the source-repo where
                        data will be restored.
  -w, --wait            Wait the end of deployment before stop the script.
                        Raise anexception if deployment failed in the given
                        time
  -t TIMEOUT, --timeout TIMEOUT
                        Time in second to let a chance to deploy the service
                        beforeraising an exception (ignored without ``--wait``
                        option)
```

## Install

### on you hosted python to use it

```bash
$ git clone https://github.com/mlfmonde/cluster_cli
$ cd cluster_cli
$ pip3 install .
```

### For development with a python virtualenv

```bash
$ python3 -m venv clister_cli_venv
$ source clister_cli_venv/bin/activate
$ git clone https://github.com/mlfmonde/cluster_cli
$ cd cluster_cli
$ pip install -r requirements.tests.txt
$ python setup.py develop
$ py.test --cov=cluster -v --pep8
```


## TODOs

* switch method for an existing service
* deploy to deploy a service (new or not)
* clear a node, move all the service from one given node
* add some controls to make sure node exists
* Find a way to add some checks to avoid deploy some branch (likes qualif) into
  some nodes (reserved for production). this could be implemented by [cluster](
  https://github.com/mlfmonde/cluister) as well
