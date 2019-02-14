import os
import sys
import json
import base64


class Config:
    """Reads Platform.sh configuration from environment variables.

    See: https://docs.platform.sh/development/variables.html

    The following are 'magic' properties that may exist on a Config object. Before accessing a property, check its
    existence with hasattr(config, variableName). Attempting to access a nonexistent variable will throw an exception.

    Attributes:
        directVariables (dict):
            Local index of the variables that can be accessed as direct properties (build and
            runtime). The key is the property that will be read. The value is the environment variables, minus prefix,
            that contains the value to look up.
        directVariablesRuntime (dict):
            Local index of the variables that can be accessed as direct properties
            (runtime only). The key is the property that will be read. The value is the environment variables, minus
            prefix, that contains the value to look up.
        environmentVariables (dict):
            A local copy of all environment variables as of when the object was initialized.
        envPrefix (string):
            The vendor prefix for all environment variables we care about.
        routesDef (dict):
            The routes definition array. Only available at runtime.
        relationshipsDef (dict):
            The relationships definition array. Only available at runtime.
        variablesDef (dict):
            The variables definition array. Available in both build and runtime, although possibly with different
            values.
        applicationDef (dict):
            The application definition array. This is, approximately, the .platform.app.yaml file in nested array form.

        (The following properties are available at build time and run time.)

        project (string):
            The project ID.
        applicationName (string):
            The name of the application, as defined in its configuration.
        treeId (string):
            An ID identifying the application tree before it was built: a unique hash is generated based on the contents
            of the application's files in the repository.
        appDir (string):
            The absolute path to the application.
        entropy (string):
            A random string generated for each project, useful for generating hash keys.

        (The following properties are only available at runtime.)

        branch (string):
            The Git branch name.
        environment (string):
            The environment ID (usually the Git branch plus a hash).
        documentRoot (string):
            The absolute path to the web root of the application.
        smtpHost (string):
            The hostname of the Platform.sh default SMTP server (an empty string if emails are disabled on the
            environment.

    .. Platform.sh Environment Variables
            https://docs.platform.sh/development/variables.html

    """

    directVariables = {
        "project": "PROJECT",
        "appDir": "APP_DIR",
        "applicationName": 'APPLICATION_NAME',
        "treeID": "TREE_ID",
        "entropy": "PROJECT_ENTROPY"
    }

    directVariablesRuntime = {
        "branch": "BRANCH",
        "environment": "ENVIRONMENT",
        "documentRoot": "DOCUMENT_ROOT",
        "smtpHost": "SMTP_HOST"
    }

    environmentVariables = []
    envPrefix = ''

    routesDef = []
    relationshipsDef = []
    variablesDef = []
    applicationDef = []

    def __init__(self, environment_variables=None, env_prefix='PLATFORM_'):
        """Constructs a ConfigReader object.

        Args:
            environment_variables (dict):
                The environment variables to read. Defaults to the current environment. Defaults to None.
            env_prefix (string):
                The prefix for environment variables. Defaults to 'PLATFORM_'.

        """

        self.environmentVariables = os.environ if environment_variables is None else environment_variables
        self.envPrefix = env_prefix

        if self.is_valid_platform():
            if not self.in_build():
                if self['ROUTES']:
                    routes = self['ROUTES']
                    self.routesDef = self.decode(routes)
                if self['RELATIONSHIPS']:
                    relationships = self['RELATIONSHIPS']
                    self.relationshipsDef = self.decode(relationships)
            if self['VARIABLES']:
                variables = self['VARIABLES']
                self.variablesDef = self.decode(variables)
            if self['APPLICATION']:
                application = self['APPLICATION']
                self.applicationDef = self.decode(application)

    def is_valid_platform(self):
        """Checks whether the code is running on a platform with valid environment variables.

        Returns:
            bool:
                True if configuration can be used, False otherwise.

        """

        # return bool(self._get_value('APPLICATION_NAME'))
        return bool(self['APPLICATION_NAME'])

    def in_build(self):
        """Checks whether the code is running in a build environment.

        Returns:
            bool: True if running in build environment, False otherwise.

        """

        return self.is_valid_platform() and not self['ENVIRONMENT']

    def credentials(self, relationship, index=0):
        """Retrieves the credentials for accessing a relationship.

        Args:
            relationship (string):
                The relationship name as defined in .platform.app.yaml
            index (int):
                The index within the relationship to access. This is always 0, but reserved for future extension.

        Returns:
            The credentials array for the service pointed to by the relationship.

        Raises:
            RuntimeError:
                Thrown if called in a context that has no relationships (eg, in build).
            ValueError:
                Thrown if the relationship/index pair requested does not exist.

        """

        if not self.is_valid_platform():
            raise RuntimeError(
                'You are not running on Platform.sh, so relationships are not available.'
            )
        if self.in_build():
            raise RuntimeError(
                'Relationships are not available during the build phase.')
        if relationship not in self.relationshipsDef.keys():
            raise ValueError(
                'No relationship defined: {}. Check your .platform.app.yaml file.'
                .format(relationship))
        if index not in range(len(self.relationshipsDef)):
            raise ValueError('No index {} defined for relationship: {}.  '
                             'Check your .platform.app.yaml file.'.format(
                                 index, relationship))
        return self.relationshipsDef[relationship][index]

    def variable(self, name, default=None):
        """Returns a variable from the VARIABLES array.

        Note:
            Variables prefixed with `env`: can be accessed as normal environment variables. This method will return
            such a variable by the name with the prefix still included. Generally it's better to access those variables
            directly.

        Args:
            name (string):
                The name of the variable to retrieve.
            default (mixed):
                The default value to return if the variable is not defined. Defaults to None.

        Returns:
            The value of the variable, or the specified default. This may be a string or an array.

        """

        if not self.is_valid_platform():
            return default
        return self.variablesDef.get(name, default)

    def variables(self):
        """Returns the full variables array.

        If you're looking for a specific variable, the variable() method is a more robust option.
        This method is for classes where you want to scan the whole variables list looking for a pattern.

        Returns:
            The full variables array.

        """

        if not self.is_valid_platform():
            raise RuntimeError(
                'You are not running on Platform.sh, so the variables array is not available.'
            )
        return self.variablesDef

    @property
    def routes(self):
        """Return the routes definition.

        Returns:
            The routes array.

        Raises:
            RuntimeError:
                If the routes are not accessible due to being in the wrong environment.

        """
        if not self.is_valid_platform():
            raise RuntimeError(
                'You are not running on Platform.sh, so routes are not available.'
            )
        if self.in_build():
            raise RuntimeError(
                'Routes are not available during the build phase.')
        return self.routesDef

    def get_route(self, route_id):
        """Get route definition by route ID.

        Args:
            route_id (string):
                The ID of the route to load.

        Returns:
            The route definition. The generated URL of the route is added as a 'url' key.

        Raises:
            ValueError:
                If there is no route by that ID, an exception is thrown.

        """

        for (url, route) in self.routes.items():
            if route['id'] == route_id:
                route['url'] = url
                return route
        raise ValueError('No such route id found: {}'.format(route_id))

    def application(self):
        """Returns the application definition array.

        This is, approximately, the .platform.app.yaml file as a nested array. However, it also has other information
        added by Platform.sh as part of the build and deploy process.

        Returns:
            The application definition array.

        """

        if not self.is_valid_platform():
            raise RuntimeError(
                'You are not running on Platform.sh, so the application definition are not available.'
            )
        return self.applicationDef

    def on_enterprise(self):
        """Determines if the current environment is a Platform.sh Enterprise environment.

        Returns:
            bool:
                True on an Enterprise environment, False otherwise.

        """

        return self.is_valid_platform() and self['MODE'] == 'enterprise'

    def on_production(self):
        """Determines if the current environment is a production environment.

        Note:
            There may be a few edge cases where this is not entirely correct on Enterprise, if the production branch is
            not named `production`. In that case you'll need to use your own logic.

        Returns:
            bool:
                True if the environment is a production environment, False otherwise. It will also return False if not
                running on Platform.sh or in the build phase.

        """

        if not self.is_valid_platform() and not self.in_build():
            return False
        prod_branch = 'production' if self.on_enterprise() else 'master'
        return self['BRANCH'] == prod_branch

    def __getitem__(self, item):
        """Reads an environment variable, taking the prefix into account.

        Args:
            name (string):
                The variable to read.

        """

        check_name = self.envPrefix + item.upper()
        return self.environmentVariables.get(check_name)

    @staticmethod
    def decode(variable):
        """Decodes a Platform.sh environment variable.

        Args:
            variable (string):
                Base64-encoded JSON (the content of an environment variable).

        Returns:
            An associative array (if representing a JSON object), or a scalar type.

        Raises:
            JSON decoding error.

        """

        try:
            if sys.version_info[1] > 5:
                return json.loads(base64.decodebytes(variable))
            else:
                return json.loads(base64.decodebytes(variable).decode('utf-8'))
        except json.decoder.JSONDecodeError:
            print('Error decoding JSON, code %d', json.decoder.JSONDecodeError)

    def __getattr__(self, config_property):
        """Gets a configuration property.

        Args:
            config_property (string):
                A (magic) property name. The properties are documented in the DocBlock for this class.

        Returns:
            The return types are documented in the DocBlock for this class.

        Raises:
            RuntimeError:
                If not running on Platform.sh, and the variable is not found.
            ValueError:
                If a variable is not found, or if decoding fails.

        """

        if not self.is_valid_platform():
            raise RuntimeError(
                'You are not running on Platform.sh, so the {} variable is '
                'not available.'.format(config_property))
        is_build_var = config_property in self.directVariables.keys()
        is_runtime_var = config_property in self.directVariablesRuntime.keys()
        if self.in_build() and is_runtime_var:
            raise ValueError(
                'The {} variable is not available during build time.'.format(
                    config_property))
        if is_build_var:
            return self[self.directVariables[config_property]]
        if is_runtime_var:
            return self[self.directVariablesRuntime[config_property]]
        raise ValueError('No such variable defined: '.format(config_property))

    def isset(self, config_property):
        """Checks whether a configuration property is set.

        Args:
            config_property:
                A (magic) property name.

        Returns:
            bool:
                True if the property exists and is not None, False otherwise.

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