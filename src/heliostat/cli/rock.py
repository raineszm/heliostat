import itertools
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
    RockcraftFile,
    SetBase,
    SetUcaRelease,
    SetVersionString,
    SunbeamRockRepo,
)
from heliostat.types import Release, Series
from heliostat.workarounds import Workaround, get_workarounds

rock_app = typer.Typer()


def _get_rock(
    rock_name: str,
    repo: SunbeamRockRepo | None = None,
    release: Release = Release.default(),
):
    if repo is None:
        repo = SunbeamRockRepo.ensure(release=release)
    try:
        rock = repo.rock(rock_name)
    except ValueError as e:
        typer.echo(str(e))
        raise typer.Exit(code=1)
    return rock


def _parse_ppa(ppa: str) -> str:
    return ppa.removeprefix("ppa:")


@rock_app.command(name="list")
def list_cmd(release: Annotated[Release, typer.Option()] = Release.default()):
    repo = SunbeamRockRepo.ensure(release=release)

    for folder in repo.rocks():
        typer.echo(folder.name)


@rock_app.command()
def show(
    rock_name: str,
    release: Annotated[Release, typer.Option()] = Release.default(),
):
    rock = _get_rock(rock_name, release=release)
    typer.echo(f"Rock: {rock.name}")
    typer.echo("Repositories:")
    for pkg_repo in rock.rockcraft_yaml().repositories():
        typer.echo(pkg_repo)
    typer.echo("Dependencies:")
    for dep in rock.rockcraft_yaml().deps():
        typer.echo(dep)


@rock_app.command()
def patch(
    rock_name: str,
    output: Annotated[
        Path | None,
        typer.Option(
            "-o",
            "--output",
            help="Output rockraft.yaml file to a specific path "
            "(Default: stdout)",
        ),
    ] = None,
    ppa: Annotated[
        str | None,
        typer.Option(
            parser=_parse_ppa,
        ),
    ] = None,
    release: Annotated[Release, typer.Option()] = Release.default(),
    series: Annotated[Series, typer.Option()] = Series.default(),
    suffix: Annotated[
        str,
        typer.Option(
            help="Version suffix for the rock",
        ),
    ] = "heliostat",
    enable_workarounds: Annotated[
        bool,
        typer.Option(
            help="Automatically apply workarounds for common incompatibilities"
            " between sunbeam charms and unsupported openstack versions",
        ),
    ] = True,
):
    rock = _get_rock(rock_name, release=release)

    if enable_workarounds:
        workarounds = get_workarounds(rock, release, series)
    else:
        workarounds = []
    rockcraft = _get_patched(
        rock.rockcraft_yaml(),
        ppa=ppa,
        release=release,
        series=series,
        version_suffix=suffix,
        workarounds=workarounds,
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
    rocks: Annotated[
        list[str],
        typer.Option(
            "--rock",
            help="Name of the rock to build",
        ),
    ] = [],
    sources: Annotated[
        list[str],
        typer.Option(
            "--source",
            help="Source URL for the rock",
        ),
    ] = [],
    output_dir: Annotated[
        Path | None,
        typer.Option(
            "-o",
            "--output-dir",
            help="Output directory for the built rock "
            "(Default: current working directory)",
        ),
    ] = None,
    ppa: Annotated[
        str | None,
        typer.Option(
            parser=_parse_ppa,
        ),
    ] = None,
    release: Annotated[Release, typer.Option()] = Release.default(),
    series: Annotated[Series, typer.Option()] = Series.default(),
    suffix: Annotated[
        str,
        typer.Option(
            help="Version suffix for the rock",
        ),
    ] = "heliostat",
    consolidated: Annotated[
        bool,
        typer.Option(
            help="Build only a single consolidated rock for this package if "
            "the option is available.",
        ),
    ] = False,
    enable_workarounds: Annotated[
        bool,
        typer.Option(
            help="Automatically apply workarounds for common incompatibilities"
            " between sunbeam charms and unsupported openstack versions",
        ),
    ] = True,
):
    output_dir = output_dir or Path.cwd()

    repo = SunbeamRockRepo.ensure(release=release)

    for rock in itertools.chain(
        repo.rocks(set(rocks)),
        repo.rocks_for_packages(*sources, series=series, release=release),
    ):
        if enable_workarounds:
            workarounds = get_workarounds(rock, release, series)
        else:
            workarounds = []
        rockcraft = _get_patched(
            rock.rockcraft_yaml(),
            ppa=ppa,
            release=release,
            series=series,
            version_suffix=suffix,
            workarounds=workarounds,
        )

        do_build(rock.name, rockcraft, output_dir, workarounds=workarounds)


def do_build(
    rock_name: str,
    rockcraft: RockcraftFile,
    output_dir: Path,
    workarounds: list[Workaround],
):
    with TemporaryDirectory(suffix=rock_name, prefix="heliostat") as build_dir:
        build_dir = Path(build_dir)
        for workaround in workarounds:
            workaround.pre_build(build_dir)
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
    series: Series,
    version_suffix: str | None = None,
    workarounds: list[Workaround] | None = None,
) -> RockcraftFile:
    patches = []
    if ppa:
        patches.append(AddPpa(ppa=ppa))

    if release:
        patches.append(SetUcaRelease(release=release, series=series))

    patches.append(SetBase(series_or_base=series))

    if version_suffix:
        patches.append(SetVersionString(suffix=version_suffix))

    if workarounds:
        patches.extend(workarounds)

    return rock.patch(patches)


@rock_app.callback(no_args_is_help=True)
def _setup():
    pass
