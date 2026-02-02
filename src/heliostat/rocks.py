from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

import msgspec
import yaml

from heliostat.git import ensure_repo


class PackageRepository(msgspec.Struct):
    type: str
    cloud: str | None = None
    priority: str | None = None


class RockcraftFile:
    """A rockcraft file for a sunbeam rock."""

    REPO_KEY = "package-repositories"

    def __init__(self, yaml: Mapping[str, Any]):
        self._yaml = yaml

    def repositories(self) -> Iterable[PackageRepository]:
        for repo in self._yaml.get(self.REPO_KEY, []):
            yield msgspec.convert(repo, PackageRepository)


class SunbeamRock:
    def __init__(self, path: Path):
        self.path = path

    @property
    def name(self) -> str:
        return self.path.name

    def rockcraft_yaml(self) -> RockcraftFile:
        obj = yaml.safe_load((self.path / "rockcraft.yaml").read_text())
        return RockcraftFile(obj)


class SunbeamRockRepo:
    """An interface to the canonical/ubuntu-sunbeam-rocks repo.

    heliostat uses the definitions in this repo as a starting point and then
    applies patch on top.
    """

    REPO_URI = "https://github.com/canonical/ubuntu-openstack-rocks.git"

    @classmethod
    def ensure(cls) -> "SunbeamRockRepo":
        local_path = ensure_repo(cls.REPO_URI)
        return cls(local_path)

    def __init__(self, path: Path):
        self.path = path

    def rocks(self) -> Iterable[SunbeamRock]:
        for rock_dir in (self.path / "rocks").iterdir():
            yield SunbeamRock(rock_dir)
