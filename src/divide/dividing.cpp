/* Functions to speed up dividing and splitting algorithms in Estnltk's Text class */
#include "dividing.h"

const Span none(-1,-1);
const SpanVector<Span>(1, none) vec_none;


int first(Span const& span) {
    return span.first;
}


int first(SpanVector const& spans) {
    return spans[0].first;
}


int last(Span const& span) {
    return span.second;
}


int last(SpanVector const& spans) {
    return spans[spans.size()-1].second;
}


bool span_contains_span(Span const& outer, Span const& inner) {
    return outer.first <= inner.first and outer.second >= inner.second;
}


bool span_contains_list(Span const& outer, SpanVector const& inner) {
    for (int i = 0 ; i < inner.size() ; ++i) {
        if (!span_contains_span(outer, inner[i])) {
            return false;
        }
    }
    return true;
}


bool list_contains_span(SpanVector const& outer, Span const& inner) {
    for (int i = 0 ; i < outer.size() ; ++i) {
        if (span_contains_span(outer[i], inner)) {
            return true;
        }
    }
    return false;
}


bool list_contains_list(SpanVector const& outer, SpanVector const& inner) {
    const int n = outer.size();
    const int m = inner.size();
    int i = 0;
    int j = 0;
    while (i < n && j < m) {
        if (outer[i].first > inner[j].first) {
            return false;
        }
        if (outer[i].second >= inner[j].second) {
            j += 1;
        } else {
            i += 1;
        }
    }
    return j == m;
}


Span span_translates_span(Span const& outer, Span const& inner) {
    if (span_contains_span(outer, inner)) {
        Span span(inner.first - outer.first, inner.second - outer.first);
    }
    return none;
}


SpanVector span_translates_list(Span const& outer, SpanVector const& inner) {
    const int left = outer.first;
    SpanVector translated;
    translated.reserve(inner.size());
    for (int i = 0 ; i < inner.size() ; ++i) {
        if (span_contains_span(outer, inner[i])) {
            Span span(inner[i].first - left, inner[i].second - left);
            translated.push_back(span);
        }
    }
    return translated;
}


Span list_translates_span(SpanVector const& outer, Span const& inner, std::string const& sep) {
    const int seplen = sep.size();
    int offset = 0;
    for (int i = 0 ; i < outer.size() ; ++i) {
        if (span_contains_span(outer[i], inner)) {
            Span span(inner.first - outer[i].first + offset, inner.second - outer[i].first + offset);
            return span;
        }
        offset += outer[i].second - outer[i].first + seplen;
    }
}

SpanVector list_translates_list(SpanVector const& outer, SpanVector const& inner, std::string const& sep) {
    const int n = outer.size();
    const int m = inner.size();
    const int seplen = sep.size();
    int i = 0;
    int j = 0;
    int offset = 0;
    SpanVector translated;
    translated.reserve(n + m);
    while (i < n && j < m) {
        Span const& ospan = outer[i];
        Span const& ispan = inner[j];
        if (ospan.first > ispan.first) {
            j += 1;
            continue;
        }
        if (ospan.second >= ispan.second) {
            Span span(ispan.first - ospan.first + offset, ispan.second - ospan.first + offset);
            j += 1;
        } else {
            offset += ospan.second - ospan.first + seplen;
        }
    }
    if (translated.size() > 0) {
        return translated;
    }
    return vec_none;
}


IntVectors spans_collect_spans(SpanVector const& outer_spans, SpanVector const& inner_spans) {
    const int n = outer_spans.size();
    const int m = inner_spans.size();
    int i = 0;
    int j = 0;
    IntVectors intvectors;
    intvectors.reserve(n);
    IntVector current_bin;
    while (i < n && j < m) {
        Span const& ospan = outer_spans[i];
        Span const& ispan = inner_spans[j];
        if (ospan.first > ispan.first) {
            j += 1;
            continue;
        }
        if (ospan.second >= ispan.second) {
            current_bin.append(j);
            j += 1;
        } else {
            intvectors.append(current_bin);
            current_bin.clear();
            i += 1;
        }
    }
    if (intvectors.size() < n) {
        intvectors.append(current_bin);
        current_bin.clear();
    }
    while (intvectors.size() < n) {
        intvectors.append(current_bin);
    }
    return intvectors;
}


IntVectors spans_collect_spans(SpanVector const& outer_spans, IndexedSpanVector const& inner_spans) {
    SpanVector converted;
    converted.reserve(inner_spans.size());
    for (int i = 0 : i<inner_spans.size(); ++i) {
        converted.push_back(inner_spans[i].first);
    }
    return spans_collect_spans(outer_spans, converted);
}


IntVector unique(IntVector& const vec) {
    std::unordered_set<int> seen;
    IntVector unique_vec;
    unique_vec.reserve(vec.size());
    for (int i = 0 ; i < vec.size() ; ++i) {
        int e = vec[i];
        if (seen.find(e) == seen.end()) {
            seen.insert(e);
            unique_vec.push_back(e);
        }
    }
    return unique_vec;
}


IntVectors spans_collect_lists(SpanVector const& outer_spans, SpanVectors const& inner_spans) {
    const int n = inner_spans.size();
    IndexedSpanVector flattened_spans;
    flattened_spans.reserve(n);

    for (int i = 0 ; i < n ; ++i) {
    SpanVector& spans = inner_spans[i];
        const int m = spans.size();
        for (int j = 0; j < m ; ++j) {
            flattened_spans.push_back(IndexedSpan(spans[j], i));
        }
    }
    sort(flattened_spans.first(), flattened_spans.last());

    IntVectors bins = spans_collect_spans(outer_spans, flattened_spans);
    for (int i = 0 ; i < bins.size() ; ++i) {
        IntVector& vec = bins[i];
        for (j = 0 ; j < vec.size() ; ++ j) {
            vec[j] = flattened_spans[vec[j]];
        }
        bins[i] = unique(vec);
    }
    return bins;
}


IntVectors lists_collect_spans(SpanVectors const& outer_spans, SpanVector const& inner_spans) {

}


def lists_collect_spans(outer_spans, inner_spans):
    mapping = []
    flattened_spans = []
    for idx, spans in enumerate(outer_spans):
        for s in spans:
            flattened_spans.append(s)
            mapping.append(idx)
    flattened_spans, mapping = zip(*sorted(zip(flattened_spans, mapping)))
    flat_bins = list(spans_collect_spans(flattened_spans, inner_spans))
    bins = [[] for _ in range(len(outer_spans))]
    for flatidx, flatbin in enumerate(flat_bins):
        binidx = mapping[flatidx]
        bins[binidx].extend(flatbin)
    for bin in bins:
        yield unique(bin)


def lists_collect_lists(outer_spans, inner_spans):
    mapping = []
    flattened_spans = []
    for idx, spans in enumerate(outer_spans):
        for s in spans:
            flattened_spans.append(s)
            mapping.append(idx)
    flattened_spans, mapping = zip(*sorted(zip(flattened_spans, mapping)))
    flat_bins = list(spans_collect_lists(flattened_spans, inner_spans))
    bins = [[] for _ in range(len(outer_spans))]
    for flatidx, flatbin in enumerate(flat_bins):
        binidx = mapping[flatidx]
        bins[binidx].extend(flatbin)
    for bin in bins:
        yield unique(bin)
