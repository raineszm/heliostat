from collections.abc import Iterable
from copy import deepcopy
from pathlib import Path
from typing import Any

import msgspec
from ruamel.yaml import YAML

from heliostat.git import ensure_repo


class PackageRepository(msgspec.Struct, omit_defaults=True):
    type: str
    cloud: str | None = None
    ppa: str | None = None
    priority: str | None = None


class RockcraftBuilder:
    def __init__(self, base: "RockcraftFile"):
        self.base = base
        self._ppa = None
        self._cloud = None

    def with_ppa(self, ppa: str) -> "RockcraftBuilder":
        self._ppa = ppa
        return self

    def with_base(self, base: str) -> "RockcraftBuilder":
        self._base = base
        return self

    def with_cloud(self, cloud: str) -> "RockcraftBuilder":
        self._cloud = cloud
        return self

    def build(self) -> "RockcraftFile":
        yaml_data = deepcopy(self.base.yaml)
        yaml_data[self.base.REPO_KEY] = [
            msgspec.to_builtins(
                PackageRepository(type="apt", ppa=self._ppa, cloud=self._cloud)
            )
        ]
        if self._base:
            yaml_data[self.base.BASE_KEY] = self._base
        return RockcraftFile(yaml_data)


class RockcraftFile:
    """A rockcraft file for a sunbeam rock."""

    BASE_KEY = "base"
    REPO_KEY = "package-repositories"

    def __init__(self, yaml: dict[str, Any]):
        self.yaml = yaml

    def repositories(self) -> Iterable[PackageRepository]:
        for repo in self.yaml.get(self.REPO_KEY, []):
            yield msgspec.convert(repo, PackageRepository)

    def patched(self) -> RockcraftBuilder:
        return RockcraftBuilder(self)


class SunbeamRock:
    def __init__(self, path: Path):
        self.path = path

    @property
    def name(self) -> str:
        return self.path.name

    def rockcraft_yaml(self) -> RockcraftFile:
        yaml = YAML()
        obj = yaml.load((self.path / "rockcraft.yaml").read_text())
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

    def rock(self, name: str) -> SunbeamRock:
        for rock in self.rocks():
            if rock.name == name:
                return rock

        raise ValueError(f"No rock found with name '{name}'")
