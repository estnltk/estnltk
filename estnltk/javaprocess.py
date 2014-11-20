# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from estnltk.core import JAVARES_PATH
import subprocess
import os


class JavaProcess(object):
    '''Base class for Java-based extension.
    Allows processing data line by line.'''

    def __init__(self, runnable_jar, args=[]):
        self._process = subprocess.Popen(['java', '-jar', os.path.join(JAVARES_PATH, runnable_jar)] + args,
                                         stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
    def __del__(self):
        self._process.terminate()
                                         
    def _process_line(self, line):
        '''Process a line of data.
        
        Sends the data through the pipe to the process and flush it. Reads a resulting line
        and returns it.
        
        Parameters
        ----------
        
        line: str
            The data sent to process. Make sure it does not contain any newline characters.

        Returns
        -------
        str: The line returned by the Java process
        
        Raises
        ------
        Exception
            In case of EOF is encountered.
        IoError
            In case it was impossible to read or write from the subprocess standard input / output.
        '''
        assert isinstance(line, str)
        try:
            self._process.stdin.write(line)
            self._process.stdin.write('\n')
            self._process.stdin.flush()
            result = self._process.stdout.readline()
            if result == '':
                stderr = self._process.stderr.read()
                raise Exception('EOF encountered while reading stream. Stderr is {0}.'.format(stderr))
            return result
        except Exception:
            self._process.terminate()
            raise
