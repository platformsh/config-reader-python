import os
import json
import base64
import unittest


class ConfigTest(unittest.TestCase):

    # A mock environment to simulate build time.
    mockEnvironmentBuild = []

    # A mock environment to simulate runtime.
    mockEnvironmentDeploy = []

    def runTest(self):
        pass

    def setUp(self):

        env = self.loadJsonFile('ENV')

        for item in ['PLATFORM_APPLICATION', 'PLATFORM_VARIABLES']:

            env[item] = self.encode(self.loadJsonFile(item))

        self.mockEnvironmentBuild = env

        # These sub-values are always encoded

        for item in ['PLATFORM_ROUTES', 'PLATFORM_RELATIONSHIPS']:

            env[item] = self.encode(self.loadJsonFile(item))

        env_runtime = self.loadJsonFile('ENV_runtime')

        env = self.array_merge(env, env_runtime)

        self.mockEnvironmentDeploy = env


        for key in self.mockEnvironmentBuild.keys():
            print(key, self.mockEnvironmentBuild[key])

        print('\n')

        for key in self.mockEnvironmentDeploy.keys():
            print(key, self.mockEnvironmentDeploy[key])

    @staticmethod
    def array_merge(first_array, second_array):
        if isinstance(first_array, list) and isinstance(second_array, list):
            return first_array + second_array
        elif isinstance(first_array, dict) and isinstance(second_array, dict):
            return dict(list(first_array.items()) + list(second_array.items()))
        elif isinstance(first_array, set) and isinstance(second_array, set):
            return first_array.union(second_array)
        return False

    def loadJsonFile(self, name):

        data_path = os.getcwd() + '/valid/{}.json'.format(name)

        with open(data_path, 'r') as read_file:

            return json.load(read_file)

    # def test_not_on_platform_returns_correctly(self):
    #     pass
    #
    # def test_on_platform_returns_correctly_in_runtime(self):
    #     pass
    #
    # def test_on_platform_returns_correctly_in_build(self):
    #     pass
    #
    # def test_inbuild_in_build_phase_is_true(self):
    #     pass
    #
    # def test_inbuild_in_deploy_phase_is_false(self):
    #     pass
    #
    # def _test_buildtime_properties_are_available(self):
    #     pass
    #
    # def _test_runtime_properties_are_available(self):
    #     pass
    #
    # def test_load_routes_in_runtime_works(self):
    #     pass
    #
    # def test_load_routes_in_build_fails(self):
    #     pass
    #
    # def test_get_route_by_id_works(self):
    #     pass
    #
    # def test_get_non_existent_route_throws_exception(self):
    #     pass
    #
    # def test_onenterprise_returns_true_on_enterprise(self):
    #     pass
    #
    # def test_onenterprise_returns_false_on_standard(self):
    #     pass
    #
    # def test_onproduction_on_enterprise_prod_is_true(self):
    #     pass
    #
    # def test_onproduction_on_enterprise_stg_is_false(self):
    #     pass
    #
    # def test_onproduction_on_standard_prod_is_true(self):
    #     pass
    #
    # def test_onproduction_on_standard_stg_is_false(self):
    #     pass
    #
    # def test_credentials_existing_relationship_returns(self):
    #     pass
    #
    # def test_credentials_missing_relationship_throws(self):
    #     pass
    #
    # def test_credentials_missing_relationship_index_throws(self):
    #     pass
    #
    # def test_reading_existing_variable_works(self):
    #     pass
    #
    # def test_reading_missing_variable_returns_default(self):
    #     pass
    #
    # def test_variables_returns_on_platform(self):
    #     pass
    #
    # def test_build_property_in_build_exists(self):
    #     pass
    #
    # def test_build_and_deploy_properties_in_deploy_exists(self):
    #     pass
    #
    # def test_deploy_property_in_build_throws(self):
    #     pass
    #
    # def test_missing_property_throws_in_build(self):
    #     pass
    #
    # def test_missing_property_throws_in_deploy(self):
    #     pass
    #
    # def test_application_array_available(self):
    #     pass
    #
    # def test_invalid_json_throws(self):
    #     pass
    #
    # def test_custom_prefix_works(self):
    #     pass

    def encode(self, value):

        # return base64.encodestring(json.dumps(value))
        # return json.dumps(value)
        return base64.b64encode(json.dumps(value).encode('utf-8'))
        # return base64.b64encode(json.dumps(value))


if __name__ == "__main__":
    # unittest.main()

    c = ConfigTest()
    c.setUp()