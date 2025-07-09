# Changelog

All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased](https://github.com/alexdlaird/pyngrok/compare/7.2.12...HEAD)

## [7.2.12](https://github.com/alexdlaird/pyngrok/compare/7.2.11...7.2.12) - 2025-07-09

### Added

- Support for `s390x`, `ppc64`, and `ppc64le` architectures.

## [7.2.11](https://github.com/alexdlaird/pyngrok/compare/7.2.9...7.2.11) - 2025-06-05

### Added

- Build and stability improvements.
- Documentation improvements.

## [7.2.9](https://github.com/alexdlaird/pyngrok/compare/7.2.8...7.2.9) - 2025-05-28

### Added

- Support for [MSYS2's `mingw`](https://www.msys2.org/) when installing the agent. Like `cygwin`, it is mapped to its corresponding Windows binary.
- Windows ARM 64-bit support.
- FreeBSD ARM support.
- Build and stability improvements.
- Documentation improvements.

### Removed

- `cygwin` from dict of `PLATFORMS`, since the installer can just map to its corresponding Windows CDN value instead.

## [7.2.8](https://github.com/alexdlaird/pyngrok/compare/7.2.7...7.2.8) - 2025-05-09

### Added

- [`ngrok.api()`](https://pyngrok.readthedocs.io/en/7.2.8/api.html#pyngrok.ngrok.api), allowing `api` commands to be executed from the agent.
- [Agent interface](https://pyngrok.readthedocs.io/en/7.2.8/api.html#module-pyngrok.agent), which provides access to Captured Requests and agent status.
- Stability and logging improvements.
- Documentation improvements.

## [7.2.7](https://github.com/alexdlaird/pyngrok/compare/7.2.5...7.2.7) - 2025-05-05

### Added

- `stderr` is now sent to `stdout` in [capture_run_process()](https://pyngrok.readthedocs.io/en/7.2.7/api.html#pyngrok.process.capture_run_process).
- Stability improvements around concurrency.
- Documentation improvements.
- Test improvements.

## [7.2.5](https://github.com/alexdlaird/pyngrok/compare/7.2.4...7.2.5) - 2025-04-23

### Added

- Deprecation warning when using Labeled Tunnels, since `ngrok` Edges will be sunset December 31st, 2025. See [this issue](https://github.com/alexdlaird/pyngrok/issues/145) for more details.
- Documentation improvements.
- Build improvements.

## [7.2.4](https://github.com/alexdlaird/pyngrok/compare/7.2.3...7.2.4) - 2025-04-14

### Added

- Documentation improvements.

### Removed

- Behavior where `ngrok` default config file is always installed to `conf.DEFAULT_NGROK_CONFIG_PATH`, even when override `PyngrokConfig.config_path` is given. This contradicted documentation, and is inconsistent with parallel behavior in `java-ngrok`.

## [7.2.3](https://github.com/alexdlaird/pyngrok/compare/7.2.2...7.2.3) - 2025-01-08

### Added

- Support for `ngrok` config version 3.
- [ngrok.set_api_key()](https://pyngrok.readthedocs.io/en/7.2.3/api.html#pyngrok.ngrok.set_api_key) to allowing setting the API key in the `ngrok` config file.
- If no value for `PyngrokConfig.api_key`, it will attempt to use the environment variable `NGROK_API_KEY` if it is set.

## [7.2.2](https://github.com/alexdlaird/pyngrok/compare/7.2.1...7.2.2) - 2024-12-13

### Added

- Test improvements.

### Changed

- Permission for installed binary to limit execute to user.

## [7.2.1](https://github.com/alexdlaird/pyngrok/compare/7.2.0...7.2.1) - 2024-11-04

### Added

- Include SSL handshake failures in installer retry logic.
- Documentation improvements update links to `ngrok`'s documentation.

## [7.2.0](https://github.com/alexdlaird/pyngrok/compare/7.1.6...7.2.0) - 2024-07-18

### Added

- Build and stability improvements.
- Test cases for TLS tunnels, and other test improvements.

### Changed

- `conf.DEFAULT_NGROK_PATH` defaults to installing the binary alongside `ngrok`'s configs rather than alongside the
  code (putting the binary in the `venv` can cause odd behavior, or security concerns).

## [7.1.6](https://github.com/alexdlaird/pyngrok/compare/7.1.5...7.1.6) - 2024-03-24

### Added

- Build and stability improvements.

## [7.1.5](https://github.com/alexdlaird/pyngrok/compare/7.1.4...7.1.5) - 2024-03-08

### Added

- `obj` parsing in [`NgrokLog`](https://pyngrok.readthedocs.io/en/7.1.5/api.html#pyngrok.log.NgrokLog).
- `raises` to documentation.
- Build improvements.

## [7.1.4](https://github.com/alexdlaird/pyngrok/compare/7.1.3...7.1.4) - 2024-03-05

### Added

- Build and style improvements.

### Removed

- `conf.VERSION`, moved all version information to `pyngrok/__init__.py`. Get package version
  with `from pyngrok import __version__` instead.

## [7.1.3](https://github.com/alexdlaird/pyngrok/compare/7.1.2...7.1.3) - 2024-02-26

### Added

- Build improvements.

### Changed

- Renamed `make check-style` to `make check`.

## [7.1.2](https://github.com/alexdlaird/pyngrok/compare/7.1.1...7.1.2) - 2024-02-11

### Added

- Relative dependency pinning in `pyproject.toml`.
- Style and stability improvements (check `flake8` with `make check-style`).

### Removed

- `requirements.txt` files to streamline in to `pyproject.toml`.

## [7.1.1](https://github.com/alexdlaird/pyngrok/compare/7.1.0...7.1.1) - 2024-02-09

### Added

- Migrated to `pyproject.toml`.
- Fix for instability from an `ngrok` binary change.
- Test improvements.

## [7.1.0](https://github.com/alexdlaird/pyngrok/compare/7.0.5...7.1.0) - 2024-02-02

### Added

- Documentation improvements.
- Test improvements.

### Removed

- Support for 3.6 and 3.7. To use `pyngrok` with Python 3.7 or lower, pin `pyngrok<7.1`.

## [7.0.5](https://github.com/alexdlaird/pyngrok/compare/7.0.4...7.0.5) - 2023-12-30

### Fixed

- Test improvements, suite now respects `NGROK_AUTHTOKEN` for all necessary tests (skipped if not set, rather than tests
  failing).

## [7.0.4](https://github.com/alexdlaird/pyngrok/compare/7.0.3...7.0.4) - 2023-12-27

### Added

- If a value for `PyngrokConfig.auth_token` is not set, it will attempt to use the environment variable `NGROK_AUTHTOKEN` if it is
  set.
- Documentation improvements.
- Build improvements.

## [7.0.3](https://github.com/alexdlaird/pyngrok/compare/7.0.2...7.0.3) - 2023-12-04

### Added

- Build improvements, including `wheel` support.

## [7.0.2](https://github.com/alexdlaird/pyngrok/compare/7.0.1...7.0.2) - 2023-12-01

### Changed

- `pyngrok` to no longer install the config file in a legacy location, now
  respects [`ngrok`'s default locations](https://ngrok.com/docs/agent/config/#default-locations).

### Fixed

- Build improvements.

## [7.0.1](https://github.com/alexdlaird/pyngrok/compare/7.0.0...7.0.1) - 2023-11-14

### Added

- Documentation improvements.

## [7.0.0](https://github.com/alexdlaird/pyngrok/compare/6.1.2...7.0.0) - 2023-09-20

### Added

- Support for [Python type hints](https://docs.python.org/3/library/typing.html).
- Documentation improvements.

### Changed

- Moved [`NgrokLog`](https://pyngrok.readthedocs.io/en/7.0.0/api.html#pyngrok.log.NgrokLog) from `pyngrok.process`
  to `pyngrok.log`.

### Removed

- Support for Python 3.5. To use `pyngrok` with Python 3.5, pin `pyngrok<7`.

### Fixed

- Minor bugs.

## [6.1.2](https://github.com/alexdlaird/pyngrok/compare/6.1.0...6.1.2) - 2023-09-19

### Added

- Documentation improvements.

### Fixed

- Minor bugs.

## [6.1.0](https://github.com/alexdlaird/pyngrok/compare/6.0.0...6.1.0) - 2023-09-12

### Added

- Support for `labels`,
  so [`ngrok`'s Labeled Tunnel Configuration](https://ngrok.com/docs/agent/config/v2/#labeled-tunnel-configuration)
  is now supported, which enables basic support for [`ngrok`'s Edge](https://ngrok.com/docs/universal-gateway/edges/).
- `api_key` to `PyngrokConfig`, which can be set so `pyngrok` can interface with Edges when using `labels`.
- [ngrok.api_request()](https://pyngrok.readthedocs.io/en/6.1.0/api.html#pyngrok.ngrok.api_request) now takes an `auth`
  param, so it can now be used to pass the `Bearer` token to `ngrok`'s API.
- `id` to [NgrokTunnel](https://pyngrok.readthedocs.io/en/6.1.0/api.html#pyngrok.ngrok.NgrokTunnel).
- Documentation improvements.
- Test improvements.

## [6.0.0](https://github.com/alexdlaird/pyngrok/compare/5.2.3...6.0.0) - 2023-04-12

### Changed

- Default installer behavior to download `ngrok` v3 by default.
- Documentation updates.
- Test updates.

## [5.2.3](https://github.com/alexdlaird/pyngrok/compare/5.2.2...5.2.3) - 2023-04-12

### Added

- Support for `basic_auth` parameter in `ngrok` v3.
- Documentation improvements.
- Test improvements.

## [5.2.2](https://github.com/alexdlaird/pyngrok/compare/5.2.1...5.2.2) - 2023-04-11

### Fixed

- Documentation improvements.
- Test improvements.

## [5.2.1](https://github.com/alexdlaird/pyngrok/compare/5.2.0...5.2.1) - 2022-11-29

### Added

- Support for Python 3.10 and 3.11.

### Removed

- Usage of [`nose`](https://nose.readthedocs.io/en/latest/) in testing in favor
  of [`unittest`](https://docs.python.org/3/library/unittest.html).

## [5.2.0](https://github.com/alexdlaird/pyngrok/compare/5.1.0...5.2.0) - 2022-11-28

### Added

- Support for [`ngrok` v3](https://ngrok.com/docs/guides/other-guides/upgrade-v2-v3/) (v2 is still used by default).
- Documentation and examples for using `pyngrok` with `ngrok` v3.

### Fixed

- Stability improvements.
- Documentation improvements.
- Test improvements.

## [5.1.0](https://github.com/alexdlaird/pyngrok/compare/5.0.6...5.1.0) - 2021-08-24

### Removed

- `reconnect_session_retries` from `PyngrokConfig`, instead relying on `ngrok`'s own built-in retry mechanism on startup
  fails.

### Fixed

- Logging improvements.
- Documentation improvements.
- Test improvements.

## [5.0.6](https://github.com/alexdlaird/pyngrok/compare/5.0.5...5.0.6) - 2021-08-08

### Added

- Darwin 64-bit ARM support, as this was added to `ngrok` itself.

### Removed

- Darwin 386 support, as this was removed from `ngrok` itself.

### Fixed

- Build improvements.
- Documentation improvements.

## [5.0.5](https://github.com/alexdlaird/pyngrok/compare/5.0.4...5.0.5) - 2021-03-25

### Added

- `reconnect_session_retries` is a new configuration parameter in `PyngrokConfig`, which determines the max number of
  times to retry establishing a new session with `ngrok` if the connection fails on startup.

### Fixed

- Build improvements.
- Test improvements.

## [5.0.4](https://github.com/alexdlaird/pyngrok/compare/5.0.3...5.0.4) - 2021-03-08

### Fixed

- Build improvements.

## [5.0.3](https://github.com/alexdlaird/pyngrok/compare/5.0.2...5.0.3) - 2021-03-02

### Fixed

- Build improvements.
- Test improvements.

## [5.0.2](https://github.com/alexdlaird/pyngrok/compare/5.0.1...5.0.2) - 2021-02-12

### Changed

- Migrated build from Travis CI to GitHub Actions.

### Fixed

- Errors when `bind_tls` was set to `False`.
- Documentation improvements.

## [5.0.1](https://github.com/alexdlaird/pyngrok/compare/5.0.0...5.0.1) - 2020-12-28

### Added

- Documentation improvements.

### Fixed

- Build improvements.

## [5.0.0](https://github.com/alexdlaird/pyngrok/compare/4.2.2...5.0.0) - 2020-10-25

### Added

- Support
  for [`ngrok`'s tunnel definitions](https://ngrok.com/docs/agent/config/v2/#tunnel-configurations)
  when calling [ngrok.connect()](https://pyngrok.readthedocs.io/en/5.0.0/api.html#pyngrok.ngrok.connect). If a tunnel
  definition in `ngrok`'s config matches the given `name`, it will be used to start the tunnel.
- Support for
  a [`ngrok` tunnel definition](https://ngrok.com/docs/agent/config/v2/#tunnel-configurations)
  named "pyngrok-default" when
  calling [ngrok.connect()](https://pyngrok.readthedocs.io/en/5.0.0/api.html#pyngrok.ngrok.connect). When `name`
  is `None` and a "pyngrok-default" tunnel definition exists it `ngrok`'s config, it will be used.
- [process.is_process_running()](https://pyngrok.readthedocs.io/en/5.0.0/api.html#pyngrok.process.is_process_running) to
  check if `ngrok` is already running without also implicitly starting it.
- [ngrok.get_version()](https://pyngrok.readthedocs.io/en/5.0.0/api.html#pyngrok.ngrok.get_version) to get `ngrok`
  and `pyngrok` versions in a tuple.
- [conf.get_default()](https://pyngrok.readthedocs.io/en/5.0.0/api.html#pyngrok.conf.get_default), replacing the need
  for direct references to `conf.DEFAULT_PYNGROK_CONFIG`.
- [conf.set_default()](https://pyngrok.readthedocs.io/en/5.0.0/api.html#pyngrok.conf.set_default), replacing the need
  for direct references to `conf.DEFAULT_PYNGROK_CONFIG`.
- `refresh_metrics()`
  to [NgrokTunnel](https://pyngrok.readthedocs.io/en/4.1.16/api.html#pyngrok.ngrok.NgrokTunnel.refresh_metrics).
- `data` to [NgrokTunnel](https://pyngrok.readthedocs.io/en/5.0.0/api.html#pyngrok.ngrok.NgrokTunnel), which holds the
  original tunnel data.
- [ngrok.update()](https://pyngrok.readthedocs.io/en/5.0.0/api.html#pyngrok.ngrok.update) to update `ngrok`, if an
  update is available.
- Stability improvements.
- Documentation improvements.
- Logging improvements.

### Changed

- [ngrok.connect()](https://pyngrok.readthedocs.io/en/5.0.0/api.html#pyngrok.ngrok.connect) now returns
  a [NgrokTunnel](https://pyngrok.readthedocs.io/en/5.0.0/api.html#pyngrok.ngrok.NgrokTunnel) instead of a `str` of the
  public URL. The returned `NgrokTunnel` has a reference to the previously returned `public_url` in it.
- [ngrok.connect()](https://pyngrok.readthedocs.io/en/5.0.0/api.html#pyngrok.ngrok.connect) changed its signature,
  renamed kwarg `port` (the first arg) to `addr` to match `ngrok`'s documentation.
- [ngrok.connect()](https://pyngrok.readthedocs.io/en/5.0.0/api.html#pyngrok.ngrok.connect) changed its signature,
  the `options` kwarg should now be unpacked, pass each option directly to the method as a kwarg.
- [NgrokTunnel.`__init`__()'s](https://pyngrok.readthedocs.io/en/5.0.0/_modules/pyngrok/ngrok.html#NgrokTunnel)
  params (`data`, `pyngrok_config`, and `api_url`) are now required.
- `ngrok.disconnect()` no longer installs and starts `ngrok`, it simply returns if the `ngrok` process has not been
  started.
- Renamed `conf.DEFAULT_PYNGROK_CONFIG` to `conf._default_pyngrok_config` (
  use [conf.set_default()](https://pyngrok.readthedocs.io/en/5.0.0/api.html#pyngrok.conf.set_default) instead).
- Renamed `ngrok.ensure_ngrok_installed()` to `ngrok.install_ngrok()`.
- `ngrok.install_ngrok()` (formerly `ngrok.ensure_ngrok_installed()`) changed its signature, now takes
  a `pyngrok_config` (optional) instead of `ngrok_path` as its only arg.
- Renamed `process._ensure_path_ready()` to `process._validate_path()`.

### Removed

- Support for Python 2.7. Legacy documentation for 4.1, the latest version with Python 2.7 support, can be
  found [here](https://pyngrok.readthedocs.io/en/4.1.x/).
- `return_ngrok_tunnel` from `ngrok.connect()`. The `kwarg` can still be passed, but it will do nothing, it now always
  uses the `True` behavior.

## [4.2.2](https://github.com/alexdlaird/pyngrok/compare/4.1.16...4.2.2) - 2020-10-12

The next release, 5.0.0, contains breaking changes, including dropping support for Python 2.7. 4.2.x is meant to ease
migration between 4.1.x and 5.0.0 and should not be pinned, as it will not be supported after 5.0.0 is released. To
prepare for these breaking changes, see the changelog below. To avoid these breaking changes altogether, or if
Python 2.7 support is still needed, pin `pyngrok~=4.1.0`.

### Added

- [ngrok.connect()](https://pyngrok.readthedocs.io/en/4.2.2/api.html#pyngrok.ngrok.connect) replaced `options`
  with `kwargs`, maintained backwards compatibility. Support for passing `options` as a dict will be removed in 5.0.0,
  unpack the dict as `kwargs`.
- [ngrok.connect()](https://pyngrok.readthedocs.io/en/4.2.2/api.html#pyngrok.ngrok.connect) added `return_ngrok_tunnel`
  to its args, which defaults to `False` for backwards compatibility. This will default to `True` in 5.0.0, and the flag
  will be removed.
- [conf.get_default()](https://pyngrok.readthedocs.io/en/4.2.2/api.html#pyngrok.conf.get_default), replacing the need to
  directly reference `conf.DEFAULT_PYNGROK_CONFIG`, which will be removed in 5.0.0.

## [4.1.16](https://github.com/alexdlaird/pyngrok/compare/4.1.13...4.1.16) - 2020-10-12

### Added

- [ngrok.get_version()](https://pyngrok.readthedocs.io/en/4.1.16/api.html#pyngrok.ngrok.get_version) to get `ngrok`
  and `pyngrok` versions in a tuple.
- `refresh_metrics()`
  to [NgrokTunnel](https://pyngrok.readthedocs.io/en/4.1.16/api.html#pyngrok.ngrok.NgrokTunnel.refresh_metrics).
- Documentation improvements.
- Logging improvements.

## [4.1.13](https://github.com/alexdlaird/pyngrok/compare/4.1.12...4.1.13) - 2020-10-02

### Added

-

An [integration example for Google Colab](https://pyngrok.readthedocs.io/en/4.1.13/integrations.html#google-colaboratory).

- Documentation improvements.
- Test `ngrok.api_request()` using `params` for filtering with special characters.

### Fixed

- [ngrok.api_request()](https://pyngrok.readthedocs.io/en/4.1.13/api.html#pyngrok.ngrok.api_request)'s `params` is now
  properly documented as a `dict` instead of a `list`.
- Trimmed trailing line return from `ngrok` logs.

## [4.1.12](https://github.com/alexdlaird/pyngrok/compare/4.1.11...4.1.12) - 2020-09-10

### Added

- Validation for `log_format` in `ngrok`'s `config.yaml`, as `pyngrok` depends on key/value logs.
- Validation for `log_level` in `ngrok`'s `config.yaml`, as `pyngrok` depends on the level being either `info`
  or `debug`.

## [4.1.11](https://github.com/alexdlaird/pyngrok/compare/4.1.10...4.1.11) - 2020-09-08

### Fixed

- Build improvements.
- Documentation improvements.

## [4.1.10](https://github.com/alexdlaird/pyngrok/compare/4.1.9...4.1.10) - 2020-08-14

### Fixed

- When `bind_tls` is `True`, the `public_url` return from `ngrok.connect()` is now `https`.

## [4.1.9](https://github.com/alexdlaird/pyngrok/compare/4.1.8...4.1.9) - 2020-08-12

### Fixed

- The thread that monitors `ngrok` logs now maintains its own `alive` state instead of
  modifying `PyngrokConfig.monitor_thread`.
- The thread that monitors `ngrok`
  logs [is now daemonic](https://docs.python.org/3/library/threading.html#threading.Thread.daemon), so it no longer
  blocks the Python process from terminating.
- Documentation improvements.

## [4.1.8](https://github.com/alexdlaird/pyngrok/compare/4.1.7...4.1.8) - 2020-07-26

### Added

- `DEFAULT_PYNGROK_CONFIG` variable to `conf` module, used when `pyngrok_config` is not passed to `ngrok` methods.

### Fixed

- Zombie processes remaining in certain cases when `ngrok` exited early or was terminated externally.

## [4.1.7](https://github.com/alexdlaird/pyngrok/compare/4.1.6...4.1.7) - 2020-07-23

### Fixed

- `TypeError` exception when a `NgrokLog` parses a string that contains a missing or malformed `lvl`. Default is
  now `NOTSET` in such cases.

## [4.1.6](https://github.com/alexdlaird/pyngrok/compare/4.1.5...4.1.6) - 2020-07-09

### Added

- `start_new_process` is a new configuration parameter in `PyngrokConfig`, which will be passed
  to [subprocess.Popen](https://docs.python.org/3/library/subprocess.html#subprocess.Popen) when `ngrok` is started.
  Requires Python 3 and POSIX.

### Fixed

- Documentation improvements in integration examples.

## [4.1.5](https://github.com/alexdlaird/pyngrok/compare/4.1.4...4.1.5) - 2020-07-06

### Fixed

- Appears `ngrok` itself has a bug around not properly escaping characters in tunnel names, so avoiding this bug for
  fileserver tunnels by substituting their name.

## [4.1.4](https://github.com/alexdlaird/pyngrok/compare/4.1.3...4.1.4) - 2020-07-05

### Fixed

- Inconsistent support for a local directory (ex. `file:///`) being passed as `ngrok.connect()`'s `port`. This is valid,
  and `ngrok` will use its built-in fileserver for the tunnel.

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
- Version number displayed in CLI's `--help`.
- `installer.install_ngrok()` and `installer._download_file()` now accept `**kwargs`, which are passed down
  to [urllib.request.urlopen](https://docs.python.org/3/library/urllib.request.html#urllib.request.urlopen), and
  updated [the documentation](https://pyngrok.readthedocs.io/en/4.1.0/api.html#pyngrok.installer).

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

- Exception thrown when trying to validate the config when no file is given (i.e. the variable is None and thus the
  default should be used).

## [4.0.0](https://github.com/alexdlaird/pyngrok/compare/3.1.1...4.0.0) - 2020-06-06

### Added

- `PyngrokConfig`, which contains all of `pyngrok`'s configuration for interacting with the `ngrok` binary rather than
  passing these values around in an ever-growing list of `kwargs`. It is
  documented [here](https://pyngrok.readthedocs.io/en/4.0.0/api.html#pyngrok.conf.PyngrokConfig).
- `log_event_callback` is a new configuration parameter in `PyngrokConfig`, a callback that will be invoked each time
  a `ngrok` log is emitted.
- `monitor_thread` is a new configuration parameter in `PyngrokConfig` which determines whether `ngrok` should continue
  to be monitored (for logs, etc.) after it has finished starting. Defaults to `True`.
- `startup_timeout` is a new configuration parameter in `PyngrokConfig`.
- `max_logs` is a new configuration parameter in `PyngrokConfig`.
- `start_monitor_thread()` and `stop_monitor_thread()`
  to [NgrokProcess](https://pyngrok.readthedocs.io/en/4.0.0/api.html#pyngrok.process.NgrokProcess).

### Changed

- `timeout` parameter that was passed down to `ngrok.api_request()` is now configurable by `request_timeout`
  in `PyngrokConfig`.
- Max number of logs stored by the `NgrokProcess` from 500 to 100.
- `NgrokProcess.log_boot_line()` renamed to `NgrokProcess._log_startup_line()`.
- `NgrokProcess.log_line()` renamed to `NgrokProcess._log_line()`.
- Auto-generated tunnel names (if `name` is not given when calling `ngrok.connect()`) are no prefixed with `proto`
  and `port`.
- `web_addr` cannot be set to `false` in, as the `pyngrok` modules depends on this API.

### Fixed

- `installer.install_default_config()` documentation now properly reflects that `data` is a `dict` and not a `str`.

### Removed

- `ngrok_path`, `config_path`, `auth_token`, and `region` were all removed from `process.get_process()`.
  Use [PyngrokConfig](https://pyngrok.readthedocs.io/en/4.0.0/api.html#pyngrok.conf.PyngrokConfig) instead.
- `ngrok_path`, `config_path`, `auth_token`, and `region` were all removed from `ngrok.get_ngrok_process()`.
  Use [PyngrokConfig](https://pyngrok.readthedocs.io/en/4.0.0/api.html#pyngrok.conf.PyngrokConfig) instead.
- `ngrok_path`, `config_path`, `auth_token`, `region`, and `timeout` were all removed from `ngrok.connect()`.
  Use [PyngrokConfig](https://pyngrok.readthedocs.io/en/4.0.0/api.html#pyngrok.conf.PyngrokConfig) instead.
- `ngrok_path`, `config_path`, and `timeout` were all removed from `ngrok.disconnect()`.
  Use [PyngrokConfig](https://pyngrok.readthedocs.io/en/4.0.0/api.html#pyngrok.conf.PyngrokConfig) instead.
- `ngrok_path`, and `timeout` were all removed from `ngrok.get_tunnels()`.
  Use [PyngrokConfig](https://pyngrok.readthedocs.io/en/4.0.0/api.html#pyngrok.conf.PyngrokConfig) instead.

## [3.1.1](https://github.com/alexdlaird/pyngrok/compare/3.1.0...3.1.1) - 2020-06-06

### Changed

- Limit number of `NgrokLog`s stored in `NgrokProcess`'s `logs` variable to last 500.

## [3.1.0](https://github.com/alexdlaird/pyngrok/compare/3.0.0...3.1.0) - 2020-06-04

### Added

- After `ngrok` starts, the process moves into its own thread and `NgrokLog`s continue to be parsed for programmatic
  access.

## [3.0.0](https://github.com/alexdlaird/pyngrok/compare/2.1.7...3.0.0) - 2020-05-29

### Added

- [NgrokLog](https://pyngrok.readthedocs.io/en/3.0.0/api.html#pyngrok.process.NgrokLog>) class is a parsed
  representation of `ngrok`'s logs for more accessible debugging.
- `logs` variable to `NgrokProcess` class, which is a `NgrokLog` object.

### Changed

- `ngrok_logs` in `PyngrokNgrokException` is now a list of `NgrokLog`s instead of `str`s.
- When starting the `ngrok` process, log levels now match `ngrok`s in its startup logs.

### Removed

- `startup_logs`
  from `NgrokProcess`, [use `logs` instead](https://pyngrok.readthedocs.io/en/3.0.0/api.html#pyngrok.process.NgrokProcess).

## [2.1.7](https://github.com/alexdlaird/pyngrok/compare/2.1.6...2.1.7) - 2020-05-06

### Fixed

- Documentation and SEO improvements.

## [2.1.6](https://github.com/alexdlaird/pyngrok/compare/2.1.5...2.1.6) - 2020-05-04

### Fixed

- Documentation and SEO improvements.

## [2.1.5](https://github.com/alexdlaird/pyngrok/compare/2.1.4...2.1.5) - 2020-05-01

### Added

- [Troubleshooting tips to the documentation](https://pyngrok.readthedocs.io/en/2.1.5/troubleshooting.html).
-

An [integration example for end-to-end testing](https://pyngrok.readthedocs.io/en/2.1.5/integrations.html#end-to-end-testing).

### Changed

- PyPI package classifiers.

## [2.1.4](https://github.com/alexdlaird/pyngrok/compare/2.1.3...2.1.4) - 2020-04-23

### Added

- An [integration example for FastAPI](https://pyngrok.readthedocs.io/en/2.1.4/integrations.html#fastapi).

### Fixed

- FreeBSD is now listed as a supported platform and the correct binary is chosen.

## [2.1.3](https://github.com/alexdlaird/pyngrok/compare/2.1.2...2.1.3) - 2020-03-28

### Added

- [Integration examples to the documentation](https://pyngrok.readthedocs.io/en/2.1.3/integrations.html) for common uses
  cases.

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

- `region` parameter for `ngrok.connect()`, and `process.get_process()`.
  See [ngrok module](https://pyngrok.readthedocs.io/en/2.1.0/api.html#module-pyngrok.ngrok).
- `auth_token` parameter for `ngrok.connect()`, and `process.get_process()`.
  See [ngrok module](https://pyngrok.readthedocs.io/en/2.1.0/api.html#module-pyngrok.ngrok).
- Support for [`cygwin`](https://www.cygwin.com/) as a platform by having it use the 64-bit Windows binary.

## [2.0.3](https://github.com/alexdlaird/pyngrok/compare/2.0.2...2.0.3) - 2020-02-14

### Security

- Only allow instances of `urlopen` to be executed with a `http` request.

## [2.0.2](https://github.com/alexdlaird/pyngrok/compare/2.0.1...2.0.2) - 2020-02-08

### Changed

- `DEFAULT_RETRY_COUNT` for use in `installer._download_file()`.

## [2.0.1](https://github.com/alexdlaird/pyngrok/compare/2.0.0...2.0.1) - 2020-02-01

### Fixed

- Removed code that could cause a `ModuleNotFoundError` when another module referenced this module in
  it's `requirements.txt`.

## [2.0.0](https://github.com/alexdlaird/pyngrok/compare/1.4.4...2.0.0) - 2020-01-28

### Added

- `api_url` variable to `NgrokProcess` class.
- `startup_logs` variable to `NgrokProcess` class.
- `startup_error` variable to `NgrokProcess` class.
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

- Issue where arguments passed from the command line to `ngrok` were being dropped (and thus `ngrok help` was always
  being displayed).

## [1.4.0](https://github.com/alexdlaird/pyngrok/compare/1.3.8...1.4.0) - 2019-06-25

### Added

- Configurable `timeout` parameter for `ngrok.connect()`, `ngrok.disconnect()`, and `ngrok.get_tunnels()`
  in [ngrok module](https://pyngrok.readthedocs.io/en/1.4.0/api.html#module-pyngrok.ngrok).
- A changelog, code of conduct, and contributing guide.
- A pull request template.
- Documentation now builds and publishes to [pyngrok.readthedocs.io](https://pyngrok.readthedocs.io).
- `proc` variable to `NgrokProcess`, which will replace `process` in the future due to module shadowing (`process` is
  still set for backwards compatibility, but it should no longer be relied upon as it will be removed in a future
  release).

### Fixed

- Documentation issues.

## [1.3.8](https://github.com/alexdlaird/pyngrok/compare/1.3.7...1.3.8) - 2019-06-22

### Added

- Configurable `timeout` parameter
  for [requests to the API](https://pyngrok.readthedocs.io/en/1.3.8/pyngrok.html#pyngrok.ngrok.api_request).
- Configurable `timeout` parameter when `ngrok` is
  being [downloaded and installed](https://pyngrok.readthedocs.io/en/1.3.8/pyngrok.html#pyngrok.installer.install_ngrok).
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

- Sometimes `ngrok` logs errors on startup but doesn't set the `lvl=error` flag, so `pyngrok` now also checks the `err`
  variable to see if it contains an error to surface.
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
