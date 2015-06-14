#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

"""
Module for manipulating EuroWordNet data.

All strings should be Unicode.

Output may be whatever encoding, default is utf-8

Every "higher" class should call "lower" class polarisText property
for compiling its own polarisText

__version__ = "1.%s" % filter_containing(str.isdigit, "$Revision: 418 $")
__date__ = "$Date: 2014-04-08 11:56:16 +0300 (T, 08 apr   2014) $"[6:-2]

__author__ = "Neeme Kahusk"
__copyright__ = "Copyright 2011-2014, Neeme Kahusk"
__credits__ = ["Neeme Kahusk","EKT projekt"]

__license__ = "GPL"

__maintainer__ = "Neeme Kahusk"
__email__ = "neeme.kahusk@ut.ee"
__status__ = "Development" # one of: "Development" or "Production" or "Prototype"


"""

import sys
import os.path
import codecs
import re
import six

from estnltk.core import as_unicode

POSES = ['a','b','v','n','pn'] # for eurowordnet only

LINEBREAK = '\n\n'

INTERNAL_RELATION_FILE = os.path.join(os.path.dirname(__file__ ), 'semrel.cnf')
EXTERNAL_RELATION_FILE = os.path.join(os.path.dirname(__file__ ), 'eqsemrel.cnf')


f = open(INTERNAL_RELATION_FILE, 'rb')
INTERNAL_RELATION_NAMES = list(map(lambda x: x.strip(),f.readlines()))
f.close()

f = open(EXTERNAL_RELATION_FILE, 'rb')
EQ_RELATION_NAMES = list(map(lambda x: x.strip(),f.readlines()))
f.close()


RELATION_NAMES = INTERNAL_RELATION_NAMES + EQ_RELATION_NAMES


def raiseTypeError(obj, caller, what):
    raise TypeError(
        "%s's object property %s should be %s" % \
            (obj, caller, what)
        )


class _TypedList(list):
    '''Accepts members of certain type.
    For subclassing.

    Provides property polarisText
    for _TypedList objects.
    '''
    def __init__(self, *args):
        super(list,self).__init__(*args)
        self.memberType = type(None)
        self.parent = (1, 'TEST')

    def insert(self, i, x):
        if isinstance(x, self.memberType):
            return list.insert(self, i, x)
        else:
            raise TypeError("Wrong list member")

    def append(self, x):
        if isinstance(x,self.memberType):
            return list.append(self, x)
        else:
            raise TypeError("Wrong list member")

    def __setitem__(self, i, x):
        if isinstance(x, self.memberType):
            return list.__setitem__(self, i, x)
        else:
            raise TypeError("Wrong list member")

    def polarisText():
        """polarisText part of _TypedList objects

        """
        def fget(self):
            _out = ''
            _n = '\n'
            if len(self):
                if self.parent:
                    _out = '%s%s%s' % (_out, PolarisText(
                            *self.parent).out,_n)
                _out = _out + _n.join(
                    map(lambda x: x.polarisText,
                        self)
                    )
            else:
                _out = ''
            return _out
        return locals()

    polarisText = property(**polarisText())


class Relation(object):
    """ Relation class. 
    Links current concept to another concept (in the same wordnet).

    has properties:
    name (string) - relation name (e.g. 'has_hyperonym')

    target_concept (Synset or WordInstance) - the concept 
    to which the current concept is linked to.

    features (Features) - features of the Relation

    source_ids (Source_Ids) - a list which members belong to 
    Relation_Source_Id class. (obs)

    source_id (Source_Id) - 

    """
    def __init__(self, name=None, target_concept=None,
                 source_ids=None,
                 source_id=None,
                 features=None):
        self._name = name or ''
        self._target_concept = target_concept or None
        self._features = features or Features()

        self._source_ids = source_ids or Source_Ids()
        self._source_id = source_id or 0

    def name():
        doc = "Relation's name. String"
        def fget(self):
            return self._name
        def fset(self, value):
            if isinstance(value, six.text_type): # must be string
                self._name = value
            else:
                raise TypeError(
                    "Relation's object property 'name' must be unicode")
        def fdel(self):
            self._name = None
        return locals()

    name = property(**name())

    def source_id():
        doc = "Relation's source_id. Int"
        def fget(self):
            return self._source_id
        def fset(self, value):
            if isinstance(value, int): # must be int
                self._source_id = value
            else:
                raise TypeError(
                    "Relation's object property 'source_id' must be int")
        def fdel(self):
            self._source_id = None
        return locals()

    source_id = property(**source_id())

    def target_concept():
        doc = "Relation's target_concept. Synset or WordInstance"
        def fget(self):
            return self._target_concept
        def fset(self, value):
            if isinstance(value, Synset): # must be synset
                self._target_concept = value
            else:
                raise TypeError(
                    "Relation's object property 'target_concept' must be Synset")
        def fdel(self):
            self._target_concept = None
        return locals()

    target_concept = property(**target_concept())

    def source_ids():
        doc = "ExternalInfo sourceIDs Source_Ids"
        def fget(self):
            return self._source_ids
        def fset(self, value):
            if isinstance(value, Source_Ids):  # Must be Source_Ids
                self._source_ids = value
            else:
                raise TypeError(
                    "ExternalInfo's object attribute 'source_ids' must be Source_Ids")
        def fdel(self):
            self._source_ids = None

        return locals()

    source_ids = property(**source_ids())

    def features():
        doc = "Relation's features, Features"
        def fget(self):
            return self._features
        def fset(self, value):
            if isinstance(value, Features): 
                self._features = value
            else:
                raise TypeError(
                    "Relation's object property 'features' must be Features")
            self._features = value
        def fdel(self):
            self._features = None
        return locals()
    
    features = property(**features())

    def addFeature(self, feature):
        '''Appends Feature'''
        
        if isinstance(feature, Feature):
            self.features.append(feature)
        else:
            raise TypeError(
                'feature Type should be Feature, not %s' % type(feature))

    def polarisText():
        def fget(self):
            _out = ''
            _n = '\n'
            _outList = []
            _outList.append(PolarisText(2,'RELATION',None,self.name).out)
            if self.target_concept:
                _outList.append(PolarisText(3,'TARGET_CONCEPT').out)
                _outList.append(
                    PolarisText(4,
                                'PART_OF_SPEECH',
                                None,self.target_concept.pos).out)
                _outList.append(
                    PolarisText(4,
                                'LITERAL',
                                None,
                                self.target_concept.firstVariant.literal
                                ).out)
                _outList.append(
                    PolarisText(5,
                                'SENSE',
                                None,
                                self.target_concept.firstVariant.sense
                                ).out)
            if self.features:
                _outList.append(self.features.polarisText)                
            if self.source_ids:
                _outList.append(self.source_ids.polarisText)
            if self.source_id:
                _outList.append(
                    PolarisText(3,
                                'SOURCE_ID',
                                None,
                                self.source_id).out)
            
            _out = _out + _n.join(_outList)
            return _out
        return locals()
  
    polarisText = property(**polarisText())
# === class Relation(object) === end


