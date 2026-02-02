import shutil
import subprocess
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Annotated

import typer
from ruamel.yaml import YAML

from heliostat.rocks import RockcraftFile, SunbeamRockRepo

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
    cloud: Annotated[str | None, typer.Option()] = None,
):
    rockcraft = _get_patched(rock_name, ppa=ppa, cloud=cloud)

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
    cloud: Annotated[str | None, typer.Option()] = None,
    base: Annotated[str | None, typer.Option()] = None,
):
    rockcraft = _get_patched(rock_name, ppa=ppa, cloud=cloud, base=base)

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
    rock_name: str, ppa: str | None, cloud: str | None, base: str | None
) -> RockcraftFile:
    repo = SunbeamRockRepo.ensure()

    rock = _get_rock(repo, rock_name)

    builder = rock.rockcraft_yaml().patched()

    if ppa:
        builder.with_ppa(ppa)

    if cloud:
        builder.with_cloud(cloud)

    if base:
        builder.with_base(base)

    return builder.build()


@rock_app.callback(no_args_is_help=True)
def _setup():
    pass
