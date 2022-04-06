#
#  Utilities downloading and maintaining EstNLTK's resources:
#  * Download resources according to entries in resources index;
#

import os
import re
import requests
import tempfile
import warnings

from zipfile import ZipFile

from tqdm import tqdm

from estnltk.resources_utils import get_resources_dir
from estnltk.resources_utils import get_resources_index
from estnltk.resources_utils import _normalized_resource_descriptions

def _download_and_unpack( resource_description, resources_dir ):
    """
    Downloads and unpacks the resource based on given resource_description. 
    The resource is downloaded and unpacked into resources_dir. 
    The compressed file is removed after extraction of the resource. 
    
    Currently supported downloadable file types:
    * application/zip
    
    Throws an exception when:
    *) downloadable file has unsupported Content-Type;
    *) unpack_source_path was defined, but none of the files 
       inside the archive matched it;
    *) unpack_source_path is not defined and compressed file does not 
       match unpack_target_path (TODO: this condition should be changed?)
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
    # 2) Create target path
    # =================================================
    # TODO: support 'single_file' path also
    full_target_path = os.path.join( resources_dir, \
                                     resource_description["unpack_target_path"] )
    os.makedirs(full_target_path, exist_ok=True)
    # =================================================
    # 3) Unpack resource into target path
    # =================================================
    downloaded_file = temp_f.name
    unpack_source_path = resource_description.get("unpack_source_path", "")
    unpack_target_path = resource_description.get("unpack_target_path")
    # TODO: possible correspondences between source_path and target_path 
    # should be better systematized
    items_extracted = 0
    with ZipFile(downloaded_file, mode='r') as opened_zip:
        for infolist in opened_zip.infolist():
            is_dir = (infolist.filename).endswith('/')
            if infolist.filename.startswith(unpack_source_path):
                if len(unpack_source_path) > 0:
                    # Fix directory name ending
                    target_path = unpack_target_path
                    if unpack_source_path.endswith('/') and \
                       not target_path.endswith('/'):
                        target_path += '/'
                    # Rename path
                    (infolist.filename) = \
                        (infolist.filename).replace(unpack_source_path, \
                                                    target_path)
                else:
                    if not (infolist.filename).startswith(unpack_target_path):
                        # The target path in the description does match with 
                        # the path inside the zip file. Problematic case, 
                        # raise exception ...
                        error_msg = ("Error at unzipping resource {!r}: "+\
                                     "the file path {!r} inside zip does not match "+\
                                     "the unpack_target_path {!r}.").format(desc['name'],
                                          infolist.filename, unpack_target_path )
                        raise Exception( error_msg )
                extraction_path = resources_dir
                opened_zip.extract(infolist, extraction_path)
                items_extracted += 1
    if items_extracted > 0:
        print('Unpacked resource into subfolder {!r} of the resources dir.'.format(unpack_target_path))
    else:
        if len(unpack_source_path) > 0:
            error_msg = ("Error at unzipping resource {!r}: "+\
                         "the zip file did not contain any entries matching "+\
                         "the unpack_source_path {!r}.").format( desc['name'],
                              unpack_source_path )
            raise Exception(error_msg)
    os.unlink(downloaded_file)
    assert not os.path.exists(downloaded_file)


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
        If True, then then downloads only the latest resource in case of 
        multiple versions found from index. Otherwise, downloads all versions. 
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
        was unsuccessful.
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
                _download_and_unpack(resource_desc, resources_dir)
        return True
    else:
        print( ("Unable to find resource {!r}. "+\
                "Please check that the resource name is "+\
                "correct.").format(resource) )
        return False

