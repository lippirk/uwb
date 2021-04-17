import pickle
import json
import string
from sys import stderr
from typing import Dict
import pprint
from datetime import datetime


def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def eprint_pprint(x):
    return pprint.pprint(x, stderr)


def eprint(*args, **kwargs):
    return print(*args, **kwargs, file=stderr)


def dump_json(obj: object, fname: str = None) -> None:
    with open(fname, 'w') as f:
        json.dump(obj, f)


def load_json(fname: str) -> object:
    with open(fname, 'r') as f:
        return json.load(f)


def dump_pickle(obj: object, fname: str = None) -> None:
    with open(fname, 'wb') as f:
        pickle.dump(obj, f)


def load_pickle(fname: str) -> object:
    with open(fname, 'rb') as f:
        return pickle.load(f)


def dump_str(x: str, fname: str = None) -> None:
    with open(fname, 'w') as f:
        f.write(x)


def contains_whitespace(s: str) -> bool:
    return any(c in string.whitespace for c in s)


def make_ordinal(n: int) -> str:
    '''
    Convert an integer into its ordinal representation::

        make_ordinal(0)   => '0th'
        make_ordinal(3)   => '3rd'
        make_ordinal(122) => '122nd'
        make_ordinal(213) => '213th'

    Stolen from
    =========
    https://stackoverflow.com/questions/9647202/ordinal-numbers-replacement
    '''
    suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    return str(n) + suffix
