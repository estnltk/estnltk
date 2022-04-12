#
#  Utilities downloading and maintaining EstNLTK's resources:
#  * Getting full paths to downloaded resources (incl. 
#    autodownloading missing resources);
#  * Downloading resources according to entries in resources index;
#  * Unpacking a resource according to a resource description;
#

from typing import Optional, List, Union, Dict, Any

import os
import re
import sys
import requests
import tempfile
import warnings

from zipfile import ZipFile
import gzip

from tqdm import tqdm

from estnltk.resource_utils import get_resources_dir
from estnltk.resource_utils import get_resources_index
from estnltk.resource_utils import _normalized_resource_descriptions
from estnltk.resource_utils import _normalize_resource_size

ALLOW_ALL_DOWNLOADS = False
"""
If True, then missing resources (e.g. models required by taggers) 
will be downloaded automatically without asking user's permission. 
Otherwise, user's permission is asked before proceeding with a  
download. 
Default: False.
"""


def _ask_download_permission(resource_dict: Dict[str, Any]) -> bool:
    '''
    Asks user's permission for downloading the given resource. 
    Command line prompt is used for asking the permission, meaning 
    that the program flow will stop until the user has given an 
    answer (Y or n). In case of an empty or a malformed answer, 
    the "default answer" is Y.
    '''
    size_str = \
        _normalize_resource_size(resource_dict['size']) if 'size' in resource_dict else ''
    if len(size_str) > 0:
        size_str = ' (size: {})'.format( size_str )
    msg = ('This requires downloading resource {!r}{}. '+\
           'Proceed with downloading? [Y/n]').format(resource_dict['name'], size_str)
    answer = input(msg)
    return not (answer.strip().lower() == 'n')


