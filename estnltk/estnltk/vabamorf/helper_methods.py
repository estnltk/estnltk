import re
import os



def regex_from_markers(markers):
    """Given a string of characters, construct a regex that matches them.

    Parameters
    ----------
    markers: str
        The list of string containing the markers

    Returns
    -------
    regex
        The regular expression matching the given markers.
    """
    return re.compile('|'.join([re.escape(c) for c in markers]))


def get_vm_lexicon_paths(root_path: str):
    """
    Returns lexicons paths reachable fropm the root directory in correct order.
    TODO: Specify what does this mean
    """
    return [item
            for item in sorted(os.listdir(root_path), reverse=False) if os.path.isdir(os.path.join(root_path, item))]


def get_vm_lexicon_files(vm_lexicon_dir, dict_path):
    """
    Given EstNLTK's directory that contains Vabamorf\'s lexicons,
    creates names of the lexicon files, checks for their existence
    and returns a tuple of lexicon file paths:
      ( path to analyser's lexicon,
        path to disambiguator's lexicon ).
    If vm_lexicon_dir is a directory name without path, and
    dict_path is provided, then first constructs the full path
    to Vabamorf\'s lexicon directory by joining dict_path and
    vm_lexicon_dir;
    """
    if not os.path.isdir(vm_lexicon_dir) and dict_path is not None:
        vm_lexicon_dir = os.path.join(dict_path, vm_lexicon_dir)
    assert os.path.isdir(vm_lexicon_dir), '(!) Unexpected Vabamorf\'s lexicon directory {!r}'.format(vm_lexicon_dir)
    et_file = os.path.join(vm_lexicon_dir, 'et.dct')
    et3_file = os.path.join(vm_lexicon_dir, 'et3.dct')
    assert os.path.isfile(et_file), '(!) Unable to find Vabamorf analyser\'s lexicon file: {!r}'.format(et_file)
    assert os.path.isfile(et3_file), '(!) Unable to find Vabamorf disambiguator\'s lexicon file: {!r}'.format(et3_file)
    return et_file, et3_file

