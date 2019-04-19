## `HfstEstMorphAnalyser` speed benchmarking
 
In this document, we evaluate [`HfstEstMorphAnalyser`](https://github.com/estnltk/estnltk/blob/cbda73f36b3c358add47e1e3256af1e6f074ce3f/tutorials/hfst/morph_analysis_with_hfst_analyser.ipynb)'s speed on text processing, and also compare it against the speed of `VabamorfTagger`.


### Settings of the speed evaluation

<table>
<tr><td>Python</td><td>3.5.5 (32-bit)</td></tr>
<tr><td>EstNLTK's version</td><td><a href="https://github.com/estnltk/estnltk/tree/cbda73f36b3c358add47e1e3256af1e6f074ce3f">devel_1.6, commit: cbda73f</a></td></tr>
<tr><td>System</td><td>Windows 10 running on <br> Intel Core i5-6200U CPU @ 2.40 GHz <br>with 16 GB of RAM</td></tr>
<tr><td>Evaluation corpus</td><td>Files from the <a href="http://www.cl.ut.ee/korpused/segakorpus/">Estonian Reference Corpus</a>:<br><br>
aja_EPL_2007_02_14.tasak.xml<br>
aja_EPL_2007_09_07.tasak.xml<br>
aja_ml_2004_01.tasak.xml<br>
aja_pm_2000_01_26.tasak.xml<br>
ilu_koos.tasak.xml<br>
ilu_MjaA4.tasak.xml<br>
ilu_paastke.tasak.xml<br>
tea_draama2.tasak.xml<br>
tea_EMS_2001.tasak.xml<br>
tea_perekond.tasak.xml<br>
tea_toohoive.tasak.xml</td></tr>
<tr><td>Corpus size in Text objects</td><td>389</td></tr>
<tr><td>Corpus size in words</td><td>256805</td></tr>
<tr><td>Number of repetitions in evaluation</td><td>4</td></tr>
<tr><td>Processing scripts</td><td>Derived from <a href="https://github.com/estnltk/estnltk/tree/cbda73f36b3c358add47e1e3256af1e6f074ce3f/dev_documentation/vabamorf_benchmarking">Vabamorf's speed benchmarking<br>  scripts</a></td></tr>
</table>

### Results

<table>
<tr><td><b></b></td><td><b>average processing<br> time and speed</b></td><td><b>speed decrease<br>(if compared to <br>the best)</b></td></tr>

<tr><td><b>HfstEstMorphAnalyser<br>(with "raw" output)</b></td><td>whole corpus: 180.2 s <br> words per sec:   1429</td><td>-21.18%</td></tr>

<tr><td><b>HfstEstMorphAnalyser<br>(with "morphemes_lemmas" output)</b></td><td>whole corpus:    243.1 s<br>words per sec:   1076</td><td>-40.65%</td></tr>

<tr><td><b>VabamorfTagger w/o disamb</b></td><td>whole corpus:    141.6 s <br> words per sec:   <b>1813</b> </td><td>0%</td></tr>

<tr><td><b>VabamorfTagger w disamb</b></td><td>whole corpus:    252.5 s<br>words per sec:   1017</td><td>-43.91%</td></tr>


</table>

Legend:

 * _whole corpus_ -- average time spent on processing the whole corpus;
 * _words per sec_ -- average speed: words per second;
 * _HfstEstMorphAnalyser (with "raw" output)_ -- `HfstEstMorphAnalyser` with `output_format="raw"`, and without any morphological disambiguation was used for processing texts;
 * _HfstEstMorphAnalyser (with `"morphemes_lemmas"` output)_ -- `HfstEstMorphAnalyser` with `output_format="morphemes_lemmas"`, and without any morphological disambiguation was used for processing texts;
 * _VabamorfTagger w/o disamb_ -- `VabamorfTagger` without disambiguation was used for processing texts;
 * _VabamorfTagger w disamb_ -- `VabamorfTagger` with disambiguation was used for processing texts;
	 * Note: in both cases, the `Vabamorf` extension also used Python proxy classes;