import typer

from heliostat.component import package_list
from heliostat.rocks import SunbeamRockRepo
from heliostat.types import Release, Series

package_app = typer.Typer()


@package_app.command()
def show(source: str, series: Series = "noble", release: Release = "epoxy"):
    """List all binary packages built from this source package."""
    for binpkg in package_list([source], series=series, release=release):
        typer.echo(binpkg)


@package_app.command()
def rocks(sources: list[str], series: Series = "noble", release: Release = "epoxy"):
    """List all rocks built from this source package."""
    repo = SunbeamRockRepo.ensure()
    for rock in repo.rocks_for_packages(*sources, series=series, release=release):
        typer.echo(rock.name)
