from bolt_base_action_test_case import BoltBaseActionTestCase
from lib.bolt import BoltAction
from st2common.runners.base_action import Action

import mock
import subprocess


class TestActionLibBolt(BoltBaseActionTestCase):
    __test__ = True
    action_cls = BoltAction

    def test_init(self):
        action = self.get_action_instance({})
        self.assertIsInstance(action, BoltAction)
        self.assertIsInstance(action, Action)

    def test_resolve_config_no_kwargs(self):
        action = self.get_action_instance({})
        action.config = {'cwd': '/tmp',
                         'env': {'BOLT_TEST': 'abc'}}
        result = action.resolve_config()
        self.assertEquals(result, {'cwd': '/tmp',
                                   'env': {'BOLT_TEST': 'abc'}})

    def test_resolve_config_kwargs_override_config(self):
        action = self.get_action_instance({})
        action.config = {'cwd': '/tmp'}
        result = action.resolve_config(cwd='/opt/stackstorm/packs/bolt')
        self.assertEquals(result, {'cwd': '/opt/stackstorm/packs/bolt'})

    def test_resolve_config_skip_credentials(self):
        action = self.get_action_instance({})
        action.config = {'user': 'st2admin',
                         'password': 'secret',
                         'private_key': '/home/stanley/.ssh/id_rsa',
                         'run_as': 'root',
                         'sudo_password': 'rootSecret'}
        result = action.resolve_config()
        self.assertEquals(result, {})

    def test_resolve_config_none_values(self):
        action = self.get_action_instance({})
        action.config = {'cwd': None}
        result = action.resolve_config()
        self.assertEquals(result, {})

    def test_resolve_credentials_no_config_credentials(self):
        action = self.get_action_instance({})
        action.config = {}
        result = action.resolve_credentials(test='kwargs')
        self.assertEquals(result, {'test': 'kwargs'})

    def test_resolve_credentials_no_kwargs_credentials(self):
        action = self.get_action_instance({})
        action.config = {
            'credentials': {
                'qa': {
                    'user': 'st2admin',
                    'password': 'secret',
                    'private_key': '/home/stanley/.ssh/id_rsa',
                    'run_as': 'root',
                    'sudo_password': 'rootSecret'
                }
            }
        }
        result = action.resolve_credentials(test='kwargs')
        self.assertEquals(result, {'test': 'kwargs'})

    def test_resolve_credentials_non_exist_credentials_name(self):
        action = self.get_action_instance({})
        action.config = {
            'credentials': {
                'qa': {
                    'user': 'st2admin',
                    'password': 'secret',
                    'private_key': '/home/stanley/.ssh/id_rsa',
                    'run_as': 'root',
                    'sudo_password': 'rootSecret'
                }
            }
        }
        with self.assertRaises(ValueError):
            action.resolve_credentials(credentials='doesnt_exist')

    def test_resolve_credentials_good_credentials(self):
        action = self.get_action_instance({})
        action.config = {
            'credentials': {
                'qa': {
                    'user': 'st2admin',
                    'password': 'secret',
                    'private_key': '/home/stanley/.ssh/id_rsa',
                    'run_as': 'root',
                    'sudo_password': 'rootSecret'
                }
            }
        }
        result = action.resolve_credentials(credentials='qa', otherarg='othervalue')
        self.assertEquals(result, {
            'credentials': 'qa',
            'otherarg': 'othervalue',
            'user': 'st2admin',
            'password': 'secret',
            'private_key': '/home/stanley/.ssh/id_rsa',
            'run_as': 'root',
            'sudo_password': 'rootSecret'
        })

    def test_resolve_credentials_config_credentials_dont_override_parameters(self):
        action = self.get_action_instance({})
        action.config = {
            'credentials': {
                'qa': {
                    'user': 'st2admin',
                    'password': 'secret',
                    'private_key': '/home/stanley/.ssh/id_rsa',
                    'run_as': 'root',
                    'sudo_password': 'rootSecret'
                }
            }
        }
        result = action.resolve_credentials(credentials='qa',
                                            user='param_user',
                                            run_as='param_runas')
        self.assertEquals(result, {
            'credentials': 'qa',
            'user': 'param_user',
            'password': 'secret',
            'private_key': '/home/stanley/.ssh/id_rsa',
            'run_as': 'param_runas',
            'sudo_password': 'rootSecret'
        })

    def test_resolve_credentials_config_credentials_none_value(self):
        action = self.get_action_instance({})
        action.config = {
            'credentials': {
                'qa': {
                    'user': 'st2admin',
                    'password': 'secret',
                    'private_key': '/home/stanley/.ssh/id_rsa',
                    'run_as': 'root',
                    'sudo_password': None
                }
            }
        }
        result = action.resolve_credentials(credentials='qa',
                                            user='param_user',
                                            run_as='param_runas')
        self.assertEquals(result, {
            'credentials': 'qa',
            'user': 'param_user',
            'password': 'secret',
            'private_key': '/home/stanley/.ssh/id_rsa',
            'run_as': 'param_runas'
        })

    def test_format_option(self):
        action = self.get_action_instance({})
        self.assertEquals(action.format_option('x_y_z'), 'x-y-z')
        # test that it strips trailing _
        self.assertEquals(action.format_option('x_y_z_'), 'x-y-z')

    def test_build_options_args_src_dest_args(self):
        action = self.get_action_instance({})
        options, args = action.build_options_args(src='local://localhost',
                                                  dest='ssh://stackstorm.domain.tld')
        self.assertEquals(args, ['local://localhost', 'ssh://stackstorm.domain.tld'])
        self.assertEquals(options, [])

    def test_build_options_args_params_obj_json(self):
        action = self.get_action_instance({})
        options, args = action.build_options_args(params_obj={'test': 'value'})
        self.assertEquals(args, [])
        self.assertEquals(options, ['--params', '{"test": "value"}'])

    # Test that params_obj get set properly when params is None
    def test_build_options_args_params_none(self):
        action = self.get_action_instance({})
        options, args = action.build_options_args(params_obj={'test': 'value'},
                                                  params=None)
        self.assertEquals(args, [])
        self.assertEquals(options, ['--params', '{"test": "value"}'])

    # Test that params doesn't get overwritten when params_obj is None
    @mock.patch("lib.bolt.json.dumps")
    def test_build_options_args_params_obj_empty(self, mock_json_dumps):
        action = self.get_action_instance({})
        options, args = action.build_options_args(params_obj={})
        self.assertEquals(args, [])
        self.assertEquals(options, [])
        assert not mock_json_dumps.called

    # Test that params doesn't get overwritten when params_obj is None
    @mock.patch("lib.bolt.json.dumps")
    def test_build_options_args_params_obj_none(self, mock_json_dumps):
        action = self.get_action_instance({})
        options, args = action.build_options_args(params_obj=None)
        assert not mock_json_dumps.called

    def test_build_options_args_params_overrides_params_obj_json(self):
        action = self.get_action_instance({})
        options, args = action.build_options_args(params_obj={'test': 'value'},
                                                  params='p=xxx')
        self.assertEquals(args, [])
        self.assertEquals(options, ['--params', 'p=xxx'])

    def test_build_options_args_skip_args(self):
        action = self.get_action_instance({})
        options, args = action.build_options_args(
            cmd='/bin/bolt',
            sub_command='file upload',
            cwd='/opt/stackstorm',
            env={'BOLT_ENV': 'xxx'},
            credentials='qa',
        )
        self.assertEquals(args, [])
        self.assertEquals(options, [])

    def test_build_options_args_skip_none_value(self):
        action = self.get_action_instance({})
        options, args = action.build_options_args(
            query=None,
            description='desc',
        )
        self.assertEquals(args, [])
        self.assertEquals(options, ['--description', 'desc'])

    def test_build_options_args_flag_options_true(self):
        action = self.get_action_instance({})
        options, args = action.build_options_args(
            noop=True,
            verbose=True,
            debug_=True,
            trace=True,
        )
        self.assertEquals(args, [])
        self.assertIn('--noop', options)
        options.remove('--noop')
        self.assertIn('--verbose', options)
        options.remove('--verbose')
        self.assertIn('--debug', options)
        options.remove('--debug')
        self.assertIn('--trace', options)
        options.remove('--trace')
        self.assertEquals(options, [])

    def test_build_options_args_flag_options_false(self):
        action = self.get_action_instance({})
        options, args = action.build_options_args(
            noop=False,
            verbose=False,
            debug_=False,
            trace=False,
        )
        self.assertEquals(args, [])
        self.assertEquals(options, [])

    def test_build_options_args_yes_no_options_true(self):
        action = self.get_action_instance({})
        options, args = action.build_options_args(
            host_key_check=True,
            ssl=True,
            ssl_verify=True,
            tty=True,
            color=True,
        )
        self.assertEquals(args, [])
        self.assertIn('--host-key-check', options)
        options.remove('--host-key-check')
        self.assertIn('--ssl', options)
        options.remove('--ssl')
        self.assertIn('--ssl-verify', options)
        options.remove('--ssl-verify')
        self.assertIn('--tty', options)
        options.remove('--tty')
        self.assertIn('--color', options)
        options.remove('--color')
        self.assertEquals(options, [])

    def test_build_options_args_yes_no_options_false(self):
        action = self.get_action_instance({})
        options, args = action.build_options_args(
            host_key_check=False,
            ssl=False,
            ssl_verify=False,
            tty=False,
            color=False,
        )
        self.assertEquals(args, [])
        self.assertIn('--no-host-key-check', options)
        options.remove('--no-host-key-check')
        self.assertIn('--no-ssl', options)
        options.remove('--no-ssl')
        self.assertIn('--no-ssl-verify', options)
        options.remove('--no-ssl-verify')
        self.assertIn('--no-tty', options)
        options.remove('--no-tty')
        self.assertIn('--no-color', options)
        options.remove('--no-color')
        self.assertEquals(options, [])

    def assert_remove_option(self, options, opt, value):
        self.assertIn(opt, options)
        options.remove(opt)
        self.assertIn(value, options)
        options.remove(value)

    def test_build_options_args_options(self):
        action = self.get_action_instance({})
        options, args = action.build_options_args(
            targets='targets',
            query='query',
            description='description',
            params='params',
            params_obj='params_obj',
            concurrency=12,
            compile_concurrency=100,
            modulepath='modulepath',
            boltdir='boltdir',
            project='project',
            configfile='configfile',
            inventoryfile='inventoryfile',
            transport='transport',
            connect_timeout=99,
            tmpdir='tmpdir',
            format='format',
            # credentials options
            user='user',
            password='password',
            private_key='private_key',
            run_as='run_as',
            sudo_password='sudo_password',
        )
        self.assertEquals(args, [])
        self.assert_remove_option(options, '--targets', 'targets')
        self.assert_remove_option(options, '--query', 'query')
        self.assert_remove_option(options, '--description', 'description')
        self.assert_remove_option(options, '--params', 'params')
        self.assert_remove_option(options, '--concurrency', '12')
        self.assert_remove_option(options, '--compile-concurrency', '100')
        self.assert_remove_option(options, '--modulepath', 'modulepath')
        self.assert_remove_option(options, '--boltdir', 'boltdir')
        self.assert_remove_option(options, '--project', 'project')
        self.assert_remove_option(options, '--configfile', 'configfile')
        self.assert_remove_option(options, '--inventoryfile', 'inventoryfile')
        self.assert_remove_option(options, '--transport', 'transport')
        self.assert_remove_option(options, '--connect-timeout', '99')
        self.assert_remove_option(options, '--tmpdir', 'tmpdir')
        self.assert_remove_option(options, '--format', 'format')
        self.assert_remove_option(options, '--user', 'user')
        self.assert_remove_option(options, '--password', 'password')
        self.assert_remove_option(options, '--private-key', 'private_key')
        self.assert_remove_option(options, '--run-as', 'run_as')
        self.assert_remove_option(options, '--sudo-password', 'sudo_password')
        self.assertEquals(options, [])

    def test_build_options_args_ensure_unknown_args_cast_to_strings(self):
        action = self.get_action_instance({})
        options, args = action.build_options_args(
            unknown_bool=True,
            unknown_int=123,
        )
        self.assertEquals(args, ['True', '123'])
        self.assertEquals(options, [])

    @mock.patch('lib.bolt.sys')
    @mock.patch('subprocess.Popen')
    def test_execute(self, mock_popen, mock_sys):
        action = self.get_action_instance({})

        mock_process = mock.MagicMock()
        mock_process.communicate.return_value = ('{"stdout": "value"}', '{"stderr": "data"}')
        mock_process.poll.return_value = 0

        mock_popen.return_value = mock_process

        result = action.execute('/opt/puppetlabs/bin/bolt',
                                'plan run',
                                ['--verbose'],
                                ['data=something'],
                                {'BOLT_TEST': 'Value'},
                                '/opt/stackstorm',
                                'json')

        self.assertEquals(result, (True, {"stdout": "value"}))
        mock_popen.assert_called_with(['/opt/puppetlabs/bin/bolt',
                                       'plan',
                                       'run',
                                       '--verbose',
                                       'data=something'],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      env={'BOLT_TEST': 'Value'},
                                      cwd='/opt/stackstorm')
        mock_process.communicate.assert_called_with()
        mock_process.poll.assert_called_with()
        mock_sys.stderr.write.assert_called_with('{"stderr": "data"}')

    @mock.patch('subprocess.Popen')
    def test_execute_error_return_code(self, mock_popen):
        action = self.get_action_instance({})

        mock_process = mock.MagicMock()
        mock_process.communicate.return_value = ('{"stdout": "data"}', '')
        mock_process.poll.return_value = -1

        mock_popen.return_value = mock_process

        result = action.execute('/opt/puppetlabs/bin/bolt',
                                'plan run',
                                ['--verbose'],
                                ['data=something'],
                                {'BOLT_TEST': 'Value'},
                                '/opt/stackstorm',
                                'json')

        self.assertEquals(result, (False, {"stdout": "data"}))
        mock_popen.assert_called_with(['/opt/puppetlabs/bin/bolt',
                                       'plan',
                                       'run',
                                       '--verbose',
                                       'data=something'],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      env={'BOLT_TEST': 'Value'},
                                      cwd='/opt/stackstorm')
        mock_process.communicate.assert_called_with()
        mock_process.poll.assert_called_with()

    @mock.patch('subprocess.Popen')
    def test_execute_json_parsing_failure(self, mock_popen):
        action = self.get_action_instance({})
        action.logger = mock.MagicMock()

        mock_process = mock.MagicMock()
        mock_process.communicate.return_value = ('not JSON data', '')
        mock_process.poll.return_value = 0

        mock_popen.return_value = mock_process

        result = action.execute('/opt/puppetlabs/bin/bolt',
                                'plan run',
                                ['--verbose'],
                                ['data=something'],
                                {'BOLT_TEST': 'Value'},
                                '/opt/stackstorm',
                                'json')

        self.assertEquals(result, (True, 'not JSON data'))
        mock_popen.assert_called_with(['/opt/puppetlabs/bin/bolt',
                                       'plan',
                                       'run',
                                       '--verbose',
                                       'data=something'],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      env={'BOLT_TEST': 'Value'},
                                      cwd='/opt/stackstorm')
        mock_process.communicate.assert_called_with()
        mock_process.poll.assert_called_with()
        self.assertEquals(action.logger.exception.call_count, 1)

    @mock.patch('subprocess.Popen')
    def test_execute_format_human(self, mock_popen):
        action = self.get_action_instance({})
        action.logger = mock.MagicMock()

        mock_process = mock.MagicMock()
        mock_process.communicate.return_value = ('not JSON data', '')
        mock_process.poll.return_value = 0

        mock_popen.return_value = mock_process

        result = action.execute('/opt/puppetlabs/bin/bolt',
                                'plan run',
                                ['--verbose'],
                                ['data=something'],
                                {'BOLT_TEST': 'Value'},
                                '/opt/stackstorm',
                                'human')

        self.assertEquals(result, (True, 'not JSON data'))
        mock_popen.assert_called_with(['/opt/puppetlabs/bin/bolt',
                                       'plan',
                                       'run',
                                       '--verbose',
                                       'data=something'],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      env={'BOLT_TEST': 'Value'},
                                      cwd='/opt/stackstorm')
        mock_process.communicate.assert_called_with()
        mock_process.poll.assert_called_with()
        self.assertEquals(action.logger.exception.call_count, 0)

    @mock.patch('lib.bolt.os.environ.copy')
    @mock.patch('lib.bolt.BoltAction.execute')
    def test_run(self, mock_execute, mock_os_environ_copy):
        action = self.get_action_instance({'cmd': '/opt/puppetlabs/bin/bolt',
                                           'credentials':
                                           {
                                               'stanley':
                                               {
                                                   'private_key': '/home/stanley/.ssh/id_rsa',
                                               }
                                           }})

        mock_execute.return_value = (True, {'mydata': 'xxx'})
        mock_os_environ_copy.return_value = {'INHERITED': 'true'}

        result = action.run(credentials='stanley',
                            sub_command='plan run',
                            env={'BOLT_TEST': 'Data'},
                            cwd='/opt/stackstorm',
                            params_obj={"input": "some data"},
                            plan='st2::deploy',
                            format='json')

        self.assertEquals(result, (True, {'mydata': 'xxx'}))
        mock_execute.assert_called_with('/opt/puppetlabs/bin/bolt',
                                        'plan run',
                                        ['--format', 'json',
                                         '--params', '{"input": "some data"}',
                                         '--private-key', '/home/stanley/.ssh/id_rsa'],
                                        ['st2::deploy'],
                                        {'BOLT_TEST': 'Data',
                                         'INHERITED': 'true'},
                                        '/opt/stackstorm',
                                        'json')

    @mock.patch('lib.bolt.os.environ.copy')
    @mock.patch('lib.bolt.BoltAction.execute')
    def test_run_creds_params(self, mock_execute, mock_os_environ_copy):
        action = self.get_action_instance({'cmd': '/opt/puppetlabs/bin/bolt',
                                           'credentials':
                                           {
                                               'stanley':
                                               {
                                                   'private_key': '/home/stanley/.ssh/id_rsa',
                                               }
                                           }})

        mock_execute.return_value = (True, {'mydata': 'xxx'})
        mock_os_environ_copy.return_value = {'INHERITED': 'true'}

        result = action.run(sub_command='plan run',
                            env={'BOLT_TEST': 'Data'},
                            cwd='/opt/stackstorm',
                            params_obj={"input": "some data"},
                            plan='st2::deploy',
                            user='cli_user',
                            password='cli_password',
                            format='human')

        self.assertEquals(result, (True, {'mydata': 'xxx'}))
        mock_execute.assert_called_with('/opt/puppetlabs/bin/bolt',
                                        'plan run',
                                        ['--format', 'human',
                                         '--params', '{"input": "some data"}',
                                         '--password', 'cli_password',
                                         '--user', 'cli_user'],
                                        ['st2::deploy'],
                                        {'BOLT_TEST': 'Data',
                                         'INHERITED': 'true'},
                                        '/opt/stackstorm',
                                        'human')
