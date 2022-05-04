#
#  Utilities for handling EstNLTK's resources:
#  * Detecting EstNLTK's resources directory/path
#  * Downloading/updating the index of resource descriptions
#  * Normalizing resource descriptions
#

from typing import Dict, Any

import os
import re
import json
import shutil
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
                progress = tqdm( desc="Downloading resources index",
                                 unit="B", unit_scale=True )
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        out_f.write(chunk)
                        out_f.flush()
                        progress.update(len(chunk))
                progress.close()
        else:
            response.raise_for_status()
    if os.path.exists(resources_index):
        with open(resources_index, 'r', encoding='utf-8') as in_f:
            resources_index_dict = json.load(in_f)
        return resources_index_dict
    raise Exception('(!) Unable to get resources index.')


def _target_path_exists( target_path: str, resources_dir: str ):
    '''
    Checks if the given target_path exists inside resources_dir,
    and has expected type (file or directory).
    Additional check: if the expected type is directory, the 
    directory must contain at least one item.
    '''
    if target_path.endswith('/'):
        # target_path is directory
        dir_path = os.path.join(resources_dir, target_path[:-1])
        return os.path.exists(dir_path) and \
               os.path.isdir(dir_path) and \
               len(os.listdir(dir_path)) > 0
    else:
        # target_path is file
        file_path = os.path.join(resources_dir, target_path)
        return os.path.exists(file_path) and os.path.isfile(file_path)


_date_pattern = re.compile(r'(\d\d\d\d\D\d\d\D\d\d)')

