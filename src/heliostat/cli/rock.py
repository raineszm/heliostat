from io import StringIO
from typing import Annotated

import typer
from ruamel.yaml import YAML

from heliostat.rocks import SunbeamRockRepo

rock_app = typer.Typer()


def _get_rock(repo: SunbeamRockRepo, rock_name: str):
    try:
        rock = repo.rock(rock_name)
    except ValueError as e:
        typer.echo(str(e))
        raise typer.Exit(code=1)
    return rock


@rock_app.command()
def list():
    repo = SunbeamRockRepo.ensure()

    for folder in repo.rocks():
        typer.echo(folder.name)


@rock_app.command()
def show(rock_name: str):
    repo = SunbeamRockRepo.ensure()

    rock = _get_rock(repo, rock_name)
    typer.echo(f"Rock: {rock.name}")
    for pkg_repo in rock.rockcraft_yaml().repositories():
        typer.echo(f"Cloud: {pkg_repo.cloud}")


@rock_app.command()
def create(rock_name: str, ppa: Annotated[str | None, typer.Option()] = None):
    repo = SunbeamRockRepo.ensure()

    rock = _get_rock(repo, rock_name)

    builder = rock.rockcraft_yaml().patched()

    if ppa:
        builder.with_ppa(ppa)

    yaml = YAML()
    with StringIO() as f:
        yaml.dump(builder.build().yaml, f)
        typer.echo(f.getvalue())


@rock_app.callback(no_args_is_help=True)
def _setup():
    pass
