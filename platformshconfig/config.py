import os
import sys
import json
import base64

__all__ = [
    "Config",
    "BuildTimeVariableAccessException",
    "NoCredentialFormatterFoundException",
    "NotValidPlatformException"

]


class Config:
    """Reads Platform.sh configuration from environment variables.

    See: https://docs.platform.sh/development/variables.html

    The following are 'magic' properties that may exist on a Config object. Before accessing a property, check its
    existence with hasattr(config, variableName). Attempting to access a nonexistent variable will throw an exception.

    Attributes:
        (The following properties are available at build time and run time.)

        project (string):
            The project ID.
        applicationName (string):
            The name of the application, as defined in its configuration.
        treeID (string):
            An ID identifying the application tree before it was built: a unique hash is generated based on the contents
            of the application's files in the repository.
        appDir (string):
            The absolute path to the application.
        projectEntropy (string):
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
        port (string):
            The TCP port number the application should listen to for incoming requests.
        socket (string):
            The Unix socket the application should listen to for incoming requests.

    .. Platform.sh Environment Variables
            https://docs.platform.sh/development/variables.html

    """

    """
    Local index of the variables that can be accessed as direct properties (build and
    runtime). The key is the property that will be read. The value is the environment variables, minus prefix,
    that contains the value to look up.
    """
    _directVariables = {
        "project": "PROJECT",
        "appDir": "APP_DIR",
        "applicationName": 'APPLICATION_NAME',
        "treeID": "TREE_ID",
        "projectEntropy": "PROJECT_ENTROPY"
    }

    """
    Local index of the variables that can be accessed as direct properties
    (runtime only). The key is the property that will be read. The value is the environment variables, minus
    prefix, that contains the value to look up.
    """
    _directVariablesRuntime = {
        "branch": "BRANCH",
        "environment": "ENVIRONMENT",
        "documentRoot": "DOCUMENT_ROOT",
        "smtpHost": "SMTP_HOST"
    }

    """
    Local index of variables available at runtime that have no prefix.
    """
    _unPrefixedVariablesRuntime = {
        "port": "PORT",
        "socket": "SOCKET"
    }

    """
    A local copy of all environment variables as of when the object was initialized.
    """
    _environmentVariables = []

    """
    The vendor prefix for all environment variables we care about.
    """
    _envPrefix = ''

    """
    The routes definition dict. Only available at runtime.
    """
    _routesDef = {}

    """
    The relationships definition dict. Only available at runtime.
    """
    _relationshipsDef = {}

    """
    The variables definition dict. Available in both build and runtime, although possibly with different
    values.
    """
    _variablesDef = {}

    """
    The application definition dict. This is, approximately, the .platform.app.yaml file in nested dictionary form.
    """
    _applicationDef = {}

    """
    A map of the registered credential formatters.  The key is the name, the value is a function.
    """
    _credentialFormatters = {}

    def __init__(self, environment_variables=None, env_prefix='PLATFORM_'):
        """Constructs a ConfigReader object.

        Args:
            environment_variables (dict):
                The environment variables to read. Defaults to the current environment. Defaults to None.
            env_prefix (string):
                The prefix for environment variables. Defaults to 'PLATFORM_'.

        """

        self._environmentVariables = os.environ if environment_variables is None else environment_variables
        self._envPrefix = env_prefix

        if self['ROUTES']:
            routes = self['ROUTES']
            self._routesDef = self.decode(routes)
        if self['RELATIONSHIPS']:
            relationships = self['RELATIONSHIPS']
            self._relationshipsDef = self.decode(relationships)
            self.register_formatter('pymongo', pymongo_formatter)
            self.register_formatter('pysolr', pysolr_formatter)
            self.register_formatter('postgresql_dsn', posgresql_dsn_formatter)

        if self['VARIABLES']:
            variables = self['VARIABLES']
            self._variablesDef = self.decode(variables)
        if self['APPLICATION']:
            application = self['APPLICATION']
            self._applicationDef = self.decode(application)

    def is_valid_platform(self):
        """Checks whether the code is running on a platform with valid environment variables.

        Returns:
            bool:
                True if configuration can be used, False otherwise.

        """

        return 'APPLICATION_NAME' in self

    def in_build(self):
        """Checks whether the code is running in a build environment.

        Returns:
            bool: True if running in build environment, False otherwise.

        """

        return self.is_valid_platform() and not self['ENVIRONMENT']

    def in_runtime(self):
        """Checks whether the code is running in a runtime environment.

        Returns:
            bool: True if in a runtime environment, False otherwise.
        """

        return self.is_valid_platform() and self['ENVIRONMENT']

    def credentials(self, relationship, index=0):
        """Retrieves the credentials for accessing a relationship.

        Args:
            relationship (string):
                The relationship name as defined in .platform.app.yaml
            index (int):
                The index within the relationship to access. This is always 0, but reserved for future extension.

        Returns:
            The credentials dict for the service pointed to by the relationship.

        Raises:
            RuntimeError:
                Thrown if called in a context that has no relationships (eg, in build).
            KeyError:
                Thrown if the relationship/index pair requested does not exist.

        """

        if not self._relationshipsDef:
            if self.in_build():
                raise BuildTimeVariableAccessException(
                    'Relationships are not available during the build phase.'
                )
            raise NotValidPlatformException(
                """No relationships are defined. Are you sure you are on Platform.sh?
                If you're running on your local system you may need to create a tunnel
                 to access your environment services.  See https://docs.platform.sh/gettingstarted/local/tethered.html"""
            )

        if not self.has_relationship(relationship):
            raise KeyError(
                'No relationship defined: {}. Check your .platform.app.yaml file.'
                .format(relationship))
        if index >= len(self._relationshipsDef):
            raise KeyError('No index {} defined for relationship: {}.  '
                             'Check your .platform.app.yaml file.'.format(
                                 index, relationship))
        return self._relationshipsDef[relationship][index]

    def variable(self, name, default=None):
        """Returns a variable from the VARIABLES dict.

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
            The value of the variable, or the specified default. This may be a string or a dict.

        """

        if not self._variablesDef:
            return default
        return self._variablesDef.get(name, default)

    def variables(self):
        """Returns the full variables dict.

        If you're looking for a specific variable, the variable() method is a more robust option.
        This method is for classes where you want to scan the whole variables list looking for a pattern.

        Returns:
            The full variables dict.

        """

        if not self._variablesDef:
            raise NotValidPlatformException(
                'No variables are defined.  Are you sure you are running on Platform.sh?'
            )
        return self._variablesDef

    def routes(self):
        """Return the routes definition.

        Returns:
            The routes dict.

        Raises:
            RuntimeError:
                If the routes are not accessible due to being in the wrong environment.

        """
        if self.in_build():
            raise BuildTimeVariableAccessException(
                'Routes are not available during the build phase.'
            )
        if not self._routesDef:
            raise NotValidPlatformException(
                'No routes are defined.  Are you sure you are running on Platform.sh?'
            )
        return self._routesDef

    def get_route(self, route_id):
        """Get route definition by route ID.

        Args:
            route_id (string):
                The ID of the route to load.

        Returns:
            The route definition. The generated URL of the route is added as a 'url' key.

        Raises:
            KeyError:
                If there is no route by that ID, an exception is thrown.

        """

        if not self._routesDef:
            raise NotValidPlatformException(
                'No routes are defined.  Are you sure you are running on Platform.sh?'
            )

        for (url, route) in self.routes().items():
            if route['id'] == route_id:
                route['url'] = url
                return route
        raise KeyError('No such route id found: {}'.format(route_id))

    def application(self):
        """Returns the application definition dict.

        This is, approximately, the .platform.app.yaml file as a nested dict. However, it also has other information
        added by Platform.sh as part of the build and deploy process.

        Returns:
            The application definition dict.

        """

        if not self._applicationDef:
            raise NotValidPlatformException(
                'No application definition is available.  Are you sure you are running on Platform.sh?'
            )
        return self._applicationDef

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

    def register_formatter(self, name, formatter):
        """Adds a credential formatter to the configuration.

        A credential formatter is responsible for formatting the credentials for a relationship in a way expected
        by a particular client library. For instance, it can take the credentials from Platform.sh for a MongoDB
        database and format them into a URL string expected by pymongo. Use the formatted credentials() method to
        get the formatted  version of a particular relationship.

        Args:
            name (string):
                The name of the formatter. This may be an arbitrary alphanumeric string.
            formatter (callable):
                A callback function that will format relationship credentials for a specific client library.

        Returns:
            Config. The called object, for chaining.

        """

        self._credentialFormatters[name] = formatter
        return self

    def formatted_credentials(self, relationship, formatter):
        """Returns credentials for the specified relationship as formatted by the specified formatter.

        Args:
            relationship (string):
            formatter (string):

        Returns:
            The credentials formatted with the given formatter.

        Raises:
            NoCredentialFormatterFoundException

        """
        if formatter not in self._credentialFormatters:
            raise NoCredentialFormatterFoundException(
                'There is no credential formatter named {0} registered. Did you remember to call register_formatter()?'
                .format(formatter)
            )
        return self._credentialFormatters[formatter](self.credentials(relationship))


    def has_relationship(self, relationship):
        """Determines if a relationship is defined, and thus has credentials available.

        Args:
            relationship (string):
                The name of the relationship to check.

        Returns:
            bool:
                True if the relationship is defined, False otherwise.

        """
        return relationship in self._relationshipsDef

    def __getitem__(self, item):
        """Reads an environment variable, taking the prefix into account.

        Args:
            item (string):
                The variable to read.

        """

        check_name = self._envPrefix + item.upper()

        return self._environmentVariables.get(check_name)

    @staticmethod
    def decode(variable):
        """Decodes a Platform.sh environment variable.

        Args:
            variable (string):
                Base64-encoded JSON (the content of an environment variable).

        Returns:
            An dict (if representing a JSON object), or a scalar type.

        Raises:
            JSON decoding error.

        """

        try:
            if sys.version_info[1] > 5:
                return json.loads(base64.b64decode(variable))
            else:
                return json.loads(base64.b64decode(variable).decode('utf-8'))
        except json.decoder.JSONDecodeError:
            print('Error decoding JSON, code %d', json.decoder.JSONDecodeError)

    def __contains__(self, item):
        """Defines environment variable membership in Config.

        Args:
            item (string):
                variable string to be judged.

        Returns:
            bool:
                Returns True if Config contains the variable, False otherwise.

        """

        if self[item]:
            return True
        return False

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
            AttributeError:
                If a variable is not found, or if decoding fails.

        """

        is_build_var = config_property in self._directVariables.keys()
        is_runtime_var = config_property in self._directVariablesRuntime.keys()

        # For now, all unprefixed variables are also runtime variables. If that ever changes this logic will change
        # with it.
        is_unprefixed_var = config_property in self._unPrefixedVariablesRuntime.keys()

        if is_build_var:
            value = self[self._directVariables[config_property]]
        elif is_runtime_var:
            value = self[self._directVariablesRuntime[config_property]]
        elif is_unprefixed_var:
            value = self._environmentVariables.get(self._unPrefixedVariablesRuntime[config_property])
        else:
            raise AttributeError('No such variable defined: {}'.format(config_property))

        if not value:
            if self.in_build() and (is_runtime_var or is_unprefixed_var):
                raise BuildTimeVariableAccessException(
                    'The {} variable is not available during build time.'.format(config_property)
                )
            raise NotValidPlatformException(
                'The {} variable is not defined. Are you sure you\'re running on Platform.sh?'.format(config_property)
            )

        return value

def pymongo_formatter(credentials):
    """Returns a DSN for a pymongo-MongoDB connection.

    Note that the username and password will still be needed separately in the constructor.

    Args:
        credentials (dict):
            The credentials dictionary from the relationships.

    Returns:
        (string) A formatted pymongo DSN.

    """
    return '{0}:{1}/{2}'.format(
        credentials['host'],
        credentials['port'],
        credentials['path']
    )


def pysolr_formatter(credentials):
    """
    Returns formatted Solr credentials for a pysolr-Solr connection.

    Args:
        credentials (dict):
            The credentials dictionary from the relationships.

    Returns:
        (string) A formatted pysolr credential.

    """

    return "http://{0}:{1}/{2}".format(credentials['ip'],
                                       credentials['port'],
                                       credentials['path'])


def posgresql_dsn_formatter(credentials):
    """
    Returns formatted Posgresql credentials as DSN.

    Args:
        credentials (dict):
            The credentials dictionary from the relationships.

    Returns:
        (string) A formatted postgresql DSN.
    """

    return "postgresql://{0}:{1}@{2}:{3}/{4}".format(credentials["username"],
                                                     credentials["password"],
                                                     credentials["host"],
                                                     credentials["port"],
                                                     credentials["path"])

class BuildTimeVariableAccessException(RuntimeError):
    pass


class NoCredentialFormatterFoundException(ValueError):
    pass


class NotValidPlatformException(RuntimeError):
    pass
