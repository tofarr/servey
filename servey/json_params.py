from dataclasses import MISSING
from typing import Dict, List, Union, Iterator, Tuple

from marshy.types import ExternalItemType
from urllib.parse import parse_qsl

"""
Below is a clean, concise, human readble, fully reversible method for converting between URLs and JSON data sctructures.
It should be as compatible as possible with standard http parameters.
Just jamming json into the parameters is not a great approach, and this aims to improve on that. We use ~ as a control
character a lot because it is one of the few characters that 'encodeURIComponent' will leave alone. 
The rules are outlined below:

    * Values are assumed to be strings:
        A=B -> {"A": "B"}
    * If a key has multiple values, they are assumed to represent an ordered array: 
        A=B&A=C -> {"A": ["B", "C"]}
    * Paths are split into tokens by dots. Parent elements are assumed to be dicts: 
        A.B=C -> {"A": {"B": "C"}}
        A.B=C&A.B=D -> {"A": {"B": ["C", "D"]}}
        A..B=C -> {"A": {"": {"B": "C"}}}
        A.=B -> {"A": {"": "B}}
        .=A -> {"": {"": "A"}}
    * Dots may be escaped with a tilda
        A~.B=C -> {"A.B": "C"}
        A~.B.C~.D=E -> {"A.B": {"C.D": "E"}}
    * A key ending with a ~b or ~B is assumed to be a boolean. 
      Valid case insensitive boolean values are [0, false, 1, true]
        A~B=1 -> {"A": True}
        A~b=tRuE -> {"A": True}
        A~b=0&A=B -> {"A": [False, "B"]}
        A~B=positive -> ERROR
    * A key ending with a ~f is assumed to represent a floating point number:
        A~f=1 -> {"A": 1.0}
        A~f=1.5&A=B -> {"A": [1.5, "B"]}
        A~f=one -> ERROR
    * A key ending with a ~i is assumed to represent an integer:
        A~i=1 -> {"A": 1}
        A~i=2&A=B -> {"A": [2, "B"]}
        A~i=one -> ERROR
    * A key ending with a ~n is assumed to represent a null - the only acceptable value is ""
        A~n= -> {"A": null}
        A~n=&A=B -> {"A": [null, "B"]}
        A~n=nope -> ERROR
    * A parent token may have the suffix ~a to represent an array. Child elements may be referenced by index.
        A~A.0=B -> {"A": ["B"]}
        A~a.0=&A~A.1=B -> {"A": ["", "B"]}
        A~a.B= -> ERROR
        A~a=B -> ERROR
    * Unreferenced array elements with a value less than the max index are filled with null values:
        A~a.2=B -> {"A": [null, null, "B"]}
    * All references to a parent must have the same type:
        A~a.0=B&A~a.1=C -> {"A": ['B', 'C']}
        A~a.0=B&A.1=C -> ERROR
    * Tildas are escaped by a second tilda:
        A~~B=True -> {"A~B": "True"}
        A~~~B=True -> {"A~": true}
        A~~~~B=True -> {"A~~B": "True"}
    * URL Parameters are processed in order:
        A=B&A~b=1&A=C -> {"A": ["B", true, "C"]}
"""


def from_params(params: Union[str, Iterator[Tuple[str, str]]]) -> ExternalItemType:
    if isinstance(params, str):
        params = parse_qsl(params, keep_blank_values=True, strict_parsing=False,
                           encoding='utf-8', errors='replace',
                           max_num_fields=None)
    result = {}
    for key, value in params:
        try:
            parent = result
            for token, type_name, is_last in _get_typed_path(key):
                if is_last:
                    value = _cast_value(value, type_name)
                    _upsert_last_element(parent, token, value)
                else:
                    parent = _upsert_parent_token(token, type_name, parent)
        except ValueError as e:
            raise ValueError(f'key_error:{key}:{str(e)}')
    return result


def _upsert_parent_token(token: str, type_name: str, parent: Union[List, Dict]) -> Union[List, Dict]:
    if isinstance(parent, list):
        token = int(token)
        for index in range(len(parent), token + 1):
            parent[index] = None
        element = parent[token]
    else:
        element = parent.get(token)
    if type_name == 'a':
        if element is None:
            parent[token] = element = []
            return element
        elif isinstance(element, list):
            return element
    if type_name == 'd':
        if element is None:
            parent[token] = element = {}
            return element
        elif isinstance(element, dict):
            return element
    raise ValueError(f'unknown_type:{type_name}')


def _cast_value(value: str, type_name: str):
    if type_name == 's':
        return value
    elif type_name == 'b':
        if value.lower() in ('true', '1'):
            return True
        if value.lower() in ('false', '0'):
            return False
    elif type_name == 'f':
        return float(value)
    elif type_name == 'i':
        return int(value)
    elif type_name == 'n':
        if value == '':
            return None
    raise ValueError(f'unknown_type:{type_name}')


def _upsert_last_element(parent: Union[List, Dict], token: str, value: Union[bool, float, int, str]):
    if isinstance(parent, list):
        token = int(token)
        for index in range(len(parent), token + 1):
            parent[index] = MISSING
        prev_value = parent[token]
    else:
        if not isinstance(parent, dict):
            raise ValueError(f'type_error:{parent}')
        prev_value = parent.get(token, MISSING)
    if prev_value is MISSING:
        parent[token] = value
    elif isinstance(prev_value, list):
        prev_value.append(value)
    else:
        parent[token] = [prev_value]
        parent[token].append(value)


def _get_typed_path(key: str) -> Iterator[Tuple[str, str, bool]]:
    for raw_token, is_last in _get_raw_tokens(key):
        type_name = 's' if is_last else 'd'
        if len(raw_token) > 1 and raw_token[-2] == '~' and not _is_escaped(raw_token, len(raw_token) - 2):
            type_name = raw_token[-1].lower()
            raw_token = raw_token[:-2]
        token = raw_token.replace('~~', '~')
        yield token, type_name, is_last


def _get_raw_tokens(key: str) -> Iterator[Tuple[str, bool]]:
    prev_index = 0
    index = 0
    while index < len(key):
        if key[index] == '.':
            if not _is_escaped(key, index):
                token = key[prev_index:index]
                yield token, False
                prev_index = index + 1
            else:
                key = key[:index-1] + key[index:]
        index += 1
    token = key[prev_index:index]
    yield token, True


def _is_escaped(key: str, index: int) -> bool:
    count = _count_preceding_tildas(key, index)
    escaped = count & 1 == 1
    return escaped


def _count_preceding_tildas(key: str, index: int) -> int:
    count = 0
    while index > 0:
        index -= 1
        if key[index] != '~':
            return count
        count += 1
    return count
