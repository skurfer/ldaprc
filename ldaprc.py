#!/usr/bin/env python
# encoding: utf-8
"""
ldaprc.py

Created by Rob McBroom
"""
import os
import re

from collections import namedtuple


LDAPSetting = namedtuple(
    'LDAPSetting',
    ('raw_name', 'value', 'source'),
)


class LDAPRC(object):
    """Parse various 'ldaprc' files and return the settings."""
    def __init__(self, ldaprc=None):
        self.ldaprc = ldaprc
        if ldaprc is None:
            # no ldaprc given, fall back on defaults
            # settings in later files will take precedence over earlier files
            ldaprc_files = [
                '/etc/openldap/ldap.conf',            # Red Hat, macOS
                '/etc/ldap/ldap.conf',                # Debian and friends
                '/usr/local/etc/openldap/ldap.conf',  # FreeBSD
                os.getenv('HOME', '') + '/.ldaprc',   # User
            ]
            # look for ldaprc files in this, or a parent directory
            path = os.getcwd()
            while path:
                if 'ldaprc' in os.listdir(path):
                    ldaprc_path = path + os.path.sep + 'ldaprc'
                    if os.path.isfile(ldaprc_path):
                        ldaprc_files.append(ldaprc_path)
                keep_going = (path != os.path.dirname(path))
                path = os.path.dirname(path) if keep_going else None
        else:
            # use only the user-specified ldaprc if present
            ldaprc_files = (ldaprc,)

        self._settings = {}
        setting_pattern = re.compile(r'^([a-z]\w+)\s+(.*)', flags=re.I)
        # check each available file for settings
        # for settings found in multiple files, later files take precedence
        for rc_file in ldaprc_files:
            if os.path.exists(rc_file):
                for rc_line in open(rc_file):
                    rc_line = rc_line.strip()
                    m = setting_pattern.match(rc_line)
                    if m:
                        # this looks like a valid setting
                        setting_key = m.group(1)
                        setting_value = m.group(2)
                        self._settings[setting_key.lower()] = LDAPSetting(
                            setting_key, setting_value, rc_file,
                        )
        # check environment variables, which trump everything
        # unless the user provided a conf file
        if self.ldaprc is not None:
            return
        ldap_env_vars = [v for v in os.environ if v.startswith('LDAP')]
        for rc_var in ldap_env_vars:
            setting_key = rc_var[4:]
            setting_value = os.environ[rc_var]
            self._settings[setting_key.lower()] = LDAPSetting(
                setting_key, setting_value,
                '{} environment variable'.format(rc_var),
            )

    def __getattr__(self, setting):
        if setting.lower() in self._settings:
            return self._settings[setting.lower()].value
        raise AttributeError("no value defined for '{}'".format(setting))

    def __repr__(self):
        if self.ldaprc is None:
            return 'LDAPRC()'
        return "LDAPRC('{}')".format(self.ldaprc)

    def explain(self, setting=None):
        """show where each setting came from"""
        if setting is not None and getattr(self, setting):
            explain_settings = (self._settings[setting.lower()],)
        else:
            explain_settings = sorted(
                self._settings.values(),
                key=lambda s: s.raw_name.lower(),
            )
        for data in explain_settings:
            print('{}: Using value from {}'.format(data.raw_name, data.source))
