==========================================================================
ldap-csv-exporter - Export user information from AD to csv
==========================================================================


What is this?
*************
``ldap-csv-exporter`` provides an executable called ``ldap_csv_exporter``
for exporting data about the AD users to CSV file:

 - username: sAMAccountName
 - name: cn
 - company: company
 - department: department


Installation
************
*on most UNIX-like systems, you'll probably need to run the following
`install` commands as root or by using sudo*

**from source**

::

  pip install git+http://github.com/verdel/ldap-csv-exporter

**or**

::

  git clone git://github.com/verdel/ldap-csv-exporter.git
  cd ldap-csv-exporter
  python setup.py install

as a result, the ``ldap_csv_exporter`` executable will be installed into
a system ``bin`` directory

Usage
-----
::

    ldap_csv_exporter --help
    usage: ldap_csv_exporter [-h] -d BINDDN [-w BINDPASSWD] [-W SECRETFILE] -s
                            SERVER [-p PORT] [-z] [-c TIMEOUT] [-t TIMELIMIT] -b
                            BASEDN [--csv-path CSV_PATH]
    
    Export user or computer information from AD to csv
    
    optional arguments:
      -h, --help            show this help message and exit
      -d BINDDN, --binddn BINDDN
                            DN to bind as to perform searches
      -w BINDPASSWD, --bindpasswd BINDPASSWD
                            password for binddn
      -W SECRETFILE, --secretfile SECRETFILE
                            read password for binddn from file secretfile
      -s SERVER, --server SERVER
                            LDAP server. Can be set multiple instance. Use first
                            active strategy
      -p PORT, --port PORT  LDAP server port (defaults to 389)
      -z, --ssl             SSL encrypt the LDAP connection
      -c TIMEOUT, --timeout TIMEOUT
                            connect timeout (defaults to 10)
      -t TIMELIMIT, --timelimit TIMELIMIT
                            search time limit (defaults to 10)
      -b BASEDN, --basedn BASEDN
                            base dn under where to search for users.
      --csv-path CSV_PATH   path for result csv file (defaults to result.csv)
