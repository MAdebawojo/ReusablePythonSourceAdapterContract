from abc import ABC, abstractmethod
from typing import Iterable, Iterator

from pytest import RunResult

from iris_ingest.models import CanonicalRecord

from dataclasses import dataclass, field

@dataclass 
class Rejection: 
    raw_record: dict 
    reason: str

@dataclass
class RunResult:
    adapter_name: str
    total_extracted: int
    accepted_count: int
    rejections: list[Rejection] = field(default_factory=list)

class SourceAdapter(ABC):
    # each adapter declares its own identity
    source_id: str

    @abstractmethod
    def extract(self) -> Iterator[dict]:
        """Yield raw records exactly as the source gives them."""

    @abstractmethod
    def normalize(self, raw: dict) -> CanonicalRecord:
        """Translate ONE raw record into the canonical shape."""

    def validate(self, record: CanonicalRecord) -> list[str]:
        """Return a list of problems. Empty list means valid."""
        ...

    def run(self, loader) -> RunResult:
        """The fixed workflow: extract -> normalize -> validate -> load."""
        ...