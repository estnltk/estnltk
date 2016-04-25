# -*- coding: utf-8 -*-
"""Module containing functionality to resolve conflicting matches."""
from __future__ import unicode_literals, print_function, absolute_import


def resolve_using_maximal_coverage(matches):
    """Given a list of matches, select a subset of matches
    such that there are no overlaps and the total number of
    covered characters is maximal.

    Parameters
    ----------
    matches: list of Match

    Returns
    --------
    list of Match
    """
    if len(matches) == 0:
        return matches
    matches.sort()
    N = len(matches)
    scores = [len(match) for match in matches]
    prev = [-1] * N
    for i in range(1, N):
        bestscore = -1
        bestprev = -1
        j = i
        while j >= 0:
            # if matches do not overlap
            if matches[j].is_before(matches[i]):
                l = scores[j] + len(matches[i])
                if l >= bestscore:
                    bestscore = l
                    bestprev = j
            else:
                # in case of overlapping matches
                l = scores[j] - len(matches[j]) + len(matches[i])
                if l >= bestscore:
                    bestscore = l
                    bestprev = prev[j]
            j = j - 1
        scores[i] = bestscore
        prev[i] = bestprev
    # first find the matching with highest combined score
    bestscore = max(scores)
    bestidx = len(scores) - scores[-1::-1].index(bestscore) -1
    # then backtrack the non-conflicting matchings that should be kept
    keepidxs = [bestidx]
    bestidx = prev[bestidx]
    while bestidx != -1:
        keepidxs.append(bestidx)
        bestidx = prev[bestidx]
    # filter the matches
    return [matches[idx] for idx in reversed(keepidxs)]

