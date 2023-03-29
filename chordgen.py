from __future__ import annotations
from dataclasses import dataclass
from typing import List

def chord_gen(root: str, quality: str, extensions: List[str] = []) -> List[str]:
    def _chord_gen():
        root_pitch = _Pitch.from_str(root)
        yield root_pitch
        for i in _quality_map[quality.lower()]:
            yield root_pitch.transpose(i)
        for e in extensions:
            yield root_pitch.transpose(_extension_map[e])
    
    return [str(p) for p in _chord_gen()]

def chord_symbol(root: str, quality: str, extensions: List[str] = []) -> str:
    root = _replace_ascii_accidentals(root.capitalize())
    
    if extensions:
        fmt_extensions = _replace_ascii_accidentals(','.join(extensions))
        return f'{root}{quality.lower()}({fmt_extensions})'
    
    return f'{root}{quality.lower()}'

class _Pitch:
    def __init__(self, step: str, offset: int):
        if len(step) != 1:
            raise ValueError("'root' must be a single-character string")
        step = step.upper()
        if step < 'A' or step > 'G':
            raise ValueError("invalid 'root' argument")
        self._step = step
        self._offset = offset
    
    @property
    def step(self) -> str:
        return self._step
    
    @property
    def offset(self) -> int:
        return self._offset
    
    def transpose(self, interval: _Interval) -> _Pitch:
        pos = ord(self._step) - ord('A')
        step_result = _natural_pcs[pos]
        semi_result = _natural_pcs[pos] + self._offset + interval.semitones
        
        for _ in range(interval.steps):
            step_result += _pc_intervals[pos % 7]
            pos += 1
        
        return _Pitch('ABCDEFG'[_natural_pcs.index(step_result % 12)], semi_result - step_result)
    
    @classmethod
    def from_str(cls, pitch: str):
        if not len(pitch):
            raise ValueError("'pitch' cannot be an empty string")
        
        root = pitch[0].upper()
        
        if root < 'A' or root > 'G':
            raise ValueError("'pitch' does not contain a valid root")
        
        return cls(root, _str_to_offset(pitch[1:]))
        
    
    def __str__(self):
        return f'{self._step}{_offset_to_str(self._offset)}'

@dataclass
class _Interval:
    steps: int
    semitones: int


def _offset_to_str(offset: int) -> str:
    if not offset:
        return ""
    if offset > 0:
        sharps = divmod(offset, 2)
        return f'{_double_sharp * sharps[0]}{_sharp * sharps[1]}'
    else:
        flats = divmod(-offset, 2)
        return f'{_double_flat * flats[0]}{_flat * flats[1]}'

def _str_to_offset(offset: str) -> int:
    if any(c not in ('x', '#', 'b') for c in offset):
        raise ValueError("invalid offset (valid characters: '#', 'b', 'x')")
    result = 0
    result += offset.count('x') * 2
    result += offset.count('#')
    result += offset.count('b') * -1
    return result

def _replace_ascii_accidentals(pitch_str: str) -> str:
    return pitch_str\
        .replace('x', _double_sharp)\
        .replace('#', _sharp)\
        .replace('bb', _double_flat)\
        .replace('b', _flat)

_flat = '\u266D'
_sharp = '\u266F'
_double_flat = '\U0001D12B'
_double_sharp = '\U0001D12A'

_quality_map = {
    'maj': (_Interval(2, 4), _Interval(4, 7)),
    'min': (_Interval(2, 3), _Interval(4, 7)),
    'dim': (_Interval(2, 3), _Interval(4, 6)),
    '+': (_Interval(2, 4), _Interval(4, 8)),
    'maj6': (_Interval(2, 4), _Interval(4, 7), _Interval(5, 9)),
    'min6': (_Interval(2, 3), _Interval(4, 7), _Interval(5, 9)),
    '7': (_Interval(2, 4), _Interval(4, 7), _Interval(6, 10)),
    'maj7': (_Interval(2, 4), _Interval(4, 7), _Interval(6, 11)),
    'min7': (_Interval(2, 3), _Interval(4, 7), _Interval(6, 10)),
    'minmaj7': (_Interval(2, 3), _Interval(4, 7), _Interval(6, 11)),
    'min7b5': (_Interval(2, 3), _Interval(4, 6), _Interval(6, 10)),
    'dim7' : (_Interval(2, 3), _Interval(4, 6), _Interval(6, 9)),
    '+7': (_Interval(2, 4), _Interval(4, 8), _Interval(6, 10)),
    '+maj7': (_Interval(2, 4), _Interval(4, 8), _Interval(6, 11)),
    'maj6/9': (_Interval(2, 4), _Interval(4, 7), _Interval(5, 9), _Interval(8, 14)),
    'min6/9': (_Interval(2, 3), _Interval(4, 7), _Interval(5, 9), _Interval(8, 14))
}

_extension_map = {
    '9': _Interval(8, 14),
    'b9': _Interval(8, 13),
    '#9': _Interval(8, 15),
    '11': _Interval(10, 17),
    '#11': _Interval(10, 18),
    '13': _Interval(12, 21),
    'b13': _Interval(12, 20)
}

_natural_pcs = [9, 11, 0, 2, 4, 5, 7]
_pc_intervals = [2, 1, 2, 2, 1, 2, 2]
        