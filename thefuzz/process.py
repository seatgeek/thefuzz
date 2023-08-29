#!/usr/bin/env python
from . import fuzz
from . import utils
import logging
from rapidfuzz import fuzz as rfuzz
from rapidfuzz import process as rprocess
from functools import partial

_logger = logging.getLogger(__name__)

default_scorer = fuzz.WRatio
default_processor = utils.full_process


def _get_processor(processor, scorer):
    """
    thefuzz runs both the default preprocessing of the function and the preprocessing
    function passed into process.* while rapidfuzz only runs the one passed into
    process.*. This function wraps the processor to mimic this behavior
    """
    if scorer not in (fuzz.WRatio, fuzz.QRatio,
                      fuzz.token_set_ratio, fuzz.token_sort_ratio,
                      fuzz.partial_token_set_ratio, fuzz.partial_token_sort_ratio,
                      fuzz.UWRatio, fuzz.UQRatio):
        return processor

    force_ascii = scorer not in [fuzz.UWRatio, fuzz.UQRatio]
    pre_processor = partial(utils.full_process, force_ascii=force_ascii)

    if not processor or processor == utils.full_process:
        return pre_processor

    def wrapper(s):
        return pre_processor(processor(s))

    return wrapper


# this allows lowering the scorers back to the scorers used in rapidfuzz
# this allows rapidfuzz to perform more optimizations behind the scenes.
# These mapped scorers are the same with two expceptions
# - default processor
# - result is not rounded
# these two exceptions need to be taken into account in the implementation
_scorer_lowering = {
    fuzz.ratio: rfuzz.ratio,
    fuzz.partial_ratio: rfuzz.partial_ratio,
    fuzz.token_set_ratio: rfuzz.token_set_ratio,
    fuzz.token_sort_ratio: rfuzz.token_sort_ratio,
    fuzz.partial_token_set_ratio: rfuzz.partial_token_set_ratio,
    fuzz.partial_token_sort_ratio: rfuzz.partial_token_sort_ratio,
    fuzz.WRatio: rfuzz.WRatio,
    fuzz.QRatio: rfuzz.QRatio,
    fuzz.UWRatio: rfuzz.WRatio,
    fuzz.UQRatio: rfuzz.QRatio,
}


def _get_scorer(scorer):
    """
    rapidfuzz scorers require the score_cutoff argument to be available
    This generates a compatible wrapper function
    """
    def wrapper(s1, s2, score_cutoff=0):
        return scorer(s1, s2)

    return _scorer_lowering.get(scorer, wrapper)


def _preprocess_query(query, processor):
    processed_query = processor(query) if processor else query
    if len(processed_query) == 0:
        _logger.warning("Applied processor reduces input query to empty string, "
                        "all comparisons will have score 0. "
                        f"[Query: \'{query}\']")

    return processed_query


def extractWithoutOrder(query, choices, processor=default_processor, scorer=default_scorer, score_cutoff=0):
    """
    Select the best match in a list or dictionary of choices.

    Find best matches in a list or dictionary of choices, return a
    generator of tuples containing the match and its score. If a dictionary
    is used, also returns the key for each match.

    Arguments:
        query: An object representing the thing we want to find.
        choices: An iterable or dictionary-like object containing choices
            to be matched against the query. Dictionary arguments of
            {key: value} pairs will attempt to match the query against
            each value.
        processor: Optional function of the form f(a) -> b, where a is the query or
            individual choice and b is the choice to be used in matching.

            This can be used to match against, say, the first element of
            a list:

            lambda x: x[0]

            Defaults to thefuzz.utils.full_process().
        scorer: Optional function for scoring matches between the query and
            an individual processed choice. This should be a function
            of the form f(query, choice) -> int.

            By default, fuzz.WRatio() is used and expects both query and
            choice to be strings.
        score_cutoff: Optional argument for score threshold. No matches with
            a score less than this number will be returned. Defaults to 0.

    Returns:
        Generator of tuples containing the match and its score.

        If a list is used for choices, then the result will be 2-tuples.
        If a dictionary is used, then the result will be 3-tuples containing
        the key for each match.

        For example, searching for 'bird' in the dictionary

        {'bard': 'train', 'dog': 'man'}

        may return

        ('train', 22, 'bard'), ('man', 0, 'dog')
    """
    is_mapping = hasattr(choices, "items")
    is_lowered = scorer in _scorer_lowering

    query = _preprocess_query(query, processor)
    it = rprocess.extract_iter(
        query, choices,
        processor=_get_processor(processor, scorer),
        scorer=_get_scorer(scorer),
        score_cutoff=score_cutoff
    )

    for choice, score, key in it:
        if is_lowered:
            score = int(round(score))

        yield (choice, score, key) if is_mapping else (choice, score)


