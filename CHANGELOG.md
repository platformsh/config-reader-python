# Changelog

## [2.4.0] - 2021-02-03

### Added

* GitHub actions for tests (`quality-assurance.yaml`) and publishing to pypi (`pypi-publish.yaml`).

### Changed 

* named variable`prefix` on constructor renamed to `var_prefix`.

### Removed

* CircleCI action config. 

## [2.3.1] - 2019-11-04

### Added

* `CHANGELOG` added.
* `on_dedicated` method that determines if the current environment is a Platform.sh Dedicated environment. Replaces deprecated `on_enterprise` method.

### Changed

* Deprecates `on_enterprise` method - which is for now made to wrap around the added `on_dedicated` method. `on_enterprise` **will be removed** in a future release, so update your projects to use `on_dedicated` instead as soon as possible.

## [2.3.0] - 2019-09-19

### Added

* `get_primary_route` method for accessing routes marked "primary" in `routes.yaml`.
* `get_upstream_routes` method returns an object map that includes only those routes that point to a valid upstream.

## [2.2.3] - 2019-04-30

### Changed

* Removes guard on `variables()` method.

## [2.2.2] - 2019-04-29

### Changed

* Refactors dynamic property access to be more permissive.

## [2.2.1] - 2019-04-25

### Changed

* More permissive check for relationships.

## [2.2.0] - 2019-04-24

### Added

* `postgresql_dsn` credential formatter; returns a DSN appropriate for PostgreSQL connection.

## [2.1.1] - 2019-03-22

### Changed

* Fixes build issues in `has_relationship()` and `routes()` methods.

## [2.1.0] - 2019-03-22

### Added

* `has_relationship` method to determine if a relationship is defined, and thus has credentials available.

### Changed

* Fixes `routes` method.

## [2.0.4] - 2019-03-06

### Added

* CircleCI configuration