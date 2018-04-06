# Command lines scripts for processing large corpora

This folder contains command line scripts for processing large corpora -- the Estonian Reference Corpus and the etTenTen corpus -- with EstNLTK.
You can use these scripts if you need a basic pipeline for processing large corpora and adding linguistic analyses. 
If you need a pipeline tailored for your purposes, you can also follow the example of these scripts while implementing your own pipeline.

## Processing the Estonian Reference Corpus (_Eesti keele koondkorpus_)

For processing the whole Estonian Reference Corpus with EstNLTK, proceed in the following steps:

**1.** First, download all the (zipped) XML files from the page [http://www.cl.ut.ee/korpused/segakorpus/](http://www.cl.ut.ee/korpused/segakorpus/). (The web page contains links to different subcorpora, follow the links and download zipped XML files.) Put them into a separate folder, e.g. folder named `koond`. 

   After downloading, you should have the following files ( checked with UNIX command: `ls -1 koond` ):
     
        Agraarteadus.zip
        Arvutitehnika.zip
        Doktoritood.zip
        EestiArst.zip
        Ekspress.zip
        foorum_uudisgrupp_kommentaar.zip
        Horisont.zip
        Ilukirjandus.zip
        Kroonika.zip
        LaaneElu.zip
        Luup.zip
        Maaleht.zip
        Paevaleht.zip
        Postimees.zip
        Riigikogu.zip
        Seadused.zip
        SLOleht.tar.gz
        Teadusartiklid.zip
        Valgamaalane.zip

  (19 files at total)

   _Note_: In Bash shell, you can use the script `download_koondkorpus_zip_files.sh` for downloading the files. 

**2.** Unpack the files. In UNIX, you can use commands:

        cd koond/
        unzip "*.zip"
        tar xvzf SLOleht.tar.gz

**3.** Next, XML files need to be converted into the _json_ format. First, create a new folder where the results of the conversion fill be stored. Then, use the script **`convert_koondkorpus_to_json.py`** to do the conversion. The script needs a starting directory and an output directory as arguments. For the starting directory, you can pass the name of the directory into which you unpacked the zip files in the previous step. The script will recursively traverse the directory structure, and find all the XML files suitable for converting.

   Be aware that all the converted files will be put into the output directory. So, after the conversion, there will be a lot of files in the output folder (approx. 705,000 files).
   
   You can check other possible arguments of the script with the flag `-h`:

        python  convert_koondkorpus_to_json.py  -h

     
**4.** (_Optional_) Use the script  **`split_large_corpus_files_into_subsets.py`** for splitting the large set of files from the previous step into N smaller subsets. This will enable parallel processing of the subsets.

**5.** Use the script **`process_and_save_results.py`** to analyze the JSON format files with EstNLTK 1.6.x. The script will add linguistic annotations up to the level of _morphology_. Before using the script, you'll also need to create a new folder where the script can store the results of analysis. 

   Optionally, you may want to evoke N instances of 
**`process_and_save_results.py`** for faster processing. You can get more information about the processing options with:
   
        python  process_and_save_results.py  -h


## Processing the etTenTen corpus (_Veebikorpus13_)

For processing the etTenTen corpus (aka _Eesti veeb 2013_, or _Veebikorpus13_) with EstNLTK 1.6.x, please proceed in the following steps:

**1.** Download and unpack the corpus, e.g. from here: [https://metashare.ut.ee/repository/browse/ettenten-korpus-toortekst/b564ca760de111e6a6e4005056b4002419cacec839ad4b7a93c3f7c45a97c55f](https://metashare.ut.ee/repository/browse/ettenten-korpus-toortekst/b564ca760de111e6a6e4005056b4002419cacec839ad4b7a93c3f7c45a97c55f)

You should get a large file with the extension _vert_ or _prevert_ (e.g. `ettenten13.processed.prevert`).
 
**2.** Use the script **`convert_ettenten_to_json.py`** for splitting the large file into JSON format files, one file per each document of the corpus. The script needs two input arguments: name of the corpus file, and the output directory where the script can store the JSON format files. It is advisable to create a new directory for the output. Be aware that all the converted files will be put into the output directory; so, there will be a lot of files (approx. 686,000 files).

**3.** (_Optional_) Use **`split_large_corpus_files_into_subsets.py`** for splitting the large set of files from the previous step into N smaller subsets. This will enable parallel processing of the subsets.

**4.** Use the script **`process_and_save_results.py`** to analyze the JSON format files with EstNLTK 1.6.x. The script will add linguistic annotations up to the level of _morphology_. Before using the script, you'll also need to create a new folder where the script can store the results of analysis. 

   Optionally, you may want to evoke N instances of **`process_and_save_results.py`** for faster processing. You can get more information about the processing options with:

        python  process_and_save_results.py  -h


## Helpful utilities

There are also some additional scripts that may be helpful for managing large corpora like etTenTen and koondkorpus.

 * **`select_randomly_from_large_corpus.py`** -- selects randomly a subset of files from the source directory (a directory which contains a large amount of files), and copies into the target directory. You can use this script to get a random sample of koondkorpus or etTenTen, e.g. for tool development, or for experiments;

 *  **`remove_large_amount_of_files.py`** -- deletes all the files from the target directory (a directory which contains a large amount of files). You can use this script to perform a cleanup after corpus processing;