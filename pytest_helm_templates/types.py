from dataclasses import dataclass


@dataclass
class DependencyListItem:
    name: str
    repository: str
    status: str
    version: str

    @property
    def is_missing(self) -> bool:
        return self.status == "missing"

    @property
    def is_ok(self) -> bool:
        return self.status == "ok"