def extract(query, choices, processor=default_processor, scorer=default_scorer, limit=5):
    """
    Select the best match in a list or dictionary of choices.

    Find best matches in a list or dictionary of choices, return a
    list of tuples containing the match and its score. If a dictionary
    is used, also returns the key for each match.

    Arguments:
        query: An object representing the thing we want to find.
        choices: An iterable or dictionary-like object containing choices
            to be matched against the query. Dictionary arguments of
            {key: value} pairs will attempt to match the query against
            each value.
        processor: Optional function of the form f(a) -> b, where a is the query or
            individual choice and b is the choice to be used in matching.

            This can be used to match against, say, the first element of
            a list:

            lambda x: x[0]

            Defaults to thefuzz.utils.full_process().
        scorer: Optional function for scoring matches between the query and
            an individual processed choice. This should be a function
            of the form f(query, choice) -> int.
            By default, fuzz.WRatio() is used and expects both query and
            choice to be strings.
        limit: Optional maximum for the number of elements returned. Defaults
            to 5.

    Returns:
        List of tuples containing the match and its score.

        If a list is used for choices, then the result will be 2-tuples.
        If a dictionary is used, then the result will be 3-tuples containing
        the key for each match.

        For example, searching for 'bird' in the dictionary

        {'bard': 'train', 'dog': 'man'}

        may return

        [('train', 22, 'bard'), ('man', 0, 'dog')]
    """
    return extractBests(query, choices, processor=processor, scorer=scorer, limit=limit)


def extractBests(query, choices, processor=default_processor, scorer=default_scorer, score_cutoff=0, limit=5):
    """
    Get a list of the best matches to a collection of choices.

    Convenience function for getting the choices with best scores.

    Args:
        query: A string to match against
        choices: A list or dictionary of choices, suitable for use with
            extract().
        processor: Optional function for transforming choices before matching.
            See extract().
        scorer: Scoring function for extract().
        score_cutoff: Optional argument for score threshold. No matches with
            a score less than this number will be returned. Defaults to 0.
        limit: Optional maximum for the number of elements returned. Defaults
            to 5.

    Returns: A a list of (match, score) tuples.
    """
    is_mapping = hasattr(choices, "items")
    is_lowered = scorer in _scorer_lowering

    query = _preprocess_query(query, processor)
    results = rprocess.extract(
        query, choices,
        processor=_get_processor(processor, scorer),
        scorer=_get_scorer(scorer),
        score_cutoff=score_cutoff,
        limit=limit
    )

    for i, (choice, score, key) in enumerate(results):
        if is_lowered:
            score = int(round(score))

        results[i] = (choice, score, key) if is_mapping else (choice, score)

    return results


def extractOne(query, choices, processor=default_processor, scorer=default_scorer, score_cutoff=0):
    """
    Find the single best match above a score in a list of choices.

    This is a convenience method which returns the single best choice.
    See extract() for the full arguments list.

    Args:
        query: A string to match against
        choices: A list or dictionary of choices, suitable for use with
            extract().
        processor: Optional function for transforming choices before matching.
            See extract().
        scorer: Scoring function for extract().
        score_cutoff: Optional argument for score threshold. If the best
            match is found, but it is not greater than this number, then
            return None anyway ("not a good enough match").  Defaults to 0.

    Returns:
        A tuple containing a single match and its score, if a match
        was found that was above score_cutoff. Otherwise, returns None.
    """
    is_mapping = hasattr(choices, "items")
    is_lowered = scorer in _scorer_lowering

    query = _preprocess_query(query, processor)
    res = rprocess.extractOne(
        query, choices,
        processor=_get_processor(processor, scorer),
        scorer=_get_scorer(scorer),
        score_cutoff=score_cutoff
    )

    if res is None:
        return res

    choice, score, key = res

    if is_lowered:
        score = int(round(score))

    return (choice, score, key) if is_mapping else (choice, score)


def dedupe(contains_dupes, threshold=70, scorer=fuzz.token_set_ratio):
    """
    This convenience function takes a list of strings containing duplicates and uses fuzzy matching to identify
    and remove duplicates. Specifically, it uses process.extract to identify duplicates that
    score greater than a user defined threshold. Then, it looks for the longest item in the duplicate list
    since we assume this item contains the most entity information and returns that. It breaks string
    length ties on an alphabetical sort.

    Note: as the threshold DECREASES the number of duplicates that are found INCREASES. This means that the
        returned deduplicated list will likely be shorter. Raise the threshold for dedupe to be less
        sensitive.

    Args:
        contains_dupes: A list of strings that we would like to dedupe.
        threshold: the numerical value (0,100) point at which we expect to find duplicates.
            Defaults to 70 out of 100
        scorer: Optional function for scoring matches between the query and
            an individual processed choice. This should be a function
            of the form f(query, choice) -> int.
            By default, fuzz.token_set_ratio() is used and expects both query and
            choice to be strings.

    Returns:
        A deduplicated list. For example:

            In: contains_dupes = ['Frodo Baggin', 'Frodo Baggins', 'F. Baggins', 'Samwise G.', 'Gandalf', 'Bilbo Baggins']
            In: dedupe(contains_dupes)
            Out: ['Frodo Baggins', 'Samwise G.', 'Bilbo Baggins', 'Gandalf']
    """
    deduped = set()
    for item in contains_dupes:
        matches = extractBests(item, contains_dupes, scorer=scorer, score_cutoff=threshold, limit=None)
        deduped.add(max(matches, key=lambda x: (len(x[0]), x[0]))[0])

    return list(deduped) if len(deduped) != len(contains_dupes) else contains_dupes
