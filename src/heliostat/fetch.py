import subprocess
from pathlib import Path

import xdg_base_dirs as xdg


def cache_dir() -> Path:
    return xdg.xdg_cache_home() / "heliostat"


def repo_path(name: str) -> Path:
    return cache_dir() / name


def ensure_repo(uri: str, branch: str = "main") -> Path:
    name = uri.split("/")[-1].removesuffix(".git")
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
                    "--",
                    uri,
                    path,
                ]
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to clone repo: {e}")

    try:
        subprocess.check_call(
            [
                "git",
                "fetch",
                "--all",
            ],
            cwd=path,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to fetch repo: {e}")

    try:
        subprocess.check_call(
            [
                "git",
                "switch",
                "--detach",
                f"origin/{branch}",
            ],
            cwd=path,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to switch to branch: {e}")

    return path
