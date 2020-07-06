# Changelog
All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased](https://github.com/alexdlaird/pyngrok/compare/4.1.4...HEAD)

## [4.1.4](https://github.com/alexdlaird/pyngrok/compare/4.1.3...4.1.4) - 2020-07-05
### Fixed
- Inconsistent support for a local directory (ex. `file:///`) being passed as `ngrok.connect()`'s `port`. This is valid, and `ngrok` will use its built-in fileserver for the tunnel.

## [4.1.3](https://github.com/alexdlaird/pyngrok/compare/4.1.2...4.1.3) - 2020-06-21
### Fixed
- Issue where `NgrokLog` did not properly split on just the first `=` character when parsing a log.

## [4.1.2](https://github.com/alexdlaird/pyngrok/compare/4.1.1...4.1.2) - 2020-06-19
### Fixed
- Python 2 compatibility issue with download progress bar.

## [4.1.1](https://github.com/alexdlaird/pyngrok/compare/4.1.0...4.1.1) - 2020-06-18
### Fixed
- Stability improvements.
- Documentation improvements.

## [4.1.0](https://github.com/alexdlaird/pyngrok/compare/4.0.3...4.1.0) - 2020-06-18
### Added
- Progress bar when `ngrok` is being downloaded and installed for the first time.
- Version number displayed in CLI's `--help`
- `installer.install_ngrok()` and `installer._download_file()` now accept `**kwargs`, which are passed down to [urllib.request.urlopen](https://docs.python.org/3/library/urllib.request.html#urllib.request.urlopen), and updated [the documentation](https://pyngrok.readthedocs.io/en/4.1.0/api.html#pyngrok.installer).

### Fixed
- Documentation improvements.

## [4.0.3](https://github.com/alexdlaird/pyngrok/compare/4.0.2...4.0.3) - 2020-06-17
### Fixed
- Build improvements.

## [4.0.2](https://github.com/alexdlaird/pyngrok/compare/4.0.1...4.0.2) - 2020-06-17
### Added
- PyPI package classifiers.

### Fixed
- Build improvements.

## [4.0.1](https://github.com/alexdlaird/pyngrok/compare/4.0.0...4.0.1) - 2020-06-07
### Changed
- Moved `_DEFAULT_NGROK_CONFIG_PATH` from `ngrok` module to `conf` module, renamed to `DEFAULT_NGROK_CONFIG_PATH`.

### Fixed
- Exception thrown when trying to validate the config when no file is given (i.e. the variable is None and thus the default should be used).

## [4.0.0](https://github.com/alexdlaird/pyngrok/compare/3.1.1...4.0.0) - 2020-06-06
### Added
- `PyngrokConfig`, which contains all of `pyngrok`'s configuration for interacting with the `ngrok` binary rather than passing these values around in an ever-growing list of kwargs. It is documented [here](https://pyngrok.readthedocs.io/en/4.0.0/api.html#pyngrok.conf.PyngrokConfig).
- `log_event_callback` is a new configuration parameter in `PyngrokConfig`, a callback that will be invoked each time a `ngrok` log is emitted.
- `monitor_thread` is a new configuration parameter in `PyngrokConfig` which determines whether `ngrok` should continue to be monitored (for logs, etc.) after it has finished starting. Defaults to `True.`
- `startup_timeout` is a new configuration parameter in `PyngrokConfig`. 
- `max_logs` is a new configuration parameter in `PyngrokConfig`.
- `start_monitor_thread()` and `stop_monitor_thread()` to [NgrokProcess](https://pyngrok.readthedocs.io/en/4.0.0/api.html#pyngrok.process.NgrokProcess).

### Changed
- `timeout` parameter that was passed down to `ngrok.api_request()` is now configurable by `request_timeout` in `PyngrokConfig`.
- Max number of logs stored by the `NgrokProcess` from 500 to 100.
- `NgrokProcess.log_boot_line()` renamed to `NgrokProcess._log_startup_line()`.
- `NgrokProcess.log_line()` renamed to `NgrokProcess._log_line()`.
- Auto-generated tunnel names (if `name` is not given when calling `ngrok.connect()`) are no prefixed with `proto` and `port`.
- `web_addr` cannot be set to `false` in, as the `pyngrok` modules depends on this API.

### Fixed
- `installer.install_default_config()` documentation now properly reflects that `data` is a `dict` and not a `str`.

### Removed
- `ngrok_path`, `config_path`, `auth_token`, and `region` were all removed from `process.get_process()`. Use [PyngrokConfig](https://pyngrok.readthedocs.io/en/4.0.0/api.html#pyngrok.conf.PyngrokConfig) instead.
- `ngrok_path`, `config_path`, `auth_token`, and `region` were all removed from `ngrok.get_ngrok_process()`. Use [PyngrokConfig](https://pyngrok.readthedocs.io/en/4.0.0/api.html#pyngrok.conf.PyngrokConfig) instead.
- `ngrok_path`, `config_path`, `auth_token`, `region`, and `timeout` were all removed from `ngrok.connect()`.  Use [PyngrokConfig](https://pyngrok.readthedocs.io/en/4.0.0/api.html#pyngrok.conf.PyngrokConfig) instead.
- `ngrok_path`, `config_path`, and `timeout` were all removed from `ngrok.disconnect()`.  Use [PyngrokConfig](https://pyngrok.readthedocs.io/en/4.0.0/api.html#pyngrok.conf.PyngrokConfig) instead.
- `ngrok_path`, and `timeout` were all removed from `ngrok.get_tunnels()`.  Use [PyngrokConfig](https://pyngrok.readthedocs.io/en/4.0.0/api.html#pyngrok.conf.PyngrokConfig) instead.

## [3.1.1](https://github.com/alexdlaird/pyngrok/compare/3.1.0...3.1.1) - 2020-06-06
### Changed
- Limit number of `NgrokLog`s stored in `NgrokProcess`'s `logs` variable to last 500.

## [3.1.0](https://github.com/alexdlaird/pyngrok/compare/3.0.0...3.1.0) - 2020-06-04
### Added
- After `ngrok` starts, the process moves in to its own thread and `NgrokLog`s continue to be parsed for programmatic access.

## [3.0.0](https://github.com/alexdlaird/pyngrok/compare/2.1.7...3.0.0) - 2020-05-29
### Added
- [NgrokLog](https://pyngrok.readthedocs.io/en/3.0.0/api.html#pyngrok.process.NgrokLog>) class is a parsed representation of `ngrok`'s logs for more accessible debugging.
- `logs` variable to `NgrokProcess` class, which is a `NgrokLog` object.

### Changed
- `ngrok_logs` in `PyngrokNgrokException` is now a list of `NgrokLog`s instead of `str`s.
- When starting the `ngrok` process, log levels now match `ngrok`s in its startup logs.

### Removed
- `startup_logs` from `NgrokProcess`, [use `logs` instead](https://pyngrok.readthedocs.io/en/3.0.0/api.html#pyngrok.process.NgrokProcess).

## [2.1.7](https://github.com/alexdlaird/pyngrok/compare/2.1.6...2.1.7) - 2020-05-06
### Fixed
- Documentation and SEO improvements.

## [2.1.6](https://github.com/alexdlaird/pyngrok/compare/2.1.5...2.1.6) - 2020-05-04
### Fixed
- Documentation and SEO improvements.

## [2.1.5](https://github.com/alexdlaird/pyngrok/compare/2.1.4...2.1.5) - 2020-05-01
### Added
- [Troubleshooting tips to the documentation](https://pyngrok.readthedocs.io/en/2.1.5/troubleshooting.html).
- An [integration example for end-to-end testing](https://pyngrok.readthedocs.io/en/2.1.5/integrations.html#end-to-end-testing).

### Changed
- PyPI package classifiers.

## [2.1.4](https://github.com/alexdlaird/pyngrok/compare/2.1.3...2.1.4) - 2020-04-23
### Added
- An [integration example for FastAPI](https://pyngrok.readthedocs.io/en/2.1.4/integrations.html#fastapi).

### Fixed
- FreeBSD is now listed as a supported platform and the correct binary is chosen.

## [2.1.3](https://github.com/alexdlaird/pyngrok/compare/2.1.2...2.1.3) - 2020-03-28
### Added
- [Integration examples to the documentation](https://pyngrok.readthedocs.io/en/2.1.3/integrations.html) for common uses cases.

### Fixed
- Build improvements.

## [2.1.2](https://github.com/alexdlaird/pyngrok/compare/2.1.1...2.1.2) - 2020-03-23
### Fixed
- Build improvements.

## [2.1.1](https://github.com/alexdlaird/pyngrok/compare/2.1.0...2.1.1) - 2020-03-21
### Fixed
- Version number displayed in CLI.

## [2.1.0](https://github.com/alexdlaird/pyngrok/compare/2.0.3...2.1.0) - 2020-03-21
### Added
- `region` parameter for `ngrok.connect()`, and `process.get_process()`. See [ngrok module](https://pyngrok.readthedocs.io/en/2.1.0/api.html#module-pyngrok.ngrok).
- `auth_token` parameter for `ngrok.connect()`, and `process.get_process()`. See [ngrok module](https://pyngrok.readthedocs.io/en/2.1.0/api.html#module-pyngrok.ngrok).
- Support for `Cygwin` as a platform by having it use the 64-bit Windows binary.

## [2.0.3](https://github.com/alexdlaird/pyngrok/compare/2.0.2...2.0.3) - 2020-02-14
### Security
- Only allow instances of `urlopen` to be executed with a `http` request.

## [2.0.2](https://github.com/alexdlaird/pyngrok/compare/2.0.1...2.0.2) - 2020-02-08
### Changed
- `DEFAULT_RETRY_COUNT` for use in `installer._download_file()`

## [2.0.1](https://github.com/alexdlaird/pyngrok/compare/2.0.0...2.0.1) - 2020-02-01
### Fixed
- Removed code that could cause a `ModuleNotFoundError` when another module referenced this module in it's `requirements.txt`.

## [2.0.0](https://github.com/alexdlaird/pyngrok/compare/1.4.4...2.0.0) - 2020-01-28
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
- `process` variable from `NgrokProcess` (previously deprecated in `1.4.0`, use `proc` now instead).

## [1.4.4](https://github.com/alexdlaird/pyngrok/compare/1.4.3...1.4.4) - 2020-01-28
### Fixed
- Build improvements.

## [1.4.3](https://github.com/alexdlaird/pyngrok/compare/1.4.2...1.4.3) - 2020-01-13
### Fixed
- Build improvements.
- Documentation improvements.

## [1.4.2](https://github.com/alexdlaird/pyngrok/compare/1.4.1...1.4.2) - 2019-09-09
### Changed
- Bumped PyYAML dependency version.

## [1.4.1](https://github.com/alexdlaird/pyngrok/compare/1.4.0...1.4.1) - 2019-09-09
### Fixed
- Issue where arguments passed from the command line to `ngrok` were being dropped (and thus `ngrok help` was always being displayed).

## [1.4.0](https://github.com/alexdlaird/pyngrok/compare/1.3.8...1.4.0) - 2019-06-25
### Added
- Configurable `timeout` parameter for `ngrok.connect()`, `ngrok.disconnect()`, and `ngrok.get_tunnels()` in [ngrok module](https://pyngrok.readthedocs.io/en/1.4.0/api.html#module-pyngrok.ngrok).
- A changelog, code of conduct, and contributing guide.
- A pull request template. 
- Documentation now builds and publishes to readthedocs.io.
- `proc` variable to `NgrokProcess`, which will replace `process` in the future due to module shadowing (`process` is still set for backwards compatibility, but it should no longer be relied upon as it will be removed in a future release).

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
