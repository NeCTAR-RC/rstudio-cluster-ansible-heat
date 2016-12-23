#!/usr/bin/python

import argparse
import json
import sys

import os_client_config


def get_groups_from_server(server, namegroup=True):
    groups = []

    metadata = server.metadata.get('metadata', {})

    # Check if group metadata key in servers' metadata
    if 'ansible_host_group' in metadata:
        groups.append(metadata['ansible_host_group'])

    for extra_group in server.metadata.get('ansible_host_groups', '').split(','):
        if extra_group:
            groups.append(extra_group.strip())

    metadata = server.metadata.get('ansible_host_vars')
    if metadata:
        try:
            for kv in metadata.split(';'):
                key, values = kv.split('=')
                groups.append('%s-%s' % (key, values))
        except Exception as e:
            sys.stderr.write('Error parsing metadata: %s\n' % str(e))

    groups.append('instance-%s' % server.id)
    if namegroup:
        groups.append(server.name)

    return groups


def get_ansible_host_vars(server, osdetails=False):
    host_vars = {}
    host_vars['ansible_ssh_host'] = server.accessIPv4

    if osdetails:
        host_vars['openstack'] = server.to_dict()

    metadata = server.metadata.get('ansible_host_vars')
    if metadata:
        try:
            for kv in metadata.split(';'):
                key, values = kv.split('=')
                if values.find(',') > 0:
                  values = values.split(',')
                host_vars[key] = values
            return host_vars
        except Exception as e:
            sys.stderr.write('Error parsing metadata: %s\n' % str(e))
    else:
        return None


def add_server_to_host_group(group, server, inventory):
    host_group = inventory.get(group, [])
    if server.id not in host_group:
        host_group.append(server.id)
    inventory[group] = host_group


def add_server_hostvars_to_hostvars(host_vars, server, inventory):
    inventory_host_vars = inventory['_meta']['hostvars'].get(server.id, {})
    inventory_host_vars.update(host_vars)
    inventory['_meta']['hostvars'][server.id] = inventory_host_vars


def parse_args():
    parser = argparse.ArgumentParser(description='OpenStack Inventory Module')
    parser.add_argument('--debug', action='store_true', default=False,
                        help='Enable debug output')
    parser.add_argument('--list', action='store_true', default=True,
                        help='List active servers')
    parser.add_argument('--host', action='store',
                        help='List details about the specific host')
    return parser.parse_args()


def to_json(in_dict):
    return json.dumps(in_dict, sort_keys=True, indent=2)


def main():
    args = parse_args()

    inventory = {}
    inventory['_meta'] = {'hostvars': {}}

    try:
        nc = os_client_config.make_client('compute')
        servers = [s for s in nc.servers.list()
                   if s.metadata.get('ansible_host_groups')]

        for server in servers:
            for group in get_groups_from_server(server):
                add_server_to_host_group(group, server, inventory)

            host_vars = get_ansible_host_vars(server)
            if host_vars:
                add_server_hostvars_to_hostvars(host_vars, server, inventory)

        if args.list:
            output = to_json(inventory)
        elif args.host:
            output = to_json(inventory['_meta']['hostvars'][args.host])
        print(output)
    except Exception as e:
        sys.stderr.write('Error: %s\n' % str(e))
        sys.exit(1)


if __name__ == '__main__':
    main()

