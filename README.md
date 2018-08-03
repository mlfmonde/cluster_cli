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
usage: cluster [-h] [--consul CONSUL] {checks} ...

Command line utility to administrate cluster

positional arguments:
  {checks}              sub-commands
    checks              List consul health checks per nodes/service

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
