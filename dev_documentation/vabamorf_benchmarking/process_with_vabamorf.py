#  Vabamorf speed benchmarking
#  Processes JSON Text files with pyvabamorf and VabamorfTagger
#   * repeats processing several iterations;
#   * calculates and reports avg processing times and speeds;

import os, os.path
import re, sys
import statistics

from datetime import datetime, timedelta
from collections import defaultdict

from estnltk import Text
from estnltk.taggers import VabamorfTagger
from estnltk.vabamorf.morf import Vabamorf
from estnltk.converters import json_to_text

# input data (json Text objects)
in_dir  = 'json_data'

assert os.path.isdir(in_dir), '(!) Missing input directory {!r}'.format(in_dir)
assert len( [fname for fname in os.listdir(in_dir) if fname.endswith('.json')] )>0, \
           '(!) No json files in {!r}'.format(in_dir)


# how many times processing should be repeated?
iterations = 4


# Sums up time_deltas, finds an average time delta and calculates the speed;
def summarize_times_and_find_speed( time_deltas, word_count ):
    time_delta_sum = \
         timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, 
                   minutes=0, hours=0, weeks=0)
    for delta in time_deltas:
        time_delta_sum += delta
    avg_time_delta = 0.0
    if len(time_deltas) > 0:
        avg_time_delta = time_delta_sum / len(time_deltas)
    total_sec = time_delta_sum.total_seconds()
    words_per_second = 0.0
    if total_sec > 0.0:
        words_per_second = word_count / total_sec
    return [time_delta_sum, total_sec, avg_time_delta, words_per_second]

# Calculates and reports average processing time and speed;
# Note: we only calculate and report the mean +/- the standard deviation,
# and leave it up to the interpreter to make specific assumptions about 
# the distribution (e.g. normal distribution or t distribution), and 
# to calculate the exact confidence intervals (if needed);
def report_statistics(total_end_time, iterations, text_count, word_count,
                      collected_total_secs, collected_seconds_per_text,
                      collected_words_per_second):
    print()
    print('       Total processing time: {}'.format(total_end_time))
    print()
    print('                  Iterations: {}'.format(iterations))
    print('   Text objects in iteration: {}'.format(text_count))
    print('          Words in iteration: {}'.format(word_count))
    print()
    # collected_total_secs
    mean  = 0.0
    if len(collected_total_secs) > 0:
        mean = statistics.mean(collected_total_secs)
    stdev = 0.0 
    if len(collected_total_secs) > 1:
        stdev = statistics.stdev(collected_total_secs, xbar=mean)
    print('  Avg corpus processing time: {:.2f} +/- {:.2f} s'.format( mean, stdev ))
    # collected_seconds_per_text
    mean  = 0.0
    if len(collected_seconds_per_text) > 0:
        mean = statistics.mean(collected_seconds_per_text)
    stdev = 0.0
    if len(collected_seconds_per_text) > 1:
        stdev = statistics.stdev(collected_seconds_per_text, xbar=mean)
    print('    Avg Text processing time: {:.2f} +/- {:.2f} s'.format( mean, stdev ))
    # collected_words_per_second
    mean  = 0.0
    if len(collected_words_per_second) > 0:
        mean = statistics.mean(collected_words_per_second)
    stdev = 0.0
    if len(collected_words_per_second) > 1:
        stdev = statistics.stdev(collected_words_per_second, xbar=mean)
    print('        Avg words per second: {:.0f} +/- {:.0f}'.format( mean, stdev ))
    print()


all_experiments_start_time = datetime.now()

#
# 1) Vabamorf.instance(): morph analysis only
#
print()
print('Applying Vabamorf.instance() without disambiguation on pretokenized texts')
vm_instance = Vabamorf.instance()
collected_total_secs       = []
collected_words_per_second = []
collected_seconds_per_text = []
total_start_time = datetime.now()
for i in range(iterations):
    word_count = 0
    text_count = 0
    time_deltas = []
    for fid, fname in enumerate(os.listdir(in_dir)):
        if fname.endswith('json'):
            fpath = os.path.join(in_dir, fname)
            text_obj = json_to_text(file=fpath)
            input_words = [w.text for w in text_obj['words']]
            start_time = datetime.now()
            results = vm_instance.analyze(words=input_words, disambiguate=False, propername=True, guess=True)
            time_deltas.append( datetime.now() - start_time )
            assert len(results) == len(input_words)
            word_count += len(text_obj['words'])
            text_count += 1
        #if fid > 50:
        #    break
    [time_delta_sum, total_sec, secs_per_text_delta, words_per_second] = \
                     summarize_times_and_find_speed( time_deltas, word_count )
    collected_total_secs.append( total_sec )
    collected_words_per_second.append( words_per_second )
    collected_seconds_per_text.append( secs_per_text_delta.total_seconds() )

