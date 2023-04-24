from rapidfuzz.utils import default_process as _default_process

translation_table = {i: None for i in range(128, 256)}  # ascii dammit!


def ascii_only(s):
    return s.translate(translation_table)


def full_process(s, force_ascii=False):
    """
    Process string by
    -- removing all but letters and numbers
    -- trim whitespace
    -- force to lower case
    if force_ascii == True, force convert to ascii
    """

    if force_ascii:
        s = ascii_only(str(s))

    return _default_process(s)