class Source_Id(object):
    """TODO

    """
    def __init__(self, number=None, text_key=None, number_key=None):
        self._number = number or None
        self._text_key = text_key or None
        self._number_key = number_key or None

    def number():
        doc = "Relation's number. Integer"
        def fget(self):
            return self._number
        def fset(self, value):
            if isinstance(value, int): # must be int
                self._number = value
            else:
                raise TypeError(
                    "Relation's object property 'number' must be int")
        def fdel(self):
            self._number = None
        return locals()

    number = property(**number())

    def text_key():
        doc = "Relation's text_key. String"
        def fget(self):
            return self._text_key
        def fset(self, value):
            if isinstance(value, six.string_types): # must be string
                self._text_key = value
            else:
                raise TypeError(
                    "Relation's object property 'text_key' must be string")
        def fdel(self):
            self._text_key = None
        return locals()

    text_key = property(**text_key())

    def number_key():
        doc = "Relation's number_key. Integer"
        def fget(self):
            return self._number_key
        def fset(self, value):
            if isinstance(value, int): # must be int
                self._number_key = value
            else:
                raise TypeError(
                    "Relation's object property 'number_key' must be integer")
        def fdel(self):
            self._number_key = None
        return locals()

    number_key = property(**number_key())

    def polarisText():
        def fget(self):
            _out = ''
            _n = '\n'
            _outList = []
            _outList.append(PolarisText(4,'SOURCE_ID',None,self.number).out)
            if self.text_key:
                _outList.append(
                    PolarisText(5,'TEXT_KEY',None,self.text_key).out)
            if self.number_key:
                _outList.append(
                    PolarisText(5,'NUMBER_KEY',None,self.number_key).out)
            _out = _out + _n.join(_outList)
            return _out
        return locals()
  
    polarisText = property(**polarisText())
# CLASS SOURCE_ID END


class Corpus_Id(object):
    """TODO

    """
    def __init__(self, number=None, 
                 frequency=None):
        self._number = number or None
        self._frequency = frequency or None

    def number():
        doc = "Relation's number. String"
        def fget(self):
            return self._number
        def fset(self, value):
            if isinstance(value, int): # must be int
                self._number = value
            else:
                raise TypeError(
                    "Relation's object property 'number' must be int")
        def fdel(self):
            self._number = None
        return locals()

    number = property(**number())

    def frequency():
        doc = "Relation's frequency. Int"
        def fget(self):
            return self._frequency
        def fset(self, value):
            if isinstance(value, int): # must be int
                self._frequency = value
            else:
                raise TypeError(
                    "Relation's object property 'frequency' must be int")
        def fdel(self):
            self._frequency = None
        return locals()

    frequency = property(**frequency())

    def polarisText():
        def fget(self):
            _out = ''
            _n = '\n'
            _outList = []
            _outList.append(PolarisText(4,'CORPUS_ID',None,self.number).out)
            if self.frequency or self.frequency == 0:
                _outList.append(
                    PolarisText(5,'FREQUENCY',None,self.frequency).out)
            _out = _out + _n.join(_outList)
            return _out
        return locals()
  
    polarisText = property(**polarisText())
# CLASS CORPUS_ID END


class Relation_Source_Id(Source_Id):
    def __init__(self, number=0):
        super(Source_Id,self).__init__()
        self._number = number

    def polarisText():
        def fget(self):
            _out = ''
            _n = '\n'
            _outList = []
            _outList.append(PolarisText(3,'SOURCE_ID',None,self.number).out)
            
            _out = _out + _n.join(_outList)
            return _out
        return locals()
  
    polarisText = property(**polarisText())


class FieldValue(six.text_type):
    """FieldValue class for subclassing
    single value per line 

    """
    def __init__(self, *args,**kwargs):
        """
        *args and **kwargs are needed
        to avoid 
        TypeError: __init__() takes exactly 1 argument (2 given)
        The same for subclassing this class.

        (See class Example)

        """
        super(unicode,self).__init__(*args,**kwargs)
        self.level = 0
        self.field = ''

    def polarisText():
        """
        The polarisText property of the FieldValue
        class outputs each property in form
        <level> <field> <self=field value> 

        """
        def fget(self):
            _out = ''
            _n = '\n'
            _outList = []
            _outList.append(PolarisText(self.level,self.field,None,self).out)
            
            _out = _out + _n.join(_outList)
            return _out
        return locals()
  
    polarisText = property(**polarisText())


class Example(FieldValue):
    """Example class.

    """
    def __init__(self, *args,**kwargs):
        super(FieldValue,self).__init__()
        self.level = 4
        self.field = 'EXAMPLE'


class Property(six.text_type):
    """Property class
    """
    def polarisText():
        """
        The polarisText property of the Property
        class outputs each property in form
        2 NAME "<property>"

        """
        def fget(self):
            _out = ''
            _n = '\n'
            _outList = []
            _outList.append(PolarisText(2,'NAME',None,self).out)
            
            _out = _out + _n.join(_outList)
            return _out
        return locals()
  
    polarisText = property(**polarisText())


class PropertyValue(object):
    """Property values.
    """
    def __init__(self,name=None,value=None):
        self._name = name or None
        self._value = value or None

    def name():
        doc = "Property name. Unicode"
        def fget(self):
            return self._name
        def fset(self, value):
            if isinstance(value, six.text_type):
                self._name = value
            else:
                raise TypeError(
                    "Relation's object property 'name' must be Synset")
        def fdel(self):
            self._name = None
        return locals()

    name = property(**name())

    def value():
        doc = "Value. Unicode"
        def fget(self):
            return self._value
        def fset(self, avalue):
            if isinstance(avalue, (six.text_type)):
                self._value = avalue
            else:
                raise TypeError(
                    "Relation's object property 'value' must be unicode")
        def fdel(self):
            self._value = None
        return locals()

    value = property(**value())

    def polarisText():
        def fget(self):
            _out = ''
            _n = '\n'
            _outList = []
            _outList.append(PolarisText(2,'NAME',None,self.name).out)
            if isinstance(self.value,Synset):
                _outList.append(
                    PolarisText(
                        3, 'VALUE_AS_WORD_MEANING').out)
                _outList.append(
                    PolarisText(
                        4,
                        'PART_OF_SPEECH',
                        None,self.value.pos).out)
                _outList.append(
                    PolarisText(
                        4,
                        'LITERAL',
                        None,
                        self.value.firstVariant.literal).out)
                _outList.append(
                    PolarisText(
                        5,
                        'SENSE',
                        None,
                        self.value.firstVariant.sense).out)
            elif isinstance(self.value, six.text_type):
                _outList.append(
                    PolarisText(
                        3,
                        'VALUE_AS_TEXT',
                        None,self.value).out)
            elif isinstance(self.value,int):
                _outList.append(
                PolarisText(3,'VALUE',
                            None,self.value).out)
                
            _out = _out + _n.join(_outList)
            return _out
        return locals()
  
    polarisText = property(**polarisText())


