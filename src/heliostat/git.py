import subprocess
from pathlib import Path

import xdg_base_dirs as xdg


def repo_path(name: str) -> Path:
    return xdg.xdg_cache_home() / "heliostat" / name


def ensure_repo(uri: str) -> Path:
    name = uri.split("/")[-1].strip(".git")
    path = repo_path(name)
    if not path.exists():
        # Set up parent cache dir
        path.parent.mkdir(parents=True, exist_ok=True)
        # shell out to git clone
        try:
            subprocess.check_call(
                [
                    "git",
                    "clone",
                    "--depth=1",
                    "--",
                    uri,
                    path,
                ]
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to clone repo: {e}")
    return path
