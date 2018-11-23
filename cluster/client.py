import argparse
import json
import logging

from cluster import cluster


def main():
    parser = argparse.ArgumentParser(
        prog="cluster",
        description="Command line utility to administrate cluster",
    )
    parser.add_argument(
        '--consul', '-c',
        help="consul api url",
        default="http://localhost:8500"
    )
    parser.add_argument(
        '-y', '--assume-yes', action='store_true',
        help="Always answers ``yes`` to any questions."
    )
    logging_group = parser.add_argument_group(
        'Logging params'
    )
    logging_group.add_argument(
        '-f',
        '--logging-file',
        type=argparse.FileType('r'),
        help='Logging configuration file, (logging-level and logging-format '
             'are ignored if provide)'
    )
    logging_group.add_argument(
        '-l', '--logging-level', default='WARN'
    )
    logging_group.add_argument(
        '--logging-format',
        default='%(asctime)s - %(levelname)s (%(module)s%(funcName)s): '
                '%(message)s'
    )
    subparsers = parser.add_subparsers(help='sub-commands')

    parser_checks = subparsers.add_parser(
        'checks', help='List consul health checks per nodes/service'
    )
    parser_checks.add_argument(
        '-a', '--all', action='store_true',
        help='Display all checks (any states)'
    )

    parser_deploy = subparsers.add_parser(
        'deploy', help='Deploy or re-deploy a service'
    )
    parser_deploy.add_argument(
        'repo',
        help='The repo name or whole form ('
             'ssh://git@git.example.com:22/project-slug/repo-name) '
             'for new service'
    )
    parser_deploy.add_argument(
        'branch',
        help='The branch to deploy'
    )
    parser_deploy.add_argument(
        '--master',
        metavar='NODE',
        help='Node where to deploy the master (required for new service)'
    )
    parser_deploy.add_argument(
        '--slave',
        metavar='NODE',
        help='Slave node'
    )

    parser_deploy.add_argument(
        '-d', '--no-wait',
        action='store_true',
        help='Run the script in detached mode : do not wait the end of '
             'deployment to stop the script.'
    )
    parser_deploy.add_argument(
        '-t', '--timeout',
        type=int,
        default=cluster.DEFAULT_TIMEOUT,
        help='Time in second to let a chance to deploy the service before'
             'raising an exception (ignored with ``--no-wait`` option)'
    )

    parser_migrate = subparsers.add_parser(
        'migrate',
        help='Migrate buttervolume (docker volume) data from a service '
             'to another one. Only identical volume name will be restored. '
             '``source`` service is where to get data to restore on the '
             '``target`` service. Make sure to snaphot or backup your data '
             '(ie: switch your app before migrate) on the target, target data '
             'will be lost.'
             '``prod`` branch name as a target is forbidden'
    )
    parser_migrate.add_argument(
        'source_repo',
        help='The source repo where to get data that will be restored on '
             'the target service'
    )
    parser_migrate.add_argument(
        'source_branch',
        help='The source branch where to get data that will be restored on '
             'the target service'
    )
    parser_migrate.add_argument(
        'target_branch',
        help='The target branch where data will be restored'
    )
    parser_migrate.add_argument(
        '--target-repo',
        help='The target repo if different to the source-repo where data '
             'will be restored.'
    )
    parser_migrate.add_argument(
        '-d', '--no-wait',
        action='store_true',
        help='Run the script in detached mode : do not wait the end of '
             'deployment to stop the script.'
    )
    parser_migrate.add_argument(
        '-t', '--timeout',
        type=int,
        default=cluster.DEFAULT_TIMEOUT,
        help='Time in second to let a chance to deploy the service before'
             'raising an exception (ignored with ``--no-wait`` option)'
    )

    parser_move_masters_from = subparsers.add_parser(
        'move-masters-from',
        help='If you want to do some maintenance operation on the host server.'
             'This command will helps you to send all events to services'
             'hosted on the given node to its slave or the wished master'
    )
    parser_move_masters_from.add_argument(
        'node',
        help='Node where services should not be hosted '
             'that we want to move away'
    )
    parser_move_masters_from.add_argument(
        '-m', '--master',
        help="Node to use if no replicate (slave) define on a service, "
             "otherwise slave will be used as master."
    )
    parser_move_masters_from.add_argument(
        '-d', '--no-wait',
        action='store_true',
        help='Run the script in detached mode : do not wait the end of '
             'deployment to stop the script.'
    )
    parser_move_masters_from.add_argument(
        '-t', '--timeout',
        type=int,
        default=cluster.DEFAULT_TIMEOUT,
        help='Time in second to let a chance to deploy the service before'
             'raising an exception (ignored with ``--no-wait`` option)'
    )

    parser_inspect = subparsers.add_parser(
        'inspect',
        help='Display all master services of given node.'
    )
    parser_inspect.add_argument(
        'node',
        help='Node where services should be inspected.'
    )

    def init(args):
        return cluster.Cluster(
            args.consul
        )

    def cluster_checks(args):
        cluster = init(args)
        for node, services in cluster.checks(all=args.all).items():
            print("Node {}:".format(node))
            for _, service in services.items():
                print(" - Service {}:".format(service['name']))
                for name, status, _ in service['checks']:
                    print("    - Check ({}): {}".format(status, name))

    def cluster_deploy(args):
        cluster = init(args)
        cluster.deploy(
            args.repo,
            args.branch,
            master=args.master,
            slave=args.slave,
            no_wait=args.no_wait,
            timeout=args.timeout,
            ask_user=not args.assume_yes
        )

    def cluster_migrate(cmd_args):
        cluster = init(cmd_args)
        cluster.migrate(
            cmd_args.source_repo,
            cmd_args.source_branch,
            cmd_args.target_branch,
            target_repo=cmd_args.target_repo,
            no_wait=cmd_args.no_wait,
            timeout=cmd_args.timeout,
            ask_user=not arguments.assume_yes
        )

    def cluster_move_masters_from(args):
        cluster = init(args)
        cluster.move_masters_from(
            args.node,
            master=args.master,
            no_wait=args.no_wait,
            timeout=args.timeout,
            ask_user=not args.assume_yes
        )

    def cluster_inspect(args):
        cluster = init(args)
        cluster.inspect_node(args.node)

    parser_checks.set_defaults(func=cluster_checks)
    parser_deploy.set_defaults(func=cluster_deploy)
    parser_migrate.set_defaults(func=cluster_migrate)
    parser_move_masters_from.set_defaults(func=cluster_move_masters_from)
    parser_inspect.set_defaults(func=cluster_inspect)

    arguments = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, arguments.logging_level.upper()),
        format=arguments.logging_format
    )
    if arguments.logging_file:
        try:
            json_config = json.loads(arguments.logging_file.read())
            logging.config.dictConfig(json_config)
        except json.JSONDecodeError:
            logging.config.fileConfig(arguments.logging_file.name)

    if hasattr(arguments, 'func'):
        arguments.func(arguments)
    else:
        parser.print_help()
