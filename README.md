[![Build Status](https://circleci.com/gh/StackStorm-Exchange/stackstorm-bolt.svg?style=shield&circle-token=:circle-token)](https://circleci.com/gh/StackStorm-Exchange/stackstorm-bolt) [![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# bolt Integration Pack

StackStorm integration pack for [Puppet Bolt](https://puppet.com/docs/bolt).
This pack allows you to run any `bolt` command as a StackStorm action.
ChatOps aliases are also available so `bolt` commands can be invoked from chat.

## Quick Start

Getting start with Bolt is easy!
Run the following commands to install this pack and the install Bolt on your StackStorm host:

``` shell
st2 pack install bolt
st2 run bolt.install
```

Ensure Bolt is working by running a command on the localhost:

``` shell
st2 run bolt.command_run targets=local://localhost command="date"
```

## Configuration

Copy the example configuration in [bolt.yaml.example](./bolt.yaml.example)
to `/opt/stackstorm/configs/bolt.yaml` and edit as required. These configuration options
are copied from the Bolt configuration. For more details please see the
[Bolt configuration options](https://puppet.com/docs/bolt/0.x/bolt_configuration_options.html)
documentation.

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
* `tty` - Request a pseudo TTY on targets that support it
* `tmpdir` - The directory to upload and execute temporary files on the target
* `format` - Output format to use: human or json [default = `json`]
* `color` - Whether to show output in color
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

### Configuration Credentials

Most options in the config are simply key/value pairs, with the exception of `credentials`.
In order to make working with the Bolt pack easier, we've provided a mechanism to
store credentials in the pack's config. Credentials are stored as a dictionary, sometimes
called a hash, where the key is the name of the credential and the values are
the credential information (username, password, etc).

Below is an example of a simple config with a single credential named `dev`:

``` yaml
credentials:
  dev:
    user: 'test_user'
    password: 'myPassword'
```

Multiple credentials can also be specified:

``` yaml
credentials:
  dev:
    user: 'test_user'
    password: 'myPassword'
  qa:
    user: 'qa_user'
    password: 'xxxYYYzzz!!!'
  prod:
    user: 'prod_user'
    password: 'lkdjfldsfjO#U)R$'
```

These credentials can then be referenced by name when executing a `bolt` pack action
using the `credentials` parameter available on every action. Example:

``` shell
# use login information from the "dev" credential stored in the config
st2 run bolt.command_run targets="devserver01.domain.tld" command="ls /data" credentials="dev"
```

### Configuration Example

The configuration below is an example of what a end-user config might look like.
One of the most common config options will most likely be the `modulepath`, that will
direct `bolt` at the place where they've installed their Puppet modules.

``` yaml
---
concurrency: 200
modulepath: '/opt/custom/bolt/modules'
boltdir: '/opt/custom/bolt'
configfile: /opt/custom/bolt/bolt.yaml'
inventoryfile: '/opt/custom/bolt/inventory/dev.yaml'

# map of name -> credentials object
credentials:
  windows:
    user: 'first.last@domain.tld'
    password: 'secretSauce!'
  linux:
    user: 'boltuser'
    password: 'xyz123'
    private_key: '/opt/custom/bolt/ssh/id_rsa'
    run_as: 'boltsudo'
    sudo_password: 'abc456'
```

## Actions

Actions in the Bolt pack mirror the `bolt` CLI where each action represents a different
CLI command.

**Note** Before any actions are executed, `bolt` must be installed on all StackStorm nodes.
         This can be done by Configuration Management such as Puppet, Chef, or Ansible.
         Alternatively, we've provided the `bolt.install` action that will install `bolt`
         on CentOS/RHEL 6 and 7, and Ubuntu 14.04 and 16.04.

Below is a list of currently available actions:

* `bolt.apply` - Apply Puppet manifest code.
* `bolt.command_run` - Runs a command remotely.
* `bolt.file_upload` - Upload local file `src` to `dest` on each target.
* `bolt.install` - Installs Bolt on the StackStorm node.
* `bolt.plan_list` - Show list of available plans.
* `bolt.plan_run` - Run a Puppet task plan.
* `bolt.plan_show` - Show details for plan.
* `bolt.puppetfile_install` - Install modules from a Puppetfile into a Boltdir.
* `bolt.puppetfile_show_modules` - List modules available to Bolt
* `bolt.script_run` - Upload a local script and run it remotely.
* `bolt.task_list` - Show list of available tasks.
* `bolt.task_run` - Run a Puppet task.
* `bolt.task_show` - Show documentation for task.


### Action Example - bolt.apply

`bolt.apply` is used to apply a Puppet manifest file on remote hosts using the Puppet agent.
The `manifest` parameter is the path to the manifest file on the StackStorm host that will
be uploaded to the remote targets and applied with the Puppet agent.

``` shell
st2 run bolt.apply manifest="/etc/puppetlabs/code/test.pp" targets=host1.domain.tld
```

### Action Example - bolt.command_run

`bolt.command_run` is used to execute arbitrary commands on remote hosts. The `command`
parameter is a string of what should be executed:

``` shell
st2 run bolt.command_run command="ls -l /tmp" targets=host1.domain.tld
```

### Action Example - bolt.file_upload

`bolt.file_upload` uploads a file from the local StackStorm host `src` to a remote location `dst`
on all targets specified during execution.

* `src` - Path on the local StackStorm host filesystem of the file to be uploaded.
* `dest` - Path on the remote targets where the file should be uploaded to.

``` shell
st2 run bolt.file_upload src='/opt/stackstorm/data/myfile.txt' dest='/data' targets=host1.domain.tld,host2.domain.tld
```

### Action Example - bolt.install

`bolt.install` installs Bolt on the local StackStorm host, so the rest of the actions
can be executed.

``` shell
st2 run bolt.install
```

### Action Example - bolt.plan_list

`bolt.plan_list` returns a list of plans that `bolt` has in its `modulepath`.

``` shell
st1 run bolt.plan_list
```

### Action Example - bolt.plan_run

`bolt.plan_run` runs a Bolt Plan. When executing a plan you can pass parameters
to the plan by using the `params` option which takes a string of pre-formatted
parameters, just like you would supply on the CLI. Parameters on the CLI are
specified in `parameter=value` format. For more information please consult
the [bolt plan documentation](https://puppet.com/docs/bolt/0.x/writing_plans.html#concept-2302).

``` shell
st2 run bolt.plan_run targets="devserver01.domain.tld" plan="dns::upgrade" params="zone=xyz123.domain.tld. ttl=3200"
```

Alternatively parameters can be specified in object notation using the `params_obj`
parameter. This allows native parameter passing within workflow engines such
as Orquesta, Mistral and ActionChain. On the CLI this parameter takes in a
JSON formatted string.

CLI example (JSON string):

``` shell
st2 run bolt.plan_run targets="devserver01.domain.tld" plan="dns::upgrade" params_obj='{"zone": "xyz123.domain.tld",  "ttl": 3200}'
```

Orquesta example (YAML object notation):

``` yaml
  bolt_plan_example:
    action: bolt.plan_run
    input:
      plan: "dns::upgrade"
      targets: "devserver01.domain.tld"
      params_obj:
        zone: "xyz123.domain.tld"
        ttl: 3200
```

### Action Example - bolt.plan_show

`bolt.plan_show` describes details bout a plan available in bolt's `modulepath`.

``` shell
st2 run bolt.plan_show plan="dns::upgrade"
```

### Action Example - bolt.puppetfile_install

`bolt.puppetfile_install` installs modules from the Puppetfile located in the `boltdir`,
into the first directory found in `modulepath`.

Example, if my Puppetfile lives in `/custom/data/Pupptefile` and I want to install
modules into `/custom/data/modules` I would run:

``` shell
st2 run bolt.puppetfile_install boltdir='/custom/data` modulepath='/custom/data/modules`
```

### Action Example - bolt.puppetfile_show_modules

`bolt.puppetfile_show_modules` shows all of the available Puppet modules in Bolt's `modulepath`.

``` shell
st2 run bolt.puppetfile_show_modules modulepath='/custom/data/modules`
```

### Action Example - bolt.script_run

`bolt.script_run` uploads a local script, specified by the `script` paramter, from the
StackStorm node and run it remotely.

``` shell
st2 run bolt.script_run script=/opt/stackstorm/scripts/test.sh targets=host1.domain.tld,host2.domain.tld
```

### Action Example - bolt.task_list

`bolt.task_list` shows a list of all available tasks in bolt's `modulepath`.

``` shell
st2 run bolt.task_list
```

### Action Example - bolt.task_run

`bolt.task_run` Runs a Puppet task

``` shell
st2 run bolt.task_run task="service::linux" params='name=rsyslog action=restart'
```

### Action Example - bolt.task_show

`bolt.task_show` returns documentation for a task in bolt's `modulepath`.

``` shell
st2 run bolt.task_show task="service::linux"
```

### Action Example - bolt.version

`bolt.version` returns the version of Bolt installed on the StackStorm node.

``` shell
st2 run bolt.version"
```

## Aliases

ChatOps aliases are available for a large portion of the `bolt` actions.
By default these aliases are disabled. Editing the alias files and change them to
`enabled: true`. Then run `st2ctl reload --register-aliases`.

Below is a list of available aliases:

* `bolt.command_run`
* `bolt.plan_list`
* `bolt.plan_show`
* `bolt.task_list`
* `bolt.task_run`
* `bolt.task_show`