def get_resource_paths(resource: str, only_latest:bool=False, 
                                      download_missing:bool=False) \
                                      -> Union[Optional[str], List[str]]:
    '''
    Finds and returns full paths to (all versions of) downloaded resource.
    
    If there are multiple resources with the given name (i.e. multiple resources 
    with the same alias), then returns a list of paths of downloaded resources, 
    sorted by (publishing) dates of the resources (latest resources first). 
    Resources that have not been downloaded will not appear in the list.
    
    By default, if there is no resource with the given name (or alias) or no 
    such resources have been downloaded yet, returns an empty list.
    However, if download_missing==True, then attempts to download the missing 
    resource. This stops the program flow with a command line prompt, asking
    for user's permission to download the resource. 
    If you set ALLOW_ALL_DOWNLOADS==True (in estnltk.downloader), then resources 
    will be downloaded without asking permission.
    
    Note also that if download_missing==True and there are multiple missing 
    resources that can be downloaded, only the latest one will be automatically 
    downloaded. 
    Use esnltk.downloader.download(...) to download the remaining resources. 
    
    Also, parameter `only_latest` can be used to switch returning type from list 
    to string (path of the latest resource) / None (no paths found).
    
    Parameters
    ----------
    resource: str
        The name or alias of the resource.
    only_latest: bool
        If True, then returns only the path to the latest resource (a string). 
        And if the resource is missing or not downloaded, then returns None. 
        Default: False.
    download_missing: bool
        If True and no downloaded resources were found, but the resource was 
        found in the index, then attempts to download resource. This stops the 
        program flow with a command line prompt, asking for user's permission 
        to download the resource. However, if you set ALLOW_ALL_DOWNLOADS==True 
        (in module estnltk.downloader), then resources will be downloaded 
        without asking permissions.
        Default: False.        

    Returns
    -------
    Union[List[str], Optional[str]]
        List of paths of downloaded resources if not `only_latest`.
        String with path to the latest downloaded resource if `only_latest`.
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
    # Find resource by name or by alias
    resource_paths = []
    undownloaded_resources = []
    for resource_dict in resource_descriptions:
        if resource == resource_dict['name'] or \
           resource in resource_dict['aliases']:
            # check that the resource has been downloaded already
            if resource_dict["downloaded"]:
                target_path = os.path.join(resources_dir, \
                                           resource_dict["unpack_target_path"] )
                target_path = target_path.replace('/', os.sep)
                resource_paths.append( target_path )
            else:
                # Resource has not been downloaded yet
                undownloaded_resources.append( resource_dict )
    # If no paths were found, but there are resources that can be downloaded
    if len(undownloaded_resources) > 0 and \
       len(resource_paths) == 0 and \
       download_missing:
        # Select the latest resource
        target_resource = undownloaded_resources[0]
        proceed_with_download = ALLOW_ALL_DOWNLOADS
        if not proceed_with_download:
            # Ask for user's permission 
            proceed_with_download = \
                _ask_download_permission( target_resource )
        if proceed_with_download:
            status = download(target_resource['name'])
            if status:
                # Recursively fetch the path to the 
                # downloaded resource
                return get_resource_paths(resource)
    if only_latest:
        return resource_paths[0] if len(resource_paths)>0 else None
    else:
        return resource_paths


def _unpack_zip(zip_file, resource_description, resources_dir):
    '''
    Unpacks downloaded zip file according to instructions in resource_description. 
    The content will be unpacked into (a subdirectory of) resources_dir. 
    Returns empty list if the extraction was successful. In case of errors 
    encountered, returns a list with error messages.
    
    The resource_description must contain "unpack_target_path", which 
    can be: 
    1) A directory path into which the content will be unpacked. 
    2) A single file which needs to be extracted from the zip file. 
       In case of a single file, the file path must also contain at least 
       one directory, so the file can be placed into a subdirectory
       of resources_dir.
    If "unpack_target_path" is a directory, and the zip file contains that 
    directory, then only contents from that directory will be extracted 
    and placed locally into "unpack_target_path".
    If "unpack_target_path" is a directory, but the zip file does not contain 
    the directory, then all contents of the zip file will be extracted 
    and placed locally into "unpack_target_path".
    
    Optionally, the resource_description can contain "unpack_source_path",
    which is used to rename file/directory paths during the extraction.
    Note: normally, resources should be packaged in a way that 
    "unpack_source_path" is not required. This is an extra feature to 
    handle non-standard packages. 
    If "unpack_source_path" is a file from zip, then the corresponding 
    file is renamed to "unpack_target_path" (which must also be a file).
    If "unpack_source_path" is a directory in zip, then only file(s) from 
    that directory will be extracted and placed locally into 
    "unpack_target_path" (which must also be a directory). 
    If "unpack_target_path" is a file, then only one file can be extracted 
    from "unpack_source_path" -- multiple files result in an error.
    '''
    assert isinstance(zip_file, str) and os.path.isfile(zip_file)
    assert "unpack_target_path" in resource_description
    unpack_source_path = resource_description.get("unpack_source_path", "")
    unpack_target_path = resource_description.get("unpack_target_path")
    source_type = 'dir' if unpack_source_path.endswith('/') else \
                  ('file' if len(unpack_source_path) > 0 else '')
    target_type = 'dir' if unpack_target_path.endswith('/') else 'file'
    unpack_target_file = \
        os.path.split(path)[1] if target_type is 'file' else None
    items_extracted = 0
    errors = []
    with ZipFile(zip_file, mode='r') as opened_zip:
        # 1) Try to extract items by following strictly the 'unpack_target_path'
        for infolist in opened_zip.infolist():
            # Is the file directory?
            is_dir = (infolist.filename).endswith('/')
            # Does the file path match the source path filter?
            # (and if there is no filter, everything matches)
            is_source_match = \
                (infolist.filename).startswith(unpack_source_path)
            if is_source_match:
                if source_type == 'dir':
                    if target_type == 'dir':
                        # case: source_type == 'dir', target_type == 'dir'
                        # rename path
                        (infolist.filename) = \
                            (infolist.filename).replace(unpack_source_path, \
                                                        unpack_target_path)
                        # extract item
                        extraction_path = resources_dir
                        opened_zip.extract(infolist, extraction_path)
                        items_extracted += 1
                    else:
                        # case: source_type == 'dir', target_type == 'file'
                        if not is_dir:
                            if items_extracted == 0:
                                # rename path
                                (infolist.filename) = \
                                    (infolist.filename).replace(unpack_source_path, \
                                                                unpack_target_path)
                                # extract item
                                extraction_path = resources_dir
                                opened_zip.extract(infolist, extraction_path)
                                items_extracted += 1
                            else:
                                error_msg = ("Error at unzipping resource {!r}: "+\
                                             "a file was already extracted from "+\
                                             "unpack_source_path {!r} and the "+\
                                             "unpack_target_path {!r} only lists "+\
                                             "a single file.").format( \
                                                    resource_description['name'], 
                                                    unpack_source_path, 
                                                    unpack_target_path )
                                errors.append( error_msg )
                                break
                elif source_type == 'file':
                    if target_type == 'dir':
                        # case: source_type == 'file', target_type == 'dir'
                        error_msg = ("Error at unzipping resource {!r}: "+\
                                     "if unpack_source_path {!r} is a file, "+\
                                     "then unpack_target_path {!r} must "+\
                                     "also be a file.").format( \
                                            resource_description['name'], 
                                            unpack_source_path, 
                                            unpack_target_path )
                        errors.append( error_msg )
                        break
                    else:
                        # case: source_type == 'file', target_type == 'file'
                        if not is_dir:
                            if items_extracted == 0:
                                # rename path
                                (infolist.filename) = \
                                    (infolist.filename).replace(unpack_source_path, \
                                                                unpack_target_path)
                                # extract item
                                extraction_path = resources_dir
                                opened_zip.extract(infolist, extraction_path)
                                items_extracted += 1
                            else:
                                error_msg = ("Error at unzipping resource {!r}: "+\
                                             "a file was already extracted from "+\
                                             "unpack_source_path {!r} and the "+\
                                             "unpack_target_path {!r} only lists "+\
                                             "a single file.").format( \
                                                    resource_description['name'], 
                                                    unpack_source_path, 
                                                    unpack_target_path )
                                errors.append( error_msg )
                                break
                else:
                    # The source filter was not defined.
                    # Does the file path match the target path?
                    is_target_match = \
                        (infolist.filename).startswith(unpack_target_path)
                    if target_type == 'dir':
                        # case: source_type == '', target_type == 'dir'
                        if is_target_match:
                            # extract items
                            extraction_path = resources_dir
                            opened_zip.extract(infolist, extraction_path)
                            items_extracted += 1
                    else:
                        # case: source_type == '', target_type == 'file'
                        too_many_items = False
                        if is_target_match:
                            if items_extracted == 0:
                                # extract file that has the same path
                                extraction_path = resources_dir
                                opened_zip.extract(infolist, extraction_path)
                                items_extracted += 1
                            else:
                                too_many_items = True
                        elif infolist.filename == unpack_target_file:
                            if items_extracted == 0:
                                # extract file that has a different path
                                infolist.filename = unpack_target_path
                                extraction_path = resources_dir
                                opened_zip.extract(infolist, extraction_path)
                                items_extracted += 1
                            else:
                                too_many_items = True
                        if too_many_items:
                            error_msg = ("Error at unzipping resource {!r}: "+\
                                         "multiple files named {!r} in zip: "+\
                                         "the file with the same name was "+\
                                         "already extracted from the archive."+\
                                         "").format( \
                                                resource_description['name'], 
                                                unpack_target_file )
                            errors.append( error_msg )
                            break
        # 2) No items found? Is source type is unspecified and target type 
        #    is directory, then simply unpack all the content into the given 
        #    directory
        if not errors and items_extracted == 0 and source_type == '' and \
           target_type == 'dir':
            for infolist in opened_zip.infolist():
                extraction_path = os.path.join(resources_dir, unpack_target_path)
                opened_zip.extract(infolist, extraction_path)
                items_extracted += 1
    if items_extracted > 0:
        print('Unpacked resource into subfolder {!r} of the resources dir.'.format(unpack_target_path))
    elif not errors:
        if len(unpack_source_path) > 0:
            error_msg = ("Error at unzipping resource {!r}: "+\
                         "the zip file did not contain any entries matching "+\
                         "the unpack_source_path {!r}.").format( \
                                resource_description['name'],
                                unpack_source_path )
            errors.append( error_msg )
        elif len(unpack_target_path) > 0:
            error_msg = ("Error at unzipping resource {!r}: "+\
                         "the zip file did not contain any entries matching "+\
                         "the unpack_target_path {!r}.").format( \
                                resource_description['name'],
                                unpack_target_path )
            errors.append( error_msg )
    if errors:
        # Clean up after errors
        if os.path.exists(unpack_target_path):
            if target_type == 'dir':
                os.removedirs(unpack_target_path)
            else:
                os.remove(unpack_target_path)
    # Return a list of error messages. Emtpy list on success
    return errors



def _unpack_gzip(gzip_file, resource_description, resources_dir):
    '''
    Unpacks downloaded gzip file according to instructions in resource_description. 
    The content will be unpacked into (a subdirectory of) resources_dir. 
    Returns empty list if the extraction was successful. In case of errors 
    encountered, returns a list with error messages.
    
    Note that "unpack_target_path" must be a file. Unpacking will 
    fail with an error if it is a directory.
    
    Limitations: currently, does not support unpacking tar.gz files,
    only a single file can be extracted from the archive.
    '''
    errors = []
    assert isinstance(gzip_file, str) and os.path.isfile(gzip_file)
    assert "unpack_target_path" in resource_description
    unpack_source_path = resource_description.get("unpack_source_path", "")
    unpack_target_path = resource_description.get("unpack_target_path")
    if unpack_target_path.endswith('/'):
        # Cannot unpack directory
        error_msg = ("Error at unpacking gz resource {!r}: "+\
                     "cannot unpack a directory from gzip file. "+\
                     "Invalid unpack_target_path {!r}: expected "+\
                     "file, not directory.").format( \
                          resource_description['name'],
                          unpack_target_path )
        errors.append( error_msg )
    if len(unpack_source_path) > 0:
        # Nothing to do with "unpack_source_path"
        warning_msg = ("Warning at unpacking gz resource {!r}: "+\
                       "unpack_source_path has been specified, "+\
                       "but this does not affect unpacking gz "+\
                       "file any way. This only affects zip "+\
                       "unpacking.").format( \
                            resource_description['name'] )
        warnings.warn( UserWarning(warning_msg) )
    if not errors:
        # Unpack the resource
        with gzip.open(gzip_file, 'rb') as in_f:
            file_content = in_f.read()
            outpath = \
                os.path.join(resources_dir, unpack_target_path)
            with open(outpath, 'wb') as out_f:
                out_f.write(file_content)
    return errors



def _download_and_unpack( resource_description, resources_dir ):
    """
    Downloads and unpacks the resource based on given resource_description. 
    The resource is downloaded and unpacked into resources_dir. 
    The compressed file is removed after extraction of the resource. 
    Returns True if unpacking the resource was successful, and False if 
    errors were encountered.
    
    Currently supported downloadable file types:
    * application/zip
    * application/gzip (excluding *.tar.gz)
    
    Throws an exception when:
    *) Content-Type missing from response headers (TODO: can that happen?);
    *) downloadable file has unsupported Content-Type;
    """
    assert "url" in resource_description, \
        ("(!) resource_description is missing 'url':"+\
         "{!r}").format(resource_description)
    assert "unpack_target_path" in resource_description, \
        ("(!) resource_description is missing "+\
         "'unpack_target_path': {!r}").format(resource_description)
    # =================================================
    # 1) Download resource
    # =================================================
    temp_f = tempfile.NamedTemporaryFile( mode="wb", 
                                          prefix='resource_download_', 
                                          dir=resources_dir, delete=False)
    temp_f.close()
    url = resource_description['url']
    name = resource_description['name']
    response = requests.get(url, stream=True)
    file_headers = response.headers
    if 'Content-Type' not in file_headers.keys():
        raise ValueError( ('Missing "Content-Type" in response headers '+\
                           'of the downloadable file: {!r}').format(file_headers) )
    if file_headers['Content-Type'].startswith('application/zip') or \
       file_headers['Content-Type'].startswith('application/gzip'):
        if response.status_code == requests.codes.ok:
            with open(temp_f.name, mode="wb") as out_f:
                for chunk in tqdm( response.iter_content(chunk_size=1024), 
                                   desc="Downloading {}".format(name) ):
                    if chunk:
                        out_f.write(chunk)
                        out_f.flush()
        else:
            response.raise_for_status()
    else:
        raise ValueError( ('(!) File downloadable from {!r} is not a zip or gz file.'+\
                           'Unexpected Content-Type: {!r}').format( url, 
                           file_headers['Content-Type']) )
    # =================================================
    # 2) Create target path directory structure
    # =================================================
    target_path = resource_description["unpack_target_path"]
    if not target_path.endswith('/'):
        # target_path is a file
        target_path_dir, target_file = os.path.split(target_path)
        assert len(target_path_dir) > 0, \
            '(!) "unpack_target_path" must contain at least one directory!'
        full_target_path = os.path.join(resources_dir, target_path_dir) 
        os.makedirs(full_target_path, exist_ok=True)
    else:
        # target_path is a directory
        full_target_path = os.path.join(resources_dir, target_path[:-1])
        os.makedirs(full_target_path, exist_ok=True)
    # =================================================
    # 3) Unpack resource into target path
    # =================================================
    errors = []
    downloaded_file = temp_f.name
    if file_headers['Content-Type'].startswith('application/zip'):
        errors = _unpack_zip(downloaded_file, resource_description, resources_dir)
    elif file_headers['Content-Type'].startswith('application/gzip'):
        errors = _unpack_gzip(downloaded_file, resource_description, resources_dir)
    # =================================================
    # 4) Report errors if any
    # =================================================
    if errors:
        for error_msg in errors:
            print(error_msg, file=sys.stderr)
            # TODO: add logging or something like that
    # =================================================
    # 5) Remove package
    # =================================================
    os.unlink(downloaded_file)
    assert not os.path.exists(downloaded_file)
    return len(errors) == 0


def download(resource:str, refresh_index:bool=False, 
                           redownload:bool=False, 
                           only_latest:bool=True ) -> bool:
    """
    Downloads and unpacks given resource into EstNLTK's resources folder.
    Returns True if the download was successful or if the resource already 
    exists. Returns False if the resource with given name did not exist or 
    downloading was unsuccessful.
    
    If only_latest==True (default), then downloads only the latest resource 
    in case of multiple versions in the index. Otherwise, downloads all 
    versions.
    
    Parameters
    ----------
    resource: str
        The name or alias of the resource.
    refresh_index: bool
        If True, then reloads the resources index from RESOURCES_INDEX_URL.
        Default: False.
    only_latest: bool
        If True, then downloads only the latest resource in case of multiple 
        versions found from index. Otherwise, downloads all versions. 
        Default: True.
    redownload: bool
        If True, then redownloads the resource even it has already been 
        downloaded. Basically: refreshes existing resource.
        Default: False.

    Returns
    -------
    bool
        True if the download was successful or if the resource already 
        exists. 
        False if the resource with given name did not exist or downloading 
        or unpacking was unsuccessful.
    """
    if not isinstance(resource, str):
        raise ValueError( ('(!) Expected name of a resource (string), '+
                           'but got {}.').format( type(resource) ) )
    resource_descriptions = \
        _normalized_resource_descriptions(refresh_index=refresh_index,
                                          check_existence=True)
    matching_descriptions = []
    for resource_dict in resource_descriptions:
        # check name
        if resource == resource_dict['name'] or \
           resource in resource_dict['aliases']:
           matching_descriptions.append( resource_dict )
    if matching_descriptions:
        # Fetch resources according to descriptions
        resources_dir = get_resources_dir()
        if only_latest and len(matching_descriptions) > 1:
            # Take only the latest resource
            matching_descriptions = matching_descriptions[:1]
        # Attempt to download resources
        success = True
        for resource_desc in matching_descriptions:
            if "unpack_target_path" not in resource_desc:
                msg = "(!) Unexpected resource description: the "+\
                      "description is missing 'unpack_target_path' "+\
                      "which should define the local path of the "+\
                      "downloaded resource."
                raise ValueError(msg)
            if resource_desc["downloaded"] and not redownload:
                print( ("Resource {!r} has already been downloaded."+
                        "").format(resource_desc["name"]) )
            else:
                # Download the resource
                success = \
                    _download_and_unpack(resource_desc, resources_dir)
        return success
    else:
        print( ("Unable to find resource {!r}. "+\
                "Please check that the resource name is "+\
                "correct.").format(resource) )
        return False