def _normalized_resource_descriptions(refresh_index:bool=False,
                                      check_existence:bool=True):
    '''
    Loads resources index, validates and normalizes resource descriptions.
    Returns a temporally sorted list of resource descriptions (latest 
    resources first).
    
    If refresh_index==True (default: False), then loads a fresh resources 
    index from RESOURCES_INDEX_URL.
    
    Validation: resources missing keys 'name', 'url', 'unpack_target_path' 
    will be discarded with warning messages about invalid descriptions. 
    Also, 'name' and 'unpack_target_path' must be unique among all resource
    descriptions. If a resource description contains name or target path of 
    another resource description, it will be discarded with a warning message.
    
    Normalisation: Resource 'name' and 'aliases' are converted to lowercase.
    If key 'aliases' is missing, it is added with an empty list.
    In 'unpack_source_path' and 'unpack_target_path', all slashes are converted
    to POSIX slashes (/). This is requied for the zipfile module, which also 
    uses POSIX slashes in paths.
    Each resource should be placed into a folder, so 'unpack_target_path' must 
    contain at least one path separator (/). Resource will be discarded if 
    this condition is not met.
    If 'unpack_source_path' is a file (does not end with /), then 
    'unpack_target_path' must also be a file (not end with /) or otherwise 
    the resource will be discarded.
    
    If check_existence==True (default), then adds key 'downloaded' to 
    each normalized resource description, indicating whether the corresponding 
    resource has been downloaded already ('unpack_target_path' exists inside
    ESTNLTK_RESOURCES).
    
    For resources pointing to a huggingface repository, the 'unpack_target_path' 
    must be a directory, or the resource will be discarded. (Cannot download a 
    single file from huggingface, only downloading a repository snapshot is 
    allowed).
    
    Finally, resource descriptions are sorted by their publication dates, which 
    should be present in resource names. Each resource name should contain an 
    ISO format date, e.g. "udpipe_syntax_2021-05-29" or 
    "stanza_syntax_2021-05-29".
    '''
    resources_dir = get_resources_dir()
    resources_index = get_resources_index(force_update=refresh_index)
    if "resources" not in resources_index:
        raise KeyError( ('(!) Invalid resources index: missing "resources" key:'+\
                          '\n{!r}').format(resources_index) )
    if not isinstance(resources_index["resources"], list):
        raise TypeError( ('(!) Invalid resources index: "resources" should be a list,'+\
                          'not {!r}').format(type(resources_index["resources"])) )
    # Normalize resource descriptions
    normalized_resource_descriptions = []
    seen_resource_names = set()
    seen_unpack_target_paths = set()
    for resource_dict in resources_index["resources"]:
        if not isinstance(resource_dict, dict):
            raise TypeError( ('(!) Invalid resource description: should be '+\
                              'a dict, not {!r}').format(type(resource_dict)) )
        usable = True
        # Check that all the required items are present in the rource
        for required_key in ['name', 'url', 'unpack_target_path']:
            if required_key not in resource_dict.keys():
                warning_msg = ("Missing key {!r} in resource "+\
                               "description: \n {!r}\nDiscarding the "+\
                               "resource.").format(required_key, resource_dict)
                if required_key == 'unpack_target_path':
                    warning_msg = ("(!) Invalid resource description \n{!r}\n"+\
                                  "the description is missing 'unpack_target_path' "+\
                                  "which should define the local path of the "+\
                                  "downloaded resource. Discarding the resource."+\
                                  "").format(resource_dict)
                warnings.warn( UserWarning(warning_msg) )
                usable = False
        if usable:
            # Convert names und aliases to lowercase
            resource_dict['name'] = resource_dict['name'].lower()
            resource_dict['aliases'] = \
                [a.lower() for a in resource_dict["aliases"]] \
                if "aliases" in resource_dict else []
            # Check that the resource name is unique
            if resource_dict["name"] in seen_resource_names:
                warning_msg = ("Invalid 'name' in resource "+\
                               "description: \n {!r}\nThe name {!r} has already been "+\
                               "used by another resource. "+\
                               "Discarding the resource."+\
                               "").format(resource_dict, resource_dict["name"])
                warnings.warn( UserWarning(warning_msg) )
                continue
            # Normalise slashes
            if "unpack_source_path" in resource_dict:
                resource_dict["unpack_source_path"] = \
                    resource_dict["unpack_source_path"].replace('\\', '/')
            resource_dict["unpack_target_path"] = \
                resource_dict["unpack_target_path"].replace('\\', '/')
            target_path = resource_dict["unpack_target_path"]
            # Check that the "unpack_target_path" is not an empty string
            if len(target_path) == 0:
                warning_msg = ("Invalid target path from resource "+\
                               "description: \n {!r}\nThe target path {!r} cannot "+\
                               "be an empty string. A path containing at least one "+\
                               "folder must be provided. Discarding the resource."+\
                               "").format(resource_dict, target_path)
                warnings.warn( UserWarning(warning_msg) )
                continue
            # Check that the "unpack_target_path" is contains at least one folder
            if '/' not in target_path:
                warning_msg = ("Invalid target path from resource "+\
                               "description: \n {!r}\nThe target path {!r} does "+\
                               "not contain any pathname separators '/'. The target "+\
                               "path must contain at least one folder. Discarding "+\
                               "the resource.").format(resource_dict, target_path)
                warnings.warn( UserWarning(warning_msg) )
                continue
            # Check that the "unpack_target_path" is unique
            if target_path in seen_unpack_target_paths:
                warning_msg = ("Invalid target path from resource "+\
                               "description: \n {!r}\nThe path {!r} has already been "+\
                               "used by another resource. "+\
                               "Discarding the resource."+\
                               "").format(resource_dict, target_path)
                warnings.warn( UserWarning(warning_msg) )
                continue
            # If this is a huggingface resource, check that target_path
            # is a directory, not a file
            if is_huggingface_resource(resource_dict):
                if not target_path.endswith('/') :
                    warning_msg = ("Invalid target path {!r} from resource "+\
                                   "description: \n {!r}\nThis is a huggingface "+\
                                   "resource, so the path must be a directory "+\
                                   "(must end with '/'). Discarding the resource."+\
                                   "").format(target_path, resource_dict)
                    warnings.warn( UserWarning(warning_msg) )
                    continue
            # Check that if "unpack_source_path" is a file, 
            # then "unpack_target_path" is not a directory.
            if "unpack_source_path" in resource_dict and \
               not resource_dict["unpack_source_path"].endswith('/') and \
               target_path.endswith('/'):
                warning_msg = ("Invalid target path from resource "+\
                               "description: \n {!r}\nThe source path {!r} points"+\
                               "to a file, so the target path {!r} must also be a"+\
                               "file, not a directory."+\
                               "").format( resource_dict, 
                                           resource_dict["unpack_source_path"], 
                                           target_path )
                warnings.warn( UserWarning(warning_msg) )
                continue
            seen_resource_names.add( resource_dict['name'] )
            seen_unpack_target_paths.add( target_path )
            # Detect the ISO-like date from the name
            resource_dict["date"] = ''
            date_m = _date_pattern.search(resource_dict['name'])
            if date_m:
                date_str = date_m.group(1)
                resource_dict["date"] = date_str
            else:
                warning_msg = ("(!) Unexpected resource name {!r}: "+\
                               "could not parse date from the "+\
                               "name.").format(resource_dict['name'])
                warnings.warn( UserWarning(warning_msg) )
            # Check if the resource has been downloaded already
            if check_existence:
                resource_dict["downloaded"] = \
                    _target_path_exists(target_path, resources_dir)
            normalized_resource_descriptions.append( resource_dict )
    # Sort resource descriptions temporally (latest descriptions first)
    normalized_resource_descriptions = \
        sorted( normalized_resource_descriptions, \
                key=lambda x:x["date"], reverse=True )
    return normalized_resource_descriptions


