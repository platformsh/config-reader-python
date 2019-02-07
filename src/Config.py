import os
import sys
import json
import base64

# /**
#  * @class Config
#  * Reads Platform.sh configuration from environment variables.
#  *
#  * @link https://docs.platform.sh/development/variables.html
#  *
#  * The following are 'magic' properties that may exist on a Config object.
#  * Before accessing a property, check its existence with
#  * isset($config->variableName) or !empty($config->variableName). Attempting to
#  * access a nonexistent variable will throw an exception.
#  *
#  * @property-read string $project
#  *   The project ID.
#  * @property-read string $environment
#  *   The environment ID (usually the Git branch name).
#  * @property-read string $application_name
#  *   The name of the application, as defined in its configuration.
#  * @property-read string $tree_id
#  *   An ID identifying the application tree before it was built: a unique hash
#  *   is generated based on the contents of the application's files in the
#  *   repository.
#  * @property-read string $app_dir
#  *   The absolute path to the application.
#  * @property-read string $document_root
#  *   The absolute path to the web root of the application.
#  * @property-read string $mode
#  *   The hosting mode (this will only be set on Platform.sh Enterprise, and it
#  *   will have the value 'enterprise').
#  * @property-read array  $application
#  *   The application's configuration, as defined in the .platform.app.yaml file.
#  * @property-read array  $relationships
#  *   The environment's relationships to other services. The keys are the name of
#  *   the relationship (as configured for the application), and the values are
#  *   arrays of relationship instances. For example, the hostname of a 'mysql'
#  *   relationship may be stored in $config->relationships['mysql'][0]['host'].
#  * @property-read array  $routes
#  *   The routes configured for the environment.
#  * @property-read array  $variables
#  *   Custom environment variables.
#  * @property-read string $smtp_host
#  *   The hostname of the Platform.sh default SMTP server (an empty string if
#  *   emails are disabled on the environment).
#  */


class Config:

    '''A class used to read Platform.sh configuration from environment variables.

    Attributes
    ----------
    config : array
    environmentVariables : array
    envPrefix : string
    routes : array
        The routes definition array. Only available at runtime.
    relationships : array
        The relationships definition array. Only available at runtime.
    variables : array
        The variables definition array. Available in both build and
        runtime, although possibly with different values.

    Methods
    -------
    is_valid_platform
        Checks whether any configuration is available.
    __construct(environmentVariables=None, envPrefix=None)
        Constructs a ConfigReader object.
    get_env
        Load environment variables.
    decode(variable)
        Decodes a Platform.sh environment variable.
    should_decode(property)
        Determines whether a variable needs to be decoded.
    get_variable_name(property)
        Get the name of an environment variable.
    __get(property)
        Gets a configuration property.
    __isset(property)
        Checks whether a configuration property is set.

    Methods (Removed or not Updated)
    --------------------------------
    in_build
        Checks whether the code is running in a build environment.
    credentials(relationship, index=0)
        Retrieves the credentials for accessing a relationship.
    variable(name, default=None)
        Returns a variable from the VARIABLES array.
    variables
        Returns the full variables array.
    routes
        Returns the routes definition.
    get_route(id)
        Defines the route and adds route URL as a "url" key.
    on_enterprise
        Determines if the current environment is a Platform.sh Enterprise environment.
    on_production
        Determines if the current environment is a production environment.
    get_value(name)
        Reads and environment variables, taking the prefix into account.


    '''

    def __init__(self):

        self.config = []
        self.environmentVariables = []
        self.envPrefix = ''
        self.routes = []
        self.relationships = []
        self.variables = []


############################    IS SET   ###########################
    def is_valid_platform(self):
    # public function isAvailable()
        '''
        Checks whether any configuration is available.
        :return: bool
            True if configuration can be used, False otherwise.
        '''

        return self.envPrefix + 'ENVIRONMENT' in self.environmentVariables
        # return isset($this->environmentVariables[$this->envPrefix . 'ENVIRONMENT']);
