import os
import json
import base64
import unittest

from copy import deepcopy

from platformshconfig import Config
from platformshconfig import BuildTimeVariableAccessException
from platformshconfig import NoCredentialFormatterFoundException


class ConfigTest(unittest.TestCase):

    # A mock environment to simulate build time.
    mockEnvironmentBuild = []

    # A mock environment to simulate runtime.
    mockEnvironmentDeploy = []

    def setUp(self):

        env = self.loadJsonFile('ENV')

        for item in ['PLATFORM_APPLICATION', 'PLATFORM_VARIABLES']:
            env[item] = self.encode(self.loadJsonFile(item))

        self.mockEnvironmentBuild = deepcopy(env)

        # These sub-values are always encoded

        for item in ['PLATFORM_ROUTES', 'PLATFORM_RELATIONSHIPS']:
            env[item] = self.encode(self.loadJsonFile(item))

        env_runtime = self.loadJsonFile('ENV_runtime')
        env = self.array_merge(env, env_runtime)
        self.mockEnvironmentDeploy = deepcopy(env)

    @staticmethod
    def array_merge(first_array, second_array):

        if isinstance(first_array, list) and isinstance(second_array, list):
            return first_array + second_array
        elif isinstance(first_array, dict) and isinstance(second_array, dict):
            return dict(list(first_array.items()) + list(second_array.items()))
        elif isinstance(first_array, set) and isinstance(second_array, set):
            return first_array.union(second_array)
        return False

    @staticmethod
    def loadJsonFile(name):

        data_path = os.getcwd() + '/tests/valid/{}.json'.format(name)
        with open(data_path, 'r') as read_file:
            return json.load(read_file)

    def test_not_on_platform_returns_correctly(self):

        config = Config()
        self.assertFalse(config.is_valid_platform())

    def test_on_platform_returns_correctly_in_runtime(self):

        config = Config(self.mockEnvironmentDeploy)
        self.assertTrue(config.is_valid_platform())

    def test_on_platform_returns_correctly_in_build(self):

        config = Config(self.mockEnvironmentBuild)
        self.assertTrue(config.in_build())

    def test_inbuild_in_build_phase_is_true(self):

        config = Config(self.mockEnvironmentBuild)
        self.assertTrue(config.in_build())

    def test_inbuild_in_deploy_phase_is_false(self):

        config = Config(self.mockEnvironmentDeploy)
        self.assertFalse(config.in_build())

    def test_inruntime_in_runtime_is_true(self):

        config = Config(self.mockEnvironmentDeploy)
        self.assertTrue(config.in_runtime())

    def test_inruntime_inbuild_phase_is_false(self):

        config = Config(self.mockEnvironmentBuild)
        self.assertFalse(config.in_runtime())

    def test_load_routes_in_runtime_works(self):

        config = Config(self.mockEnvironmentDeploy)
        routes = config.routes

        self.assertTrue(isinstance(routes, dict))

    def test_load_routes_in_build_fails(self):

        config = Config(self.mockEnvironmentBuild)

        with self.assertRaises(BuildTimeVariableAccessException):
            config.routes()

    def test_get_route_by_id_works(self):

        config = Config(self.mockEnvironmentDeploy)
        route = config.get_route('main')

        self.assertEqual('https://www.{default}/', route['original_url'])

    def test_get_non_existent_route_throws_exception(self):

        config = Config(self.mockEnvironmentDeploy)

        with self.assertRaises(KeyError):
            config.get_route('missing')

    def test_onenterprise_returns_true_on_enterprise(self):

        env = self.mockEnvironmentDeploy
        env['PLATFORM_MODE'] = 'enterprise'

        config = Config(env)

        self.assertTrue(config.on_enterprise())

    def test_onenterprise_returns_false_on_standard(self):

        env = self.mockEnvironmentDeploy

        config = Config(env)

        self.assertFalse(config.on_enterprise())

    def test_onproduction_on_enterprise_prod_is_true(self):

        env = self.mockEnvironmentDeploy
        env['PLATFORM_MODE'] = 'enterprise'
        env['PLATFORM_BRANCH'] = 'production'

        config = Config(env)

        self.assertTrue(config.on_production())

    def test_onproduction_on_enterprise_stg_is_false(self):

        env = self.mockEnvironmentDeploy
        env['PLATFORM_MODE'] = 'enterprise'
        env['PLATFORM_BRANCH'] = 'staging'

        config = Config(env)

        self.assertFalse(config.on_production())

    def test_onproduction_on_standard_prod_is_true(self):

        env = self.mockEnvironmentDeploy
        env['PLATFORM_BRANCH'] = 'master'

        config = Config(env)

        self.assertTrue(config.on_production())

    def test_onproduction_on_standard_stg_is_false(self):

        # The fixture has a non-master branch set by default.

        env = self.mockEnvironmentDeploy

        config = Config(env)

        self.assertFalse(config.on_production())

    def test_credentials_existing_relationship_returns(self):

        env = self.mockEnvironmentDeploy

        config = Config(env)

        creds = config.credentials('database')

        self.assertEqual('mysql', creds['scheme'])
        self.assertEqual('mysql:10.2', creds['type'])

    def test_credentials_missing_relationship_throws(self):

        env = self.mockEnvironmentDeploy

        config = Config(env)

        with self.assertRaises(KeyError):
            config.credentials('does-not-exist')

    def test_reading_existing_variable_works(self):

        env = self.mockEnvironmentDeploy

        config = Config(env)

        self.assertEqual('someval', config.variable('somevar'))

    def test_credentials_missing_relationship_index_throws(self):

        env = self.mockEnvironmentDeploy

        config = Config(env)

        with self.assertRaises(KeyError):
            config.credentials('database', 3)

    def test_reading_missing_variable_returns_default(self):

        env = self.mockEnvironmentDeploy

        config = Config(env)

        self.assertEqual('default-val',
                         config.variable('missing', 'default-val'))

    def test_variables_returns_on_platform(self):

        env = self.mockEnvironmentDeploy

        config = Config(env)

        variables = config.variables()

        self.assertEqual('someval', variables['somevar'])

    def test_build_property_in_build_exists(self):

        env = self.mockEnvironmentBuild

        config = Config(env)

        self.assertEqual('/app', config.appDir)
        self.assertEqual('app', config.applicationName)
        self.assertEqual('test-project', config.project)
        self.assertEqual('abc123', config.treeID)
        self.assertEqual('def789', config.projectEntropy)

        self.assertTrue(hasattr(config, 'appDir'))
        self.assertTrue(hasattr(config, 'applicationName'))
        self.assertTrue(hasattr(config, 'project'))
        self.assertTrue(hasattr(config, 'treeID'))
        self.assertTrue(hasattr(config, 'projectEntropy'))

    def test_build_and_deploy_properties_in_deploy_exists(self):
        env = self.mockEnvironmentDeploy

        config = Config(env)

        self.assertEqual('/app', config.appDir)
        self.assertEqual('app', config.applicationName)
        self.assertEqual('test-project', config.project)
        self.assertEqual('abc123', config.treeID)
        self.assertEqual('def789', config.projectEntropy)

        self.assertEqual('feature-x', config.branch)
        self.assertEqual('feature-x-hgi456', config.environment)
        self.assertEqual('/app/web', config.documentRoot)
        self.assertEqual('1.2.3.4', config.smtpHost)
        self.assertEqual('8080', config.port)
        self.assertEqual('unix://tmp/blah.sock', config.socket)

        self.assertTrue(hasattr(config, 'appDir'))
        self.assertTrue(hasattr(config, 'applicationName'))
        self.assertTrue(hasattr(config, 'project'))
        self.assertTrue(hasattr(config, 'treeID'))
        self.assertTrue(hasattr(config, 'projectEntropy'))

        self.assertTrue(hasattr(config, 'branch'))
        self.assertTrue(hasattr(config, 'environment'))
        self.assertTrue(hasattr(config, 'documentRoot'))
        self.assertTrue(hasattr(config, 'smtpHost'))
        self.assertTrue(hasattr(config, 'port'))
        self.assertTrue(hasattr(config, 'socket'))

    def test_deploy_property_in_build_throws(self):

        env = self.mockEnvironmentBuild

        config = Config(env)

        self.assertFalse('branch' in dir(config))

        with self.assertRaises(BuildTimeVariableAccessException):
            branch = config.branch

    def test_missing_property_throws_in_build(self):

        env = self.mockEnvironmentBuild

        config = Config(env)

        self.assertFalse('missing' in dir(config))

        with self.assertRaises(AttributeError):
            missing = config.missing

    def test_missing_property_throws_in_deploy(self):

        env = self.mockEnvironmentDeploy

        config = Config(env)

        self.assertFalse('missing' in dir(config))

        with self.assertRaises(AttributeError):
            missing = config.missing

    def test_application_array_available(self):

        env = self.mockEnvironmentDeploy

        config = Config(env)

        app = config.application()

        self.assertEqual('python:3.7', app['type'])

    def test_invalid_json_throws(self):

        with self.assertRaises(TypeError):
            config = Config({
                'PLATFORM_APPLICATION_NAME':
                'app',
                'PLATFORM_ENVIRONMENT':
                'test-environment',
                'PLATFORM_VARIABLES':
                base64.encodebytes('{some-invalid-json}')
            })

    def test_custom_prefix_works(self):

        config = Config({'FAKE_APPLICATION_NAME': 'test-application'}, 'FAKE_')

        self.assertTrue(config.is_valid_platform())

    def test_formatted_credentials_throws_when_no_formatter_defined(self):

        config = Config(self.mockEnvironmentDeploy)

        with self.assertRaises(NoCredentialFormatterFoundException):
            config.formatted_credentials('database', 'not-defined')

    def test_formatted_credentials_calls_a_formatter(self):

        config = Config(self.mockEnvironmentDeploy)

        config.register_formatter('test', lambda credentials: 'called')
        formatted = config.formatted_credentials('database', 'test')

        self.assertEqual('called', formatted)

    def test_pymongo_formatter(self):

        config = Config(self.mockEnvironmentDeploy)

        formatted = config.formatted_credentials('mongodb', 'pymongo')

        self.assertEqual('mongodb.internal:27017/main', formatted)  # include formatted string

    @staticmethod
    def encode(value):

        return base64.b64encode(json.dumps(value).encode('utf-8'))


if __name__ == "__main__":
    unittest.main()