total_end_time = datetime.now() - total_start_time
report_statistics(total_end_time,iterations,text_count,word_count,collected_total_secs,
                                                                  collected_seconds_per_text,
                                                                  collected_words_per_second)

#sys.exit()

#
# 2) Vabamorf.instance(): morph analysis with disambiguation
#
print()
print('Applying Vabamorf.instance() with disambiguation on pretokenized texts')
vm_instance = Vabamorf.instance()
collected_total_secs       = []
collected_words_per_second = []
collected_seconds_per_text = []
total_start_time = datetime.now()
for i in range(iterations):
    word_count = 0
    text_count = 0
    time_deltas = []
    for fid, fname in enumerate(os.listdir(in_dir)):
        if fname.endswith('json'):
            fpath = os.path.join(in_dir, fname)
            text_obj = json_to_text(file=fpath)
            input_words = [w.text for w in text_obj['words']]
            start_time = datetime.now()
            results = vm_instance.analyze(words=input_words, disambiguate=True, propername=True, guess=True)
            time_deltas.append( datetime.now() - start_time )
            assert len(results) == len(input_words)
            word_count += len(text_obj['words'])
            text_count += 1
        #if fid > 50:
        #    break
    [time_delta_sum, total_sec, secs_per_text_delta, words_per_second] = \
                     summarize_times_and_find_speed( time_deltas, word_count )
    collected_total_secs.append( total_sec )
    collected_words_per_second.append( words_per_second )
    collected_seconds_per_text.append( secs_per_text_delta.total_seconds() )

total_end_time = datetime.now() - total_start_time
report_statistics(total_end_time,iterations,text_count,word_count,collected_total_secs,
                                                                  collected_seconds_per_text,
                                                                  collected_words_per_second)

#sys.exit()

#
# 3) VabamorfTagger: morph analysis only
#
morph_tagger1 = VabamorfTagger(disambiguate=False, guess=True, propername=True)
print()
print('Applying VabamorfTagger without disambiguation on pretokenized texts')
collected_total_secs       = []
collected_words_per_second = []
collected_seconds_per_text = []
total_start_time = datetime.now()
for i in range(iterations):
    word_count = 0
    text_count = 0
    time_deltas = []
    for fid, fname in enumerate(os.listdir(in_dir)):
        if fname.endswith('json'):
            fpath = os.path.join(in_dir, fname)
            text_obj = json_to_text(file=fpath)
            assert 'morph_analysis' not in text_obj.layers
            start_time = datetime.now()
            morph_tagger1.tag( text_obj )
            time_deltas.append( datetime.now() - start_time )
            assert 'morph_analysis' in text_obj.layers
            word_count += len(text_obj['words'])
            text_count += 1
        #if fid > 50:
        #    break
    [time_delta_sum, total_sec, secs_per_text_delta, words_per_second] = \
                     summarize_times_and_find_speed( time_deltas, word_count )
    collected_total_secs.append( total_sec )
    collected_words_per_second.append( words_per_second )
    collected_seconds_per_text.append( secs_per_text_delta.total_seconds() )

total_end_time = datetime.now() - total_start_time
report_statistics(total_end_time,iterations,text_count,word_count,collected_total_secs,
                                                                  collected_seconds_per_text,
                                                                  collected_words_per_second)

#
# 4) VabamorfTagger: morph analysis + disambiguation
#
morph_tagger2 = VabamorfTagger(disambiguate=True, guess=True, propername=True)
print()
print('Applying VabamorfTagger with disambiguation on pretokenized texts')
collected_total_secs       = []
collected_words_per_second = []
collected_seconds_per_text = []
total_start_time = datetime.now()
for i in range(iterations):
    word_count = 0
    text_count = 0
    time_deltas = []
    for fid, fname in enumerate(os.listdir(in_dir)):
        if fname.endswith('json'):
            fpath = os.path.join(in_dir, fname)
            text_obj = json_to_text(file=fpath)
            assert 'morph_analysis' not in text_obj.layers
            start_time = datetime.now()
            morph_tagger2.tag( text_obj )
            time_deltas.append( datetime.now() - start_time )
            assert 'morph_analysis' in text_obj.layers
            word_count += len(text_obj['words'])
            text_count += 1
        #if fid > 50:
        #    break
    [time_delta_sum, total_sec, secs_per_text_delta, words_per_second] = \
                     summarize_times_and_find_speed( time_deltas, word_count )
    collected_total_secs.append( total_sec )
    collected_words_per_second.append( words_per_second )
    collected_seconds_per_text.append( secs_per_text_delta.total_seconds() )

total_end_time = datetime.now() - total_start_time
report_statistics(total_end_time,iterations,text_count,word_count,collected_total_secs,
                                                                  collected_seconds_per_text,
                                                                  collected_words_per_second)

print()
print('  All experiments total time: {}'.format(datetime.now() - all_experiments_start_time))
