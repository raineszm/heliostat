import copy
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Protocol

import msgspec
from ruamel.yaml import YAML

from heliostat.component import package_list
from heliostat.git import ensure_repo


class Patch(Protocol):
    def apply(self, rockcraft: dict[str, Any]): ...


@dataclass
class AddPpa(Patch):
    ppa: str

    def apply(self, rockcraft: dict[str, Any]):
        rockcraft[RockcraftFile.REPO_KEY].append(
            msgspec.to_builtins(PpaPackageRepository(type="apt", ppa=self.ppa))
        )


Release = Literal["yoga", "antelope", "caracal", "epoxy"]
Series = Literal["jammy", "noble"]
Base = Literal["ubuntu@22.04", "ubuntu@24.04"]


@dataclass
class SetUcaRelease(Patch):
    DEFAULT_RELEASE = {
        "jammy": "yoga",
        "noble": "caracal",
    }

    release: Release
    series: Series | None

    def apply(self, rockcraft: dict[str, Any]):
        # if we're using the default pairing, we can just fall back to
        # the ubuntu archives
        series = self.series or "noble"
        if self.DEFAULT_RELEASE.get(series) == self.release:
            del rockcraft[RockcraftFile.REPO_KEY][0]
            return

        cloud_repo = msgspec.convert(
            rockcraft[RockcraftFile.REPO_KEY][0], CloudPackageRepository
        )

        cloud_repo.cloud = self.release

        rockcraft[RockcraftFile.REPO_KEY][0] = msgspec.to_builtins(cloud_repo)


@dataclass
class SetBase(Patch):
    SERIES_TO_BASE = {
        "jammy": "ubuntu@22.04",
        "noble": "ubuntu@24.04",
    }

    series_or_base: Series | Base

    def apply(self, rockcraft: dict[str, Any]):
        rockcraft[RockcraftFile.BASE_KEY] = self.SERIES_TO_BASE.get(
            self.series_or_base, self.series_or_base
        )


Priority = Literal["always", "prefer", "defer"] | int


class PpaPackageRepository(msgspec.Struct, omit_defaults=True):
    type: Literal["apt"]
    ppa: str
    priority: Priority | None = None
    key_id: str | None = None


class CloudPackageRepository(msgspec.Struct, omit_defaults=True):
    type: Literal["apt"]
    cloud: str
    pocket: Literal["updates", "proposed"] | None = None
    priority: Priority | None = None
    key_id: str | None = None


class DebPackageRepository(msgspec.Struct, omit_defaults=True):
    type: Literal["apt"]
    architectures: list[str] = []
    formats: list[str] = msgspec.field(default_factory=lambda: ["deb"])
    priority: Priority | None = None
    path: str | None = None
    key_id: str | None = None
    pocket: Literal["updates", "proposed"] | None = None
    series: str | None = None
    url: str | None = None


PackageRepository = PpaPackageRepository | CloudPackageRepository | DebPackageRepository


class RockcraftFile:
    """A rockcraft file for a sunbeam rock."""

    BASE_KEY = "base"
    REPO_KEY = "package-repositories"

    def __init__(self, yaml: dict[str, Any]):
        self.yaml = yaml

    def repositories(self) -> Iterable[PackageRepository]:
        for repo in self.yaml.get(self.REPO_KEY, []):
            if "ppa" in repo:
                yield msgspec.convert(repo, PpaPackageRepository)
            elif "cloud" in repo:
                yield msgspec.convert(repo, CloudPackageRepository)
            else:
                yield msgspec.convert(repo, DebPackageRepository)

    def patch(self, patches: Iterable[Patch]) -> "RockcraftFile":
        yaml = copy.deepcopy(self.yaml)
        for patch in patches:
            patch.apply(yaml)
        return RockcraftFile(yaml)

    def deps(self) -> set[str]:
        deps = set()
        for part in self.yaml["parts"].values():
            if "overlay-packages" in part:
                deps.update(part["overlay-packages"])

        return deps


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

    def rocks_for_package(self, source: str) -> Iterable[SunbeamRock]:
        binpkgs = set(package_list(source))
        for rock in self.rocks():
            if rock.rockcraft_yaml().deps().intersection(binpkgs):
                yield rock