class EqLink(Relation):
    """Interlingual Eqivalence links

    """
    def __init__(self, **args):
        super(Relation,self).__init__()
        try:
            self._name = args['name'] or ''
        except KeyError:
            self._name = ''
        try:
            self._target_concept = args['target_concept']
        except KeyError:
            self._target_concept = None
        try:
            self._features = args['features']
        except KeyError:
            self._features = []
        try:
            self._source_ids = args['source_ids']
        except KeyError:
            self._source_ids = Source_Ids()
        try:
            self._source_id = args['source_id']
        except KeyError:
            self._source_id = 0

    def target_concept():
        doc = "Relation's target_concept. Synset, tuple or int"
        def fget(self):
            return self._target_concept
        def fset(self, value):
            if isinstance(value, (Synset,tuple,int)):
                self._target_concept = value
            else:
                raise TypeError(
                    "Relation's object property 'target_concept' must be Synset, tuple or int")
        def fdel(self):
            self._target_concept = None
        return locals()

    target_concept = property(**target_concept())

    def polarisText():
        def fget(self):
            _out = ''
            _n = '\n'
            _outList = []
            _outList.append(PolarisText(2,'EQ_RELATION',None,self.name).out)
            if self.target_concept and (
                not isinstance(self.target_concept,int)):
                _outList.append(
                    PolarisText(3,'TARGET_ILI').out)
                if isinstance(self.target_concept,Synset):
                    _outList.append(
                        PolarisText(
                            4,
                            'PART_OF_SPEECH',
                            None,self.target_concept.pos).out)
                    if self.target_concept.variants:
                        _outList.append(
                            PolarisText(
                                4,
                                'LITERAL',
                                None,
                                self.target_concept.firstVariant.literal).out)
                        _outList.append(
                            PolarisText(
                                5,
                                'SENSE',
                                None,
                            self.target_concept.firstVariant.sense).out)
                    elif self.target_concept.add_on_id:
                        _outList.append(
                            PolarisText(
                                4,
                                'ADD_ON_ID',
                                None,
                                self.target_concept.add_on_id).out)
                    elif self.target_concept.wordnet_offset:
                        _outList.append(
                            PolarisText(
                                4,
                                'WORDNET_OFFSET',
                                None,
                                self.target_concept.wordnet_offset).out)
                elif isinstance(self.target_concept, type(tuple)):
                    _outList.append(
                        PolarisText(
                            4,
                            'PART_OF_SPEECH',
                            None,self.target_concept[0]).out)
                    _outList.append(
                        PolarisText(
                            4,
                            'FILE_OFFSET',
                            None,
                            self.target_concept[1]).out)
                    
            elif self.target_concept and (isinstance(self.target_concept,int)):
                _outList.append(
                    PolarisText(3,'TARGET_ILI',
                                None,
                                '@%d@' % self.target_concept,True).out)

            if self.source_ids:
                _outList.append(self.source_ids.polarisText)

            if self.source_id:
                _outList.append(
                    PolarisText(3,
                                'SOURCE_ID',
                                None,
                                self.source_id).out)
            _out = _out + _n.join(_outList)
            return _out
        return locals()
  
    polarisText = property(**polarisText())


class External_Info(object):
    """Needs reviewing!!!
    TODO: text_key and number_key not needed
    """
    def __init__(self,
                 yes=False,
                 source_ids=None,
                 corpus_ids=None,
                 frequency=None,
                 textKey=None,
                 numberKey=None
                 ):

        self.yes = yes or False
        self._source_ids = source_ids or Source_Ids()
        self._corpus_ids = corpus_ids or Corpus_Ids()
        self._frequency = frequency or None
        self._textKey = textKey or None
        self._numberKey = numberKey or None

    def source_ids():
        doc = "ExternalInfo sourceIDs Source_Ids"
        def fget(self):
            return self._source_ids
        def fset(self, value):
            if isinstance(value, Source_Ids):  # Must be Source_Ids
                self._source_ids = value
            else:
                raise TypeError(
                    "ExternalInfo's object attribute 'source_ids' must be Source_Ids")
        def fdel(self):
            self._source_ids = None

        return locals()

    source_ids = property(**source_ids())

    def corpus_ids():
        doc = "ExternalInfo corpusID number. Integer"
        def fget(self):
            return self._corpus_ids
        def fset(self, value):
            if isinstance(value, list):  # Must be list
                self._corpus_ids = value
            else:
                raise TypeError(
                    "ExternalInfo's object attribute 'corpus_ids' must be list")
        def fdel(self):
            self._corpus_ids = None
        return locals()

    corpus_ids = property(**corpus_ids())

    def textKey():
        doc = "ExternalInfo textKey."
        def fget(self):
            return self._textKey
        def fset(self, value):
            if isinstance(value, six.string_types):  # Must be string
                self._textKey = value
            else:
                raise TypeError(
                    "ExternalInfo's object attribute 'textKey' must be string")
        def fdel(self):
            self._textKey = None
        return locals()

    textKey = property(**textKey())

    def numberKey():
        doc = "ExternalInfo numberKey."
        def fget(self):
            return self._numberKey
        def fset(self, value):
            if isinstance(value, int):  # Must be number
                self._numberKey = value
            else:
                raise TypeError(
                    "ExternalInfo's object attribute 'numberKey' must be number")
        def fdel(self):
            self._numberKey = None
        return locals()

    numberKey = property(**numberKey())

    def frequency():
        doc = "ExternalInfo frequency."
        def fget(self):
            return self._frequency
        def fset(self, value):
            if isinstance(value, int):  # Must be number
                self._frequency = value
            else:
                raise TypeError(
                    "ExternalInfo's object attribute 'frequency' must be number")
        def fdel(self):
            self._frequency = None
        return locals()

    frequency = property(**frequency())

    def addSourceId(self, value):
        '''Adds SourceId to External_Info
        '''
        if isinstance(value, Source_Id):
            self.source_ids.append(value)
        else:
            raise (TypeError,
                   'source_id Type should be Source_Id, not %s' % type(source_id))
    def addCorpusId(self, value):
        '''Adds SourceId to External_Info
        '''
        if isinstance(value, Corpus_Id):
            self.corpus_ids.append(value)
        else:
            raise (TypeError,
                   'source_id Type should be Source_Id, not %s' % type(source_id))

    def polarisText():
        def fget(self):
            _out = ''
            _n = '\n'
            _outList = []
            _outList.append(PolarisText(3,'EXTERNAL_INFO').out)

            if self.corpus_ids:
                _outList.append(self.corpus_ids.polarisText)

            if self.source_ids:
                _outList.append(self.source_ids.polarisText)

            _out = _out + _n.join(_outList)
            return _out
        return locals()
  
    polarisText = property(**polarisText())


class Feature(object):
    """Feature class.

    """
    def __init__(self, name=None,
                 featureValue=None):
        self._name = name or ''
        self._featureValue = featureValue or None

    def name():
        doc = "Feature name. Base string."
        def fget(self):
            return self._name
        def fset(self, value):
            if isinstance(value, six.string_types):  
                self._name = value
            else:
                raise TypeError(
                    "Feature's object attribute 'name' must be six.string_types")
        def fdel(self):
            self._name = None
        return locals()

    name = property(**name())

    def featureValue():
        doc = "Feature featureValue."
        def fget(self):
            return self._featureValue
        def fset(self, value):
            if isinstance(value, (bool, int, tuple, six.text_type)):  
                self._featureValue = value
            else:
                raise TypeError(
                    "Feature's object attribute 'featureValue' must be bool, int or tuple or unicode")
        def fdel(self):
            self._featureValue = None
        return locals()

    featureValue = property(**featureValue())

    def polarisText():
        def fget(self):
            _out = ''
            _n = '\n'
            _outList = []
            if self.name:
                if isinstance(self.featureValue, bool):
                    if self.name == 'factive':
                        if self.featureValue == True:
                            _outList.append(PolarisText(4,'FACTIVE').out)
                        else:
                            _outList.append(PolarisText(4,'NON_FACTIVE').out)
                    else:
                        _outList.append(PolarisText(4,self.name.upper()).out)

                elif isinstance(self.featureValue, int):
                    _outList.append(PolarisText(
                            4,self.name.upper(),None,self.featureValue).out)
                elif isinstance(self.featureValue, tuple):
                    _outList.append(PolarisText(4,'VARIANT_TO_VARIANT').out)
                    _outList.append(PolarisText(
                            5,'SOURCE_VARIANT',None,self.featureValue[0]).out)
                    _outList.append(PolarisText(
                            5,'TARGET_VARIANT',None,self.featureValue[1]).out)

                elif isinstance(self.featureValue, six.string_types):
                    _outList.append(PolarisText(
                            4,'FEATURE',None,self.name).out)

                    _outList.append(PolarisText(
                            5,'FEATURE_VALUE',None,self.featureValue).out)

            _out = _out + _n.join(_outList)
            return _out

        return locals()
  
    polarisText = property(**polarisText())


