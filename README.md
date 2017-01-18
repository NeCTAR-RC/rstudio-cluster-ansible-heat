# R-Studio cluster with OpenStack Heat and Ansible

This repository contains a set of scripts to provision an R-Studio cluster
based on OpenStack Heat and Ansible.

The steps required to create the cluster are:

 - Load your OpenStack credentials
 - Modify your SSH key in ansible.cfg
 - Modify any necessary variables in the group_vars directory
 - Build the cluster with `openstack stack create rstudio -t heat-rstudio-cluster.yaml`
 - Provision the software with ansible-playbook playbook.yml
 - Create a Shibboleth SP with the AAF

Variables:
key_name
availability_zone: melbourne-np
image_id: 8ccac42b-2ea4-4abd-b4da-32a97a97fb46 (NeCTAR Ubuntu 16.04 LTS (Xenial) amd64 v11)
flavor: m2.small
volume_size: 10
host_name: rstudio
domain_name:
stage: prod

Launching the stack requires the OpenStack client to be installed and available
in the path.

It can be launched like this:
```
$ openstack stack create rstudio-test --parameter stage=test --wait --template heat-rstudio-cluster.yaml
2017-01-08 23:02:07 [rstudio-test]: CREATE_IN_PROGRESS  Stack CREATE started
2017-01-08 23:02:07 [rstudio-test.secgroup]: CREATE_IN_PROGRESS  state changed
2017-01-08 23:02:08 [rstudio-test.master_server_volume]: CREATE_IN_PROGRESS  state changed
2017-01-08 23:02:09 [rstudio-test.secgroup]: CREATE_COMPLETE  state changed
2017-01-08 23:02:09 [rstudio-test.master_secgroup_rules]: CREATE_IN_PROGRESS  state changed
2017-01-08 23:02:14 [rstudio-test.worker_secgroup_rules]: CREATE_IN_PROGRESS  state changed
2017-01-08 23:02:18 [rstudio-test.master_secgroup_rules]: CREATE_COMPLETE  state changed
2017-01-08 23:02:18 [rstudio-test.worker_secgroup_rules]: CREATE_COMPLETE  state changed
2017-01-08 23:02:18 [rstudio-test.master_server_volume]: CREATE_COMPLETE  state changed
2017-01-08 23:02:18 [rstudio-test.worker_servers]: CREATE_IN_PROGRESS  state changed
2017-01-08 23:02:20 [rstudio-test.master_server]: CREATE_IN_PROGRESS  state changed
2017-01-08 23:02:52 [rstudio-test.worker_servers]: CREATE_COMPLETE  state changed
2017-01-08 23:02:56 [rstudio-test.master_server]: CREATE_COMPLETE  state changed
2017-01-08 23:02:56 [rstudio-test.master_server_volume_attachment]: CREATE_IN_PROGRESS  state changed
2017-01-08 23:02:57 [rstudio-test.master_dns_record]: CREATE_IN_PROGRESS  state changed
2017-01-08 23:03:00 [rstudio-test.master_dns_record]: CREATE_COMPLETE  state changed
2017-01-08 23:03:03 [rstudio-test.master_server_volume_attachment]: CREATE_COMPLETE  state changed
2017-01-08 23:03:03 [rstudio-test]: CREATE_COMPLETE  Stack CREATE completed successfully
+---------------------+--------------------------------------+
| Field               | Value                                |
+---------------------+--------------------------------------+
| id                  | 64d16e18-c5f2-4d5a-8a9f-cd3d94d932f9 |
| stack_name          | rstudio-test                         |
| description         | R-Studio cluster                     |
| creation_time       | 2017-01-08T23:02:05                  |
| updated_time        | None                                 |
| stack_status        | CREATE_COMPLETE                      |
| stack_status_reason | Stack CREATE completed successfully  |
+---------------------+--------------------------------------+
```

This will create a 'test' cluster.


```
$ openstack stack delete rstudio --yes --wait
2016-12-06 00:51:13 [rstudio]: DELETE_IN_PROGRESS  Stack DELETE started
2016-12-06 00:51:13 [rstudio.security_group_worker_rules]: DELETE_IN_PROGRESS  state changed
2016-12-06 00:51:15 [rstudio.worker_servers]: DELETE_IN_PROGRESS  state changed
2016-12-06 00:51:15 [rstudio.master_server_volume_attachment]: DELETE_IN_PROGRESS  state changed
2016-12-06 00:51:16 [rstudio.master_dns_record]: DELETE_IN_PROGRESS  state changed
2016-12-06 00:51:16 [rstudio.master_dns_record]: DELETE_COMPLETE  state changed
2016-12-06 00:51:16 [rstudio.security_group_worker_rules]: DELETE_COMPLETE  state changed
2016-12-06 00:51:21 [rstudio.worker_servers]: DELETE_COMPLETE  state changed
2016-12-06 00:51:22 [rstudio.master_server_volume_attachment]: DELETE_COMPLETE  state changed
2016-12-06 00:51:23 [rstudio.master_server]: DELETE_IN_PROGRESS  state changed
2016-12-06 00:51:26 [rstudio.master_server]: DELETE_COMPLETE  state changed
2016-12-06 00:51:26 [rstudio.security_group_rules]: DELETE_IN_PROGRESS  state changed
2016-12-06 00:51:29 [rstudio.master_server_volume]: DELETE_IN_PROGRESS  state changed
2016-12-06 00:51:30 [rstudio.security_group_rules]: DELETE_COMPLETE  state changed
2016-12-06 00:51:31 [rstudio.security_group]: DELETE_IN_PROGRESS  state changed
2016-12-06 00:51:33 [rstudio.master_server_volume]: DELETE_COMPLETE  state changed
2016-12-06 00:51:33 [rstudio.security_group]: DELETE_COMPLETE  state changed
```

Authentication is handled with the AAF Shibboleth service. For this to work,
you will need to create a Service Provider.

This can be done through the AAF Create Service Provider page, for either
Production or Testing:

 * https://manager.aaf.edu.au/federationregistry/membership/serviceprovider/create (Production)
 * https://manager.test.aaf.edu.au/federationregistry/membership/serviceprovider/create (Testing)

When filling out the form, select your Organisation from the list, add a
Display Name and a Description. For the Service URL, add the HTTPS address you
expect to use.

This URL is also required in the _SAML Configuration_ section. You should use
the _Easy registration using defaults_ option (choose Shibboleth 2.5) and
enter the URL (e.g. https://rstudio.your-domain.org.au).

ansible-playbook playbook.yml -l rstudio-test
