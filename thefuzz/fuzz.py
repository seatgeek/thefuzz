#!/usr/bin/env python

from rapidfuzz.fuzz import (
    ratio as _ratio,
    partial_ratio as _partial_ratio,
    token_set_ratio as _token_set_ratio,
    token_sort_ratio as _token_sort_ratio,
    partial_token_set_ratio as _partial_token_set_ratio,
    partial_token_sort_ratio as _partial_token_sort_ratio,
    WRatio as _WRatio,
    QRatio as _QRatio,
)

from . import utils

###########################
# Basic Scoring Functions #
###########################


def _rapidfuzz_scorer(scorer, s1, s2, force_ascii, full_process):
    """
    wrapper around rapidfuzz function to be compatible with the API of thefuzz
    """
    if full_process:
        if s1 is None or s2 is None:
            return 0

        s1 = utils.full_process(s1, force_ascii=force_ascii)
        s2 = utils.full_process(s2, force_ascii=force_ascii)

    return int(round(scorer(s1, s2)))


def ratio(s1, s2):
    return _rapidfuzz_scorer(_ratio, s1, s2, False, False)


def partial_ratio(s1, s2):
    """
    Return the ratio of the most similar substring
    as a number between 0 and 100.
    """
    return _rapidfuzz_scorer(_partial_ratio, s1, s2, False, False)


##############################
# Advanced Scoring Functions #
##############################

# Sorted Token
#   find all alphanumeric tokens in the string
#   sort those tokens and take ratio of resulting joined strings
#   controls for unordered string elements
def token_sort_ratio(s1, s2, force_ascii=True, full_process=True):
    """
    Return a measure of the sequences' similarity between 0 and 100
    but sorting the token before comparing.
    """
    return _rapidfuzz_scorer(_token_sort_ratio, s1, s2, force_ascii, full_process)


def partial_token_sort_ratio(s1, s2, force_ascii=True, full_process=True):
    """
    Return the ratio of the most similar substring as a number between
    0 and 100 but sorting the token before comparing.
    """
    return _rapidfuzz_scorer(
        _partial_token_sort_ratio, s1, s2, force_ascii, full_process
    )


def token_set_ratio(s1, s2, force_ascii=True, full_process=True):
    return _rapidfuzz_scorer(_token_set_ratio, s1, s2, force_ascii, full_process)


def partial_token_set_ratio(s1, s2, force_ascii=True, full_process=True):
    return _rapidfuzz_scorer(
        _partial_token_set_ratio, s1, s2, force_ascii, full_process
    )


###################
# Combination API #
###################

# q is for quick
def QRatio(s1, s2, force_ascii=True, full_process=True):
    """
    Quick ratio comparison between two strings.

    Runs full_process from utils on both strings
    Short circuits if either of the strings is empty after processing.

    :param s1:
    :param s2:
    :param force_ascii: Allow only ASCII characters (Default: True)
    :full_process: Process inputs, used here to avoid double processing in extract functions (Default: True)
    :return: similarity ratio
    """
    return _rapidfuzz_scorer(_QRatio, s1, s2, force_ascii, full_process)


def UQRatio(s1, s2, full_process=True):
    """
    Unicode quick ratio

    Calls QRatio with force_ascii set to False

    :param s1:
    :param s2:
    :return: similarity ratio
    """
    return QRatio(s1, s2, force_ascii=False, full_process=full_process)


# w is for weighted
def WRatio(s1, s2, force_ascii=True, full_process=True):
    """
    Return a measure of the sequences' similarity between 0 and 100, using different algorithms.

    **Steps in the order they occur**

    #. Run full_process from utils on both strings
    #. Short circuit if this makes either string empty
    #. Take the ratio of the two processed strings (fuzz.ratio)
    #. Run checks to compare the length of the strings
        * If one of the strings is more than 1.5 times as long as the other
          use partial_ratio comparisons - scale partial results by 0.9
          (this makes sure only full results can return 100)
        * If one of the strings is over 8 times as long as the other
          instead scale by 0.6

    #. Run the other ratio functions
        * if using partial ratio functions call partial_ratio,
          partial_token_sort_ratio and partial_token_set_ratio
          scale all of these by the ratio based on length
        * otherwise call token_sort_ratio and token_set_ratio
        * all token based comparisons are scaled by 0.95
          (on top of any partial scalars)

    #. Take the highest value from these results
       round it and return it as an integer.

    :param s1:
    :param s2:
    :param force_ascii: Allow only ascii characters
    :type force_ascii: bool
    :full_process: Process inputs, used here to avoid double processing in extract functions (Default: True)
    :return:
    """
    return _rapidfuzz_scorer(_WRatio, s1, s2, force_ascii, full_process)


def UWRatio(s1, s2, full_process=True):
    """
    Return a measure of the sequences' similarity between 0 and 100,
    using different algorithms. Same as WRatio but preserving unicode.
    """
    return WRatio(s1, s2, force_ascii=False, full_process=full_process)
