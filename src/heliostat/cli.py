import typer

from heliostat.rocks import SunbeamRockRepo

main = typer.Typer()


@main.command()
def rocks():
    repo = SunbeamRockRepo()
    repo.ensure_repo()

    for folder in repo.rocks():
        typer.echo(folder.name)


@main.command()
def cloud(rock_name: str):
    repo = SunbeamRockRepo()
    repo.ensure_repo()
    matches = [f for f in repo.rocks() if f.name == rock_name]

    if not matches:
        typer.echo(f"No rock found with name '{rock_name}'")
        raise typer.Exit(code=1)

    folder = matches[0]
    typer.echo(f"Rock: {folder.name}")
    for pkg_repo in folder.rockcraft_yaml().repositories():
        typer.echo(f"Cloud: {pkg_repo.cloud}")


@main.command()
def help(ctx: typer.Context):
    typer.echo(ctx.get_help())


if __name__ == "__main__":
    main()