class Usage_Label(object):
    """Usage_Label class.

    """
    def __init__(self, name=None,
                 usage_label_value=None):
        self._name = name or ''
        self._usage_label_value = usage_label_value or ''

    def name():
        doc = "Usage_Label name number. Integer"
        def fget(self):
            return self._name
        def fset(self, value):
            if isinstance(value, six.string_types):  
                self._name = value
            else:
                raise TypeError(
                    "Usage_Label's object attribute 'name' must be six.string_types")
        def fdel(self):
            self._name = None
        return locals()

    name = property(**name())

    def usage_label_value():
        doc = "Usage_Label usage_label_value."
        def fget(self):
            return self._usage_label_value
        def fset(self, value):
            if isinstance(value, six.string_types):  
                self._usage_label_value = value
            else:
                raise TypeError(
                    "Usage_Label's object attribute 'usage_label_value' must be six.string_types")
        def fdel(self):
            self._usage_label_value = None
        return locals()

    usage_label_value = property(**usage_label_value())

    def polarisText():
        def fget(self):
            _out = ''
            _n = '\n'
            _outList = []
            if self.name:
                _outList.append(
                    PolarisText(4,
                                'USAGE_LABEL',
                                None,self.name).out)
            if self.usage_label_value:
                _outList.append(
                    PolarisText(5,
                                'USAGE_LABEL_VALUE',
                                None,self.usage_label_value).out)
                _out = _out + _n.join(_outList)
            return _out
        return locals()
  
    polarisText = property(**polarisText())


class Translation(object):
    """Translation.
    Has language and translation_value
    """

    def __init__(self, language=None,
                 translation_value=None):

        self._language = language or ''
        self._translation_value = translation_value or ''

    def language():
        doc = "Translation language number. Integer"
        def fget(self):
            return self._language
        def fset(self, value):
            if isinstance(value, six.string_types):  
                self._language = value
            else:
                raise TypeError(
                    "Translation's object attribute 'language' must be six.string_types")
        def fdel(self):
            self._language = None
        return locals()

    language = property(**language())

    def translation_value():
        doc = "Translation translation_value."
        def fget(self):
            return self._translation_value
        def fset(self, value):
            if isinstance(value, six.string_types):  
                self._translation_value = value
            else:
                raise TypeError(
                    "Translation's object attribute 'translation_value' must be six.string_types")
        def fdel(self):
            self._translation_value = None
        return locals()

    translation_value = property(**translation_value())

    def polarisText():
        def fget(self):
            _out = ''
            _n = '\n'
            _outList = []
            if self.language and self.translation_value:
                _outList.append(
                    PolarisText(4,
                                'TRANSLATION',
                                None,
                                '%s:%s' % (
                            self.language, self.translation_value)
                                ).out)
                _out = _out + _n.join(_outList)
            return _out

        return locals()
  
    polarisText = property(**polarisText())


