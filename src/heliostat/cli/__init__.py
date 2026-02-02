import typer

from . import rock

main = typer.Typer()
main.add_typer(rock.rock_app, name="rock")


@main.callback(no_args_is_help=True)
def _setup():
    pass


if __name__ == "__main__":
    main()
