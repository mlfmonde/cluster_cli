[![Build Status](https://travis-ci.org/mlfmonde/cluster_cli.svg?branch=master)](https://travis-ci.org/mlfmonde/cluster_cli)
[![Coverage Status](https://coveralls.io/repos/github/mlfmonde/cluster_cli/badge.svg?branch=master)](https://coveralls.io/github/mlfmonde/cluster_cli?branch=master)

# Cluster cli

This is a command line utility tool to helps administrator to manage their
[cluster](https://github.com/mlfmonde/cluster).

Features are:

* List consul health checks per nodes and service
* Deploy or switch services
* Migrate anybox/buttervolume docker volumes from one service to an other
* Clear a node by moving all services running on it
* Inspect a node to display all master services of that node
* Run anywhere you can contact your consul API

## Commands

Use the embedded help command, to know the list of available commands:

```bash
$ cluster -h
usage: cluster [-h] [--consul CONSUL] [-y] [-f LOGGING_FILE]
               [-l LOGGING_LEVEL] [--logging-format LOGGING_FORMAT]
               {checks,deploy,migrate,move-masters-from} ...

Command line utility to administrate cluster

positional arguments:
  {checks,deploy,migrate,move-masters-from}
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
    move-masters-from   If you want to do some maintenance operation on the
                        host server.This command will helps you to send all
                        events to serviceshosted on the given node to its
                        slave or the wished master

optional arguments:
  -h, --help            show this help message and exit
  --consul CONSUL, -c CONSUL
                        consul api url
  -y, --assume-yes      Always answers ``yes`` to any questions.

Logging params:
  -f LOGGING_FILE, --logging-file LOGGING_FILE
                        Logging configuration file, (logging-level and
                        logging-format are ignored if provide)
  -l LOGGING_LEVEL, --logging-level LOGGING_LEVEL
  --logging-format LOGGING_FORMAT
```

The default consul value is ``http://localhost:8500`` so you may want to
create a ssh tunnel to access to your consul before running this client

```bash
ssh -L 8500:localhost:8500 consul.host.org
```

### Checks

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

### Deploy

Re-deploy a service.

if master / slave are not provided, system will choose for you. For replicate
service it will try to switch master/slave. You can force master or slave only.


```bash
$ cluster deploy -h
usage: cluster deploy [-h] [--master NODE] [--slave NODE] [-u] [-d]
                      [-t TIMEOUT]
                      repo branch

positional arguments:
  repo                  The repo name or whole form
                        (ssh://git@git.example.com:22/project-slug/repo-name)
                        for new service
  branch                The branch to deploy

optional arguments:
  -h, --help            show this help message and exit
  --master NODE         Node where to deploy the master (required for new
                        service)
  --slave NODE          Slave node
  -u, --update          Ask for update (update script) before services are up
  -d, --no-wait         Run the script in detached mode : do not wait the end
                        of deployment to stop the script.
  -t TIMEOUT, --timeout TIMEOUT
                        Time in second to let a chance to deploy the service
                        beforeraising an exception (ignored with ``--no-wait``
                        option)
```
### Migrate

Migrate buttervolume (docker volume) data from a service to another one.

Only identical volume name will be restored.

``source`` service is where to get data to restore on the ``target`` service.

Make sure to have a recent snaphot or backup of your target data (ie: switch
your app before migrate) target data will be lost.

``prod`` branch name as a target is forbidden.


```bash
$ cluster migrate -h
usage: cluster migrate [-h] [--target-repo TARGET_REPO] [-d] [-t TIMEOUT]
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
  -d, --no-wait         Run the script in detached mode : do not wait the end
                        of deployment to stop the script.
  -t TIMEOUT, --timeout TIMEOUT
                        Time in second to let a chance to deploy the service
                        beforeraising an exception (ignored with ``--no-wait``
                        option)
  -n, --no-update       When migrate, do not run the upgrade script.
                        Recommended when you migrate a prod db on an iso
                        staging app.
```

### Move from master

This script allow to move all masters hosted on the given node away.

```bash
$ cluster move-masters-from -h
usage: cluster move-masters-from [-h] [-m MASTER] [-d] [-t TIMEOUT] node

positional arguments:
  node                  Node where services should not be hosted that we want
                        to move away

optional arguments:
  -h, --help            show this help message and exit
  -m MASTER, --master MASTER
                        Node to use if no replicate (slave) define on a
                        service, otherwise slave will be used as master.
  -d, --no-wait         Run the script in detached mode : do not wait the end
                        of deployment to stop the script.
  -t TIMEOUT, --timeout TIMEOUT
                        Time in second to let a chance to deploy the service
                        beforeraising an exception (ignored with ``--no-wait``
                        option)
```

## Install

This tool is tested on python 3.5 ans greater

### Using docker image

> **Note**: The default ``--consul`` parameter is ``http://localhost:8500``
> so you may want to create a ssh tunnel to access to your consul API
> endpoint before running this client

```bash
docker run -it --rm --network host mlfmonde/cluster_cli -h
```

### On you hosted python to use it

```bash
$ pip3 install git+https://github.com/mlfmonde/cluster_cli@master
```

or

```bash
$ git clone https://github.com/mlfmonde/cluster_cli
$ cd cluster_cli
$ pip3 install .
```

### For development with a python virtualenv

```bash
$ python3 -m venv cluster_cli_venv
$ source cluster_cli_venv/bin/activate
$ git clone https://github.com/mlfmonde/cluster_cli
$ cd cluster_cli
$ pip install -r requirements.txt
$ pip install -r requirements.tests.txt
$ python setup.py develop
$ py.test --pep8 --cov=cluster --cov-report=html --lf --nf --ff -v
```


## TODOs

* Find a way to add some checks to avoid deploy some branch (likes qualif) into
  some nodes (reserved for production). this could be implemented by [cluster](
  https://github.com/mlfmonde/cluister) as well
