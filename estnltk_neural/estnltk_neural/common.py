#    
#    Constants and paths commonly used in the EstNLTK neural library.
#
import os.path

NEURAL_PACKAGE_PATH = os.path.dirname(__file__)

def neural_abs_path(repo_path: str) -> str:
    """Absolute path to estnltk_neural_repo_path.
       Note: It is recommended to use neural_abs_path instead of 
       a relative path in order  to  make  the  code successfully 
       runnable on all platforms, including Windows.
       If you are using relative paths on Windows, the code may
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
    return os.path.join(NEURAL_PACKAGE_PATH, repo_path)


def check_if_hf_repo_is_available(repo_id:str, cache_dir:str=None, 
                                  revision:str=None):
    '''Scans local huggingface cache for the availablity of the 
       given repository (`repo_id`). 
       Optionally, parameter `cache_dir` can be used to provide 
       the exact location of the cache dir that will be scanned. 
       Optionally, parameter `revision` can be used to specify 
       the exact revision (`commit_hash`) of the repository.
       Returns True iff the repository is available locally (and 
       if it meets the `revision` requirement), and False 
       otherwise. Also returns False if the local cache directory 
       cannot be not found. 
    '''
    from huggingface_hub import scan_cache_dir
    from huggingface_hub.errors import CacheNotFound
    try:
        cache_info = scan_cache_dir(cache_dir=cache_dir)
        for repo in cache_info.repos:
            if repo.repo_id == repo_id:
                if revision is None:
                    return True
                elif isinstance(revision, str):
                    # check for specific revision hash value
                    for rev in repo.revisions:
                        if (rev.commit_hash).startswith(revision):
                            return True
    except CacheNotFound as err:
        # CacheNotFound: Cache directory not found: /root/.cache/huggingface/hub. 
        pass
    return False

