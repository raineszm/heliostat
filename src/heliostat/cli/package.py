import typer

from heliostat.component import package_list
from heliostat.rocks import SunbeamRockRepo

package_app = typer.Typer()


@package_app.command()
def show(source: str):
    """List all binary packages built from this source package."""
    for binpkg in package_list(source):
        typer.echo(binpkg)


@package_app.command()
def rocks(sources: list[str]):
    """List all rocks built from this source package."""
    repo = SunbeamRockRepo.ensure()
    for rock in repo.rocks_for_packages(*sources):
        typer.echo(rock.name)
