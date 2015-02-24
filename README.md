IMS Service Orchestrator
------------------------

Welcome to the user guide of the IMS Service Orchestrator (IMSSO).

Installation guide
==================


In order to install the IMSSO you need to install the following libraries:


```bash
pip install python-heatclient six python-novaclient python-ceilometerclient python-neutronclient bottle sqlalchemy==0.9.8 pyzmq httplib2
```

as the orchestrator requires the MCN SDK in place, you might use the following script for installing all in one the required dependencies:


```bash
cd support
./build
```


Execute the IMSSO
=================

In order to start the IMSSO you need to configure some environment variables:


```
export PYTHONPATH=%%imsso_path%%
export DESIGN_URI=http://bart.cloudcomplab.ch:35357/v2.0
export OPENSHIFT_REPO_DIR=%%imsso_path%%
```

For starting the IMSSO:

```
python wsgi/application
```


Instantiate an IMS instance
===========================

First of all you need to initialize the IMSSO. In a new terminal do get a token from keystone (token must belong to a user which has the admin role for the tenant):

```bash
keystone token-get
export KID='...'
export TENANT='...'
```

Once you have the token you can send the init request to the SO:

```
curl -v -X PUT http://127.0.0.1:8051/orchestrator/default
          -H 'Content-Type: text/occi'
          -H 'Category: orchestrator; scheme="http://schemas.mobile-cloud-networking.eu/occi/service#"'
          -H 'X-Auth-Token: '$KID
          -H 'X-Tenant-Name: '$TENANT
```

Trigger the deployment of a service instance:

```
curl -v -X POST http://127.0.0.1:8051/orchestrator/default?action=deploy
          -H 'Content-Type: text/occi'
          -H 'Category: deploy; scheme="http://schemas.mobile-cloud-networking.eu/occi/service#"'
          -H 'X-Auth-Token: '$KID
          -H 'X-Tenant-Name: '$TENANT
```

Trigger update on SO + service instance:

```
curl -v -X POST http://127.0.0.1:8051/orchestrator/default
          -H 'Content-Type: text/occi'
          -H 'X-Auth-Token: '$KID
          -H 'X-Tenant-Name: '$TENANT
          -H 'X-OCCI-Attribute: mcn.endpoint.maas="160.85.4.50"'
```

Trigger delete of SO + service instance:

```
curl -v -X DELETE http://127.0.0.1:8051/orchestrator/default
          -H 'X-Auth-Token: '$KID
          -H 'X-Tenant-Name: '$TENANT
```



