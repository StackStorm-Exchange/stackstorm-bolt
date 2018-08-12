[![Build Status](https://circleci.com/gh/StackStorm-Exchange/stackstorm-bolt.svg?style=shield&circle-token=:circle-token)](https://circleci.com/gh/StackStorm-Exchange/stackstorm-bolt) [![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# TODO
* This readme
* Tests

# bolt Integration Pack

StackStorm integration pack for [Puppet Bolt](https://puppet.com/docs/bolt).
This pack allows you to run any `bolt` command as a StackStorm action.
ChatOps aliases are also available so `bolt` commands can be invoked from chat.

## Quick Start

Getting start with Bolt is easy, simply run the following commands:

``` shell
st2 pack install bolt
st2 run bolt.install
```

Execute a test by running a command on the localhost:

``` shell
st2 run bolt.command_run nodes=local://localhost command="date"
```

## Configuration

Copy the example configuration in [bolt.yaml.example](./bolt.yaml.example)
to `/opt/stackstorm/configs/bolt.yaml` and edit as required.

* `cwd` - Current working directory where bolt will be executed
* `env` - Environment variables to override when executing bolt
* `cmd` - Path to the bolt executable [default = `/usr/local/bin/bolt`]
* `host_key_check` - Check host keys with SSH
* `ssl` - Use SSL with WinRM
* `ssl_verify` - Verify remote host SSL certificate with WinRM
* `concurrency` - Maximum number of simultaneous connections (default: 100)
* `compile_concurrency` - Maximum number of simultaneous manifest block compiles (default: number of cores)
* `modulepath` - List of directories containing modules, separated by ':'
* `boltdir` - Specify what Boltdir to load config from (default: autodiscovered from current working dir)
* `configfile` - Specify where to load config from (default: ~/.puppetlabs/bolt/bolt.yaml)
* `inventoryfile` - Specify where to load inventory from (default: ~/.puppetlabs/bolt/inventory.yaml)
* `transport` - Specify a default transport: ssh, winrm, pcp, local
* `connect_timeout` - Connection timeout (defaults vary)
* `tty` - Request a pseudo TTY on nodes that support it
* `tmpdir` - The directory to upload and execute temporary files on the target
* `format` - Output format to use: human or json [default = `json`]
* `verbose` - Display verbose logging
* `debug_` - Display debug logging
* `trace` - Display error stack traces
* `credentials` - Mapping of name to an object containing credential information
  * `user` - User to authenticate as
  * `password` - Password to authenticate with. Omit the value to prompt for the password.
  * `private_key` - Private ssh key to authenticate with
  * `run_as` - User to run as using privilege escalation
  * `sudo_password` - Password for privilege escalation. Omit the value to prompt for the password.

**Note** : All actions allow you to specify a `credentials` parameter that will
           reference the `credentials` information in the config. Alternatively
           all actions allow you to override these credential parameters so a
           config isn't required.

**Note** : When modifying the configuration in `/opt/stackstorm/configs/` please
           remember to tell StackStorm to load these new values by running
           `st2ctl reload --register-configs`

## Actions

* bolt.command_run
* bolt.file_upload
* bolt.install
* bolt.plan_list
* bolt.plan_run
* bolt.plan_show
* bolt.script_run
* bolt.task_list
* bolt.task_run
* bolt.task_show

### examples
TODO: Describe action


## Aliases

* bolt.command_run
* bolt.plan_list
* bolt.plan_show
* bolt.task_list
* bolt.task_run
* bolt.task_show

### examples
TODO: Describe action
