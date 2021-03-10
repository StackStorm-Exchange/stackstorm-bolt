#!/usr/bin/env python
from st2common.runners.base_action import Action

import json
import os
import six
import subprocess
import sys

# paramters/args that are 'metadata' and used for execution runtime
# these should not be processed as bolt arguments or options
SKIP_ARGS = [
    'cmd',
    'sub_command',
    'cwd',
    'env',
    'credentials',
]

# options for login credentials
BOLT_CREDENTIALS_OPTIONS = [
    'user',
    'password',
    'private_key',
    'run_as',
    'sudo_password',
]

# --option
BOLT_FLAG_OPTIONS = [
    'noop',
    'verbose',
    'debug_',
    'trace',
]

# --[no-]option
BOLT_YES_NO_OPTIONS = [
    'host_key_check',
    'ssl',
    'ssl_verify',
    'tty',
    'color',
]

# --option OPTION
BOLT_OPTIONS = [
    'targets',
    'query',
    'description',
    'params',
    'concurrency',
    'compile_concurrency',
    'modulepath',
    'boltdir',
    'project',
    'configfile',
    'inventoryfile',
    'transport',
    'connect_timeout',
    'tmpdir',
    'format',
]


class BoltAction(Action):

    def resolve_config(self, **kwargs):
        for k, v in six.iteritems(self.config):
            # skip if we're looking a the `credentials` options
            if k in BOLT_CREDENTIALS_OPTIONS:
                continue

            # skip if the user explicitly set this parameter when invoking the action
            if kwargs.get(k) is not None:
                continue

            # only set the property if the value is set in the config
            if v is not None:
                kwargs[k] = v

        return kwargs

    def resolve_credentials(self, **kwargs):
        """ Lookup credentials, by name, specified by the 'credentials' parameter
        during action invocation from the credentials dict stored in the config
        """
        # if there are no credentials specified in the config, we have nothing to lookup
        if not self.config.get('credentials'):
            return kwargs

        # get the name of credentials asked for during action invocation
        cred_name = kwargs.get('credentials')
        if not cred_name:
            return kwargs

        # if we couldn't find the credential in the config (by name), then raise an error
        if cred_name not in self.config['credentials']:
            raise ValueError('Unable to find credentials in config: {}'.format(cred_name))

        # lookup the credential by name
        credentials = self.config['credentials'][cred_name]
        for k, v in six.iteritems(credentials):
            # skip if the user explicitly set this property during action invocation
            if kwargs.get(k) is not None:
                continue

            # only set the property if the value in the credential object is set
            if v is not None:
                kwargs[k] = v

        return kwargs

    def format_option(self, option):
        # remove trailing _ in debug_
        if option[-1] == '_':
            option = option[:-1]
        return option.replace('_', '-')

    def build_options_args(self, **kwargs):
        options = []
        args = []

        # hack to make sure src comes before dest
        if 'src' in kwargs:
            args.append(kwargs['src'])
            del kwargs['src']
        if 'dest' in kwargs:
            args.append(kwargs['dest'])
            del kwargs['dest']

        # if params_obj is sepcified, convert it into JSON
        # only do this if 'params' was not specified ('params' overrides 'params_obj')
        if kwargs.get('params_obj'):
            if not kwargs.get('params'):
                kwargs['params'] = json.dumps(kwargs['params_obj'])

        # Need to remove if exists to prevent dict from getting passed into the options
        if "params_obj" in kwargs:
            del kwargs['params_obj']

        # parse all remaining arguments and options
        for k, v in sorted(six.iteritems(kwargs)):
            if k in SKIP_ARGS:
                continue
            if v is None:
                continue

            k_formatted = self.format_option(k)
            if k in BOLT_FLAG_OPTIONS:
                if v:
                    options.append('--{}'.format(k_formatted))

            elif k in BOLT_YES_NO_OPTIONS:
                if v:
                    options.append('--{}'.format(k_formatted))
                else:
                    options.append('--no-{}'.format(k_formatted))
            elif k in BOLT_OPTIONS or k in BOLT_CREDENTIALS_OPTIONS:
                options.append('--{}'.format(k_formatted))
                options.append(str(v))
            else:
                # assume it's an argument since it wasn't any of the options above
                args.append(str(v))
        return options, args

    def execute(self, cmd, sub_command, options, args, env, cwd, format):
        full_cmd = [cmd] + sub_command.split(' ') + options + args
        process = subprocess.Popen(full_cmd,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   env=env,
                                   cwd=cwd)
        stdout, stderr = process.communicate()
        # only try to parse JSON when the requested output format is JSON
        # if it's 'human' format, then skip JSON parsing to avoid the unecessary
        # exceptions
        if stdout and format == 'json':
            try:
                stdout = json.loads(stdout)
            except Exception as e:
                self.logger.exception(e)

        if stderr:
            sys.stderr.write(stderr)

        return_code = process.poll()
        success = False if return_code else True
        return (success, stdout)

    def run(self, **kwargs):
        # resolve credentials first so that creds from the CLI override
        # credentials in the config
        kwargs = self.resolve_credentials(**kwargs)
        kwargs = self.resolve_config(**kwargs)

        cmd = kwargs['cmd']
        sub_command = kwargs['sub_command']
        format = kwargs['format']
        # inherit from OS environment by default
        env = os.environ.copy()
        # merge in any environment variables set as action arguments
        env.update(kwargs.get('env', {}))
        cwd = kwargs.get('cwd', None)

        options, args = self.build_options_args(**kwargs)
        return self.execute(cmd, sub_command, options, args, env, cwd, format)
