#!/usr/bin/env python
"""
Copyright 2009 Richard Quirk

Licensed under the Apache License, Version 2.0 (the "License"); you may not
use this file except in compliance with the License. You may obtain a copy of
the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations under
the License.
"""
import unittest
import cmakelint
import os

class ErrorCollector(object):
    def __init__(self):
        self._errors = []

    def __call__(self, unused_filename, unused_line, category, message):
        self._errors.append(message)

    def Results(self):
        if len(self._errors) < 2:
            return ''.join(self._errors)
        return self._errors

class CMakeLintTestBase(unittest.TestCase):
    def TestLint(self, code, expected_message):
        errors = ErrorCollector()
        clean_lines = cmakelint.CleansedLines([code])
        cmakelint.ProcessLine('foo.cmake', 0, clean_lines, errors)
        self.assertEquals(expected_message, errors.Results())

    def TestMultiLineLint(self, code, expected_message):
        errors = ErrorCollector()
        clean_lines = cmakelint.CleansedLines(code.split('\n'))
        for i in clean_lines.LineNumbers():
            cmakelint.ProcessLine('foo.cmake', i, clean_lines, errors)
        self.assertEquals(expected_message, errors.Results())

    def TestCheckRepeatLogic(self, code, expected_message):
        errors = ErrorCollector()
        clean_lines = cmakelint.CleansedLines(code.split('\n'))
        for i in clean_lines.LineNumbers():
            cmakelint.CheckRepeatLogic('foo.cmake', i, clean_lines, errors)
        self.assertEquals(expected_message, errors.Results())

    def TestCheckFileName(self, filename, expected_message):
        errors = ErrorCollector()
        cmakelint.CheckFileName(filename, errors)
        self.assertEquals(expected_message, errors.Results())

    def TestCheckFindPackage(self, filename, code, expected_message):
        errors = ErrorCollector()
        clean_lines = cmakelint.CleansedLines(code.split('\n'))
        for i in clean_lines.LineNumbers():
            cmakelint.CheckFindPackage(filename, i, clean_lines, errors)
        cmakelint._package_state.Done(filename, errors)
        self.assertEquals(expected_message, errors.Results())

    def TestGetArgument(self, expected_arg, code):
        clean_lines = cmakelint.CleansedLines(code.split('\n'))
        self.assertEquals(expected_arg, cmakelint.GetCommandArgument(0, clean_lines))

