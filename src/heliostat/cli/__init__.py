import typer

from . import charm, package, rock

main = typer.Typer()
main.add_typer(rock.rock_app, name="rock")
main.add_typer(package.package_app, name="package")
main.add_typer(charm.charm_app, name="charm")


@main.callback(no_args_is_help=True)
def _setup():
    pass


if __name__ == "__main__":
    main()
