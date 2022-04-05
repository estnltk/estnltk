#
#  Utilities for handling EstNLTK's resources:
#  * Detecting EstNLTK's resources directory/path
#  * Downloading/updating resources index
#

from typing import Dict, Any

import os
import json
import warnings
from pathlib import Path
from datetime import datetime

import requests
from tqdm import tqdm

from estnltk.common import PACKAGE_PATH

def _is_folder_writable(folder) -> bool:
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


def get_resources_dir() -> str:
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
        else:
            warning_msg = ("Cannot use resources folder {!r}: "+\
                           "the folder is not writable.").format(env_folder)
            warnings.warn( UserWarning(warning_msg) )
    elif env_folder is not None:
        warning_msg = ("Cannot use resources folder {!r}: "+\
                       "no such folder exists.").format(env_folder)
        warnings.warn( UserWarning(warning_msg) )
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

RESOURCES_INDEX_URL = \
    'https://raw.githubusercontent.com/estnltk/estnltk_resources/master/resources_index.json'
"""
URL of the resources index.
"""

INDEX_TIMEOUT = 7200
"""
Freshness period of the index file in seconds.
If this period has elapsed since the last update of the index file,
the index will be re-downloaded.
Default value: 7200 (2 h).
"""

def get_resources_index(force_update:bool=False) -> Dict[str, Any]:
    """
    Fetches and returns resources index (a dictionary).
    
    If the current ESTNLTK_RESOURCES directory does not contain
    'resources_index.json', then downloads the file from RESOURCES_INDEX_URL,
    places into the ESTNLTK_RESOURCES directory, and returns it's content as 
    a dict.
    
    If the current ESTNLTK_RESOURCES directory already contains
    'resources_index.json', checks the modification time of the file. 
    If the file is older than INDEX_TIMEOUT (by default: 2 hours), then it's 
    content will be redownloaded; otherwise, the content of the old file will 
    be returned.
    
    And, finally, if force_update=True, then 'resources_index.json'
    is redownloaded from RESOURCES_INDEX_URL regardless the modification
    time of the existing index file.
    """
    resources_dir = get_resources_dir()
    resources_index = os.path.join(resources_dir, 'resources_index.json')
    # Check if the resources file has already been downloaded
    if os.path.exists(resources_index):
        if not force_update:
            assert isinstance(INDEX_TIMEOUT, int)
            # Should we update the index? Check the last modification time
            mod_time = \
                datetime.fromtimestamp(Path(resources_index).stat().st_mtime)
            if (datetime.now() - mod_time).seconds >= INDEX_TIMEOUT:
                # Update if INDEX_TIMEOUT seconds has passed
                # (default value: 2 hours)
                force_update = True
    if force_update or not os.path.exists(resources_index):
        # Download resources index
        response = requests.get(RESOURCES_INDEX_URL, stream=True)
        if response.status_code == requests.codes.ok:
            with open(resources_index, mode="wb") as out_f:
                for chunk in tqdm( response.iter_content(chunk_size=1024), \
                                   desc="Downloading resources index" ):
                    if chunk:
                        out_f.write(chunk)
                        out_f.flush()
        else:
            response.raise_for_status()
    if os.path.exists(resources_index):
        with open(resources_index, 'r', encoding='utf-8') as in_f:
            resources_index_dict = json.load(in_f)
        return resources_index_dict
    raise Exception('(!) Unable to get resources index.')

    