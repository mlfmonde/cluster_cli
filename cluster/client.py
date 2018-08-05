import argparse

from cluster.cluster import Cluster


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
             'for new service.'
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

    def init(args):
        return Cluster(
            args.consul
        )

    def cluster_checks(args):
        cluster = init(args)
        for node, services in cluster.checks(all=args.all).items():
            print("Node {}:".format(node))
            for _, service in services.items():
                print(" - Service {}:".format(service['name']))
                for name, status, _ in service['checks']:
                    print("    - Cehck ({}): {}".format(status, name))

    def cluster_deploy(args):
        cluster = init(args)
        cluster.deploy(
            args.repo, args.branch, master=args.master, slave=args.slave
        )

    parser_checks.set_defaults(func=cluster_checks)
    parser_deploy.set_defaults(func=cluster_deploy)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
