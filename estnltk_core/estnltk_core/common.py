#    
#    This module contains constants, paths and functions commonly used in the EstNLTK core library.
#
import os

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


