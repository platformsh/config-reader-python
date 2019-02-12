import os
import json
import base64


class Config:
    """A class used to read Platform.sh configuration from environment variables.

    Methods
    -------
    is_available
        Checks whether any configuration is available.
    get_env
        Load environment variables.
    decode(variable)
        Decodes a Platform.sh environment variable.
    should_decode(property)
        Determines whether a variable needs to be decoded.
    get_variable_name(property)
        Get the name of an environment variable.

    """

    # Local index of the variables that can be accessed as direct properties (build and runtime).

    # The key is the property that will be read. The value is the environment variables, minus
    # prefix, that contains the value to look up.

    # ..todo:: Do we want these instance variables to be class variables, or defined specifically
    #       as instance attributes?

    directVariables = {'project': 'PROJECT', 'appDir': 'APP_DIR', 'applicationName': 'APPLICATION_NAME',
                       'treeID': 'TREE_ID', 'entropy': 'PROJECT_ENTROPY'}

    # Local index of the variabels that can be accessed as direct properties (runtime only).

    # The key is the property that will be read. THe value is the environment variables, minus
    # prefix, that contains the value to look up.

    directVariablesRuntime = {'branch': 'BRANCH', 'environment': 'ENVIRONMENT', 'documentRoot': 'DOCUMENT_ROOT',
                              'smtpHost': 'SMTP_HOST'}

    # A local copy of all environment variables as of when the object was initialized

    environmentVariables = []

    # The vendor prefix for all environment variables we care about.

    envPrefix = ''

    # The routes definition array.

    # Only available at runtime.

    routesDef = []

    # The relationships definition array.

    # Only available at runtime.

    relationshipsDef = []

    # The variables definition array.

    # Available in both build and runtime, although possibly with different values.

    variablesDef = []

    # The application definition array.

    # This is, approximately, the .platform.app.yaml file in nested array form.

    applicationDef = []

    def __init__(self, environment_variables=None, env_prefix='PLATFORM_'):
        """Constructs a ConfigReader object.

        :param environment_variables: array|None
            The environment variables to read. Defaults to the current environment.
        :param env_prefix: string|None
            The prefix for environment variables. Defaults to 'PLATFORM_'.

        """

        self.environmentVariables = os.environ if environment_variables is None else environment_variables
        self.envPrefix = env_prefix

        if self.is_valid_platform():

            if not self.in_build() and self.get_value('ROUTES'):

                routes = self.get_value('ROUTES')
                self.routesDef = self.decode(routes)

            if not self.in_build() and self.get_value('RELATIONSHIPS'):

                relationships = self.get_value('RELATIONSHIPS')
                self.relationshipsDef = self.decode(relationships)

            if self.get_value('VARIABLES'):

                variables = self.get_value('VARIABLES')
                self.variablesDef = self.decode(variables)

            if self.get_value('APPLICATION'):

                application = self.get_value('APPLICATION')
                self.applicationDef = self.decode(application)

    def is_valid_platform(self):
        """Checks whether the code is running on a platform with valid environment variables.

        :return: bool
            True if configuration can be used, False otherwise.
        """

        return bool(self.get_value('APPLICATION_NAME'))

    def in_build(self):
        """Checks whether the code is running in a build environment.

        :return: bool
            True if running in build environment, False otherwise.
        """

        return self.is_valid_platform() and not self.get_value('ENVIRONMENT')

    @staticmethod
    def empty(given_variable):
        """Python replacement for PHPs empty().
        Determine whether a variable is considered to be empty.

        :param given_variable: mixed
            Variable to be checked.
        :return: bool
            True if variable is empty, False otherwise.
        """

        if not given_variable:

            return True

        return False

    def credentials(self, relationship, index=0):
        """Retrieves the credentials for accessing a relationship.

        :param relationship: string
            The relationship name as defined in .platform.app.yaml
        :param index: int
            The index within the relationship to access. This is always 0, but reserved for future extension.
        :return: array
            The credentials array for the service pointed to by the relationship.
        :exception RuntimeError:
            Thrown if called in a context that has no relationships (eg, in build).
        :exception ValueError:
            Thrown if the relationship/index pair requested does not exist.

        """

        if not self.is_valid_platform():
            raise RuntimeError('You are not running on Platform.sh, so relationships are not available.')

        if self.in_build():
            raise RuntimeError('Relationships are not available during the build phase.')

        if self.empty(self.relationshipsDef[relationship]):
            raise ValueError('No relationship defined: {}. Check your .platform.app.yaml file.'.format(relationship))

        if self.empty(self.relationshipsDef[relationship][index]):
            raise ValueError('No index {} defined for relationship: {}.  '
                             'Check your .platform.app.yaml file.'.format(index, relationship))

        return self.relationshipsDef[relationship][index]

    def variable(self, name, default=None):
        """Returns a variable from the VARIABLES array.

        Note: variables prefixed with `env`: can be accessed as normal environment variables.
        This method will return such a variable by the name with the prefix still included.
        Generally it's better to access those variables directly.

        :param name: string
            The name of the variable to retrieve.
        :param default: mixed
            The default value to return if the variable is not defined. Defaults to None.
        :return: mixed
            The value of the variable, or the specified default. This may be a string or an array.

        """

        if not self.is_valid_platform():

            return default

        return self.variablesDef[name] or default

    def variables(self):
        """Returns the full variables array.

        If you're looking for a specific variable, the variable() method is a more robust option.
        This method is for classes where you want to scan the whole variables list looking for a pattern.

        :return: array
            The full variables array
        """

        if not self.is_valid_platform():

            RuntimeError('You are not running on Platform.sh, so the variables array is not available.')

        return self.variablesDef

    def routes(self):
        """Return the routes definition.

        :return: array
            The routes array, in PHP nested array form.
        :exception RuntimeException:
            If the routes are not accessible due to being in the wrong environment.
        """
        if not self.is_valid_platform():
            RuntimeError('You are not running on Platform.sh, so routes are not available.')

        if self.in_build():
            RuntimeError('Routes are not available during the build phase.')

        return self.routesDef

    def get_route(self, route_id):
        """Get route definition by route ID.

        :param route_id: string
            The ID of the route to load.
        :return: array
            The route definition. The generated URL of the route is added as a 'url' key.
        :exception ValueError:
            If there is no route by that ID, an exception is thrown.

        ..todo:: Double-check for loop logic
        ..todo:: Double-check if statement logic
        ..todo:: Double-check ValueError syntax
        """

        # for (url, route) in self.routes().items:  # For dictionaries
        for (url, route) in enumerate(self.routes()):  # For lists

            if route['id'] == route_id:

                route['url'] = url

                return route

        ValueError('No such route id found: {}'.format(route_id))

    def application(self):
        """Returns the application definition array.

        This is, approximately, the .platform.app.yaml file as a nested array. However, it also has other information
        added by Platform.sh as part of the build and deploy process.

        :return: array
            The application definition array.
        """

        if not self.is_valid_platform():

            RuntimeError('You are not running on Platform.sh, so the application definition are not available.')

        return self.applicationDef

    def on_enterprise(self):
        """Determines if the current environment is a Platform.sh Enterprise environment.

        :return: bool
            True on an Enterprise environment, False otherwise.
        """

        return self.is_valid_platform() and self.get_value('MODE') == 'enterprise'

    def on_production(self):
        """Determines if the current environment is a production environment.

        Note: There may be a few edge cases where this is not entirely correct on Enterprise, if the production
        branch is not named `production`. In that case you'll need to use your own logic.

        :return: bool
            True if the environment is a production environment, False otherwise.
            It will also return False if not running on Platform.sh or in the build phase.

        """

        if not self.is_valid_platform() and not self.in_build():

            return False

        prod_branch = 'production' if self.on_enterprise() else 'master'

        return self.get_value('BRANCH') == prod_branch

    def get_value(self, name):
        """Reads an environment variable, taking the prefix into account.

        :param name: string
            The variable to read.
        :return: string|None
        """

        check_name = self.envPrefix + name.upper()

        return self.environmentVariables[check_name] or None

    @staticmethod
    def decode(variable):
        """Decodes a Platform.sh environment variable.

        :param variable: string
            Base64-encoded JSON (the content of an environment variable).
        :exception:
            JSON decoding error.
        :return: mixed
            An associative array (if representing a JSON object), or a scalar type.

        ..todo:: Figure out json_decode()
        ..todo:: Figure base64_decode()

        ..todo:: Update Exception to more elegant type. (see oop/accounts.py)
        """

        try:
            return json.loads(base64.decodebytes(variable))
        # variables = json.loads(base64.b64decode(os.getenv('PLATFORM_VARIABLES')).decode('utf-8'))

        except json.decoder.JSONDecodeError:
            print('Error decoding JSON, code %d', json.decoder.JSONDecodeError)

        # $result = json_decode(base64_decode($variable), true);
        # if (json_last_error()) {
        #     throw new \Exception(
        #         sprintf('Error decoding JSON, code: %d', json_last_error())
        #     );
        # }

    def __get__(self, instance, owner, config_property):
        """Gets a configuration property.

        :param config_property: string
            A (magic) property name. The properties are documented in the DocBlock for this class.
        :exception:
            If a variable is not found, or if decoding fails.
        :return: mixed
            The return types are documented in the DocBlock for this class.

        ..todo:: Double check __get__ magic logic.
        """

        if not self.is_valid_platform():

            RuntimeError('You are not running on Platform.sh, so the {} variable are not available.'.format(config_property))

        is_build_var = config_property in self.directVariables.keys()
        is_runtime_var = config_property in self.directVariablesRuntime.keys()

        if self.in_build() and is_runtime_var:

            ValueError('The {} variable is not available during build time.'.format(config_property))

        if is_build_var:

            return self.get_value(self.directVariables[config_property])

        if is_runtime_var:

            return self.get_value(self.directVariablesRuntime[config_property])

        raise ValueError('No such variable defined: '.format(config_property))

    def isset(self, config_property):
        """Checks whether a configuration property is set.

        :param config_property:
            A (magic) property name.
        :return: bool
            True if the property exists and is not None, False otherwise.

        ..todo:: Review isset return logic.
        """

        if not self.is_valid_platform():

            return False

        is_build_var = config_property in self.directVariables.keys()
        is_runtime_var = config_property in self.directVariablesRuntime.keys()

        if self.in_build():

            return is_build_var and config_property is not None

        if is_build_var or is_runtime_var:

            return True and config_property is not None

        return False
