# Platform.sh Config Reader (Python)

[![CircleCI Status](https://circleci.com/gh/platformsh/config-reader-python.svg?style=shield&circle-token=:circle-token)](https://circleci.com/gh/platformsh/config-reader-python)

This library provides a streamlined and easy to use way to interact with a Platform.sh environment. It offers utility methods to access routes and relationships more cleanly than reading the raw environment variables yourself.

This library requires Python 3.5 or later.

## Install

```bash
pip install platformshconfig
```

## Usage Example

Example:

```python
import sys
import pysolr

from platformshconfig import Config


config = Config()

if not config.is_valid_platform():
    sys.exit("Not in a Platform.sh Environment.")
    
credentials = config.credentials('solr')

formatted = config.formatted_credentials('solr', 'pysolr')

conn = pysolr.Solr(formatted)

# Do stuff with the conn here.
```

## API Reference

### Create a config object

```python
from platformshconfig import Config

config = Config()
```

`config` is now a `Config` object that provides access to the Platform.sh environment.

The `is_valid_platform()` method returns `True` if the code is running in a context that has Platform.sh environment variables defined.  If it returns `False` then most other functions will throw exceptions if used.

### Inspect the environment

The following methods return `True` or `False` to help determine in what context the code is running:

```python
config.in_build()

config.in_runtime()

config.on_enterprise()

config.on_production()
```

### Read environment variables

The following magic properties return the corresponding environment variable value.  See the [Platform.sh documentation](https://docs.platform.sh/development/variables.html) for a description of each.

The following are available both in Build and at Runtime:

```python
config.applicationName

config.appDir

config.project

config.treeID

config.projectEntropy
```

The following are available only if `in_runtime()` returned `True`:

```python
config.branch

condig.documentRoot

config.smtpHost

config.environment

config.socket

config.port
```

### Reading service credentials

[Platform.sh services](https://docs.platform.sh/configuration/services.html) are defined in a `services.yaml` file, and exposed to an application by listing a `relationship` to that service in the application's `.platform.app.yaml` file.  User, password, host, etc. information is then exposed to the running application in the `PLATFORM_RELATIONSHIPS` environment variable, which is a base64-encoded JSON string.  The following method allows easier access to credential information than decoding the environment variable yourself.

```python
creds = config.credentials('database')
```

The return value of `credentials()` is a dictionary matching the relationship JSON object, which includes the appropriate user, password, host, database name, and other pertinent information.  See the [Service documentation](https://docs.platform.sh/configuration/services.html) for your service for the exact structure and meaning of each property.  In most cases that information can be passed directly to whatever other client library is being used to connect to the service.

## Formatting service credentials

In some cases the library being used to connect to a service wants its credentials formatted in a specific way; it could be a DSN string of some sort or it needs certain values concatenated to the database name, etc.  For those cases you can use "Credential Formatters".  A Credential Formatter is any `callable` (function, anonymous function, object method, etc.) that takes a credentials array and returns any type, since the library may want different types.

Credential Formatters can be registered on the configuration object, and a few are included out of the box.  That allows 3rd party libraries to ship their own formatters that can be easily integrated into the `Config` object to allow easier use.

```python
def format_my_service(credentials):
    return "some string based on 'credentials'."

# Call this in setup
config.register_formatter('my_service', 'format_my_service')

# Then call this method to get the formatted version
formatted = config.formatted_credentials('database', 'my_service')
```

The first parameter is the name of a relationship defined in `.platform.app.yaml`.  The second is a formatter that was previously registered with `register_formatter()`.  If either the service or formatter is missing an exception will be thrown.  The type of `formatted` will depend on the formatter function and can be safely passed directly to the client library.

Two formatters are included out of the box:

* `pymongo` returns a DSN appropriate for using `pymongo` to connect to MongoDB. Note that `pymongo` will still need the username and password from the credentials dictionary passed as separate parameters.
* `pysolr`  returns a DSN appropriate for using `pysolr` to connect to Apache Solr. 

### Reading Platform.sh variables

Platform.sh allows you to define arbitrary variables that may be available at build time, runtime, or both.  They are stored in the `PLATFORM_VARIABLES` environment variable, which is a base64-encoded JSON string.  

The following two methods allow access to those values from your code without having to bother decoding the values yourself:

```python
config.variables()
```

This method returns a dictionary of all variables defined.  Usually this method is not necessary and `config.variable()` is preferred.

```python
config.variable("foo", "default")
```

This method looks for the "foo" variable.  If found, it is returned.  If not, the optional second parameter is returned as a default.

### Reading Routes

[Routes](https://docs.platform.sh/configuration/routes.html) on Platform.sh define how a project will handle incoming requests; that primarily means what application container will serve the request, but it also includes cache configuration, TLS settings, etc.  Routes may also have an optional ID, which is the preferred way to access them.

```python
config.route("main")
```

The `route()` method takes a single string for the route ID ("main" in this case) and returns the corresponding route array.  If the route is not found it will throw an exception.

To access all routes, or to search for a route that has no ID, the `routes()` method returns an dictionary of routes keyed by their URL.  That mirrors the structure of the `PLATFORM_ROUTES` environment variable.

If called in the build phase an exception is thrown.
