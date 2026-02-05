from __future__ import annotations

import copy
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Protocol, Self

import msgspec
from ruamel.yaml import YAML

from heliostat.component import package_list
from heliostat.fetch import ensure_repo
from heliostat.types import Base, Release, Series


class Patch(Protocol):
    def apply(self, rockcraft: dict[str, Any]): ...


@dataclass
class AddPpa(Patch):
    ppa: str

    def apply(self, rockcraft: dict[str, Any]):
        rockcraft[RockcraftFile.REPO_KEY].append(
            msgspec.to_builtins(PpaPackageRepository(type="apt", ppa=self.ppa))
        )


@dataclass
class SetUcaRelease(Patch):
    release: Release
    series: Series = Series.default()

    def apply(self, rockcraft: dict[str, Any]):
        # if we're using the default pairing, we can just fall back to
        # the ubuntu archives
        package_repos = rockcraft.setdefault(RockcraftFile.REPO_KEY, [])
        if self.series.default_release() == self.release:
            if package_repos:
                del rockcraft[RockcraftFile.REPO_KEY][0]
            return

        if package_repos:
            cloud_repo = msgspec.convert(
                rockcraft[RockcraftFile.REPO_KEY][0], CloudPackageRepository
            )
            cloud_repo.cloud = self.release
            package_repos[0] = msgspec.to_builtins(cloud_repo)
        else:
            cloud_repo = CloudPackageRepository(type="apt", cloud=self.release)
            package_repos.append(msgspec.to_builtins(cloud_repo))

        rockcraft[RockcraftFile.REPO_KEY] = package_repos


@dataclass
class SetBase(Patch):
    series_or_base: Series | Base

    def apply(self, rockcraft: dict[str, Any]):
        if isinstance(self.series_or_base, Series):
            base = self.series_or_base.to_base()
        else:
            base = self.series_or_base
        rockcraft[RockcraftFile.BASE_KEY] = str(base)


@dataclass
class SetVersionString(Patch):
    suffix: str

    def apply(self, rockcraft: dict[str, Any]):
        version = rockcraft[RockcraftFile.VERSION_KEY]
        rockcraft[RockcraftFile.VERSION_KEY] = f"{version}-{self.suffix}"


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
    VERSION_KEY = "version"

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

    def patch(self, patches: Iterable[Patch]) -> RockcraftFile:
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

    RELEASE_BRANCH = {
        Release.ANTELOPE: "stable/2023.1",
        Release.BOBCAT: "stable/2023.2",
        Release.CARACAL: "stable/2024.1",
        Release.DALMATIAN: "dalmatian",
        Release.EPOXY: "main",
    }

    @classmethod
    def ensure(cls, release: Release = Release.default()) -> Self:
        local_path = ensure_repo(cls.REPO_URI, branch=cls.RELEASE_BRANCH[release])
        return cls(local_path)

    def __init__(self, path: Path):
        self.path = path

    def rocks(self, names: set[str] | None = None) -> Iterable[SunbeamRock]:
        return (
            SunbeamRock(rock_dir)
            for rock_dir in (self.path / "rocks").iterdir()
            if names is None or rock_dir.name in names
        )

    def rock(self, name: str) -> SunbeamRock:
        result = list(self.rocks({name}))
        if not result:
            raise ValueError(f"No rock found with name '{name}'")
        return result[0]

    def rocks_for_packages(
        self, *sources: str, series: Series, release: Release
    ) -> Iterable[SunbeamRock]:
        binpkgs = set(package_list(list(sources), series=series, release=release))
        return (
            rock
            for rock in self.rocks()
            if rock.rockcraft_yaml().deps().intersection(binpkgs)
        )
