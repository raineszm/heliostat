import gzip
from collections.abc import Iterable
from typing import Protocol

import requests
from debian import deb822
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from heliostat.types import Pocket, Release, Series

UCA_BASE_URL = "https://ubuntu-cloud.archive.canonical.com/ubuntu/dists/"
REQUEST_TIMEOUT = 10
REQUEST_RETRIES = 3


def uca_sources_url(
    series: Series, release: Release, pocket: Pocket = Pocket.UPDATES
):
    return f"{UCA_BASE_URL}{series}-{pocket}/{release}/main/source/Sources.gz"


def rmadison_url(source: str, series: Series):
    return f"https://ubuntu-archive-team.ubuntu.com/madison.cgi?package={source}&a=&c=&s={series}&S=on&text=on"


def build_retrying_session() -> requests.Session:
    retry = Retry(
        total=REQUEST_RETRIES,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


class PackageResolver(Protocol):
    def binaries_for_source(
        self,
        src_packages: set[str],
        *,
        series: Series,
        release: Release,
    ) -> Iterable[str]: ...


class NetworkPackageResolver:
    def __init__(
        self,
        session: requests.Session | None = None,
        timeout: float = REQUEST_TIMEOUT,
    ):
        self.session = build_retrying_session() if session is None else session
        self.timeout = timeout

    def binaries_for_source(
        self,
        src_packages: set[str],
        *,
        series: Series,
        release: Release,
    ) -> Iterable[str]:

        if release == series.default_release():
            for source in src_packages:
                yield from self.madison_packages(source, series)
            return

        yield from self.uca_packages(src_packages, series, release)

    def uca_packages(
        self, src_packages: set[str], series: Series, release: Release
    ) -> Iterable[str]:
        response = self.session.get(
            uca_sources_url(series, release), timeout=self.timeout
        )
        response.raise_for_status()
        data = gzip.decompress(response.content).decode("utf-8")
        for source_pkg in deb822.Sources.iter_paragraphs(
            data, use_apt_pkg=False
        ):
            if source_pkg["Package"] in src_packages:
                yield from (
                    pkg["package"] for pkg in source_pkg["Package-List"]
                )

    def madison_packages(
        self, source: str, series: Series = Series.default()
    ) -> Iterable[str]:
        response = self.session.get(
            rmadison_url(source, series), timeout=self.timeout
        )
        response.raise_for_status()
        for line in response.text.splitlines():
            if not line.endswith("source"):
                yield line.split("|")[0].strip()


DEFAULT_PACKAGE_RESOLVER = NetworkPackageResolver()
