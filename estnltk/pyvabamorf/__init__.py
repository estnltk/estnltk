# -*- coding: utf-8 -*-
from __future__ import absolute_import

from . import vabamorf as vm
import atexit

if not vm.FSCInit():
    raise Exception('Could not initiate pyvabamorf library. FSCInit() returned false!')

@atexit.register
def terminate():
    vm.FSCTerminate()
