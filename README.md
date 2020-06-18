# comedian

*Configuration-driven media preparation*

## Summary

`comedian` prepares destination-media for Linux installation via data
configuration. Using an extensive format, `comedian` can represent nearly any
configuration imaginable, and mutate the media to match.

## Usage

`comedian` is an executable Python application. You should be able to run it
directly (`comedian ...`), or with Python (`python comedian ...`).

```
comedian [-h] [--doc] [--version] [--config CONFIG]
         [--mode {exec,dryrun,shell}] [--debug | --quiet]
         {apply,up,down} specification
```

### Configuration

`comedian` can be configured with a JSON config file, which can be specified
with the `--config` command-line argument. By default a [standard config
file](data/default.config.json) is loaded if no other file is specified.

### Modes

`comedian` can run in one of three modes: `exec`, `dryrun`, or `shell`. The
desired mode can be selected with the `--mode` command-line argument.

`exec`: This mode runs commands on the same system that `comedian` is being
invoked on.

`dryrun`: This mode logs the commands that would be run in `exec` mode, but does
not run them.

`shell`: This mode outputs the commands that would be run to stdout in the
format of a shell script.

### Output

By default `comedian` will product some modest output while running. You can
control this with one of the `--debug` or `--quiet` command-line flags.
`--debug` will enable far more logging output, while `--quiet` will trim the
output down to error-reporting only.

### Actions

`comedian` can perform one of three actions: `apply`, `up`, or `down`. The
desired action can be selected with the `--action` command-line argument.

`apply`: This action will make destructive changes to the underlying media,
leaving the system in a "live" state.

`up`: This action will bring the system to a "live" state by decrypting,
assembling, activating, mounting, etc all elements in the specification.

`down`: This action will bring the system to a halted state by dismounting,
deactivating, etc ell elements in the specification.

### Specification

`comedian` loads a specification from a JSON file that you provide using last
positional command-line argument. This file describes the way to identify and
prepare your media. The complete specification format is documented
[here](SPECIFICATION_FORMAT.md). An [example specification
file](data/example.spec.json) has been provided.

## Packaging / Distribution

`comedian` uses `PyInstaller` to package distributable releases. You can use the
make target `dist` to create your own distribution:

```
make dist
```

This will create (among other things) the output file `./dist/comedian` which is
a self-contained executable that you can redeploy to any Linux machine.

## Tests

`comedian` has several different test suites, each with their own intent and
requirements. Some of these test suites must be run as `root` because they make
changes to the system they are running on. It is recommended that you run these
tests in VM - such as the one provided by this project's
[Vagrantfile](Vagrantfile).

You can use Vagrant for this purpose with the following commands:

```
vagrant up --provision
vagrant ssh
cd /vagrant
sudo su
```

You can invoke all tests with a single command:

```
make test
```

Or you can invoke specific test suites explicitly:

```
make unit_test
make integration_test
make dist_test
```

## License

`comedian` is licensed under either of the following, at your option:

* Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE) or
  http://www.apache.org/licenses/LICENSE-2.0)
* MIT license ([LICENSE-MIT](LICENSE-MIT) or http://opensource.org/licenses/MIT)

## Contributing

Contributions are welcome in the form of bug reports, feature requests, or pull
requests.

Contribution to `comedian` is organized under the terms of the [Contributor
Covenant](CONTRIBUTOR_COVENANT.md).
