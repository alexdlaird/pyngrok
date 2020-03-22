# Changelog
All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased](https://github.com/alexdlaird/pyngrok/compare/2.1.0...HEAD)

## [2.1.0](https://github.com/alexdlaird/pyngrok/compare/2.0.3...2.1.0) - 2020-02-21
### Added
- `region` parameter for `ngrok.connect()`, and `process.get_process()`. See [ngrok module](https://pyngrok.readthedocs.io/en/2.1.0/api.html#module-pyngrok.ngrok).
- `authtoken` parameter for `ngrok.connect()`, and `process.get_process()`. See [ngrok module](https://pyngrok.readthedocs.io/en/2.1.0/api.html#module-pyngrok.ngrok).
- Adding support for `Cygwin` as a platform by having it use the 64-bit Windows binary

## [2.0.3](https://github.com/alexdlaird/pyngrok/compare/2.0.2...2.0.3) - 2020-02-14
### Security
- Only allow instances of `urlopen` to be execute with an `http` request.

## [2.0.2](https://github.com/alexdlaird/pyngrok/compare/2.0.1...2.0.2) - 2020-02-08
### Changed
- Added `DEFAULT_RETRY_COUNT` for use in `installer._download_file`

## [2.0.1](https://github.com/alexdlaird/pyngrok/compare/2.0.0...2.0.1) - 2020-02-01
### Fixed
- Removed code that could cause a `ModuleNotFoundError` when another module referenced this module in it's `requirements.txt`.

## [2.0.0](https://github.com/alexdlaird/pyngrok/compare/1.4.1...2.0.0) - 2020-01-28
### Added
- `api_url` variable to `NgrokProcess` class.
- `startup_logs` variable to `NgrokProcess` class.
- `startup_errors` variable to `NgrokProcess` class.
- `pyngrok` console alias that mirrors `ngrok`.
- `pyngrok`'s version is now also reported alongside `ngrok`'s version when invoked via the console.

### Changed
- Refactored the boot loop for improved stability and accessibility.

### Fixed
- Properly identify more ARM processors, including `aarch64`.

### Removed
- Removed `NgrokProcess`'s `process` variable (previously deprecated in `1.4.0`, use `proc` now instead).

## [1.4.1](https://github.com/alexdlaird/pyngrok/compare/1.4.0...1.4.1) - 2019-09-09
### Fixed
- Issue where arguments passed from the command line to `ngrok` were being dropped (and thus `ngrok help` was always being displayed).

## [1.4.0](https://github.com/alexdlaird/pyngrok/compare/1.3.8...1.4.0) - 2019-06-25
### Added
- Configurable `timeout` parameter for `ngrok.connect()`, `ngrok.disconnect()`, and `ngrok.get_tunnels()` in [ngrok module](https://pyngrok.readthedocs.io/en/1.4.0/api.html#module-pyngrok.ngrok).
- A changelog, code of conduct, and contributing guide.
- A pull request template. 
- Documentation now builds and publishes to readthedocs.io.

### Changed
- Renamed `NgrokProcess`'s instance variable `process` to `proc` due to module shadowing (`process` is still set for backwards compatibility, but it should no longer be relied upon as it will be removed in a future release)

### Fixed
- Documentation issues.

## [1.3.8](https://github.com/alexdlaird/pyngrok/compare/1.3.7...1.3.8) - 2019-06-22
### Added
- Configurable `timeout` parameter for [requests to the API](https://pyngrok.readthedocs.io/en/1.3.8/pyngrok.html#pyngrok.ngrok.api_request).
- Configurable `timeout` parameter when `ngrok` is being [downloaded and installed](https://pyngrok.readthedocs.io/en/1.3.8/pyngrok.html#pyngrok.installer.install_ngrok).
- `PyngrokNgrokURLError`, which is thrown when a request timeout occurs.

### Changed
- Improvements to the bug reports issue template.

## [1.3.7](https://github.com/alexdlaird/pyngrok/compare/1.3.4...1.3.7) - 2019-06-01
### Added
- `config_path` variable to `NgrokProcess` class.
- Ability to pass `args` to `ngrok.run()`.
- A bug report issue template.
- A feature request issue template.

### Changed
- Renamed `CURRENT_PROCESSES` in `process` module to a private `_current_processes`.
- Reduced many log levels to `debug` to minimize noise and make `info `logs most relevant.

### Fixed
- Sometimes `ngrok` logs errors on startup but doesn't set the `lvl=error` flag, so `pyngrok` now also checks the `err` variable to see if it contains an error to surface.
- If the `ngrok` process started by `pyngrok` is killed externally, `pyngrok` now handles its own state properly. 
- Documentation issues.

## [1.3.4](https://github.com/alexdlaird/pyngrok/compare/1.3.0...1.3.4) - 2019-05-26
### Added
- Support for all platforms for which `ngrok` is compatible, including ARM processors.

### Changed
- Cleaned up code around ensuring the `ngrok` binary is present.
- Cleaned up code around process termination.
- Cleaned up tests.

### Fixed
- Documentation issues.

## [1.3.0](https://github.com/alexdlaird/pyngrok/compare/1.2.0...1.3.0) - 2019-01-20
### Added
- `config_path` parameter to `ngrok.disconnect()`.
- `ngrok.run()` method for more flexibility in starting `ngrok` programmatically.
- `__str__` and `__repr__` methods.
- Initial Sphinx configuration and dependencies for documentation.
- Code documentation.

## [1.2.0](https://github.com/alexdlaird/pyngrok/compare/1.1.1...1.2.0) - 2019-01-18
### Added
- Updates to README with more usage examples.
- `ngrok` command line usage via `entry_points` in packaging configuration.
- Updates to PyPI categorization.

### Changed
- Improvements to log messages.
- Improvements to exception messages.

## [1.1.1](https://github.com/alexdlaird/pyngrok/compare/1.0.0...1.1.1) - 2018-12-19
### Added
- Several more specific exceptions to the `exception` module.

### Changed
- Renamed the `ngrokexception` module to `exception`.
- Improvements to the README.

### Fixed
- Issues with the Travis CI build.
- Issues with `ngrok` binary download/installation.

## [1.0.0](https://github.com/alexdlaird/pyngrok/releases/tag/1.0.0) - 2018-12-18
- First stable release of `pyngrok`.
