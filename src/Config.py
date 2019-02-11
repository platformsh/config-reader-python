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

    def __init__(self, environment_variables=None, env_prefix=None):
        """Constructs a ConfigReader object.

        :param environment_variables: array|None
            The environment variables to read. Defaults to the current environment.
        :param env_prefix: string|None
            The prefix for environment variables. Defaults to 'PLATFORM_'.
        """
        self.environmentVariables = self.get_env() if environment_variables is None else environment_variables
        self.envPrefix = 'PLATFORM_' if env_prefix is None else env_prefix

    def is_available(self):
        """
        Checks whether any configuration is available.
        :return: bool
            True if configuration can be used, False otherwise.

        ..todo:: Re-define PHP-equivalent isset() function.
        """

        return self.envPrefix + 'ENVIRONMENT' in self.environmentVariables
        # return isset($this->environmentVariables[$this->envPrefix . 'ENVIRONMENT']);

    def get_env(self):
        """Load environment variables.

        :return: array

        ..todo:: Figure out PHP-equivalent $_ENV.
            return os.environ if 'VERSIONER_PYTHON_VERSION' >= 3.7 else $_ENV
        ..todo:: Figure out passing function to constructor __init__ logic?
        """
        pass

        # return os.environ if 'VERSIONER_PYTHON_VERSION' >= 3.7 else $_ENV

        # return PHP_VERSION_ID >= 70100 ? getenv(): $_ENV;

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


    @staticmethod
    def should_decode(current_property):
        """Determines whether a variable needs to be decoded.

        :param current_property: string
            The property name.
        :return: bool
            True if the variable is base64- and JSON-encoded, False otherwise.
        """

        return current_property.lower() in ['application', 'relationships', 'routes', 'variables']

    def get_variable_name(self, property_name):
        """Get the name of an environment variable.

        :param property_name: string
            The property name, e.g. 'relationships'.
        :return: string
            The environment variable name, e.g. PLATFORM_RELATIONSHIPS.
        """

        return self.envPrefix + property_name.upper()

    def __get__(self, instance, owner, config_property):
        """Gets a configuration property.

        :param config_property: string
            A (magic) property name. The properties are documented in the DocBlock for this class.
        :exception:
            If a variable is not found, or if decoding fails.
        :return: mixed
            The return types are documented in the DocBlock for this class.

        ..todo:: Flush out this __get__ (magic) function.
        """
        pass

    # def __get(self, property):
    #     # public function __get($property)
    #     '''Gets a configuration property.
    #
    #     :param property: string
    #         A (magic) property name. The properties are documented in the DocBlock for this class.
    #     :exception:
    #         Expection if a variable is not found, or if decoding fails.
    #     :return: mixed
    #         The return types are documented in the DocBlock for this class.
    #     '''
    #
    #     variableName = self.get_variable_name(property)
    #     # $variableName = $this->getVariableName($property);
    #
    #     if self.config[variableName] not in locals() and self.config[variableName] not in globals(): # !isset
    #     equivalent?
    #
    #     if (!isset($this->config[$variableName])) {
    #
    #         if variableName not in self.environmentVariables:
    #         # if (!array_key_exists($variableName, $this->environmentVariables)) {
    #
    #             value = self.environmentVariables[variableName]
    #             # $value = $this->environmentVariables[$variableName];
    #
    #             if self.should_decode(property):
    #             # if ($this->shouldDecode($property)) {
    #
    #                 value = self.decode(value)
    #                 # $value = $this->decode($value);
    #
    #             self.config[variableName] = value
    #             # $this->config[$variableName] = $value;
    #
    #         else:
    #             print('Environment variable not found: %s', variableName)
    #             # throw new \Exception(sprintf('Environment variable not found: %s', $variableName));
    #
    #     return self.config[variableName]
    #     # return $this->config[$variableName];

    def __isset(self, config_property):  # Is there an equivalent Python (magic) function to take this place?
        # public function __isset($property)
        """Checks whether a configuration property is set.

        :param config_property:
            A (magic) property name.
        :return: bool
            True if the property exists and is not None, False otherwise.

        ..todo:: Create a Python equivalent __isset or place equivalent in places where used
                (http://code.activestate.com/recipes/59892/)
        """

        return self.environmentVariables[self.get_variable_name(config_property)] in locals() \
            and self.environmentVariables[self.get_variable_name(config_property)] not in globals()  # isset equivalent?
        # return isset($this->environmentVariables[$this->getVariableName($property)]);
