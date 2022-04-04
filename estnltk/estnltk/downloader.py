#
#  * EstNLTK's resources directory
#  * Resource downloader and maintainer
#

import os
from pathlib import Path

from estnltk.common import PACKAGE_PATH

def _is_folder_writable(folder):
    """
    Checks if the given folder/path is writable. 
    Following the principle "It's easier to ask for forgiveness 
    than for permission", simply tries to write a file 
    named '_writability_check' into the directory. 
    Returns True, if the file already exists or if the file 
    was successfully created. 
    Otherwise (exceptions encountered) returns False.
    Idea borrowed from: https://stackoverflow.com/a/25868839
    """
    fpath = os.path.join(folder, '_writability_check')
    if os.path.exists(fpath):
        return True
    try:
        with open(fpath, mode='w') as testfile:
            pass
    except Exception as e:
        return False
    return True


def get_resources_dir():
    """
    Returns the current ESTNLTK_RESOURCES directory.
    
    There are 3 possible locations for the resources directory
    (in the order in which they are checked):
    1) directory in environment variable 'ESTNLTK_RESOURCES';
    2) directory 'estnltk_resources' in estnltk's installation folder;
    3) directory 'estnltk_resources' in user's home folder (`Path.home()`);
    The first suitable directory from the above list is returned.
    
    Each folder is first checked for existence. If directories 2) or 3) 
    do not exist, an attempt is made to create them. If directories 
    exist (or were created), checks for writability (attempts to write 
    file '_writability_check' into the directory). If writability also 
    holds, returns the directory (path).
    
    If suitable directory cannot be found nor created, throws 
    an Exception (asking user to set the ESTNLTK_RESOURCES environment
    variable).
    """
    # 1) get directory from environment variable
    env_folder = os.environ.get("ESTNLTK_RESOURCES", None)
    if env_folder is not None and os.path.isdir(env_folder):
        # Check if the folder is writable
        if _is_folder_writable(env_folder):
            return env_folder
    # TODO: warn user that the directory from ESTNLTK_RESOURCES
    # could not be used ...
    # 2) get directory inside estnltk's installation folder
    resources_in_install = \
        os.path.join(PACKAGE_PATH, 'estnltk_resources')
    if not os.path.exists(resources_in_install):
        # If there is no 'estnltk_resources' folder in PACKAGE_PATH,
        # try to create it (with the possibility of PermissionError)
        try:
            os.mkdir( resources_in_install )
        except Exception as e:
            pass
    if os.path.isdir(resources_in_install):
        # Check if the folder is writable
        if _is_folder_writable(resources_in_install):
            return resources_in_install
    # 3) finally, try to place resources in user's home directory
    home_resources = os.path.join(Path.home(), 'estnltk_resources')
    if not os.path.exists(home_resources):
        # If there is no 'estnltk_resources' folder in user's home
        # directory, try to create it (with the possibility of PermissionError)
        try:
            os.mkdir( home_resources )
        except Exception as e:
            pass
    if os.path.isdir(home_resources):
        # Check if the folder is writable
        if _is_folder_writable(home_resources):
            return home_resources
    raise Exception('(!) Unable to create or locate "estnltk_resources" folder. '+\
                    "It seems that writing into estnltk's installation folder is prohibited, "+\
                    "and it is also not possible to write into the home folder. Please "+\
                    "provide an environment variable 'ESTNLTK_RESOURCES' with the name of an "+\
                    "existing directory where resources can be downloaded and unpacked.")
    
    