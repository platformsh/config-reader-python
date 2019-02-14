# pshconfig

[![Build Status](https://travis-ci.org/platformsh/platformsh-config-reader-python3.svg?branch=master)](https://travis-ci.org/platformsh/platformsh-config-reader-python3)

A small helper to access a Platform.sh application's configuration, via [environment variables](https://docs.platform.sh/development/variables.html).

Include it in your project with:

```bash
pip install pshconfig
```

## Usage

The available variables are documented as properties of the [Config](pshconfig/config.py) class

```python
from pshconfig import Config

# You can check for any particular value being available (recommended):


# Or you can check that any configuration is available at all:

```