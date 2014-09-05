# -*- coding: utf-8 -*-
#
#   Methods for initializing and terminating Java Virtual Machine with the JAR files 
#  necessary providing linguistic analysis tools.
#   Basically wraps around the javabridge library, which needs to be installed
#  before using the methods. More information on javabridge:
#     https://pypi.python.org/pypi/javabridge/1.0.7
#     http://pythonhosted.org//javabridge/index.html
#
#   NB! Tool configuration has been tested with Java version 1.7.0_02 (at least version 
#  1.7.x is expected) and with Python 2.7.8 (32 bit);
#   NB! If there are multiple Java installations available in the system, it might be 
#  necessary to set correct JAVA_HOME path before starting the Python with javabridge; 
#  E.g. on the Windows it was necessary to set:
#      SET JAVA_HOME=C:\Program Files (x86)\Java\jdk1.7.0_02
#
#

import javabridge
import os.path

def initializeJVM(jarFilesDir):
    ''' Uses Python's javabridge and initializes JVM with necessary jar files. 
        Input argument jarFilesDir must be the full path to the java resources directory.
        NB! After JVM has been successfully initialized, it must be terminated by 
        calling the method terminateJVM() '''
    jars = javabridge.JARS[:]
    jars.append( os.path.join(jarFilesDir, 'joda-time-1.6.jar') )
    jars.append( os.path.join(jarFilesDir, 'javax.json-1.0.4.jar') )
    jars.append( os.path.join(jarFilesDir, 'Ajavt.jar') )
    jars.append( os.path.join(jarFilesDir, 'Osalau.jar') )
    # Check whether necessary jar files exist
    for jar in jars:
        if not os.path.exists(jar):
            raise Exception(" Unable to find jar file from location: ", jar)
    # Initialize javabridge
    try:
        javabridge.start_vm( run_headless=True, class_path=jars )
    except:
        terminateJVM()
        raise

def terminateJVM():
    ''' Uses Python's javabridge and terminates the JVM started with method initializeJVM().
        NB! After this method has been called, no subsequent calling of method initializeJVM()
        is possible. '''
    javabridge.kill_vm()
