## Vabamorf speed benchmarking

The _Vabamorf_ extension in EstNLTK can be compiled with [the option `-builtin`](http://www.swig.org/Doc3.0/Python.html#Python_nn28) that turns off usage of Python proxy classes, and improves _Vabamorf_'s speed. 
However, using this option leads to a conflict with one of the EstNLTK's dependency libraries that uses different settings for compiling its extension (see [this document](https://github.com/estnltk/estnltk/blob/eca541f64d29a633ef0dcefbba3ca445bde0d4e3/dev_documentation/hfst_integration_problems/solving_stringvector_segfault.md) for a details). 
Therefore, the performance-improving option needs to be turned off. 
In this document, we evaluate how much this affects the processing speed of the _Vabamorf_ extension.


### Settings of the speed evaluation

<table>
<tr><td>Python</td><td>3.5.5 (64-bit)</td></tr>
<tr><td>EstNLTK's version</td><td><a href="https://github.com/estnltk/estnltk/tree/89d067250a7132c26a7c1d70f212fd3a4418f9ce">devel_1.6 : 89d0672</a></td></tr>
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
</table>

### Scripts

 * `preprocess.py` -- Loads XML files as Texts with the default tokenization and saves into JSON files;
 * `process_with_vabamorf.py` -- Loads Texts from JSON files, and processes with pyvabamorf and VabamorfTagger. Calculates and reports avg processing times and speeds;

### Results

<table>
<tr><td><b></b></td><td><b>without Python proxy classes</b></td><td><b>with Python proxy classes</b></td></tr>

<tr><td><b>Vabamorf.analyse w/o disamb</b></td><td>whole corpus: 39.892 s <br> words per sec:   6440</td><td>whole corpus: 42.555 s <br> words per sec:   6037  <b>(-6.26 %)</b></td></tr>

<tr><td><b>Vabamorf.analyse w disamb</b></td><td>whole corpus:    59.083 s<br>words per sec:   4347</td><td>whole corpus:   61.933 s <br> words per sec:   4147 <b>(-4.6%)</b></td></tr>

<tr><td><b>VabamorfTagger w/o disamb</b></td><td>whole corpus:    103.7 s <br> words per sec:   2477 </td><td>whole corpus:   140.970 s<br>words per sec:   1822  <b>(-26.44%)</b></td></tr>

<tr><td><b>VabamorfTagger w disamb</b></td><td>whole corpus:    191.098 s<br>words per sec:   1344</td><td>whole corpus:   250.573 s <br> words per sec:   1025  <b>(-23.74%)</b></td></tr>


</table>

Legend:

 * _whole corpus_ -- average time spent on processing the whole corpus;
 * _words per sec_ -- average speed: words per second;
 * _Vabamorf.analyse w/o disamb_ -- "pure Vabamorf" (that is: morphological analysis without any post-corrections) without disambiguation was used for processing texts;
 * _Vabamorf.analyse w disamb_ -- "pure Vabamorf" (that is: morphological analysis without any post-corrections) with disambiguation was used for  processing texts;
 * _VabamorfTagger w/o disamb_ -- `VabamorfTagger` without disambiguation was used for processing texts;
 * _VabamorfTagger w disamb_ -- `VabamorfTagger` with disambiguation was used for processing texts;  