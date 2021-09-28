# -*- coding: utf-8 -*-

from . import vabamorf as vm
import atexit
import sys

# A patch: use vm.FSCInit() & vm.FSCTerminate() only on Windows & MacOS
# Patch discussed in here: https://github.com/estnltk/estnltk/issues/97
# Credit for the patch goes to: https://github.com/cslarsen
if sys.platform.startswith('win') or sys.platform.startswith('darwin'):
    # end of patch
    if not vm.FSCInit():
        raise Exception('Could not initiate estnltk vabamorf library. FSCInit() returned false!')

    @atexit.register
    def terminate():
        vm.FSCTerminate()
