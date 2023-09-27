import unicodedata
from rapidfuzz.utils import default_process as _default_process


def to_ascii(s):
    """
    Replace non-ascii characters with their "close enough" ascii counterparts (e.g. 'é' -> 'e')
    """
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()

  
def full_process(s, force_ascii=False):
    """
    Process string by
    -- removing all but letters and numbers
    -- trim whitespace
    -- force to lower case
    if force_ascii == True, force convert to ascii
    """

    if force_ascii:
        s = to_ascii(str(s))

    return _default_process(s)
