## Vabamorf speed benchmarking

The _Vabamorf_ extension in EstNLTK can be compiled with [the option `-builtin`](http://www.swig.org/Doc3.0/Python.html#Python_nn28) that turns off usage of Python proxy classes, and improves _Vabamorf_'s speed. 
However, using this option leads to a conflict with one of the EstNLTK's dependency libraries that uses different settings for compiling its extension (see [this document](https://github.com/estnltk/estnltk/blob/eca541f64d29a633ef0dcefbba3ca445bde0d4e3/dev_documentation/hfst_integration_problems/solving_stringvector_segfault.md) for a details). 
Therefore, the performance-improving option needs to be turned off. 
In this document, we evaluate how much this affects the processing speed of the _Vabamorf_ extension.


### Settings of the speed evaluation

<table>
<tr><td>Python</td><td>3.5.5 (64-bit)</td></tr>
<tr><td>EstNLTK's version</td><td><a href="https://github.com/estnltk/estnltk/tree/353905537958f9984e2c3182602edae91ff9d153">devel_1.6 : 3539055</a></td></tr>
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

<tr><td><b>Vabamorf.analyse w/o disamb</b></td><td>whole corpus: 36.66 s <br> words per sec:   6477</td><td>whole corpus: 42.01 s <br> words per sec:   6114  <b>(-5.6 %)</b></td></tr>

<tr><td><b>Vabamorf.analyse w disamb</b></td><td>whole corpus:    57.88 s<br>words per sec:   4438</td><td>whole corpus:   61.27 s <br> words per sec:   4193 <b>(-5.5%)</b></td></tr>

<tr><td><b>VabamorfTagger w/o disamb</b></td><td>whole corpus:    135.95 s <br> words per sec:   1889 </td><td>whole corpus:   140.76 s<br>words per sec:   1824  <b>(-3.4%)</b></td></tr>

<tr><td><b>VabamorfTagger w disamb</b></td><td>whole corpus:    237.95 s<br>words per sec:   1079</td><td>whole corpus:   246.01 s <br> words per sec:   1044  <b>(-3.2%)</b></td></tr>


</table>

Legend:

 * _whole corpus_ -- average time spent on processing the whole corpus;
 * _words per sec_ -- average speed: words per second;
 * _Vabamorf.analyse w/o disamb_ -- "pure Vabamorf" (that is: morphological analysis without any post-corrections) without disambiguation was used for processing texts;
 * _Vabamorf.analyse w disamb_ -- "pure Vabamorf" (that is: morphological analysis without any post-corrections) with disambiguation was used for  processing texts;
 * _VabamorfTagger w/o disamb_ -- `VabamorfTagger` without disambiguation was used for processing texts;
 * _VabamorfTagger w disamb_ -- `VabamorfTagger` with disambiguation was used for processing texts;  