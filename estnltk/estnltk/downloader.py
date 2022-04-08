#
#  Utilities downloading and maintaining EstNLTK's resources:
#  * Download resources according to entries in resources index;
#  * Unpack resource according to a resource description;
#  * ...
#

import os
import re
import sys
import requests
import tempfile
import warnings

from zipfile import ZipFile

from tqdm import tqdm

from estnltk.resources_utils import get_resources_dir
from estnltk.resources_utils import get_resources_index
from estnltk.resources_utils import _normalized_resource_descriptions

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
                                    desc['name'], unpack_source_path, unpack_target_path )
                                errors.append( error_msg )
                                break
                elif source_type == 'file':
                    if target_type == 'dir':
                        # case: source_type == 'file', target_type == 'dir'
                        error_msg = ("Error at unzipping resource {!r}: "+\
                                     "if unpack_source_path {!r} is a file, "+\
                                     "then unpack_target_path {!r} must "+\
                                     "also be a file.").format( \
                            desc['name'], unpack_source_path, unpack_target_path )
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
                                    desc['name'], unpack_source_path, unpack_target_path )
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
                                desc['name'], unpack_target_file )
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
                         "the unpack_source_path {!r}.").format( desc['name'],
                              unpack_source_path )
            errors.append( error_msg )
        elif len(unpack_target_path) > 0:
            error_msg = ("Error at unzipping resource {!r}: "+\
                         "the zip file did not contain any entries matching "+\
                         "the unpack_target_path {!r}.").format( desc['name'],
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


def _download_and_unpack( resource_description, resources_dir ):
    """
    Downloads and unpacks the resource based on given resource_description. 
    The resource is downloaded and unpacked into resources_dir. 
    The compressed file is removed after extraction of the resource. 
    Returns True if unpacking the resource was successful, and False if 
    errors were encountered.
    
    Currently supported downloadable file types:
    * application/zip
    
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
    if file_headers['Content-Type'].startswith('application/zip'):
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
        # TODO: application/gzip should also be allowed
        raise ValueError( ('(!) File downloadable from {!r} is not a zip file.'+\
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
    downloaded_file = temp_f.name
    if file_headers['Content-Type'].startswith('application/zip'):
        errors = _unpack_zip(downloaded_file, resource_description, resources_dir)
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
                           only_latest:bool=True ):
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

