# -*- coding: utf-8 -*-
import unittest

from estnltk import Text
from estnltk.names import START, END
from estnltk.taggers import EventTagger


class EventTaggerTest(unittest.TestCase):
    
    def test_resolve_conflicts_MAX(self):
        event_tagger = EventTagger([], conflict_resolving_strategy='MAX')
        # empty list
        events = []
        result = event_tagger._resolve_conflicts(events)
        expected = []
        self.assertListEqual(expected, result)

        # one event
        events = [{START: 1, END:  4}]
        result = event_tagger._resolve_conflicts(events)
        expected = [{START: 1, END:  4}]
        self.assertListEqual(expected, result)

        # equal events
        events = [{START: 1, END:  4},
                  {START: 1, END:  4}]
        result = event_tagger._resolve_conflicts(events)
        expected = [{START: 1, END:  4}]
        self.assertListEqual(expected, result)

        # common start
        events = [{START: 1, END:  4},
                  {START: 1, END:  6}]
        result = event_tagger._resolve_conflicts(events)
        expected = [{START: 1, END:  6}]
        self.assertListEqual(expected, result)

        # common end
        events = [{START: 3, END:  6},
                  {START: 1, END:  6}]
        result = event_tagger._resolve_conflicts(events)
        expected = [{START: 1, END:  6}]
        self.assertListEqual(expected, result)

        # complex
        events = [{START: 1, END:  8},
                  {START: 2, END:  4},
                  {START: 3, END:  6}]
        result = event_tagger._resolve_conflicts(events)
        expected = [{START: 1, END:  8}]
        self.assertListEqual(expected, result)        

    def test_resolve_conflicts_MIN(self):
        event_tagger = EventTagger([], conflict_resolving_strategy='MIN')
        # empty list
        events = []
        result = event_tagger._resolve_conflicts(events)
        expected = []
        self.assertListEqual(expected, result)

        # one event
        events = [{START: 1, END:  4}]
        result = event_tagger._resolve_conflicts(events)
        expected = [{START: 1, END:  4}]
        self.assertListEqual(expected, result)

        # equal events
        events = [{START: 1, END:  4},
                  {START: 1, END:  4}]
        result = event_tagger._resolve_conflicts(events)
        expected = [{START: 1, END:  4}]
        self.assertListEqual(expected, result)

        # common start
        events = [{START: 1, END:  4},
                  {START: 1, END:  6}]
        result = event_tagger._resolve_conflicts(events)
        expected = [{START: 1, END:  4}]
        self.assertListEqual(expected, result)

        # common end
        events = [{START: 3, END:  6},
                  {START: 1, END:  6}]
        result = event_tagger._resolve_conflicts(events)
        expected = [{START: 3, END:  6}]
        self.assertListEqual(expected, result)

        # complex
        events = [{START: 1, END:  8},
                  {START: 2, END:  4},
                  {START: 3, END:  6}]
        result = event_tagger._resolve_conflicts(events)
        expected = [{START: 2, END:  4},
                    {START: 3, END:  6}]
        self.assertListEqual(expected, result)        

    def test_resolve_conflicts_ALL(self):
        event_tagger = EventTagger([], conflict_resolving_strategy='ALL')
        # complex
        events = [{START: 1, END:  8},
                  {START: 2, END:  4},
                  {START: 3, END:  6}]
        result = event_tagger._resolve_conflicts(events)
        expected = [{START: 1, END:  8},
                    {START: 2, END:  4},
                    {START: 3, END:  6}]
        self.assertListEqual(expected, result)        

    def test_event_tagger_tag_events(self):
        event_vocabulary = [{'term': 'Harv', 'type': 'sagedus'}, 
                            {'term': 'peavalu', 'type': 'sümptom'}]
        text = Text('Harva esineb peavalu.')
        event_tagger = EventTagger(event_vocabulary, return_layer=True)
        result = event_tagger.tag(text)
        expected = [{'term':    'Harv', 'type': 'sagedus', 'start':  0, 'end':  4, 'wstart_raw': 0, 'wend_raw': 1, 'cstart':  0, 'wstart': 0}, 
                    {'term': 'peavalu', 'type': 'sümptom', 'start': 13, 'end': 20, 'wstart_raw': 2, 'wend_raw': 3, 'cstart': 10, 'wstart': 2}]
        self.assertListEqual(expected, result)


    def test_event_tagger_sort_events(self):
        event_vocabulary = [{'term': 'neli'}, 
                            {'term': 'kolm neli'},
                            {'term': 'kaks kolm'},
                            {'term': 'kaks kolm neli'}]
        text = Text('Üks kaks kolm neli.')
        event_tagger = EventTagger(event_vocabulary, 'naive', 
                                   case_sensitive=True,
                                   conflict_resolving_strategy='ALL', 
                                   return_layer=True)
        result = event_tagger.tag(text)
        expected = [{'term': 'kaks kolm',      'start':  4, 'end': 13, 'wstart_raw': 1, 'wend_raw': 3},
                    {'term': 'kaks kolm neli', 'start':  4, 'end': 18, 'wstart_raw': 1, 'wend_raw': 4},
                    {'term': 'kolm neli',      'start':  9, 'end': 18, 'wstart_raw': 2, 'wend_raw': 4},
                    {'term': 'neli',           'start': 14, 'end': 18, 'wstart_raw': 3, 'wend_raw': 4}]

        self.assertListEqual(expected, result)
        
    def test_event_tagger_naive_equals_ahocorasick(self):
        event_vocabulary = [{'term': 'üks'},
                            {'term': 'kaks'},
                            {'term': 'kaks kolm'},
                            {'term': 's k'}]
        text = """kolm kaks kaks kaks kolm kaks viis kolm neli kolm üks neli kaks neli 
        kaks kaks üks üks neli kolm viis kolm üks kaks kaks kolm kolm üks viis neli"""
        
        event_tagger = EventTagger(event_vocabulary, 'naive', 
                                   case_sensitive=True,
                                   conflict_resolving_strategy='ALL', 
                                   return_layer=True)
        
        naive = event_tagger._find_events_naive(text)
        ahocorasick = event_tagger._find_events_ahocorasick(text)
        
        naive.sort(key=lambda event: event['end'])
        naive.sort(key=lambda event: event['start'])
        
        ahocorasick.sort(key=lambda event: event['end'])
        ahocorasick.sort(key=lambda event: event['start'])
        
        self.assertListEqual(naive, ahocorasick)

    def test_event_tagger_case_insensitive(self):
        event_vocabulary = [{'term': u'üKs'},
                            {'term': 'KaKs'}]
        text = Text(u'ÜkS kAkS üks KAKS.')
        event_tagger = EventTagger(event_vocabulary, 
                                   case_sensitive=False,
                                   conflict_resolving_strategy='ALL', 
                                   return_layer=True)
        result = event_tagger.tag(text)
        expected = [{'term': u'üKs',  'start':  0, 'end':  3, 'wstart_raw': 0, 'wend_raw': 1, 'cstart':  0, 'wstart': 0},
                    {'term': 'KaKs', 'start':  4, 'end':  8, 'wstart_raw': 1, 'wend_raw': 2, 'cstart':  2, 'wstart': 1},
                    {'term': u'üKs',  'start':  9, 'end': 12, 'wstart_raw': 2, 'wend_raw': 3, 'cstart':  4, 'wstart': 2},
                    {'term': 'KaKs', 'start': 13, 'end': 17, 'wstart_raw': 3, 'wend_raw': 4, 'cstart':  6, 'wstart': 3}]

        self.assertListEqual(expected, result)
