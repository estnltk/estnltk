## Command line scripts for processing corpora

This folder contains command line scripts that can be used for processing large corpora -- namely, Koondkorpus and etTenTen -- with EstNLTK 1.6.

### Processing etTenTen

1. Download and unpack the corpus, e.g. from here: [https://metashare.ut.ee/repository/browse/ettenten-korpus-toortekst/b564ca760de111e6a6e4005056b4002419cacec839ad4b7a93c3f7c45a97c55f](https://metashare.ut.ee/repository/browse/ettenten-korpus-toortekst/b564ca760de111e6a6e4005056b4002419cacec839ad4b7a93c3f7c45a97c55f) 
2. Use the script `convert_ettenten_to_json.py` for splitting the large file into JSON format files, one file per each document of the corpus. You'll also need to create a new folder where the script can store the JSON format files.
3. (_Optional_) Use `split_large_corpus_files_into_subsets.py` for splitting the large set of files from the previous step into N smaller subsets. This will enable parallel processing of the subsets.
4.  Use the script `add_morph_and_save_results.py` to analyze the JSON format files with EstNLTK 1.6.0. You'll also need to create a new folder where the script can store the results of analysis. Optionally, you may want to evoke N instances of `add_morph_and_save_results.py` for faster processing. See `python add_morph_and_save_results.py -h` for details about processing options.

### Processing Koondkorpus

1.  First, you'll need to get [Koondkorpus](http://www.cl.ut.ee/korpused/segakorpus/) into JSON format. There are two options:

	a. You can download the Koondkorpus files that have already been converted into JSON format with EstNLTK 1.4. These files are available here: [http://ats.cs.ut.ee/keeletehnoloogia/estnltk/koond.zip](http://ats.cs.ut.ee/keeletehnoloogia/estnltk/koond.zip) **(!)** Note that this package completely _misses_ a subset of the corpus -- files from the newspaper SL Õhtuleht.

    b. You can use EstNLTK 1.4.1, follow the instructions from the page [https://estnltk.github.io/estnltk/1.4.1/tutorials/tei.html](https://estnltk.github.io/estnltk/1.4.1/tutorials/tei.html), and convert the [corpus files](http://www.cl.ut.ee/korpused/segakorpus/) from TEI format to JSON format.

    Once you have acquired the corpus files in JSON format, you should copy all the files into a single folder.

2. (_Optional_) Use `split_large_corpus_files_into_subsets.py` for splitting the large set of files from the previous step into N smaller subsets. This will enable parallel processing of the subsets.
3.  Use the script `add_morph_and_save_results.py` to analyze the JSON format files with EstNLTK 1.6.0. You'll also need to create a new folder where the script can store the results of analysis. Optionally, you may want to evoke N instances of `add_morph_and_save_results.py` for faster processing. See `python add_morph_and_save_results.py -h` for details about processing options.