############################    IS SET   ###########################


    def __construct(self, environment_variables=None, env_prefix=None):
        # public function __construct(array $environmentVariables = null, $envPrefix = null)
        '''Constructs a ConfigReader object.

        :param environment_variables: array|null
            The environment variables to read. Defaults to the current environment.
        :param env_prefix: string|null
            The prefix for environment variables. Defaults to 'PLATFORM_'.
        :return:
        '''

        self.environmentVariables = os.environ() if environment_variables is None else environment_variables
        # $this->environmentVariables = $environmentVariables === null ? $this->getEnv() : $environmentVariables;

        self.envPrefix = 'PLATFORM_' if env_prefix is not None else env_prefix
        # $this->envPrefix = $envPrefix === null ? 'PLATFORM_' : $envPrefix;

        # if self.is_valid_platform():
        #
        #     if not self.in_build() and self.routes == self.get_value('ROUTES'):
        #         # if (!$this->inBuild() & & $routes = $this->getValue('ROUTES'))
        #
        #         self.routes = self.decode(self.routes)
        #         # $this->routes != $routes: $this->routes = $this->decode($routes)
        #
        #     if not self.in_build() and self.relationships == self.get_value('RELATIONSHIPS'):
        #         # if (!$this->inBuild() & & $relationships = $this->getValue('RELATIONSHIPS'))
        #
        #         self.relationships = self.decode(self.relationships)
        #         # $this->relationships = $this->decode($relationships);
        #
        #     if self.variables == self.get_value('VARIABLES'):
        #         # if ($variables = $this->getValue('VARIABLES')) {
        #
        #         self.variables = self.decode(self.variables)
        #         # $this->variables = $this->decode($variables);


############################    MAGIC '_ENV'    ###########################
    def get_env(self):
        # private function getEnv()
        '''Load environment variables.

        :return: array
        '''

        # return os.environ() if some_check else _env
        # return PHP_VERSION_ID >= 70100 ? getenv() : $_ENV;
        # if PHP_VERSION_ID >= 70100:
        #     return getenv()
        # else:
        #     return $_ENV
        pass
############################    MAGIC '_ENV'   ###########################


############################    JSON DECODE/ERROR HANDLING   ###########################
    def decode(self, variable):
        # private function decode($variable)
        '''Decodes a Platform.sh environment variable.

        :param variable: string
            Base64-encoded JSON (the content of an environment variable).
        :exception:
            Exception if there is a JSON decoding error.
        :return: mixed
            An associative array (if representing a JSON object), or a scalar type.
        '''

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
############################    JSON DECODE/ERROR HANDLING   ###########################


    def should_decode(self, property):
        # private function shouldDecode($property)
        '''Determines whether a variable needs to be decoded.

        :param property: string
            The property name.
        :return: bool
            True if the variable is base64- and JSON-encoded, False otherwise.
        '''

        return property.lower() in ['application', 'relationships', 'routes', 'variables']
    # {
    #     return in_array(strtolower($property), [
    #         'application',
    #         'relationships',
    #         'routes',
    #         'variables',
    #     ]
    #     );
    # }


    def get_variable_name(self, property):
        # private function getVariableName($property)
        '''Get the name of an environment variable.

        :param property: string
            The property name, e.g. 'relationships'.
        :return: string
            The environment variable name, e.g. PLATFORM_RELATIONSHIPS.
        '''

        return self.envPrefix + property.upper()
        # return $this->envPrefix.strtoupper($property);

############################    IS SET   ###########################
    def __get(self, property):
        # public function __get($property)
        '''Gets a configuration property.

        :param property: string
            A (magic) property name. The properties are documented in the DocBlock for this class.
        :exception:
            Expection if a variable is not found, or if decoding fails.
        :return: mixed
            The return types are documented in the DocBlock for this class.
        '''

        variableName = self.get_variable_name(property)
        # $variableName = $this->getVariableName($property);

        if self.config[variableName] not in locals() and self.config[variableName] not in globals(): # !isset equivalent?
        # if (!isset($this->config[$variableName])) {

            if variableName not in self.environmentVariables:
            # if (!array_key_exists($variableName, $this->environmentVariables)) {

                value = self.environmentVariables[variableName]
                # $value = $this->environmentVariables[$variableName];

                if self.should_decode(property):
                # if ($this->shouldDecode($property)) {

                    value = self.decode(value)
                    # $value = $this->decode($value);

                self.config[variableName] = value
                # $this->config[$variableName] = $value;

            else:
                print('Environment variable not found: %s', variableName)
                # throw new \Exception(sprintf('Environment variable not found: %s', $variableName));

        return self.config[variableName]
        # return $this->config[$variableName];
############################    IS SET   ###########################


############################    IS SET   ###########################
    def __isset(self, property):
    # public function __isset($property)
        '''Checks whether a configuration property is set.

        :@param $property: string
            A (magic) property name.
        :return: bool
            True if the property exists and is not null, False otherwise.
        '''

        return self.environmentVariables[self.get_variable_name(property)] in locals() \
               and self.environmentVariables[self.get_variable_name(property)] not in globals() # isset equivalent?
        # return isset($this->environmentVariables[$this->getVariableName($property)]);
