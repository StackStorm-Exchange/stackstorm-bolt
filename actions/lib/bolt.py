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
    'env'
]

BOLT_OPTIONS = [
    'nodes',
    'query',
    'noop',
    'description',
    'params',
    'params_obj',
    'user',
    'password',
    'private_key',
    'host_key_check',
    'ssl',
    'ssl_verify',
    'run_as',
    'sudo_password',
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
        self.logger.debug(' '.join(full_cmd))

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
        cmd = kwargs['cmd']
        sub_command = kwargs['sub_command']
        env = os.environ.copy()
        env.update(kwargs.get('env', {}))
        cwd = kwargs.get('cwd', None)

        args, options = self.build_args(**kwargs)
        return self.execute(cmd, sub_command, env, cwd, args, options)
