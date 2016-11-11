%module vabamorf

%include "typemaps.i"
%include "std_string.i"
%include "std_vector.i"
%include "std_map.i"
%include "std_set.i"
%include "std_pair.i"
%include "cdata.i"
%include "exception.i"

// wrap C++ standard exceptions
%exception {
    try {
        $action
    }
    catch (const std::runtime_error& e) {
        SWIG_exception(SWIG_RuntimeError, e.what());
    }
    catch (const std::invalid_argument& e) {
        SWIG_exception(SWIG_ValueError, e.what());
    }
    catch (const std::out_of_range& e) {
        SWIG_exception(SWIG_IndexError, e.what());
    }
    catch (const VEAD& e) {
        SWIG_exception(SWIG_RuntimeError, e.Teade());
    }
    catch (const CFSException &e) {
        SWIG_exception(SWIG_RuntimeError, "CFSException: internal error with vabamorf");
    }
    catch (...) {
        SWIG_exception(SWIG_RuntimeError, "unknown exception");
    }
}

namespace std {
   %template(StringVector) vector<string>;
};

%{
#include "vabamorf.h"
%}

namespace std {
    %template(AnalysisVector) vector<Analysis>;
    %template(WordAnalysis) pair<string, vector<Analysis> >;
    %template(SentenceAnalysis) vector<pair<string, vector<Analysis> > >;
    %template(StringVector) vector<std::string>;
    %template(SpellingSuggestions) vector<SpellingResults>;
    %template(Syllables) vector<Syllable>;
    %template(SentenceSyllables) vector<vector<Syllable> >;
}

%include "include/estnltk/vabamorf.h"
