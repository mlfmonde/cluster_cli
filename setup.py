from setuptools import setup, find_packages


def parse_requirements(file):
    required = []
    with open(file) as f:
        for req in f.read().splitlines():
            if not req.strip().startswith('#'):
                required.append(req)
    return required


version = '0.1'
requires = parse_requirements('requirements.txt')
tests_requires = parse_requirements('requirements.tests.txt')

setup(
    name='cluster-cli',
    version=version,
    description="Command line cluster client tool",
    long_description="""A client utility to help administrage cluster
    """,
    classifiers=[],
    author='Pierre Verkest',
    author_email='pverkest@anybox.fr',
    url='https://github.com/mlfmonde/cluster_cli',
    license='MIT',
    packages=find_packages(
        exclude=['ez_setup', 'examples', 'tests']
    ),
    include_package_data=True,
    zip_safe=False,
    namespace_packages=['cluster'],
    install_requires=requires,
    tests_require=requires + tests_requires,
    entry_points="""
    [console_scripts]
    cluster=cluster.client:main
    """,
)
