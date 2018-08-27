# OpenLDAP Settings Library #

This small library allows you to use your system’s existing OpenLDAP-style configuration settings with Python libraries like [ldap3][1] and [Python-LDAP][2].

```python
>>> from ldaprc import LDAPRC
>>> conf = LDAPRC()
>>> conf.uri
ldaps://ldap.example.com
```

## Why? ##

If all of your Python tools use this library to obtain LDAP settings, you will…

  * Avoid maintaining identical settings in multiple places
  * Always know that your Python tools are acting on the same data as `ldapsearch`, `ldapmodify`, etc.

## Settings Discovery ##

We follow the same rules for discovering settings as the OpenLDAP library by checking in this order (from least to most specific):

  * System-wide configuration files (such as `/etc/openldap/ldap.conf`)
  * The current user’s configuration file (`~/.ldaprc`)
  * An `ldaprc` file in the current working directory or a parent
  * Files referenced by the `LDAPCONF` and `LDAPRC` environment variables
  * Environment variables starting with “LDAP” (like `LDAPURI`)

More specific settings replace any that were previously discovered. All of the above steps are skipped if the `LDAPNOINIT` variable is set.

You can circumvent the discovery process by explicitly providing a configuration file, causing all other files and environment variables to be ignored.

```python
>>> from ldaprc import LDAPRC
>>> conf = LDAPRC('/path/to/file')
```

This can be useful for testing, or for applications that should not inherit anything from the rest of the system.

## Accessing Settings ##

All discovered settings are made available as case-insensitive properties of your `LDAPRC` object.

```python
>>> conf.base
dc=example,dc=com
>>> conf.BASE
dc=example,dc=com
```

## Troubleshooting ##

Since there are so many possible sources for these settings, you can find out where each came from (when you see unexpected/incorrect values, etc).

```python
>>> conf.binddn
uid=wrong_guy,ou=people,dc=example,dc=com
>>> conf.explain('binddn')
BINDDN: Using value from LDAPBINDDN environment variable
```

To see everything, just call `explain()` with no arguments.

```python
>>> conf.explain()
BASE: Using value from /etc/openldap/ldap.conf
BINDDN: Using value from LDAPBINDDN environment variable
SASL_MECH: Using value from /home/you/.ldaprc
TLS_CACERTDIR: Using value from /home/you/.ldaprc
TLS_REQCERT: Using value from /etc/openldap/ldap.conf
URI: Using value from /etc/openldap/ldap.conf
```

## Examples ##

Look up a user’s e-mail address (using the ldap3 library).

```python
from ldap3 import Connection, Server
from ldaprc import LDAPRC


conf = LDAPRC()
server = Server(conf.uri)
with Connection(server) as conn:
    conn.search(
        conf.base,
        '(&(objectClass=posixAccount)(uid=rob))',
        attributes=['mail'],
    )
    if conn.entries:
        print(conn.entries[0].mail.value)
```

## Installation ##

```console
$ pip install ldaprc
```

## Requirements ##

Python 2 or 3

[1]: https://github.com/cannatag/ldap3
[2]: https://www.python-ldap.org/
