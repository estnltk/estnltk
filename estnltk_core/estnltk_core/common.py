#    
#    This module contains constants, paths and functions commonly used in the EstNLTK core library.
#
from typing import Union, Tuple, Sequence, Any

import os
import importlib, importlib.util

CORE_PACKAGE_PATH = os.path.dirname(__file__)

# Output configuration parameters commonly used in the package
OUTPUT_CONFIG = {
    # Maximum length for string representation in html output
    'html_str_max_len' : 100,
    # Which types of attributes will have their values displayed?
    'attr_val_repr_types' : (str, int, float, bool, list, tuple, set, dict),
}


def _create_attr_val_repr( seq_attribute_values: Sequence[Tuple[str, Any]] ) -> str:
    """Creates a concise string representation of annotations' attributes and values. 
       A value of an attribute will be rendered only if it is None or an instance of 
       a type listed in OUTPUT_CONFIG['attr_val_repr_types']. If value is sequence or 
       mapping, it will be rendered only if it consists of basic types (None, str, 
       int, float, bool). In all other cases, values will be rendered as their type 
       names. 
       Returns a string, which follows the dict representation: { k1: v1, ..., kN: vN }
    """
    basic_types = (str, int, float, bool)
    allowed_types = OUTPUT_CONFIG.get( 'attr_val_repr_types', basic_types )
    key_value_strings = []
    for (attr, val) in seq_attribute_values:
        if val is None:
            # None will always be displayed
            key_value_strings.append( '{!r}: {!r}'.format(attr, val) )
        elif isinstance( val, allowed_types ):
            has_all_basic_types = True
            if isinstance( val, (list, tuple, set) ):
                # Check the contents of the sequence: display only if 
                # it consists of basic types
                has_all_basic_types = \
                    all([i is None or isinstance(i, basic_types) for i in val])
            elif isinstance( val, dict ):
                # Check the contents of the mapping: display only if 
                # it consists of basic types
                has_all_basic_types = \
                    all([isinstance(k2, basic_types) and (isinstance(v2, basic_types) or \
                         v2 is None) for k2,v2 in val.items()])
            if has_all_basic_types:
                key_value_strings.append( '{!r}: {!r}'.format(attr, val) )
            else:
                # If it included some non-basic types, display type name only
                key_value_strings.append( '{!r}: {!r}'.format(attr, type(val)) )
        else:
            # If the type is not allowed, display type name only
            key_value_strings.append( '{!r}: {!r}'.format(attr, type(val)) )
    return '{{{attributes}}}'.format( attributes=', '.join(key_value_strings) )


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
    """ Uses importlib to load the Text or BaseText class based on currently available packages. 
        First tries to load the full-fledged Text class from the package path "estnltk.text.Text".
        If this fails ("estnltk" is not installed), then falls back to loading BaseText class 
        from "estnltk_core.base_text.BaseText".
        Returns the Text or BaseText class, which can be used to create new text instances. 
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
        # Second: try to load the BaseText class from EstNLTK core
        module = importlib.import_module("estnltk_core.base_text")
        partial_text_class = getattr(module, "BaseText")
        return partial_text_class
    except:
        raise


def create_text_object(text: str = None) -> Union['BaseText', 'Text']:
    """ Uses importlib to create a BaseText or Text object based on currently available packages. 
        First tries to create the full-fledged Text object from the package path "estnltk.text.Text".
        If this fails (the "estnltk" not installed), then falls back to creating BaseText object 
        from "estnltk_core.base_text.BaseText".
        Returns created BaseText or Text object. 
    """
    text_class = load_text_class()
    return text_class( text )


