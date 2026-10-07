from dataclasses import dataclass
from typing import Dict


@dataclass
class ChoiceResult:
    value: str
    probabilities: Dict[str, float]


@dataclass
class ScoreResult:
    value: int
    probabilities: Dict[int, float]


@dataclass
class NoulResult:
    value: float