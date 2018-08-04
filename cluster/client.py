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

    parser_checks.set_defaults(func=cluster_checks)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
