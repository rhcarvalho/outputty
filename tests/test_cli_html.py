#!/usr/bin/env python
# coding: utf-8

# Copyright 2011 Álvaro Justen
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
import os
import tempfile
from textwrap import dedent
from utils import execute, sh, OUTPUTTY_EXECUTABLE


class TestOutputtyCliHtml(unittest.TestCase):
    def test_should_receive_csv_data_from_stdin_and_print_html_to_stdout(self):
        out, err = execute('--read-csv --write-html', 'a\n')
        expected = dedent('''
        <table>
          <thead>
            <tr class="header">
              <th>a</th>
            </tr>
          </thead>
        </table>
        ''').strip() + '\n'
        self.assertEquals(out, expected)

    def test_receive_csv_data_in_stdin_and_save_in_a_html_file(self):
        temp_fp = tempfile.NamedTemporaryFile(delete=False)
        temp_fp.close()
        out, err = execute('--read-csv --write-html ' + temp_fp.name,
                           'a,b\n1,2\n')
        temp_fp = open(temp_fp.name)
        csv_contents = temp_fp.read()
        os.remove(temp_fp.name)
        self.assertEquals(csv_contents, dedent('''
        <table>
          <thead>
            <tr class="header">
              <th>a</th>
              <th>b</th>
            </tr>
          </thead>
          <tbody>
            <tr class="odd">
              <td>1</td>
              <td>2</td>
            </tr>
          </tbody>
        </table>
        ''').strip() + '\n')

    def test_write_html_with_wrong_filename_returns_1_and_stderr_not_empty(self):
        process = sh(OUTPUTTY_EXECUTABLE  + ' --read-csv --write-html /a/b/c',
                     finalize=False)
        process.stdin.write('a,b\n1,2')
        process.stdin.close()
        process.wait()
        self.assertEquals(process.returncode, 2)
        expected_error = "[Errno 2] No such file or directory: '/a/b/c'\n"
        self.assertEquals(process.stderr.read(), expected_error)

    def test_write_html_without_permissions_returns_1_and_stderr_not_empty(self):
        process = sh(OUTPUTTY_EXECUTABLE + ' --read-csv --write-html /root/test',
                     finalize=False)
        process.stdin.write('a,b\n1,2')
        process.stdin.close()
        process.wait()
        self.assertEquals(process.returncode, 2)
        expected_error = "[Errno 13] Permission denied: '/root/test'\n"
        self.assertEquals(process.stderr.read(), expected_error)

    def test_read_stdin_with_input_encoding(self):
        input_string = u'álvaro\ntesting'.encode('utf16')
        out, err = execute('--read-csv --input-encoding utf16 --write-html',
                           input_string)
        expected = dedent('''
        <table>
          <thead>
            <tr class="header">
              <th>álvaro</th>
            </tr>
          </thead>
          <tbody>
            <tr class="odd">
              <td>testing</td>
            </tr>
          </tbody>
        </table>
        ''').strip() + '\n'
        self.assertEquals(out, expected)

    def test_output_encoding_should_work(self):
        input_string = '"álvaro"\n"testing"\n'
        out, err = execute('--read-csv --write-html --output-encoding iso-8859-1',
                           input_string)
        expected = dedent('''
        <table>
          <thead>
            <tr class="header">
              <th>álvaro</th>
            </tr>
          </thead>
          <tbody>
            <tr class="odd">
              <td>testing</td>
            </tr>
          </tbody>
        </table>
        ''').strip() + '\n'
        expected = expected.decode('utf8').encode('iso-8859-1')
        self.assertEquals(out, expected)