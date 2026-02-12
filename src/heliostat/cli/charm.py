from pathlib import Path

import typer

from heliostat.resources.juju import attach_rock

charm_app = typer.Typer()


@charm_app.command()
def attach(
    charm: str,
    rock: Path,
    resource_name: str,
):
    attach_rock(charm, rock, resource_name)
