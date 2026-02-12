"""
Tools for adding built rocks to the local containerd registry in a way
that they can be accessed by juju.
"""

import json
import subprocess
import tarfile

# https://documentation.ubuntu.com/canonical-kubernetes/latest/snap/howto/image-management/
from pathlib import Path

CTR_BIN = "/snap/k8s/current/bin/ctr"
CTR_SOCK = "/run/containerd/containerd.sock"
K8S_NS = "k8s.io"

FAKE_REGISTRY = "phantom-registry.zmraines.com"


def ctr_cmd(*args: str) -> list[str]:
    return [
        "sudo", CTR_BIN, "--address", CTR_SOCK, "--namespace", K8S_NS
    ] + list(args)


def image_name(rock_name: str) -> str:
    return f"{FAKE_REGISTRY}/{rock_name}"


def image_digest(rock_path: Path) -> str:
    with tarfile.open(rock_path, "r") as tar:
        f = tar.extractfile("index.json")
        if not f:
            raise ValueError(f"Failed to extract index.json from {rock_path}")
        parsed = json.load(f)
        return parsed["manifests"][0]["digest"]


def import_image(rock_path: Path, rock_name: str):
    subprocess.check_call(
        ctr_cmd(
            "images",
            "import",
            "--digests",
            "--base-name",
            image_name(rock_name),
            str(rock_path),
        )
    )


def has_image(digest: str) -> bool:
    return any(
        line.endswith(digest)
        for line in subprocess.check_output(ctr_cmd("images", "ls", "-q"))
        .decode("utf-8")
        .splitlines()
    )
