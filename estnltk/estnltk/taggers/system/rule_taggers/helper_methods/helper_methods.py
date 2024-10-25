from typing import List, Tuple, Generator

from estnltk_core import ElementaryBaseSpan
from estnltk.vabamorf.morf import synthesize




def conflict_priority_resolver(sorted_tuples: List[Tuple[ElementaryBaseSpan, str]], priority_matches: List) \
    -> List[Tuple[ElementaryBaseSpan, str]]:
    """

    Parameters
    ----------
    sorted_tuples: list of tuples returned by the extract_matches method in rule-based taggers
    priority_matches: priority information for the corresponding tuples

    Returns
    -------
    sorted_tuples list without the elements that are filtered out by priority

    """
    #TODO make sure it is equivalent to the EstNLTK conflict resolver
    deleted_tuples = []
    for tuple1, priority_info1 in zip(sorted_tuples, priority_matches):
        for tuple2, priority_info2 in zip(sorted_tuples,priority_matches):
            group1 = priority_info1[1][0][0]
            group2 = priority_info2[1][0][0]
            if group1 == group2:
                if tuple1[0].start <= tuple2[0].end and tuple1[0].end >= tuple2[0].start:
                    priority1 = priority_info1[1][0][1]
                    priority2 = priority_info2[1][0][1]
                    if priority1 > priority2:
                        deleted_tuples.append(tuple1)

    for tuple in deleted_tuples:
        sorted_tuples.remove(tuple)

    return sorted_tuples


def keep_maximal_matches(sorted_tuples: List[Tuple[ElementaryBaseSpan, str]]) \
        -> Generator[Tuple[ElementaryBaseSpan, str], None, None]:
    """
    Given a list of canonically ordered spans removes spans that are covered by another span.
    The outcome is also in canonical order.

    Recall that canonical order means:
        span[i].start <= span[i+1].start
        span[i].start == span[i+1].start ==> span[i].end < span[i + 1].end
    """

    sorted_tuples = iter(sorted_tuples)
    current_tuple = next(sorted_tuples, None)
    while current_tuple is not None:
        next_tuple = next(sorted_tuples, None)

        # Current span is last
        if next_tuple is None:
            yield current_tuple
            return

        # Check if the next span covers the current_tuple
        if current_tuple[0].start == next_tuple[0].start:
            assert current_tuple[0].end <= next_tuple[0].end, "Tuple sorting does not work as expected"
            current_tuple = next_tuple
            continue

        yield current_tuple

        # Ignore following spans that are covered by the current span
        while next_tuple[0].end <= current_tuple[0].end:
            next_tuple = next(sorted_tuples, None)
            if next_tuple is None:
                return

        current_tuple = next_tuple


def keep_minimal_matches(sorted_tuples: List[Tuple[ElementaryBaseSpan, str]]) \
        -> Generator[Tuple[ElementaryBaseSpan, str], None, None]:
    """
    Given a list of canonically ordered spans removes spans that enclose another smaller span.
    The outcome is also in canonical order.

    Recall that canonical order means:
        span[i].start <= span[i+1].start
        span[i].start == span[i+1].start ==> span[i].end < span[i + 1].end
    """

    work_list = []
    sorted_tuples = iter(sorted_tuples)
    current_tuple = next(sorted_tuples, None)
    while current_tuple is not None:
        new_work_list = []
        add_current = True
        # Work list is always in canonical order and span ends are strictly increasing.
        # This guarantees that candidates are released in canonical order as well.
        for candidate_tuple in work_list:

            # Candidate tuple is inside the current tuple. It must be last candidate
            if current_tuple[0].start == candidate_tuple[0].start:
                new_work_list.append(candidate_tuple)
                add_current = False
                break

            # No further span can be inside the candidate span
            if candidate_tuple[0].end < current_tuple[0].start:
                yield candidate_tuple
                continue

            # Current tuple is not inside the candidate tuple
            if candidate_tuple[0].end < current_tuple[0].end:
                new_work_list.append(candidate_tuple)

            assert candidate_tuple[0].start < current_tuple[0].start, "Tuple sorting does not work as expected"

        # The current tuple is always a candidate for minimal match
        work_list = new_work_list + [current_tuple] if add_current else new_work_list
        current_tuple = next(sorted_tuples, None)

    # Output work list as there were no invalidating spans left
    for candidate_tuple in work_list:
        yield candidate_tuple


def noun_forms_expander(word):
    cases = [
        ('n', 'nimetav'),
        ('g', 'omastav'),
        ('p', 'osastav'),
        ('ill', 'sisseütlev'),
        ('in', 'seesütlev'),
        ('el', 'seestütlev'),
        ('all', 'alaleütlev'),
        ('ad', 'alalütlev'),
        ('abl', 'alaltütlev'),
        ('tr', 'saav'),
        ('ter', 'rajav'),
        ('es', 'olev'),
        ('ab', 'ilmaütlev'),
        ('kom', 'kaasaütlev')]

    expanded = []
    for case, name in cases:
        expanded.append(', '.join(synthesize(word, 'sg ' + case, 'S')))
        expanded.append(', '.join(synthesize(word, 'pl ' + case, 'S')))

    return expanded


def verb_forms_expander(word):
    raise NotImplementedError


def default_expander(word):
    #TODO determine if word is noun or verb and use respective expander
    return noun_forms_expander(word)