import os
import shutil
import errno
import inspect


class ModelStorageUtil(object):
    """ Class with helper functions for storing information about NER models """
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
        try:
            shutil.copyfile(source, dest)
        except shutil.SameFileError as sf_error:
            print('(!) Warning: Location of the new "settings.py" is the same one as the old one. Model\'s settings are not copied.')
            pass
        except:
            raise

    def load_settings(self):
        """Load settings module from the model_dir directory."""
        mname = 'loaded_module'
        import importlib.machinery
        loader = importlib.machinery.SourceFileLoader(mname, self.settings_filename)
        return loader.load_module(mname)

