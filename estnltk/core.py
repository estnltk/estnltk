import os

PACKAGE_PATH = os.path.dirname(__file__)

# Path to Java resources used by EstNLTK
JAVARES_PATH = os.path.join(PACKAGE_PATH, 'java', 'res')


def abs_path(repo_path):
    """absolute path to repo_path"""
    return os.path.join(PACKAGE_PATH, repo_path)
