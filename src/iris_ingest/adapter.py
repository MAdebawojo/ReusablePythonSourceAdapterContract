from abc import ABC, abstractmethod
from typing import Iterable, Iterator

from pytest import RunResult

from iris_ingest.errors import NormalizationError
from iris_ingest.loaders import Loader
from iris_ingest.models import CanonicalRecord

from dataclasses import dataclass, field

from iris_ingest.validation import validate_record

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
    """Base class every source adapter must extend.

    Subclasses implement extract() and normalize(). run() is fixed:
    it defines extract -> normalize -> validate -> load for every
    adapter and must not be overridden.
    """

    adapter_name: str

    @abstractmethod
    def extract(self) -> Iterator[dict]:
        """Yield raw records exactly as the source gives them."""

    @abstractmethod
    def normalize(self, raw: dict) -> CanonicalRecord:
        """Translate ONE raw record into the canonical shape.

        Raise NormalizationError if the raw record cannot be normalized.
        """

    def run(self, loader: Loader) -> RunResult:
        total_extracted = 0
        accepted_count = 0
        rejections: list[Rejection] = []

        for raw in self.extract():
            total_extracted += 1

            try:
                record = self.normalize(raw)
            except NormalizationError as e:
                rejections.append(Rejection(raw_record=raw, reason=str(e)))
                continue

            problems = validate_record(record)
            if problems:
                rejections.append(Rejection(raw_record=raw, reason="; ".join(problems)))
                continue

            loader.load(record)
            accepted_count += 1

        return RunResult(
            adapter_name=self.adapter_name,
            total_extracted=total_extracted,
            accepted_count=accepted_count,
            rejections=rejections,
        )