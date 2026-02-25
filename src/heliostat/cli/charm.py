from pathlib import Path

import typer

from heliostat.cli._bins import check_bins
from heliostat.resources.ctr import CTR_BIN
from heliostat.resources.juju import JUJU_BIN, attach_rock

charm_app = typer.Typer()


@charm_app.callback(no_args_is_help=True)
def _setup():
    check_bins([JUJU_BIN, CTR_BIN])


@charm_app.command()
def attach(
    charm: str,
    rock: Path,
    resource_name: str,
):
    attach_rock(charm, rock, resource_name)
