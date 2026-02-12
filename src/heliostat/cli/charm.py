from pathlib import Path

import typer

from heliostat.resources.ctr import import_image
from heliostat.resources.juju import attach_rock

charm_app = typer.Typer()


@charm_app.command()
def attach(
    charm: str,
    rock: Path,
):
    rock_name = rock.name.split("_")[0]
    import_image(rock, rock_name)
    attach_rock(charm, rock)
