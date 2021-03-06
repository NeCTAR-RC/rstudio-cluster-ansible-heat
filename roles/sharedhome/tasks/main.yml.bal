---
# This task is used to mount a filesystem via NFS.
# 
# Variables you need to define:
# nfsserver:   the nfs server to mount from
# nfspath:     the remote filesystem to mount from the nfs server
# nfsmount:    the directory where you want to mount the filesystem.
# nfsoptions:  options to use when mounting the filesystem. If not
#              defined, `rw,sync` will be used.
#
# Please note that the task will check if the {{nfsmount}} directory
# exists and create it otherwise.
#

- name: install nfs client
  action: apt pkg=nfs-common state=present

- name: Ensure rpcbind is running
  action: service name=rpcbind state=started enabled=yes

- name: Ensure {{ sharedhome_nfsmount }} directory exists
  action: file path={{ sharedhome_nfsmount }} state=directory

- name: Ensure {{ shared_homenfsmount }} directory exists
  action: file path={{ sharedhome_nfsmount }} state=directory

- name: configure /etc/fstab on clients
  action: mount name={{sharedhome_nfsmount}} src={{sharedhome_nfsserver}}:{{sharedhome_nfspath}} fstype=nfs opts={{nfsoptions}} state=mounted