def _normalize_resource_size( resource_size: float ) -> str:
    '''Returns normalized resource_size with human-readable units.
    '''
    if not isinstance(resource_size, float):
        return ''
    if resource_size < 1.0:
        return '{:.0f}M'.format(resource_size*1000.0)
    else:
        return '{:.1f}G'.format(resource_size)


_hf_url_pattern = re.compile(r'^(https://)?huggingface.co/([^/ ]+/[^/ ]+)$')

def is_huggingface_resource(resource_dict: Dict[str, Any]) -> bool:
    '''Checks if the given resource url points to a huggingface.co repository.
    '''
    return _hf_url_pattern.match(resource_dict['url']) is not None


def ping_resource(resource_dict: Dict[str, Any]) -> bool:
    '''
    Checks if the url of the resource is valid. 
    Basically, makes a HTTP request (in streaming mode) and 
    checks that the response status code is OK.
    '''
    status_code_ok = False
    with requests.get(resource_dict['url'], stream=True) as resp:
        status_code_ok = (resp.status_code == requests.codes.ok)
    return status_code_ok


def delete_resource(resource: str) -> bool:
    '''
    Deletes downloaded resource by name. 
    Note that the resource name must be specific (e.g. "stanza_syntax_2020-11-30"), 
    and not an alias ("stanza_syntax", "stanza").
    Returns boolean indicating whether the resource was found and deleted.
    '''
    if not isinstance( resource, str ):
        raise TypeError(('(!) Invalid resource name: '+\
                         'expected a string, not {!r}').format(type(resource)))
    # Get resources directory and normalized resource descriptions
    resources_dir = get_resources_dir()
    resource_descriptions = \
        _normalized_resource_descriptions(refresh_index=False,
                                          check_existence=True)
    resource = resource.lower()
    # Find resource by name
    found_by_alias = []
    deleted = False
    for resource_dict in resource_descriptions:
        # only downloaded resources can be deleted ...
        if resource_dict["downloaded"]:
            if resource == resource_dict['name']:
                    target_path = os.path.join(resources_dir, \
                                               resource_dict["unpack_target_path"] )
                    target_path = target_path.replace('/', os.sep)
                    if target_path.endswith( os.sep ):
                        # delete directory tree
                        shutil.rmtree(target_path)
                        deleted = True
                    else:
                        # delete file
                        os.remove(target_path)
                        deleted = True
                    break
            elif resource in resource_dict['aliases']:
                found_by_alias.append(resource_dict['name'])
    if not deleted and found_by_alias:
        print( ('Cannot delete resource by alias. '+\
                'Please use a specific resource name '+\
                'from the list: {!r}').format( found_by_alias ) )
    return deleted

