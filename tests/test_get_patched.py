import copy

from heliostat.cli.rock import _get_patched
from heliostat.rocks import (
    CloudPackageRepository,
    PpaPackageRepository,
    RockcraftFile,
)
from heliostat.types import Release, Series

_BASE_YAML = {
    "name": "test-rock",
    "base": "ubuntu@24.04",
    "version": "2024.1",
    "parts": {"part": {"plugin": "nil", "overlay-packages": ["pkg-a"]}},
    "package-repositories": [
        {"type": "apt", "cloud": "epoxy", "priority": "always"}
    ],
}


def _rock() -> RockcraftFile:
    return RockcraftFile(copy.deepcopy(_BASE_YAML))


class TestGetPatched:
    def test_sets_base_from_series(self):
        result = _get_patched(
            _rock(), ppa=None, release=Release.EPOXY, series=Series.NOBLE
        )
        assert result.yaml["base"] == "ubuntu@24.04"

    def test_ppa_added_when_specified(self):
        result = _get_patched(
            _rock(), ppa="foo/bar", release=Release.EPOXY, series=Series.NOBLE
        )
        repos = list(result.repositories())
        ppa_repos = [r for r in repos if isinstance(r, PpaPackageRepository)]
        assert len(ppa_repos) == 1
        assert ppa_repos[0].ppa == "foo/bar"

    def test_no_ppa_entry_when_not_specified(self):
        result = _get_patched(
            _rock(), ppa=None, release=Release.EPOXY, series=Series.NOBLE
        )
        repos = list(result.repositories())
        assert not any(isinstance(r, PpaPackageRepository) for r in repos)

    def test_version_suffix_appended(self):
        result = _get_patched(
            _rock(),
            ppa=None,
            release=Release.EPOXY,
            series=Series.NOBLE,
            version_suffix="heliostat",
        )
        assert result.yaml["version"] == "2024.1-heliostat"

    def test_cloud_repo_appears_before_ppa(self):
        # release patch runs before ppa patch — cloud repo must be index 0
        result = _get_patched(
            _rock(),
            ppa="foo/bar",
            release=Release.ANTELOPE,
            series=Series.NOBLE,
        )
        repos = list(result.repositories())
        assert isinstance(repos[0], CloudPackageRepository)
        assert isinstance(repos[1], PpaPackageRepository)

    def test_release_updates_cloud_repo_value(self):
        result = _get_patched(
            _rock(), ppa=None, release=Release.ANTELOPE, series=Series.NOBLE
        )
        repos = list(result.repositories())
        assert repos[0].cloud == "antelope"

    def test_workarounds_appended_last(self):
        from heliostat.workarounds.wsgi import WSGIShim

        shim = WSGIShim(module="nova.wsgi", script_name="nova-api")
        result = _get_patched(
            _rock(),
            ppa=None,
            release=Release.EPOXY,
            series=Series.NOBLE,
            workarounds=[shim],
        )
        assert "wsgi_shim" in result.yaml["parts"]
