import shutil

import typer

from heliostat.cli._bins import check_bins
from heliostat.component import NetworkPackageResolver

from heliostat.rocks import SunbeamRockRepo
from heliostat.types import Release, Series

package_app = typer.Typer()


@package_app.command()
def show(
    source: str,
    series: Series = Series.default(),
    release: Release = Release.default(),
):
    """List all binary packages built from this source package."""
    resolver = NetworkPackageResolver()

    for binpkg in resolver.binaries_for_source(
        {source}, series=series, release=release
    ):
        typer.echo(binpkg)


@package_app.command()
def rocks(
    sources: list[str],
    series: Series = Series.default(),
    release: Release = Release.default(),
    consolidated: bool = False,
):
    """List all rocks built from this source package."""
    check_bins([shutil.which("git") or "/usr/bin/git"])
    repo = SunbeamRockRepo.ensure(release=release)

    resolver = NetworkPackageResolver()

    for rock in repo.rocks_for_packages(
        *sources,
        series=series,
        release=release,
        resolver=resolver,
        consolidated=consolidated,
    ):
        typer.echo(rock.name)


@package_app.callback(no_args_is_help=True)
def _setup():
    pass