############################    IS SET   ###########################
















    # def in_build(self):
    #     '''
    #     Checks whether the code is running in a build environment.
    #     :return: If False, it's running at deploy time.
    #     '''
    #
    #     return self.is_valid_platform() and not self.get_value('ENVIRONMENT')
    #     # return $this->isAvailable() & & !$this->getValue('ENVIRONMENT');
    #
    # def credentials(self, relationship, index=0):
    #
    #     # Retrieves the credentials for accessing a relationship.
    #
    #     # The relationship must be defined in the .platform.app.yaml file.
    #
    #     # str $relationship: The relationship name as defined in .platform.app.yaml
    #     # int $index: The index within the relationship to access. This is always 0, but reserved for future extension.
    #     # array return: The credentials array for the service pointed to by the relationship.
    #     # throws RuntimeException: Thrown if called in a context that has no relationships (eg, in build)
    #     # throws InvalidArgumentException: If the relationship/index pair requested does not exist.
    #
    #     try:
    #         not self.is_available()
    #     except RuntimeError:
    #         raise RuntimeError\
    #             ('You are not running on Platform.sh, so relationships are not available.')
    #     try:
    #         self.in_build()
    #     except RuntimeError:
    #         raise RuntimeError\
    #             ('Relationships are not available during the build phase.')
    #
    #     try:
    #         self.relationships[relationship] is None
    #     except ValueError:
    #         raise ValueError\
    #             ('No relationship defined: %s. Check your .platform.app.yaml file.', relationship)
    #
    #     try:
    #         self.relationships[relationship][index] is None
    #     except ValueError:
    #         raise ValueError\
    #             ('No index %d defined for relationship: %s. Check your .platform.app.yaml file.', index, relationship)
    #
    #     return self.relationships[relationship][index]
    #

#     def variable(self, name, default=None):
#
#         # Returns a variable from the VARIABLES array.
#
#         # Note: variables prefixed with `env:` can be accessed as normal environment variables.
#         # This method will return such a variable by the name with the prefix still included.
#         # Generally it's better to access those variables directly.
#
#         if not self.is_available():
#
#             return default
#
#         else:
#
#             return self.variables[name] if self.variables[name] is not None else default
#
#     def variables(self):
#
#         # Returns the full variable array
#
#         # If you're looking for a specific variables, the variable() method is a more robust option.
#         # This method is for cases where you want to scan the whole variables list looking for a pattern.
#
#         # return array: The full variables array
#         # throws \RuntimeException: If not running on Platform.sh.
#
#         try:
#             not self.is_available()
#
#         except RuntimeError:
#             raise RuntimeError\
#                 ('You are not running on Platform.sh, so the variables array is not available.')
#
#         return self.variables # Variable collision: This should be the property self.variables, not the function; Should rename one.
#
#     def routes(self):
#
#         # Returns the routes definition.
#
#         # return array: The routes array, in PHP nested array form.
#         # throws \RunTimeException: If the routes are not accessible due to being in the wrong environment.
#
#         try:
#             not self.is_available()
#         except RuntimeError:
#             raise RuntimeError\
#                 ('You are not running on Platform.sh, so routes are not available.')
#
#         try:
#             not self.in_build() # Is this the right logic here?
#         except RuntimeError:
#             raise RuntimeError\
#                 ('Routes are not available during the build phase.')
#
# ######################
#
#     def get_route(self, id):
#
#         # string id: The ID of the route to load.
#
#         # return array: The route definition. The generated URL of the route is added as a "url" key.
#
#         try:
#
#             for route in self.routes():
#
#                 if self.route['id'] = id: # variable collision
#
#                     self.route['url'] = self.url
#
#         except RuntimeError:
#             raise RuntimeError\
#                 ('No such route id found: %s', id)
#
# #####################
#
#
#     def on_enterprise(self):
#
#         # Determines if the current environment is a Platform.sh Enterprise environment.
#
#         # return bool: True on an Enterprise environment, False otherwise.
#
#         return self.is_available() and self.get_value('MODE') == 'enterprise'
#
#     def on_production(self):
#
#         # Determines if the current environment is a production environment.
#
#         # Note: There may be a few edge cases where this is not entirely correct on Enterprise,
#         # if the production branch is not named `production`. In that case you'll need to use
#         # your own logic.
#
#         # return bool: True if the environment is a production environment, False otherwise.
#         # It will also return false if not running on Platform.sh or in the build phase.
#
#         if not self.is_available() and not self.in_build():
#
#             return False
#
#         prodBranch = 'production' if self.on_enterprise() else 'master'
#         # ('master', 'production')[self.on_enterprise()]
#
#         return self.get_value('BRANCH') == prodBranch
#
#     def get_value(self, name):
#
#         # Reads an environment variable, taking the prefix into account.
#
#         # param string name: The variable to read.
#         # return string|None
#
#         checkName = self.envPrefix + name
#
#         return self.environmentVariables[checkName] or None
#



