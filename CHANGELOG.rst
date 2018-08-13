Change log
==========

Unreleased
----------

* wait the end of consumption before stop (replace --wait option per --no-wait)

* Build docker image

* Improve various user feedback/usage, add confirmation, logging config and typo

* Implement move-masters-from to move all services hosted on the given node

* Implement migrate subcommand to move buttervolume docker volumes from a
  service to another one (ie: prod to qualif)

* Implement deploy subcommand to Deploy or re-deploy a service

* First implementation, list checks per nodes
