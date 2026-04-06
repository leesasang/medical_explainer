from dataclasses import dataclass, field
from typing import Optional, List, Any

@dataclass
class Person:
    age: int
    sex: str

@dataclass
class LabInput:
    value: Any = None
    ref_low: Optional[float] = None
    ref_high: Optional[float] = None
    unit: str = ""

@dataclass
class ItemResult:
    key: str
    name_ko: str
    value: Any
    unit: str
    status: str
    short: str
    easy_explain: str
    possible_causes: List[str] = field(default_factory=list)
    next_steps: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)
    urgency: str = "routine"