class CMakeLintTest(CMakeLintTestBase):
    def testLineLength(self):
        self.TestLint(
                '# '+('o'*80),
                'Lines should be <= 80 characters long')

    def testUpperAndLowerCase(self):
        self.TestMultiLineLint(
                '''project()
                CMAKE_MINIMUM_REQUIRED()''',
                'Do not mix upper and lower case commands')

    def testContainsCommand(self):
        self.assertTrue(cmakelint.ContainsCommand('project()'))
        self.assertTrue(cmakelint.ContainsCommand('project('))
        self.assertTrue(cmakelint.ContainsCommand('project  ( '))
        self.assertFalse(cmakelint.ContainsCommand('VERSION'))

    def testGetCommand(self):
        self.assertEquals('project', cmakelint.GetCommand('project()'))
        self.assertEquals('project', cmakelint.GetCommand('project('))
        self.assertEquals('project', cmakelint.GetCommand('project  ( '))
        self.assertEquals('', cmakelint.GetCommand('VERSION'))

    def testIsCommandUpperCase(self):
        self.assertTrue(cmakelint.IsCommandUpperCase('PROJECT'))
        self.assertTrue(cmakelint.IsCommandUpperCase('CMAKE_MINIMUM_REQUIRED'))
        self.assertFalse(cmakelint.IsCommandUpperCase('cmake_minimum_required'))
        self.assertFalse(cmakelint.IsCommandUpperCase('project'))
        self.assertFalse(cmakelint.IsCommandUpperCase('PrOjEct'))

    def testIsCommandMixedCase(self):
        self.assertTrue(cmakelint.IsCommandMixedCase('PrOjEct'))
        self.assertFalse(cmakelint.IsCommandMixedCase('project'))
        self.assertFalse(cmakelint.IsCommandMixedCase('CMAKE_MINIMUM_REQUIRED'))
        self.assertTrue(cmakelint.IsCommandMixedCase('CMAKE_MINIMUM_required'))

    def testCleanComment(self):
        self.assertEquals('', cmakelint.CleanComments('# Comment to zap'))
        self.assertEquals(
                'project()',
                cmakelint.CleanComments('project() # Comment to zap'))

    def testCommandSpaces(self):
        self.TestMultiLineLint(
                """project ()""",
                "Extra spaces between 'project' and its ()")

    def testTabs(self):
        self.TestLint('\tfoo()', 'Tab found; please use spaces')

    def testTrailingSpaces(self):
        self.TestLint('# test ', 'Line ends in whitespace')
        self.TestMultiLineLint('  foo() \n  foo()\n', 'Line ends in whitespace')
        self.TestLint('    set(var value)', '')

    def testCommandSpaceBalance(self):
        self.TestMultiLineLint(
                """project( Foo)""",
                'Mismatching spaces inside () after command')
        self.TestMultiLineLint(
                """project(Foo )""",
                'Mismatching spaces inside () after command')

    def testCommandNotEnded(self):
        self.TestMultiLineLint(
                """project(
                Foo
                #
                #""",
                'Unable to find the end of this command')

    def testRepeatLogicExpression(self):
        self.TestCheckRepeatLogic('else(foo)',
                'Expression repeated inside else; '
                'better to use only else()')
        self.TestCheckRepeatLogic('ELSEIF(NOT ${VAR})', '')
        self.TestCheckRepeatLogic('ENDMACRO( my_macro foo bar baz)',
                'Expression repeated inside endmacro; '
                'better to use only ENDMACRO()')

    def testFindTool(self):
        self.TestCheckFileName('path/to/FindFooBar.cmake',
                'Find modules should use uppercase names; '
                'consider using FindFOOBAR.cmake')
        self.TestCheckFileName('CMakeLists.txt', '')
        self.TestCheckFileName('cmakeLists.txt',
                    'File should be called CMakeLists.txt')

    def testIsFindPackage(self):
        self.assertTrue(cmakelint.IsFindPackage('path/to/FindFOO.cmake'))
        self.assertFalse(cmakelint.IsFindPackage('path/to/FeatureFOO.cmake'))

    def testCheckFindPackage(self):
        self.TestCheckFindPackage(
                'FindFoo.cmake',
                '',
                ['Package should include FindPackageHandleStandardArgs',
                'Package should use FIND_PACKAGE_HANDLE_STANDARD_ARGS'])
        self.TestCheckFindPackage(
                'FindFoo.cmake',
                '''INCLUDE(FindPackageHandleStandardArgs)''',
                'Package should use FIND_PACKAGE_HANDLE_STANDARD_ARGS')
        self.TestCheckFindPackage(
                'FindFoo.cmake',
                '''FIND_PACKAGE_HANDLE_STANDARD_ARGS(FOO DEFAULT_MSG)''',
                'Package should include FindPackageHandleStandardArgs')
        self.TestCheckFindPackage(
                'FindFoo.cmake',
                '''INCLUDE(FindPackageHandleStandardArgs)
                FIND_PACKAGE_HANDLE_STANDARD_ARGS(KK DEFAULT_MSG)''',
                'Weird variable passed to std args, should be FOO not KK')
        self.TestCheckFindPackage(
                'FindFoo.cmake',
                '''INCLUDE(FindPackageHandleStandardArgs)
                FIND_PACKAGE_HANDLE_STANDARD_ARGS(FOO DEFAULT_MSG)''',
                '')

    def testGetCommandArgument(self):
        self.TestGetArgument('KK',
                '''SET(
                KK)''')
        self.TestGetArgument('KK', 'Set(  KK)')
        self.TestGetArgument('KK', 'FIND_PACKAGE_HANDLE_STANDARD_ARGS(KK BLEUGH)')

    def testIsValidFile(self):
        self.assertTrue(cmakelint.IsValidFile('CMakeLists.txt'))
        self.assertTrue(cmakelint.IsValidFile('cmakelists.txt'))
        self.assertTrue(cmakelint.IsValidFile('/foo/bar/baz/CMakeLists.txt'))
        self.assertTrue(cmakelint.IsValidFile('Findkk.cmake'))
        self.assertFalse(cmakelint.IsValidFile('foobar.h.in'))

    def testIndent(self):
        try:
            cmakelint._lint_state.spaces = 2
            self.TestLint('no_indent(test)', '')
            self.TestLint('  two_indent(test)', '')
            self.TestLint('    four_indent(test)', '')
            self.TestLint(' one_indent(test)',
                    'Weird indentation; use 2 spaces')
            self.TestLint('   three_indent(test)',
                    'Weird indentation; use 2 spaces')

            cmakelint._lint_state.spaces = 3
            self.TestLint('no_indent(test)', '')
            self.TestLint('  two_indent(test)',
                    'Weird indentation; use 3 spaces')
            self.TestLint('    four_indent(test)',
                    'Weird indentation; use 3 spaces')
            self.TestLint(' one_indent(test)',
                    'Weird indentation; use 3 spaces')
            self.TestLint('   three_indent(test)', '')
        finally:
            cmakelint._lint_state.spaces = 2

    def testParseArgs(self):
        old_usage = cmakelint._USAGE
        old_version = cmakelint._VERSION
        old_cats = cmakelint._ERROR_CATEGORIES
        old_spaces = cmakelint._lint_state.spaces
        try:
            cmakelint._USAGE = ""
            cmakelint._ERROR_CATEGORIES = ""
            cmakelint._VERSION = ""
            self.assertRaises(SystemExit, cmakelint.ParseArgs, [])
            self.assertRaises(SystemExit, cmakelint.ParseArgs, ['--help'])
            self.assertRaises(SystemExit, cmakelint.ParseArgs, ['--bogus-option'])
            self.assertRaises(SystemExit, cmakelint.ParseArgs, ['--filter='])
            self.assertRaises(SystemExit, cmakelint.ParseArgs, ['--filter=foo'])
            self.assertRaises(SystemExit, cmakelint.ParseArgs, ['--filter=+x,b,-c', 'foo.cmake'])
            self.assertRaises(SystemExit, cmakelint.ParseArgs, ['--spaces=c', 'foo.cmake'])
            self.assertRaises(SystemExit, cmakelint.ParseArgs, ['--version'])
            cmakelint._lint_state.filters = []
            self.assertEquals(['foo.cmake'], cmakelint.ParseArgs(['--filter=-whitespace', 'foo.cmake']))
            cmakelint._lint_state.filters = []
            self.assertEquals(['foo.cmake'], cmakelint.ParseArgs(['foo.cmake']))
            filt = '-,+whitespace'
            cmakelint._lint_state.filters = []
            self.assertEquals(['foo.cmake'], cmakelint.ParseArgs(['--config=None', '--spaces=3', '--filter='+filt, 'foo.cmake']))
            self.assertEquals(['-', '+whitespace'], cmakelint._lint_state.filters)
            self.assertEquals(3, cmakelint._lint_state.spaces)
            cmakelint._lint_state.filters = []

            cmakelint.ParseArgs(['--config=./foo/bar', 'foo.cmake'])
            self.assertEquals('./foo/bar', cmakelint._lint_state.config)
            cmakelint.ParseArgs(['--config=None', 'foo.cmake'])
            self.assertEquals(None, cmakelint._lint_state.config)
            cmakelint.ParseArgs(['foo.cmake'])
            self.assertEquals(os.environ['HOME']+os.path.sep+'.cmakelintrc', cmakelint._lint_state.config)

        finally:
            cmakelint._USAGE = old_usage
            cmakelint._ERROR_CATEGORIES = old_cats
            cmakelint._VERSION = old_version
            cmakelint._lint_state.filters = []
            cmakelint._lint_state.spaces = old_spaces

    def testParseOptionsFile(self):
        old_usage = cmakelint._USAGE
        old_cats = cmakelint._ERROR_CATEGORIES
        old_spaces = cmakelint._lint_state.spaces
        try:
            cmakelint._USAGE = ""
            cmakelint._ERROR_CATEGORIES = ""
            cmakelint.ParseOptionFile("""
                    # skip comment
                    filter=-,+whitespace
                    spaces= 3
                    """.split('\n'), ignore_space=False)
            self.assertEquals(['-', '+whitespace'], cmakelint._lint_state.filters)
            cmakelint.ParseArgs(['--filter=+syntax','foo.cmake'])
            self.assertEquals(['-', '+whitespace', '+syntax'], cmakelint._lint_state.filters)
            self.assertEquals(3, cmakelint._lint_state.spaces)

            cmakelint._lint_state.spaces = 2
            cmakelint.ParseOptionFile("""
                    # skip comment
                    spaces= 4
                    """.split('\n'), ignore_space=True)
            self.assertEquals(2, cmakelint._lint_state.spaces)

            cmakelint.ParseOptionFile("""
                    # skip comment
                    """.split('\n'), ignore_space=False)
            self.assertEquals(2, cmakelint._lint_state.spaces)
        finally:
            cmakelint._USAGE = old_usage
            cmakelint._ERROR_CATEGORIES = old_cats
            cmakelint._lint_state.spaces = old_spaces

if __name__ == '__main__':
    unittest.main()