class ParseError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class Parser(object):
    """Parser for Polaris import-export files.

    Attributes:
    
    fileName (string) - name of file to parse

    Methods:
    parse_line(<iStr>) - parses one line (iStr)

    parse_synset() - parses synset (WORD_MEANING or 
    WORD_INSTANCE) Returns self.synset (Synset object).

    """
    def __init__(self, fileName=''):
        # self._file = file or None
        self._fileName = fileName or ''
        if self._fileName:
            self.file = open(self._fileName, 'rb')
        else:
            self.file = None

        self.levelNumber = None
        self.DRN = None
        self.fieldTag = None
        self.fieldValue = None
        self.noQuotes = None

        self.milestone = 0
        self.synset = None
        self.target_synset = None
        self.before = None

        self.encoding = 'utf-8'
        # self.encoding = 'latin1'

        self.pn = False
        self.targetType = None
        self.variant_to_variant_source = None
        self.variant_to_variant_target = None

    def fileName():
        doc = "FileName to read from"
        def fget(self):
            return self._fileName
        def fset(self, value):
            self._fileName = value
            self.file = open(self._fileName, 'rb')
        def fdel(self):
            self.file.close()
            self._fileName = None
        return locals()

    fileName = property(**fileName())

    def parse_line(self,iStr):
        """Parses ewn file line
        """
        self.levelNumber = None
        self.DRN = None
        self.fieldTag = None
        self.fieldValue = None
        self.noQuotes = None
        if iStr and not(iStr.strip().startswith('#')):
            iList = iStr.strip().split(' ')
            self.levelNumber = int(iList.pop(0))
            if iList[0].startswith('@') and self.levelNumber != 3:
                self.DRN = int(iList.pop(0).strip('@'))
            else:
                self.DRN = None
            self.fieldTag = iList.pop(0)
            if iList and (
                iList[0].startswith('"') or
                iList[0].startswith('@')
                ):
                fv = ' '.join(iList)
                self.fieldValue = fv[1:-1]
            elif iList:
                if len(iList) == 1:
                    self.fieldValue = iList.pop(0)
                else:
                    self.fieldValue = ' '.join(iList)
                try:
                    self.fieldValue = int(self.fieldValue)
                except ValueError:
                    self.noQuotes = True

    def parse_synset(self, offset=None, debug=False):
        """Parses Synset from file
        """
        if False:
            pass
        else:
            # WORD_INSTANCE
            def _word_instance():
                _synset(True)

            # WORD_MEANING
            def _synset(pn=False):
                if not pn:
                    self.synset = Synset()
                    self.pn = False
                else:
                    self.synset = WordInstance()
                    self.pn = True
                if self.DRN:
                    self.synset.number = self.DRN
                self.targetType = None

            def _variants():
                self.synset.variants = Variants()

            def _literal():
                a = Variant()
                self.synset.variants.append(a)
                self.synset.variants[-1].literal = self.fieldValue

            def _target_literal():
                    self.target_synset.variants.append(Variant())
                    self.target_synset.variants[-1].literal = self.fieldValue

            def _sense():
                self.synset.variants[-1].sense = self.fieldValue

            def _status():
                self.noQuotes = True
                try:
                    self.synset.variants[-1].status = as_unicode(self.fieldValue)
                except:
                    self.synset.variants[-1].status = as_unicode(str(self.fieldValue))
                self.noQuotes = False

            def _target_sense():
                self.target_synset.variants[-1].sense = self.fieldValue
                if self.targetType == 'internal':
                    self.synset.internalLinks[
                        -1].target_concept = self.target_synset
                elif self.targetType == 'ili':
                    self.synset.eqLinks[-1].target_concept = self.target_synset
                elif self.targetType == 'pv':
                    self.synset.propertyValues[-1].value = self.target_synset
                else:
                    print ('BOOOOOOOOO!!') # Error TODO

            def _gloss():
                self.synset.variants[-1].gloss = self.fieldValue
                self.synset.definition = self.fieldValue                            # ADDED BY KOM

            def _translations():
                self.synset.variants[-1].translations = Translations()

            def _translation():
                self.synset.variants[-1].translations.append(
                    Translation(
                        language=self.fieldValue.split(':')[0],
                        translation_value = self.fieldValue.split(':')[1])
                    )

            def _examples():
                self.synset.variants[-1].examples = Examples()
            def _usage_labels():
                self.synset.variants[-1].usage_labels = Usage_Labels()

            def _external_info():
                self.synset.variants[-1].externalInfo = External_Info()

            def _example():
                self.synset.variants[-1].examples.append(
                    Example(self.fieldValue)
                    )

            def _usage_label():
                self.synset.variants[
                    -1].usage_labels.append(
                    Usage_Label(name=self.fieldValue)
                    )

            def _usage_label_value():
                self.synset.variants[
                    -1].usage_labels[-1].usage_label_value = self.fieldValue

            def _source_id():
                if self.targetType == 'internal':
                    self.synset.internalLinks[-1].source_id = self.fieldValue
                    # self.synset.internalLinks[-1].source_ids.append(
                    #     Relation_Source_Id(number=self.fieldValue))
                elif self.targetType == 'ili':
                    self.synset.eqLinks[-1].source_id = self.fieldValue
                    # self.synset.eqLinks[-1].source_ids.append(
                    #     Relation_Source_Id(number=self.fieldValue))

                else:
                    if self.synset.variants[-1].external_info:
                        self.synset.variants[
                            -1].external_info.source_ids.append(
                            Source_Id(number=self.fieldValue)
                            )
                    else:
                        self.synset.variants[-1].external_info = External_Info()
                        self.synset.variants[
                            -1].external_info.source_ids.append(
                            Source_Id(number=self.fieldValue)
                            )

            def _corpus_id():
                if self.targetType == 'internal': # not needed
                    self.synset.internalLinks[-1].corpus_ids.append(
                        Relation_Corpus_Id(number=self.fieldValue))
                else:
                    if self.synset.variants[-1].external_info:
                        self.synset.variants[
                            -1].external_info.corpus_ids.append(
                            Corpus_Id(number=self.fieldValue)
                            )
                    else:
                        self.synset.variants[-1].external_info = External_Info()
                        self.synset.variants[
                            -1].external_info.corpus_ids.append(
                            Corpus_Id(number=self.fieldValue)
                            )

            def _frequency():
                self.synset.variants[
                    -1].external_info.corpus_ids[-1].frequency = self.fieldValue

            def _text_key():
                self.synset.variants[
                    -1].external_info.source_ids[-1].text_key = self.fieldValue

            def _number_key():
                self.synset.variants[
                    -1].external_info.source_ids[
                    -1].number_key = self.fieldValue
            def _pos():
                self.synset.pos = self.fieldValue

            # INTERNAL_LINKS
            def _target_concept():
                self.target_synset = Synset()
                self.target_synset.variants = Variants()
                if self.levelNumber == 3: # and self.fieldValue:
                    self.target_synset.number = int(self.fieldValue or 0)

            def _target_pos():
                self.target_synset.pos = self.fieldValue

            def _internal_links():
                self.synset.internalLinks = InternalLinks()
                self.targetType = 'internal'

            def _relation():
                if self.targetType == 'internal':
                    self.synset.internalLinks.append(Relation())
                    self.synset.internalLinks[-1].name = self.fieldValue
                elif self.targetType == 'ili':
                    self.synset.eqLinks.append(EqLink())
                    self.synset.eqLinks[-1].name = self.fieldValue
                else:
                    print ('BOOOOOOOOO!!') # Error TODO

            def _features():
                if self.targetType == 'internal':
                    self.synset.internalLinks[-1].features = Features()
                else:
                    self.synset.variants[-1].features = Features()
                    self.synset.variants[-1].features.append(Feature())

            def _feature():
                self.synset.variants[-1].features[-1].name = self.fieldValue

            def _feature_value():
                self.synset.variants[
                    -1].features[-1].featureValue = self.fieldValue

            def _reversed():
                self.synset.internalLinks[-1].features.append(Feature())
                self.synset.internalLinks[-1].features[-1].name = self.fieldTag
                self.synset.internalLinks[-1].features[-1].featureValue = True

            def _variant_to_variant():
                self.synset.internalLinks[-1].features.append(Feature())
                self.synset.internalLinks[-1].features[-1].name = self.fieldTag

            def _source_variant():
                self.variant_to_variant_source = self.fieldValue

            def _target_variant():
                self.variant_to_variant_target = self.fieldValue
                self.synset.internalLinks[
                    -1].features[-1].featureValue = (
                    self.variant_to_variant_source,
                    self.variant_to_variant_target)

            # EQ_LINKS
            def _eq_links():
                self.synset.eqLinks = EqLinks()
                self.targetType = 'ili'

            def _wn_offset():
                self.target_synset.wordnet_offset = self.fieldValue
                self.synset.eqLinks[-1].target_concept = self.target_synset

            def _add_on_id():
                self.target_synset.add_on_id = self.fieldValue
                self.synset.eqLinks[-1].target_concept = self.target_synset

            # PROPERTIES
            def _properties():
                self.synset.properties = Properties()

            def _name():
                if self.pn:
                    self.synset.propertyValues.append(
                        PropertyValue(name=self.fieldValue))
                else:
                    self.synset.properties.append(Property(self.fieldValue))

            # PROPERTY_VALUES
            def _property_values():
                self.synset.propertyValues = PropertyValues()

            def _property_value():
                self.synset.propertyValues[-1].value = self.fieldValue
                self.targetType = 'pv'

            def _property_wm():
                pass

            rulez = {
                (0,'WORD_MEANING'): _synset,
                (0,'WORD_INSTANCE'): _word_instance,
                (1,'PART_OF_SPEECH'): _pos,
                (1,'VARIANTS'): _variants,
                (2,'LITERAL'): _literal,
                (3,'SENSE'): _sense,
                (3,'STATUS'): _status,
                (3,'DEFINITION'): _gloss,
                (3,'EXAMPLES'): _examples,
                (3,'USAGE_LABELS'): _usage_labels,
                (4,'USAGE_LABEL'): _usage_label,
                (5,'USAGE_LABEL_VALUE'): _usage_label_value,
                (4,'EXAMPLE'): _example,
                (3,'TRANSLATIONS'): _translations,
                (4,'TRANSLATION'): _translation,
                (3,'EXTERNAL_INFO'): _external_info,
                (4,'SOURCE_ID'): _source_id,
                (4,'CORPUS_ID'): _corpus_id,
                (5,'FREQUENCY'): _frequency,
                (5,'TEXT_KEY'): _text_key,
                (5,'NUMBER_KEY'): _number_key,
                (1,'INTERNAL_LINKS'): _internal_links,
                (2,'RELATION'): _relation,
                (3,'TARGET_CONCEPT'): _target_concept,
                (4,'PART_OF_SPEECH'): _target_pos,
                (4,'LITERAL'): _target_literal,
                (5,'SENSE'): _target_sense,
                (3,'FEATURES'): _features,
                (4,'FEATURE'): _feature,
                (5,'FEATURE_VALUE'): _feature_value,
                (4,'REVERSED'): _reversed,
                (4,'VARIANT_TO_VARIANT'): _variant_to_variant,
                (5,'SOURCE_VARIANT'): _source_variant,
                (5,'TARGET_VARIANT'): _target_variant,
                (3,'SOURCE_ID'): _source_id,
                (1,'EQ_LINKS'): _eq_links,
                (2,'EQ_RELATION'): _relation,
                (3,'TARGET_ILI'): _target_concept,
                (4,'WORDNET_OFFSET'): _wn_offset,
                (4,'ADD_ON_ID'): _add_on_id,
                (1,'PROPERTIES'): _properties,
                (1,'PROPERTY_VALUES'): _property_values,
                (2,'NAME'): _name,
                (3,'VALUE'): _property_value,
                (3,'VALUE_AS_TEXT'): _property_value,
                (3,'VALUE_AS_WORD_MEANING'): _target_concept,
                }

            if not offset:
                offset = self.milestone
            else:
                self.milestone=offset
            if self.file:
                self.file.seek(offset,0)

            line = 'X'
            ili = False
            var = False
            while line.strip():

                offset = self.file.tell()
                self.file.seek(offset,0)

                line = as_unicode(self.file.readline(), self.encoding).strip()
                if debug:
                    print (line.encode('utf-8'))


                self.parse_line(line)
                self.noQuotes = None

                select = (self.levelNumber,self.fieldTag)

                if select in rulez.keys():
                    rulez[select]()
                else:
                    if line:
                        print (self.synset.polarisText)
                        raise ParseError("No parsing rule for '%s'" % line)
        return self.synset

    def parse_wordnet(self,debug=False):
        '''Parses wordnet from 
        <self.file>
        '''
        synList = []
        self.milestone = 0 # to start from beginning of file
        while self.milestone < os.path.getsize(self.fileName) - 5:
            if debug:
                print ('self.milestone', self.milestone)
            a = self.parse_synset(offset=self.milestone)
            synList.append(a)
            self.milestone = self.file.tell()
        return synList


