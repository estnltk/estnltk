import pytest

import os
from estnltk.resource_utils import delete_resource
from estnltk.resource_utils import _normalized_resource_descriptions
from estnltk.resource_utils import _check_version
from estnltk.downloader import download, get_resource_paths

TEST_ESTNLTK_DOWNLOADER = os.environ.get('TEST_ESTNLTK_DOWNLOADER', '')

def get_downloaded_resource_names(resource: str):
    ''' 
    Find out which resources with the given name/alias have 
    already been downloaded.
    '''
    resource_descriptions = \
        _normalized_resource_descriptions(refresh_index=False,
                                          check_existence=True)
    resource = resource.lower()
    # Find resource by name or by alias
    resource_names = []
    for resource_dict in resource_descriptions:
        if resource_dict["downloaded"]:
            if resource == resource_dict['name'] or \
               resource in resource_dict['aliases']:
                resource_names.append( resource_dict['name'] )
    return resource_names



@pytest.mark.skipif(len(TEST_ESTNLTK_DOWNLOADER) == 0,
                    reason="set environment variable TEST_ESTNLTK_DOWNLOADER "+\
                            "to non-zero length value to enable this test.")
def test_resource_dir_download():
    resource_name  = 'udpipe_syntax_2021-05-29'
    resource_alias = 'udpipe'
    resource_path_components = ['udpipe_syntax', 'models_2021-05-29']
    # The initial state of the resource: which models have been downloaded
    initial_resources = get_downloaded_resource_names(resource_alias)
    
    # Download by name
    download_successful = download(resource_name, redownload=True, only_latest=True)
    assert download_successful
    
    dir_paths = get_resource_paths(resource_name, download_missing=False)
    assert len(dir_paths) > 0
    assert all([comp in dir_paths[0] for comp in resource_path_components])
    
    # Delete resource 
    delete_resource(resource_name)
    
    # Download by alias
    download_successful = download(resource_alias, redownload=True, only_latest=True)
    assert download_successful
    
    dir_paths = get_resource_paths(resource_alias, download_missing=False)
    assert len(dir_paths) > 0
    assert all([comp in dir_paths[0] for comp in resource_path_components])
    
    if len(initial_resources) == 0:
        # Clean up the initial resource
        delete_resource(resource_name)



@pytest.mark.skipif(len(TEST_ESTNLTK_DOWNLOADER) == 0,
                    reason="set environment variable TEST_ESTNLTK_DOWNLOADER "+\
                            "to non-zero length value to enable this test.")
def test_resource_file_download():
    resource_name  = "word2vec_lemmas_cbow_s100_2015-06-21"
    resource_alias = 'word2vec'
    resource_path_components = ['word2vec', 'lemmas.cbow.s100.w2v.bin']
    # The initial state of the resource: which models have been downloaded
    initial_resources = get_downloaded_resource_names(resource_alias)
    
    # Download by name
    download_successful = download(resource_name, redownload=True, only_latest=True)
    assert download_successful
    
    file_paths = get_resource_paths(resource_alias, download_missing=False)
    assert len(file_paths) > 0
    assert all([comp in file_paths[0] for comp in resource_path_components])
    
    if len(initial_resources) == 0:
        # Clean up the initial resource
        delete_resource(resource_name)


def test_estnltk_version_checking_smoke():
    # Test estnltk's version checking component works
    # (this is used by the get_resource_paths function)
    assert _check_version('my_resource', 'estnltk', '>1.4.1')
    assert _check_version('my_resource', 'estnltk_core', '>=1.4.1.1')
    result = _check_version('my_resource', 'estnltk', '<1.4')
    assert result is not None and not result  # returns False, but not None
    assert _check_version('my_resource', 'estnltk', '>= 1.7.0')
    result = _check_version('my_resource', 'estnltk', '>=30.0.0')
    assert result is not None and not result  # returns False, but not None
    assert _check_version('my_resource', 'estnltk', '> 1.6.9.1, <30.0.0')
    result = _check_version('my_resource', 'estnltk', '<3.0.0, > 2.0.0')
    assert result is not None and not result  # returns False, but not None
