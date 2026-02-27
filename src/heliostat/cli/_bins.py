import os

import typer


def check_bins(bins: list[str]):
    missing_bins = [exe for exe in bins if not os.path.exists(exe)]

    if missing_bins:
        typer.echo(
            "Commands required for this functionality are not available."
        )
        typer.echo(
            f"Please make sure the following are installed: {
                ', '.join(os.path.basename(exe) for exe in missing_bins)
            }"
        )
        raise typer.Exit(1)
