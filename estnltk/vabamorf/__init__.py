# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
from . import vabamorf as vm
import atexit

if not vm.FSCInit():
    raise Exception('Could not initiate estnltk vabamorf library. FSCInit() returned false!')

@atexit.register
def terminate():
    vm.FSCTerminate()
