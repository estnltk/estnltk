# -*- coding: utf-8 -*-
#
#   Functionality for using Java-based components.
#   Ported from:
#      https://github.com/estnltk/estnltk/tree/1.4.1.1/estnltk
#

import subprocess
import os

# ==============================================================================
#   Methods for converting between Unicode <=> Binary
#   Ported from EstNLTK 1.4.1.1 ( with slight modifications ):
#      https://github.com/estnltk/estnltk/blob/1.4.1.1/estnltk/core.py
# ==============================================================================

def as_unicode(s, encoding='utf-8'):
    """Force conversion of given string to unicode type.
       If the string is already in unicode, then no conversion is done and 
       the same string is returned.
       
       Parameters
       ----------
       s: str or bytes
           The string to convert to unicode.
       encoding: str
           The encoding of the input string (default: utf-8)

       Raises
       ------
       ValueError
           In case an input of invalid type was passed to the function.
       Returns
       -------
           s converted to ``str``
    """
    if isinstance(s, str):
        return s
    elif isinstance(s, bytes):
        return s.decode(encoding)
    else:
        raise ValueError('Can only convert types {0} and {1}'.format(str, bytes))


def as_binary(s, encoding='utf-8'):
    """Force conversion of given string to binary type.
       If the string is already in binary, then no conversion is done and 
       the same string is returned and ``encoding`` argument is ignored.
       
       Parameters
       ----------
       s: str or bytes
           The string to convert to binary.
       encoding: str
           The encoding of the resulting binary string (default: utf-8)
       Raises
       ------
       ValueError
           In case an input of invalid type was passed to the function.
       Returns
       -------
           s converted to ``bytes`` 
    """
    if isinstance(s, str):
        return s.encode(encoding)
    elif isinstance(s, bytes):
        # make sure the binary is in required encoding
        return s.decode(encoding).encode(encoding)
    else:
        raise ValueError('Can only convert types {0} and {1}'.format(str, bytes))


# ==============================================================================
#   Class for processing texts with Java-based tools
#   Ported from EstNLTK 1.4.1.1:
#      https://github.com/estnltk/estnltk/blob/1.4.1.1/estnltk/javaprocess.py
# ==============================================================================

class JavaProcess( object ):
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

    def __init__(self, runnable_jar, jar_path=None, args=[]):
        """Initialize a Java VM.
        
        Parameters
        ----------
        runnable_jar: str
            Name of the JAR file to be run. 
        jar_path: str 
            Path to the JAR file. If provided, then the path will 
            be concatenated to the JAR file name before launching 
            the command.
        args: list of str
            The list of arguments given to the Java program.
        """
        if jar_path:
            runnable_jar = os.path.join(jar_path, runnable_jar)
        self._process = subprocess.Popen(['java', '-jar', runnable_jar] + args,
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

