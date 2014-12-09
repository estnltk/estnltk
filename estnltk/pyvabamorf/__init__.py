# -*- coding: utf-8 -*-
from __future__ import absolute_import

from estnltk.pyvabamorf import vabamorf as vm
import atexit
import sys

if not vm.FSCInit():
    #sys.stderr.write('Could not initiate pyvabamorf library. FSCInit() returned false!\n')
    raise Exception('Could not initiate pyvabamorf library. FSCInit() returned false!')

@atexit.register
def terminate():
    vm.FSCTerminate()

from estnltk.morf import analyze, synthesize
