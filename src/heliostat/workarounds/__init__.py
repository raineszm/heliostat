from heliostat.rocks import SunbeamRock
from heliostat.types import Release, Series

from .workaround import Workaround
from .wsgi import WSGIShim


def get_workarounds(
    rock: SunbeamRock, release: Release, series: Series
) -> list[Workaround]:
    result = []

    if (
        rock.name in {"octavia-api", "octavia-consolidated"}
        and release >= Release.FLAMINGO
    ):
        result.append(WSGIShim("octavia.wsgi.api", "octavia-wsgi"))

    return result
