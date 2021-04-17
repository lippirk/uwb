import uwb.src.util as u
from typing import Dict, Optional
import importlib_resources
import re


def eprint(x: str) -> None:
    u.eprint(f"dictionary.py: {x}")


T = Dict[str, str]

_english_dict_json_fname = (importlib_resources.files(
    'uwb') / "resources" / "english-dict-clean.json")


def _dict_sanity_check(t: T) -> None:
    for w in t.keys():
        assert re.search(
            r"^[A-Za-z]+$", w), f"'{word}' in dict does not match regex"
    assert len(t.keys()) == 95885


def init() -> T:
    t = u.load_json(_english_dict_json_fname)
    _dict_sanity_check(t)
    return t


def is_valid_word(t: T, word: str) -> bool:
    return word in t


def definition(t: T, word: str) -> Optional[str]:
    return t.get(word, None)


def size(t: T) -> int:
    """
    Total number of words in the dictionary
    """
    return len(t)
