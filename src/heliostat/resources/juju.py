"""Utilities for updating the oci-image resources associated with Juju k8s
charms."""

import shutil
import subprocess
from pathlib import Path

from .ctr import has_image, image_digest, image_name, import_image

JUJU_BIN = shutil.which("juju") or "/snap/juju/current/bin/juju"
SUNBEAM_MODEL = "openstack"


def juju_cmd(cmd: str, *args: str) -> list[str]:
    return [JUJU_BIN, cmd, "--model", SUNBEAM_MODEL] + list(args)


def attach_resource(
    charm_name: str, resource_name: str, image_name: str, digest: str
):
    subprocess.check_call(
        juju_cmd(
            "attach-resource",
            charm_name,
            f"{resource_name}={image_name}@{digest}",
        )
    )


def attach_rock(charm_name: str, rock_path: Path, resource_name: str):
    rock_name = rock_path.name.split("_")[0]
    name = image_name(rock_name)
    digest = image_digest(rock_path)
    if not has_image(digest):
        import_image(rock_path, rock_name)
    attach_resource(charm_name, resource_name, name, digest)