class PolarisText(object):
    """Level number of record. Min 0, max 32 (for EuroWordNet)
    levelNumber  (public)

    Database record number. Optional, applicable for level 0 records only. 
    Between @-s.

    DRN  (public)

    Field tag.

    fieldTag  (public)

    Field value. String or int.

    fieldValue  (public)

    indent. Defaults to 2. Real indendation equals to indent * levelNumber.
    """
    indent = 2

    def __init__(self, levelNumber=None, fieldTag=None, 
                 DRN=None,
                 fieldValue=None,noQuotes=None):
        self.levelNumber = levelNumber
        self.DRN = DRN
        self.fieldTag = fieldTag
        self.noQuotes = noQuotes
        self.fieldValue = fieldValue

    def out():
        def fget(self):
            _out = ' '*PolarisText.indent*self.levelNumber
            if (not self.DRN) and (not self.fieldValue):
                if type(self.fieldValue) == type(1):
                    _out = '%s%d %s %d' % (_out,self.levelNumber,
                                           self.fieldTag,self.fieldValue)
                else:
                    _out = '%s%d %s' % (_out,self.levelNumber,self.fieldTag)
            elif self.DRN and (not self.fieldValue):
                try:
                    _out = '%s%d @%d@ %s' % (_out,self.levelNumber,
                                             self.DRN,self.fieldTag)
                except TypeError:
                    raise TypeError("wrong type in synset definition")
                # _out = 'MINGI JAMA ON'

            elif (not self.DRN) and self.fieldValue:
                if type(self.fieldValue) == type(1):
                    _out = '%s%d %s %d' % (_out,self.levelNumber,
                                           self.fieldTag,self.fieldValue)
                elif isinstance(self.fieldValue,six.string_types) : # peab nii olema
                    if self.noQuotes:
                        _out = '%s%d %s %s' % (_out,self.levelNumber,
                                               self.fieldTag,self.fieldValue)
                    else:
                        _out = '%s%d %s "%s"' % (_out,self.levelNumber,
                                                 self.fieldTag,self.fieldValue)
            return _out
        return locals()

    out = property(**out())


class Variant(object):
    """
    Variant. Holds info about variants.
    properties:

    literal (six.text_type)
    sense  (int)
    gloss  (six.text_type)
    examples  (Examples)

    """
    def __init__(self, literal=None, sense=None,
                 gloss=None, status=None,
                 examples=None,
                 translations=None,
                 external_info=None,
                 features=None,
                 usage_labels=None):
        self._literal = literal or None
        self._sense = sense or None
        self._gloss = gloss or None
        self._status = status or None
        self._examples = examples or Examples()
        self._translations = translations or Translations()
        self._external_info = external_info or None
        self._features = features or Features()
        self._usage_labels = usage_labels or Usage_Labels()

    def sense():
        doc = "Variant sense number. Integer"
        def fget(self):
            return self._sense
        def fset(self, value):
            if isinstance(value, int):  # Must be integer
                self._sense = value
            else:
                raise TypeError(
                    "Variant's object attribute 'sense' must be integer")
        def fdel(self):
            self._sense = None
        return locals()

    sense = property(**sense())

    def literal():
        doc = "Variant literal."
        def fget(self):
            return self._literal
        def fset(self, value):
            if isinstance(value, six.text_type):  # Must be string
                self._literal = value
            else:
                raise TypeError(
                    "Variant's object attribute 'literal' must be unicode string")
        def fdel(self):
            self._literal = None
        return locals()

    literal = property(**literal())

    def gloss():
        doc = "Variant gloss (definition)."
        def fget(self):
            return self._gloss
        def fset(self, value):
            if isinstance(value, six.string_types):  # Must be string
                self._gloss = value
            else:
                raise TypeError(
                    "Variant's object attribute 'gloss' must be string, not %s" %  type(value))
        def fdel(self):
            self._gloss = None
        return locals()

    gloss = property(**gloss())

    def status():
        doc = "Variant status."
        def fget(self):
            return self._status
        def fset(self, value):
            if isinstance(value, six.text_type):
                self._status = value
            else:
                raise TypeError(
                    "Variant's object attribute 'status' must be unicode string")
        def fdel(self):
            self._status = None
        return locals()

    status = property(**status())

    def examples():
        doc = "Variant examples."
        def fget(self):
            return self._examples
        def fset(self, value):
            if isinstance(value, Examples):
                self._examples = value
            else:
                raise TypeError(
                    "Variant's object attribute 'examples' must be Examples")
        def fdel(self):
            self._examples = None
        return locals()

    examples = property(**examples())

    def translations():
        doc = "Variant translations."
        def fget(self):
            return self._translations
        def fset(self, value):
            self._translations = value
        def fdel(self):
            self._translations = None
        return locals()

    translations = property(**translations())

    def external_info():
        doc = "Variant external_info."
        def fget(self):
            return self._external_info
        def fset(self, value):
            self._external_info = value
        def fdel(self):
            self._external_info = None
        return locals()
    
    external_info = property(**external_info())

    def features():
        doc = "Variant features."
        def fget(self):
            return self._features
        def fset(self, value):
            self._features = value
        def fdel(self):
            self._features = None
        return locals()

    features = property(**features())

    def usage_labels():
        doc = "Variant usage_labels."
        def fget(self):
            return self._usage_labels
        def fset(self, value):
            self._usage_labels = value
        def fdel(self):
            self._usage_labels = None
        return locals()

    usage_labels = property(**usage_labels())

    # methods for adding stuff
    def addTranslation(self,translation):
        '''Appends one Translation to translations
        '''
        if isinstance(translation, Translation):
            self.translations.append(translation)
        else:
            raise(TranslationError,
                   'translation Type should be Translation, not %s' % type(
                    translation)
                   )    

    def addVariantFeature(self,variantFeature):
        '''Appends one VariantFeature to variantFeatures
        '''
        if isinstance(variantFeature, Feature):
            self.features.append(variantFeature)
        else:
            raise(TypeError,
                  'variantFeature Type should be Feature, not %s' % type(
                    variantFeature)
                  )

    def addUsage_Label(self,usage_label):
        '''Appends one Usage_Label to usage_labels
        '''
        if isinstance(usage_label, Usage_Label):
            self.usage_labels.append(usage_label)
        else:
            raise (Usage_LabelError,
                   'usage_label Type should be Usage_Label, not %s' % type(
                    usage_label)
                   )

    def addExample(self,example):
        '''Appends one Example to examples
        '''
        if isinstance(example, Example):
            self.examples.append(example)
        else:
            raise (ExampleError,
                   'example Type should be Example, not %s' % type(example)
                   )

    def polarisText():
        def fget(self):
            _out = ''
            _n = '\n'
            _outList = []
            elementz = {
                (1,self.literal): (2, 'LITERAL'),
                (2,self.sense): (3, 'SENSE'),
                (3,self.gloss): (3, 'DEFINITION')
                }
            elKeys = elementz.keys()
            elKeys.sort()
            for i in elKeys:
                if i[1]:
                    _outList.append(
                        PolarisText(
                            elementz[i][0],elementz[i][1],None,i[1]).out)
            if self.status:
                _outList.append(PolarisText(3,'STATUS',None,self.status,
                                            True).out)
            if self.translations:
                _outList.append(self.translations.polarisText)

            if self.examples:
                _outList.append(self.examples.polarisText)
            if self.features:
                _outList.append(self.features.polarisText)
            if self.usage_labels:
                _outList.append(self.usage_labels.polarisText)
            if self.external_info:
                _outList.append(self.external_info.polarisText)
            _out = _out + _n.join(_outList)
            return _out
        return locals()
  
    polarisText = property(**polarisText())

