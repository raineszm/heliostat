import gzip
from collections.abc import Iterable

import requests

from heliostat.types import Pocket, Release, Series

UCA_BASE_URL = "https://ubuntu-cloud.archive.canonical.com/ubuntu/dists/"

DEFAULT_RELEASE = {
    "jammy": "yoga",
    "noble": "caracal",
}


def uca_sources_url(series: Series, release: Release, pocket: Pocket = "updates"):
    return f"{UCA_BASE_URL}{series}-{pocket}/{release}/main/source/Sources.gz"


def uca_packages(sources: set[str], series: Series, release: Release):
    url = uca_sources_url(series, release)
    response = requests.get(url)
    response.raise_for_status()

    data = gzip.decompress(response.content).decode("utf-8")

    lines = data.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("Package: "):
            source_pkg = line.split()[1].strip()
            if source_pkg in sources:
                yield from _parse_bin_pkgs(lines, i)

        i += 1


def _parse_bin_pkgs(lines: list[str], start: int) -> Iterable[str]:
    i = start + 1
    while i < len(lines):
        line = lines[i]
        if line.startswith("Package-List:"):
            yield line.removeprefix("Package-List: ").split()[0]
            i += 1
            break
        i += 1
    while i < len(lines) and lines[i].startswith(" "):
        yield lines[i].strip().split()[0]
        i += 1


def rmadison_url(source: str, series: Series):
    return f"https://ubuntu-archive-team.ubuntu.com/madison.cgi?package={source}&a=&c=&s={series}&S=on&text=on"


def madison_packages(source: str, series: Series = "noble") -> Iterable[str]:
    url = rmadison_url(source, series)
    response = requests.get(url)
    response.raise_for_status()
    for line in response.text.splitlines():
        if not line.endswith("source"):
            yield line.split("|")[0].strip()


def package_list(
    src_packages: list[str],
    series: Series,
    release: Release,
) -> Iterable[str]:
    if release == DEFAULT_RELEASE.get(series):
        for src_package in src_packages:
            yield from madison_packages(src_package, series)
        return

    yield from uca_packages(set(src_packages), series, release)
