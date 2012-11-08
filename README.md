Usage
----

cmakelint requires Python.

    Syntax: cmakelint.py [--config=file] [--filter=-x,+y] <file> [file] ...
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
