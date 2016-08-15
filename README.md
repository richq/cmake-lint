cmakelint parses CMake files and reports style issues.

cmakelint requires Python.

## Installation

sudo pip install cmakelint

## Usage

    Syntax: cmakelint [--config=file] [--filter=-x,+y] <file> [file] ...
    filter=-x,+y,...
      Specify a comma separated list of filters to apply

    config=file
      Use the given file for configuration. By default the file
      $HOME/.cmakelintrc is used if it exists.  Use the value "None" to use no
      configuration file (./None for a file called literally None)
      Only the option "filter=" is currently supported in this file.

Run the `--filter=` option with no filter to see available options. Currently
these are:

    convention/filename
    linelength
    package/consistency
    readability/logic
    readability/mixedcase
    readability/wonkycase
    syntax
    whitespace/eol
    whitespace/extra
    whitespace/indent
    whitespace/mismatch
    whitespace/newline
    whitespace/tabs

An example .cmakelintrc file would be as follows:

    filter=-whitespace/indent

With this file in your home directory, running these commands would have the
same effect:

    cmakelint.py CMakeLists.txt
    cmakelint.py --filter=-whitespace/indent CMakeLists.txt

# Output status codes

The program should exit with the following status codes:

* 0 if everything went fine
* 1 if an error message was issued
* 32 on usage error

## Changes

### 1.4

- Add --quiet flag to supress "Total Errors: 0"
- Add --linelength=N flag to allow longer default lines (default remains 80)

### 1.3.4

- fix false positives in indented blocks

### 1.3.3

- fix crash on invalid `# lint_cmake: pragma` line
- fix deprecation warning with Python 3.4
- fix false positive warnings related to non-CMake quoted chunks (Issue #2)

### 1.3.2

- return error code 0, 1, 32 on error

### 1.3.1

- fix version number

### 1.3

- individual CMake files can control filters with `# lint_cmake: pragma` comment
- improved `SetFilters` function to allow spaces around the commas
- use `${XDG_CONFIG_HOME}` for the cmakelintrc file, with backwards compatible check for `~/.cmakelintrc`

### 1.2.01

- Published on pypi

### 1.2

- Moved to github
