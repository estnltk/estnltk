# -*- coding: utf-8 -*-
"""Functionality for using Java-based components.

Attributes
----------
JAVARES_PATH: str
    The root path for Java components of Estnltk library.
"""
from __future__ import unicode_literals, print_function

from estnltk.core import PACKAGE_PATH, as_unicode, as_binary
import subprocess
import os

JAVARES_PATH = os.path.join(PACKAGE_PATH, 'java-res')


class JavaProcess(object):
    """Base class for Java-based components.
    
    It opens a pipe to a Java VM running the component and interacts with
    it using standard input and standard output.
    
    The data is encoded as a single line and then flushed down the pipe.
    The Java component receives the input, processes it and writes the
    output also encoded on a single line and flushes it.
    
    This line-based approach is easy to implement and debug.
    
    To implement a Java component, inherit from this class and use
    `process_line` method to interact with the process.
    
    It deals with input/output and errors.
    """

    def __init__(self, runnable_jar, args=[]):
        """Initialize a Java VM.
        
        Parameters
        ----------
        runnable_jar: str
            Path of the JAR file to be run. The java program is expected
            to reside in `java-res` folder of the estnltk project.
        args: list of str
            The list of arguments given to the Java program.
        """
        self._process = subprocess.Popen(['java', '-jar', os.path.join(JAVARES_PATH, runnable_jar)] + args,
                                         stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
                                         
    def process_line(self, line):
        """Process a line of data.
        
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
        """
        assert isinstance(line, str)
        try:
            self._process.stdin.write(as_binary(line))
            self._process.stdin.write(as_binary('\n'))
            self._process.stdin.flush()
            result = as_unicode(self._process.stdout.readline())
            if result == '':
                stderr = as_unicode(self._process.stderr.read())
                raise Exception('EOF encountered while reading stream. Stderr is {0}.'.format(stderr))
            return result
        except Exception:
            self._process.terminate()
            raise
