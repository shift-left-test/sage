# SAGE

> Note: As a sub-project of the meta-shift project, sage is not intended to be run independently.

## About

Sage runs a set of static analysis tools to collect and visualizae the various software quality metrics, including:

* Lines of code
* Complexity
* Duplicates
* Static analysis issues

Currently, sage uses the following static analysis tools to evaluate the source code quality.

* cppcheck
* cpplint
* clang-tidy


## Development

To prepare your host environment, you can simply download a preconfigured dockerfile to start a docker container.

    $ git clone https://github.com/shift-left-test/dockerfiles.git
    $ cd dockerfiles
    $ docker build -f ubuntu-dev/Dockerfile -t ubuntu-dev .
    $ docker run --rm -it ubuntu-dev

To test the source code:

    $ tox

To install the package:

    $ pip3 install .


## Command-line arguments

```bash
usage: sage [-h] [--source-path SOURCE_PATH] [--build-path BUILD_PATH]
            [--tool-path TOOL_PATH] [--output-path OUTPUT_PATH]
            [--exclude-path EXCLUDE_PATH] [--target-triple TARGET_TRIPLE] [-v]
            [tools [tools ...]]

Static Analysis Group Execution

positional arguments:
  tools                 List of tools.
                        Tool-specific command-line options separated by colons can be added after the tool name.
                        ex) 'cppcheck:--library=googletest'

optional arguments:
  -h, --help            show this help message and exit
  --source-path SOURCE_PATH
                        source path
  --build-path BUILD_PATH
                        build path
  --tool-path TOOL_PATH
                        if this option is specified, only tools in this path is executed
  --output-path OUTPUT_PATH
                        output path
  --exclude-path EXCLUDE_PATH
                        exclude path
  --target-triple TARGET_TRIPLE
                        compile target triple
  -v, --verbose         increase output verbosity
```


## Licenses

The project source code is available under MIT license. See [LICENSE](LICENSE).
