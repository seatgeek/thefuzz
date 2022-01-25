from collections.abc import Mapping
import typing
from typing import Any, Callable, Iterable, Union, Tuple, Generator, TypeVar


ChoicesT = Union[Mapping[str, str], Iterable[str]]
T = TypeVar('T')
ProcessorT = Union[Callable[[str, bool], str], Callable[[Any], Any]]
ScorerT = Callable[[str, str, bool, bool], int]


@typing.overload
def extractWithoutOrder(query: str, choices: Mapping[str, str], processor: ProcessorT, scorer: ScorerT, score_cutoff: int = ...) -> Generator[Tuple[str, int, str], None, None]: ...


@typing.overload
def extractWithoutOrder(query: str, choices: Iterable[str], processor: ProcessorT, scorer: ScorerT, score_cutoff: int = ...) -> Generator[Tuple[str, int], None, None]: ...
