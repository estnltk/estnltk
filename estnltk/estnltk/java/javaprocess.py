# -*- coding: utf-8 -*-
#
#   Functionality for using Java-based components.
#   Ported from:
#      https://github.com/estnltk/estnltk/tree/1.4.1.1/estnltk
#

import subprocess
import atexit
import os

from estnltk_core.converters import as_unicode, as_binary

# keep track of started java processes
_STARTED_JAVA_PROCESSES = []

# ==============================================================================
#   Class for processing texts with Java-based tools
#   Base class ported from EstNLTK 1.4.1.1:
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

    def __init__(self, runnable_jar, jar_path=None, check_java=True, \
                       lazy_initialize=True, args=[]):
        """Initialize a Java VM.
        
        Parameters
        ----------
        runnable_jar: str
            Name of the JAR file to be run. 
        jar_path: str 
            Path to the JAR file. If provided, then the path will 
            be concatenated to the JAR file name before launching 
            the command.
        check_java: boolean
            If set, then before initialization of the java subprocess,
            launches command 'java -version' to check that java is 
            accessible from the shell. If java is not accessible, 
            throws an exception informing the user that the java may 
            not be properly installed.
            Note: this check adds some extra time to initializing
            the java subprocess.
            (default: False)
        lazy_initialize: boolean
            If set, then java subprocess will not be initialized at 
            the constructor (which would cause an expection if
            java is missing), but it will be delayed and initialized 
            later, when the method process_line() is called first 
            time. Otherwise, the java subprocess will be initialized 
            right away.
            (default: True)
        args: list of str
            The list of arguments given to the Java program.
        """
        if jar_path:
            runnable_jar = os.path.join(jar_path, runnable_jar)
        self._check_java   = check_java
        self._process      = None
        self._java_args    = args
        self._runnable_jar = runnable_jar
        if not lazy_initialize:
            self.initialize_java_subprocess()


    @staticmethod
    def check_for_java_accessibility():
        """Checks if java is accessible from the shell by launching the command 
           'java -version'. If launching the command fails, throws an exception 
            informing the user that the java is not properly installed."""
        with open(os.devnull, "w") as trash: 
            returncode = subprocess.call('java -version', shell=True, stdout=trash, stderr=trash)
            if returncode != 0:
                raise Exception('(!) Unable to launch a java process. '+\
                                'Please make sure that java is installed into the system and '+\
                                'available via environment variable PATH.')



    def initialize_java_subprocess(self):
        """Checks for java's accessibility (if _check_java==True), and initializes java 
           subprocess."""
        if self._check_java:
            self.check_for_java_accessibility()
        self._process = subprocess.Popen(['java', '-jar', self._runnable_jar] + self._java_args,
                                          stdin=subprocess.PIPE,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE)
        # keep track of started java processes
        _STARTED_JAVA_PROCESSES.append( self._process )



    def process_line(self, line):
        """Process a line of data.
       
        Sends the data through the pipe to the process and flush it. Reads a resulting line
        and returns it.

        Note: self._process is None (lazy initialization), then calls initialize_java_subprocess() 
        before processing the line.

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
        # Lazy initialization:
        if self._process is None:
            self.initialize_java_subprocess()
        else:
            assert self._process.poll() is None, \
               '(!) The tagger cannot be used anymore, '+\
               'because its Java process has been terminated.'
        
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


# ==============================================================================
#   Clean-up : terminate all started java processes
# ==============================================================================

@atexit.register
def _close_java_processes():
    for process in _STARTED_JAVA_PROCESSES:
        if process is not None: # if the process was initialized ...
            if process.poll() is None: # ... and it is still up and running ...
                # The proper way to terminate the process:
                # 1) Send out the terminate signal
                process.terminate()
                # 2) Interact with the process. Read data from stdout and stderr, 
                #    until end-of-file is reached. Wait for process to terminate.
                process.communicate()
                # 3) Assert that the process terminated
                assert process.poll() is not None