# ===== Synset =====
class Synset(object):
    """

    Properties:

    number
    pos
    variants
    internalLinks
    eqLinks
    properties
    polarisText 
    definiton             ADDED BY KOM

    """
    linebreak = LINEBREAK


    def __init__(self, number=0, pos=None, 
                 wordnet_offset=None, add_on_id=None,
                 variants=None, 
                 internalLinks=None, eqLinks=None, properties=None, definition=None):
        self._number = number or 0
        self._pos = pos or ''
        self._wordnet_offset = wordnet_offset or None
        self._add_on_id = add_on_id or None
        self._variants = variants or Variants()
        self._internalLinks = internalLinks or InternalLinks()
        self._eqLinks = eqLinks or EqLinks()
        self._properties = properties or Properties()
        self._definition = definition or ''                 # ADDED BY KOM

    def definition():                       # ADDED BY KOM \/
        doc = "Synset definition"
        def fget(self):
            return self._definition
        def fset(self, value):
            self._definition = value
        def fdel(self):
            self._definition = "" 
        return locals()
            
    definition = property(**definition())       # ADDED BY KOM /\

    def pos():
        doc = "Synset part of speech."
        def fget(self):
            return self._pos
        def fset(self, value):
            if value in POSES:
                self._pos = value
            else:
                print (value)
                raiseTypeError(self.__class__.__name__, 
                               'pos',
                               'one of ' + str(POSES))
        def fdel(self):
            self._pos = None
        return locals()

    pos = property(**pos())

    def number():
        doc = "Synset identificator number"
        def fget(self):
            return self._number
        def fset(self, value):
            if type(value) == type(1):
                self._number = value
            else:
                raiseTypeError(self.__class__.__name__, 
                               'number',
                               'integer')
        def fdel(self):
            self._number = None
        return locals()

    number = property(**number())

    def add_on_id():
        doc = "WHY??? Nada, Fedja, nada!"
        def fget(self):
            return self._add_on_id
        def fset(self, value):
            # int
            self._add_on_id = value

        def fdel(self):
            self._add_on_id = None
        return locals()

    add_on_id = property(**add_on_id())

    def wordnet_offset():
        doc = "Synset part of speech."
        def fget(self):
            return self._wordnet_offset
        def fset(self, value):
            # int
            self._wordnet_offset = value

        def fdel(self):
            self._wordnet_offset = None
        return locals()

    wordnet_offset = property(**wordnet_offset())

    def variants():
        doc = "variants"
        def fget(self):
            return self._variants
        def fset(self, value):
            self._variants = value
            if isinstance(value, list):
                self._variants = value
            else:
                raiseTypeError(self.__class__.__name__, 
                               'variants',
                               'list')

        def fdel(self):
            self._variants = None
        return locals()

    variants = property(**variants())


    def internalLinks():
        doc = "internal links (relations)"
        def fget(self):
            return self._internalLinks
        def fset(self, value):
            if isinstance(value, list):
                self._internalLinks = value
            else:
                raiseTypeError(self.__class__.__name__, 
                               'internalLinks',
                               'list')

        def fdel(self):
            self._internalLinks = None
        return locals()

    internalLinks = property(**internalLinks())

    def eqLinks():
        doc = "Synset part of speech."
        def fget(self):
            return self._eqLinks
        def fset(self, value):
            if isinstance(value, list):
                self._eqLinks = value
            else:
                raiseTypeError(self.__class__.__name__, 
                               'eqLinks',
                               'list')
        def fdel(self):
            self._eqLinks = None
        return locals()

    eqLinks = property(**eqLinks())

    def properties():
        doc = "Synset properties"
        def fget(self):
            return self._properties
        def fset(self, value):
            if isinstance(value, Properties):
                self._properties = value
            else:
                raiseTypeError(self.__class__.__name__, 
                               'properties',
                               'list')
        def fdel(self):
            self._properties = None
        return locals()

    properties = property(**properties())

    # methods for geting special information
    def firstVariant():
        """first variant of Variants
        Read-only
        
        """
        def fget(self):
            if self.variants:
                return self.variants[0]
            else:
                variant = Variant()
                return variant

        return locals()

    firstVariant = property(**firstVariant())

    def literals():
        '''Returns a list of literals
        in the Synset
        read-only
        '''
        def fget(self):
            if self.variants:
                return map(lambda x: x.literal,
                           self.variants)
            else:
                return None
 
        return locals()
    
    literals = property(**literals())

    def addVariantOld(self,
                      literal='',
                      sense=0,
                      gloss='',
                      examples=[]):
        '''Appends variant
        sth to do that it would be possible
        to add Variant object

        '''
        var = Variant(literal=literal,
                      sense=sense,
                      gloss=gloss,
                      examples=examples)
        self.variants.append(var)

    def addVariant(self,variant):
        '''Appends one Variant to variants

        '''
        if isinstance(variant, Variant):
            self.variants.append(variant)
        else:
            raise (VariantError,
                   'variant Type should be Variant, not %s' % type(variant))


    def addInternalLink(self, link):
        '''Appends InternalLink
        
        '''
        if isinstance(link, InternalLink):
            self.internalLinks.append(link)
        else:
            raise InternalLinkError( 
                'link Type should be InternalLink, not %s' % type(link))

    def addRelation(self, link):
        '''Appends Relation
        
        '''
        if isinstance(link, Relation):
            self.internalLinks.append(link)
        else:
            raise TypeError(
                'link Type should be InternalLink, not %s' % type(link))


    def addEqLink(self, link):
        '''Appends EqLink

        '''
        if isinstance(link, EqLink):
            self.eqLinks.append(link)
        else:
            raise TypeError(
                'link Type should be InternalLink, not %s' % type(link))
      

    def named_relations(self, name, neg=False):
        '''Returns list of named Relations.
        
        <name> may be string or list.
        '''
        if self.internalLinks and not neg:

            if isinstance(name, six.string_types):
                return filter(lambda x: x.name == name,
                              self.internalLinks)

            elif isinstance(name, list):
                return filter(lambda x: x.name in name,
                              self.internalLinks)
            else:
                return None #should rise error

        elif self.internalLinks and neg:

            if isinstance(name, six.string_types):
                return filter(lambda x: x.name != name,
                              self.internalLinks)

            elif isinstance(name, list):
                return filter(lambda x: x.name not in name,
                              self.internalLinks)
            else:
                return None #should rise error
      
        else:
            return []


    def named_eq_relations(self, name, neg=False):
        '''Returns list of named eqLinks.

        <name> may be string or list.
        '''
        if self.eqLinks and not neg:

            if isinstance(name, six.string_types):
                return filter(lambda x: x.relation.name == name,
                              self.eqLinks)

            elif isinstance(name, list):
                return filter(lambda x: x.relation.name in name,
                              self.eqLinks)
            else:
                return None #should rise error

        elif self.eqLinks and neg:

            if isinstance(name, six.string_types):
                return filter(lambda x: x.relation.name != name,
                              self.eqLinks)

            elif isinstance(name, list):
                return filter(lambda x: x.relation.name not in name,
                              self.eqLinks)
            else:
                return None #should rise error
        else:
            return None


    def polarisText():
        """polarisText method of Synset class

        """
        def fget(self):
            _out = ''
            _n = '\n'

            ptSynsetHead = PolarisText(levelNumber=0, 
                                       fieldTag='WORD_MEANING',
                                       DRN=self.number)
            _out = '%s%s' % (_out,ptSynsetHead.out)

            if self.pos:
                ptPos = PolarisText(levelNumber=1, 
                                    fieldTag='PART_OF_SPEECH',
                                    fieldValue=self.pos)
                _out = '%s%s%s' % (_out,_n,ptPos.out)
            if self.variants:
                _out =  '%s%s%s' % (_out, _n, self.variants.polarisText)
            if self.internalLinks:
                    _out =  '%s%s%s' % (_out, _n, 
                                        self.internalLinks.polarisText)
            if self.eqLinks:        
                _out =  '%s%s%s' % (_out, _n, self.eqLinks.polarisText)
            if self.properties:
                _out =  '%s%s%s' % (_out, _n, self.properties.polarisText)
            return _out

        return locals()

    polarisText = property(**polarisText())

    def __cmp__(self, other):
        """At first only polarisText.
        TODO: more precise comparison, as the order
        may be different (e.g. variants)

        This should be AFTER polarisText
        TODO
        """
        return self.polarisText == other.polarisText
  
    def parse(self,fileName,offset):
        '''Parses synset from file <fileName>
        from offset <offset>
        '''
        p = Parser()
        p.file = open(fileName, 'rb')
        a = p.parse_synset(offset=offset)
        p.file.close()
        self.__dict__.update(a.__dict__)


    def write(self,fileName):
        '''Appends synset to Polaris IO file <fileName>
        '''
        f = open(fileName, 'ab')
        f.write('%s%s' % (self.polarisText,
                          Synset.linebreak)
                )
        f.close()
