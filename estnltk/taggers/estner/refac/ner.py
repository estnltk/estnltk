# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from estnltk import EnvelopingBaseSpan
from estnltk.layer.layer import Layer
from estnltk.layer.enveloping_span import EnvelopingSpan
from estnltk.layer.annotation import Annotation

"""
Module containing functionality for training and using NER models.

Attributes
----------
tagger: NerTagger
    Ner tagger with default model and parameters.

"""
import os
import shutil
import errno
import inspect



class ModelStorageUtil(object):
    def __init__(self, model_dir):
        self.model_dir = model_dir
        self.model_filename = os.path.join(model_dir, 'model.bin')
        self.settings_filename = os.path.join(model_dir, 'settings.py')

    def makedir(self):
        """ Create model_dir directory """
        try:
            os.makedirs(self.model_dir)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    def copy_settings(self, settings_module):
        """ Copy settings module to the model_dir directory """
        source = inspect.getsourcefile(settings_module)
        dest = os.path.join(self.model_dir, 'settings.py')
        shutil.copyfile(source, dest)

    def load_settings(self):
        """Load settings module from the model_dir directory."""
        mname = 'loaded_module'
        import importlib.machinery
        loader = importlib.machinery.SourceFileLoader(mname, self.settings_filename)
        return loader.load_module(mname)

