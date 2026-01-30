import subprocess
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

import xdg_base_dirs as xdg
import yaml
from pydantic import BaseModel


class PackageRepository(BaseModel):
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
            yield PackageRepository.model_validate(repo)


class RockFolder:
    def __init__(self, name: str, path: Path):
        self.name = name
        self.path = path

    def yaml(self) -> str:
        return (self.path / "rockcraft.yaml").read_text()

    def load(self) -> RockcraftFile:
        return RockcraftFile(yaml.safe_load(self.yaml()))


class SunbeamRocks:
    """An interface to the canonical/ubuntu-sunbeam-rocks repo.

    heliostat uses the definitions in this repo as a starting point and then
    applies patch on top.
    """

    def ensure_repo(self):
        if not self.repo_cache.exists():
            # Set up parent cache dir
            self.repo_cache.parent.mkdir(parents=True, exist_ok=True)
            # shell out to git clone
            try:
                subprocess.check_call(
                    [
                        "git",
                        "clone",
                        "--depth=1",
                        "--",
                        "https://github.com/canonical/ubuntu-openstack-rocks.git",
                        self.repo_cache,
                    ]
                )
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Failed to clone repo: {e}")

    @property
    def repo_cache(self) -> Path:
        return xdg.xdg_cache_home() / "heliostat" / "ubuntu-sunbeam-rocks"

    def rocks(self) -> Iterable[RockFolder]:
        for rock_dir in (self.repo_cache / "rocks").iterdir():
            yield RockFolder(rock_dir.name, rock_dir)
