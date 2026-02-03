import shutil
import subprocess
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Annotated

import typer
from ruamel.yaml import YAML

from heliostat.rocks import (
    AddPpa,
    Release,
    RockcraftFile,
    Series,
    SetBase,
    SetUcaRelease,
    SunbeamRockRepo,
)

rock_app = typer.Typer()


def _get_rock(rock_name: str, repo: SunbeamRockRepo | None = None):
    if repo is None:
        repo = SunbeamRockRepo.ensure()
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
    rock = _get_rock(rock_name)
    typer.echo(f"Rock: {rock.name}")
    for pkg_repo in rock.rockcraft_yaml().repositories():
        typer.echo(pkg_repo)


@rock_app.command()
def patch(
    rock_name: str,
    output: Annotated[
        Path | None,
        typer.Option(
            "-o",
            "--output",
            help="Output rockraft.yaml file to a specific path (Default: stdout)",
        ),
    ] = None,
    ppa: Annotated[str | None, typer.Option()] = None,
    release: Annotated[Release | None, typer.Option()] = None,
    series: Annotated[Series | None, typer.Option()] = None,
):
    rock = _get_rock(rock_name)
    rockcraft = _get_patched(
        rock.rockcraft_yaml(), ppa=ppa, release=release, series=series
    )

    yaml = YAML()
    if output is None:
        with StringIO() as f:
            yaml.dump(rockcraft.yaml, f)
            typer.echo(f.getvalue())
    else:
        with output.open("w") as f:
            yaml.dump(rockcraft.yaml, f)


@rock_app.command()
def build(
    rock_name: str,
    output_dir: Annotated[
        Path | None,
        typer.Option(
            "-o",
            "--output-dir",
            help="Output directory for the built rock (Default: current working directory)",
        ),
    ] = None,
    ppa: Annotated[str | None, typer.Option()] = None,
    release: Annotated[Release | None, typer.Option()] = None,
    series: Annotated[Series | None, typer.Option()] = None,
):
    rock = _get_rock(rock_name)
    rockcraft = _get_patched(
        rock.rockcraft_yaml(), ppa=ppa, release=release, series=series
    )

    output_dir = output_dir or Path.cwd()

    with TemporaryDirectory(suffix=rock_name, prefix="heliostat") as build_dir:
        build_dir = Path(build_dir)
        yaml = YAML()
        yaml.dump(rockcraft.yaml, build_dir / "rockcraft.yaml")
        try:
            subprocess.check_call(["rockcraft", "pack"], cwd=build_dir)
        except subprocess.CalledProcessError as e:
            typer.echo(f"Build failed with error code {e.returncode}")
            raise typer.Exit(1)
        for file in build_dir.glob("*.rock"):
            shutil.copy(build_dir / file, output_dir)


def _get_patched(
    rock: RockcraftFile,
    ppa: str | None,
    release: Release | None,
    series: Series | None,
) -> RockcraftFile:
    patches = []
    if ppa:
        patches.append(AddPpa(ppa=ppa))

    if release:
        patches.append(SetUcaRelease(release=release, series=series))

    if series:
        patches.append(SetBase(series_or_base=series))

    return rock.patch(patches)


@rock_app.callback(no_args_is_help=True)
def _setup():
    pass
