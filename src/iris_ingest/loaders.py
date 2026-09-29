import json
from abc import ABC, abstractmethod

from iris_ingest.models import CanonicalRecord

class Loader(ABC):
    @abstractmethod
    def load(self, record: CanonicalRecord) -> None:
        """Persist one valid canonical record to staging."""

class JsonlLoader(Loader):
    """Writes each record as one JSON line to a file."""

    def __init__(self, path: str):
        self.path = path
        self._file = open(path, "w")

    def load(self, record: CanonicalRecord) -> None:
        line = json.dumps(record.to_dict())
        self._file.write(line + "\n")

    def close(self) -> None:
        self._file.close()

    def __enter__(self) -> "JsonlLoader":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()