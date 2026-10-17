import pytest

from thefuzz import fuzz, process


def test_process_warning(caplog):
    """Check that a string reduced to 0 by processor logs a warning to stderr"""

    query = ':::::::'
    choices = [':::::::']

    _ = process.extractOne(query, choices)

    logstr = ("Applied processor reduces "
              "input query to empty string, "
              "all comparisons will have score 0. "
              "[Query: ':::::::']")

    assert 1 == len(caplog.records)
    log = caplog.records[0]

    assert log.levelname == "WARNING"
    assert log.name == "thefuzz.process"
    assert logstr == log.message


@pytest.mark.parametrize('scorer', [fuzz.partial_ratio, fuzz.token_sort_ratio])
def test_score_cutoff_uses_returned_rounded_score(scorer):
    query = 'abcdefghijklmnopqrs'
    choice = 'abtdefghijklmnopqrs'
    expected = (choice, 95)

    assert scorer(query, choice) == 95
    assert process.extract(query, [choice], scorer=scorer) == [expected]
    assert list(process.extractWithoutOrder(query, [choice], scorer=scorer,
                                           score_cutoff=95)) == [expected]
    assert process.extractBests(query, [choice], scorer=scorer,
                                score_cutoff=95) == [expected]
    assert process.extractOne(query, [choice], scorer=scorer,
                              score_cutoff=95) == expected


def test_score_cutoff_excludes_score_rounded_below_cutoff():
    query = 'a' * 200
    choice = 'a' * 189 + 'b' * 11

    assert fuzz.token_sort_ratio(query, choice) == 94
    assert list(process.extractWithoutOrder(query, [choice],
                                           scorer=fuzz.token_sort_ratio,
                                           score_cutoff=95)) == []
    assert process.extractBests(query, [choice], scorer=fuzz.token_sort_ratio,
                                score_cutoff=95) == []
    assert process.extractOne(query, [choice], scorer=fuzz.token_sort_ratio,
                              score_cutoff=95) is None
