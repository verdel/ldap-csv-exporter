#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ldap3 import Server, ServerPool, Connection, FIRST, AUTO_BIND_NO_TLS, SUBTREE
import argparse
from os import path
import sys
import unicodecsv as csv


def get_ldap_connection(server=[], port='', ssl=False, timeout=0, binddn='', bindpasswd=''):
    try:
        server_pool = ServerPool([Server(item, port, use_ssl=ssl, connect_timeout=3) for item in server],
                                 FIRST,
                                 active=3,
                                 exhaust=60)
        conn = Connection(server_pool,
                          auto_bind=AUTO_BIND_NO_TLS,
                          read_only=True,
                          receive_timeout=timeout,
                          check_names=True,
                          user=binddn, password=bindpasswd)
    except Exception as exc:
        print('ldap_csv_exporter LDAP bind error {}({})'.format(type(exc).__name__, exc))
        return False
    else:
        return conn


def get_ldap_info(connection='', timelimit=0, basedn='', filter=u'(&(objectClass=user))', attributes=[],):
    result = []
    if not connection:
        return result

    try:
        entry_list = connection.extend.standard.paged_search(search_base=basedn,
                                                             search_filter=filter,
                                                             search_scope=SUBTREE,
                                                             attributes=attributes,
                                                             time_limit=timelimit,
                                                             get_operational_attributes=True,
                                                             paged_size=10,
                                                             generator=False)

    except Exception as exc:
        raise exc

    else:
        if len(entry_list) > 0:
            for entry in entry_list:
                try:
                    result.append(entry['attributes'])
                except KeyError:
                    pass
            return result
        else:
            return result


def create_cli():
    parser = argparse.ArgumentParser(description='Export user or computer information from AD to csv')
    parser.add_argument('-d', '--binddn', type=str, required=True,
                        help='DN to bind as to perform searches')
    parser.add_argument('-w', '--bindpasswd', type=str,
                        help='password for binddn')
    parser.add_argument('-W', '--secretfile',
                        help='read password for binddn from file secretfile')
    parser.add_argument('-s', '--server', action='append', required=True,
                        help='LDAP server. Can be set multiple instance. Use first active strategy')
    parser.add_argument('-p', '--port', type=int, default=389,
                        help='LDAP server port (defaults to %(default)i)')
    parser.add_argument('-z', '--ssl', action='store_true',
                        help='SSL encrypt the LDAP connection')
    parser.add_argument('-c', '--timeout', type=int, default=10,
                        help='connect timeout (defaults to %(default)i)')
    parser.add_argument('-t', '--timelimit', type=int, default=10,
                        help='search time limit (defaults to %(default)i)')
    parser.add_argument('-b', '--basedn', type=str, required=True,
                        help='base dn under where to search for users.')
    parser.add_argument('--csv-path', default='result.csv',
                        help='path for result csv file (defaults to %(default)s)')

    return parser


def main():
    parser = create_cli()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()
    conn = None

    if hasattr(args, 'bindpasswd') and args.bindpasswd:
        bindpasswd = args.bindpasswd
    elif hasattr(args, 'secretfile') and args.secretfile:
        if path.isfile(args.secretfile):
            try:
                with open(args.secretfile, 'r') as passwdfile:
                    bindpasswd = passwdfile.readline().replace('\n', '')
            except Exception as exc:
                print('ldap_csv_exporter Runtime error {}({})'.format(type(exc).__name__, exc))
                bindpasswd = ''
        else:
            print('ldap_csv_exporter Password file {} not found'.format(args.secretfile))
            bindpasswd = ''
    else:
        print('ldap_csv_exporter Password for binddn is not set')
        bindpasswd = ''
    sys.stdout.flush()
    if bindpasswd:
        try:
            conn = get_ldap_connection(server=args.server,
                                       port=args.port,
                                       ssl=args.ssl,
                                       timeout=int(args.timeout),
                                       binddn=args.binddn,
                                       bindpasswd=bindpasswd)
            if conn.bound:
                try:
                    search_result = get_ldap_info(connection=conn,
                                                  timelimit=int(args.timelimit),
                                                  basedn=args.basedn,
                                                  filter=u'(&(objectClass=user)(!(objectClass=computer)))',
                                                  attributes=['sAMAccountName',
                                                              'cn',
                                                              'company',
                                                              'department'])
                except Exception as exc:
                    print('{} {}({})'.format(id, type(exc).__name__, exc))
                    conn.strategy.close()
                    if conn.closed:
                        conn.bind()

                else:
                    with open(args.csv_path, mode='w') as csv_file:
                        fieldnames = ['username',
                                      'name',
                                      'company',
                                      'department']

                        writer = csv.DictWriter(csv_file,
                                                fieldnames=fieldnames)
                        writer.writeheader()
                        if len(search_result) > 0:
                            for entry in search_result:
                                writer.writerow({'username': entry['sAMAccountName'],
                                                 'name': entry['cn'],
                                                 'company': entry['company'] if type(entry['company']) is not list else '',
                                                 'department': entry['department'] if type(entry['department']) is not list else ''})
        except Exception as exc:
            print('ldap_csv_exporter Runtime error {}({})'.format(type(exc).__name__, exc))
    else:
        sys.exit()


if __name__ == '__main__':
    main()
