#    
#    This module contains constants, paths and functions commonly used in the EstNLTK core library.
#
import os
import importlib, importlib.util

CORE_PACKAGE_PATH = os.path.dirname(__file__)

def core_abs_path(repo_path: str) -> str:
    """Absolute path to core_repo_path.
       Note: It is recommended to use core_abs_path instead of 
       core_rel_path  in  order  to  make  the  code successfully 
       runnable on all platforms, including Windows.
       If you are using relative paths in Windows, the code may
       break for the following reasons:
       A) If a Windows system has more than one drive (e.g. "C:" and
          "D:"), and the estnltk is installed on one drive, and
          the code using estnltk is executed from the other drive,
          then the relative path from one drive to another does not
          exist, and the path creator function fails with an error;
       B) If you are trying to execute a code that uses estnltk
          in a deeply nested directory structure, and as a result,
          the relative path from the current directory to estnltk's
          repo directory becomes long and exceeds the Windows Maximum
          Path Limitation, you will get a FileNotFoundError.
          About the Windows Maximum Path Limitation:
              https://docs.microsoft.com/en-us/windows/win32/fileio/naming-a-file#maximum-path-length-limitation
    """
    return os.path.join(CORE_PACKAGE_PATH, repo_path)


def core_rel_path(repo_path: str) -> str:
    """Relative path to core_repo_path."""
    return os.path.relpath(os.path.join(CORE_PACKAGE_PATH, repo_path))


def load_text_class() -> 'type':
    """ Uses importlib to load the Text class based on currently available packages. 
        First tries to load the full-fledged Text class from the package path "estnltk.text.Text".
        If this fails ("estnltk" is not installed), then falls back to loading Text class 
        from "estnltk_core.text.Text".
        Returns the Text class, which can be used to create new Text instances.
    """
    try:
        # First: try to load the full-fledged Text class
        module_spec = importlib.util.find_spec("estnltk.text")
        if module_spec:
            module = importlib.import_module("estnltk.text")
            full_text_class = getattr(module, "Text")
            return full_text_class
    except:
        # Pass the exception: attempt to load in different way
        pass
    try:
        # Second: try to load the Text class from EstNLTK core
        module = importlib.import_module("estnltk_core.text")
        partial_text_class = getattr(module, "Text")
        return partial_text_class
    except:
        raise


def create_text_object(text: str = None) -> 'Text':
    """ Uses importlib to create a Text object based on currently available packages. 
        First tries to create the full-fledged Text object from the package path "estnltk.text.Text".
        If this fails (the "estnltk" not installed), then falls back to creating Text object 
        from "estnltk_core.text.Text".
        Returns created Text object. 
    """
    text_class = load_text_class()
    return text_class( text )


