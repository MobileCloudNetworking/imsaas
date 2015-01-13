from setuptools import setup

setup(
    name='IMSServiceOrchestrator',
    version='3.1',
    packages=['core', 'test', 'util', 'wsgi', 'model', 'services', 'interfaces', 'clients', 'emm_exceptions'],
    install_requires=[
        'python-heatclient',
        'python-novaclient',
        'python-ceilometerclient',
        'python-neutronclient',
        'python-novaclient',
        'bottle',
        'sqlalchemy',
    ],
    # test_suite="test",
    url='',
    license='',
    author='Giuseppe Carella',
    author_email='giuseppe.a.carella@tu-berlin.de',
    description='IMS Service Orchestrator',
)
