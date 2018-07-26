#!/usr/bin/env python
from __future__ import print_function

from st2common.runners.base_action import Action

import json
import os
import six
import subprocess
import sys

SKIP_ARGS = [
    'cmd',
    'sub_command',
    'cwd',
    'env',
    'credentials',
]

CREDENTIALS_OPTIONS = [
    'user',
    'password',
    'private_key',
    'run_as',
    'sudo_password',
]

BOLT_OPTIONS = [
    'nodes',
    'query',
    'noop',
    'description',
    'params',
    'params_obj',
    'host_key_check',
    'ssl',
    'ssl_verify',
    'concurrency',
    'compile_concurrency',
    'modulepath',
    'boltdir',
    'configfile',
    'inventoryfile',
    'transport',
    'connect_timeout',
    'tty',
    'tmpdir',
    'format',
    'verbose',
    'debug_',
    'trace',
]


class BoltAction(Action):

    def resolve_config(self, **kwargs):
        for k, v in six.iteritems(self.config):
            # skip if we're looking a the `credentials` options
            if k in CREDENTIALS_OPTIONS:
                continue

            # skip if the user explicitly set this proper on the action
            if kwargs[k] is not None:
                continue

            # only set the property if the value is set in the config
            if v is not None:
                kwargs[k] = v

        return kwargs

    def resolve_credentials(self, **kwargs):
        if not self.config.get('credentials'):
            return kwargs

        cred_name = kwargs.get('credentials')
        if not cred_name:
            return kwargs

        if cred_name not in self.config['credentials']:
            raise ValueError('Unable to find credentials in config: {}'.format(cred_name))

        credentials = self.config['credentials'][cred_name]
        for k, v in six.iteritems(credentials):
            # skip if the user explicitly set this proper on the action
            if kwargs[k] is not None:
                continue

            # only set the property if the value in the credential is set
            if v is not None:
                kwargs[k] = v

        return kwargs

    def format_option(self, option):
        # remove trailing _ in debug_
        if option[-1] == '_':
            option = option[:-1]
        return option.replace('_', '-')

    def build_args(self, **kwargs):
        args = []
        options = []

        # hack to make sure src comes before dest
        if 'src' in kwargs:
            args.append(kwargs['src'])
            del kwargs['src']
        if 'dest' in kwargs:
            args.append(kwargs['dest'])
            del kwargs['dest']

        for k, v in six.iteritems(kwargs):
            if k in SKIP_ARGS:
                continue
            if v is None:
                continue

            if k in BOLT_OPTIONS:
                k_formatted = self.format_option(k)
                if isinstance(v, bool):
                    if v:
                        options.append('--{}'.format(k_formatted))
                    else:
                        options.append('--no-{}'.format(k_formatted))
                else:
                    options.append('--{}'.format(k_formatted))
                    options.append(v)
            else:
                args.append(v)
        return args, options

    def execute(self, cmd, sub_command, env, cwd, args, options):
        full_cmd = [cmd] + sub_command.split(' ') + args + options
        # self.logger.debug(' '.join(full_cmd))
        process = subprocess.Popen(full_cmd,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   env=env,
                                   cwd=cwd)
        stdout, stderr = process.communicate()
        if stdout:
            try:
                stdout = json.loads(stdout)
            except Exception as e:
                self.logger.exception(e)

        if stderr:
            try:
                stderr = json.loads(stderr)
            except:
                pass
            sys.stderr.write(stderr)

        return_code = process.poll()
        success = False if return_code else True
        return (success, stdout)

    def run(self, **kwargs):
        kwargs = self.resolve_config(**kwargs)
        kwargs = self.resolve_credentials(**kwargs)

        cmd = kwargs['cmd']
        sub_command = kwargs['sub_command']
        env = os.environ.copy()
        env.update(kwargs.get('env', {}))
        cwd = kwargs.get('cwd', None)


        args, options = self.build_args(**kwargs)
        return self.execute(cmd, sub_command, env, cwd, args, options)