# ===== class Synset ===== end =====


# ===== WordInstance ===== start =====
class WordInstance (Synset):
    """Synset pos="pn"
    No properties, has PROPERTY_VALUES
    """
    def __init__(self, number=0, pos='pn', 
                 wordnet_offset=None,
                 add_on_id=None, variants=None, 
                 internalLinks=None, eqLinks=None,
                 propertyValues=None):
        super(WordInstance,self).__init__()

        self._number = number or 0

        self._wordnet_offset = wordnet_offset or None
        self._add_on_id = add_on_id or None
        self._variants = variants or Variants()
        self._internalLinks = internalLinks or InternalLinks()
        self._eqLinks = eqLinks or EqLinks()

        self.propertyValues = propertyValues or PropertyValues()
        self.pos = 'pn'

    def propertyValues():
        doc = "Synset propertyValues"
        def fget(self):
            return self._propertyValues
        def fset(self, value):
            if isinstance(value, PropertyValues):
                self._propertyValues = value
            else:
                raiseTypeError(self.__class__.__name__, 
                               'propertyValues',
                               'list')
        def fdel(self):
            self._propertyValues = None
        return locals()

    propertyValues = property(**propertyValues())

    def polarisText():
        def fget(self):
            _out = ''
            _n = '\n'
            ptSynsetHead = PolarisText(levelNumber=0, 
                                       fieldTag='WORD_INSTANCE',
                                       DRN=self.number)
            _out = '%s%s' % (_out,ptSynsetHead.out)
            if self.pos:
                ptPos = PolarisText(levelNumber=1, 
                                    fieldTag='PART_OF_SPEECH',
                                    fieldValue=self.pos)
                _out = '%s%s%s' % (_out,_n,ptPos.out)
            if self.variants:
                _out =  '%s%s%s' % (_out, _n, self.variants.polarisText)
            if self.internalLinks:
                _out =  '%s%s%s' % (_out, _n, self.internalLinks.polarisText)
            if self.eqLinks:
                _out =  '%s%s%s' % (_out, _n, self.eqLinks.polarisText)
            if self.propertyValues:
                _out =  '%s%s%s' % (_out, _n, self.propertyValues.polarisText)
            return _out
        return locals()

    polarisText = property(**polarisText())
# ===== WordInstance ===== end =====


# ===== Classes that subclass _TypedList =====
class Variants(_TypedList):
    '''List of variants
    '''
    def __init__(self, *args):
        super(_TypedList,self).__init__(*args)
        self.memberType = Variant
        self.parent = (1, 'VARIANTS')


class Properties(_TypedList):
    '''List of properties
    '''
    def __init__(self, *args):
        super(_TypedList,self).__init__(*args)
        self.memberType = Property
        self.parent = (1, 'PROPERTIES')


class PropertyValues(_TypedList):
    '''List of propertyValues
    '''
    def __init__(self, *args):
        super(_TypedList,self).__init__(*args)
        self.memberType = PropertyValue
        self.parent = (1, 'PROPERTY_VALUES')


class InternalLinks(_TypedList):
    '''List of links
    '''
    def __init__(self, *args):
        super(_TypedList,self).__init__(*args)
        self.memberType = Relation
        self.parent = (1, 'INTERNAL_LINKS')


class EqLinks(_TypedList):
    '''
    List of eqLinks
    '''
    def __init__(self):
        super(_TypedList,self).__init__()
        self.memberType = EqLink
        self.parent = (1, 'EQ_LINKS')


class Examples(_TypedList):
    '''List of examples
    '''
    def __init__(self,*args):
        super(_TypedList,self).__init__(*args)
        self.memberType = Example
        self.parent = (3, 'EXAMPLES')


class Translations(_TypedList):
    '''List of translations
    '''
    def __init__(self):
        super(_TypedList,self).__init__()
        self.memberType = Translation
        self.parent = (3, 'TRANSLATIONS')


class Corpus_Ids(_TypedList):
    '''List of corpus_ids
    '''
    def __init__(self):
        super(_TypedList,self).__init__()
        self.memberType = Corpus_Id
        self.parent = None

class Source_Ids(_TypedList):
    '''List of source_ids
    '''
    def __init__(self):
        super(_TypedList,self).__init__()
        self.memberType = (Source_Id,Relation_Source_Id)
        self.parent = None


class Morphological_Codes(_TypedList):
    '''List of morphological_codes

    OLD
    '''
    def __init__(self, items=[]):
        list.__init__(self, items)
        a = ''
        self.memberType = type(a)
        self.parent = (3, 'MORPHOLOGICAL_CODES')


class Usage_Labels(_TypedList):
    '''List of usage_labels
    '''
    def __init__(self):
        super(_TypedList,self).__init__()
        self.memberType = Usage_Label
        self.parent = (3, 'USAGE_LABELS')


class Features(_TypedList):
    '''List of features
    '''
    def __init__(self):
        super(_TypedList,self).__init__()
        self.memberType = Feature
        self.parent = (3, 'FEATURES')


# ===== Errors =====
class SynsetError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class EqLinkError(SynsetError):
    '''Class for EqLinks errors'''
    pass

class InternalLinkError(SynsetError):
    pass

class VariantError(SynsetError):
    pass


# ===== Functions =====
def addRelation(sourceSynset,relationName,targetSynset):
    """
    Adds relation with name <relationName> to
    <targetSynset>.

    """
    if not isinstance(sourceSynset, Synset):
        raise TypeError("sourceSynset not Synset instance")
    elif not isinstance(targetSynset, Synset):
        raise TypeError("targetSynset not Synset instance")
    elif relationName not in RELATION_NAMES:
        raise TypeError("relationName not in RELATION_NAMES")
    else:
        sourceSynset.addRelation(
            Relation(relationName,targetSynset)
            )
        return sourceSynset
