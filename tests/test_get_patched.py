import copy

from heliostat.rocks import (
    CloudPackageRepository,
    RockPatchOptions,
    PpaPackageRepository,
    RockPatcher,
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


class TestRockPatcher:
    def _patch(
        self,
        *,
        ppa: str | None = None,
        release: Release | None = Release.EPOXY,
        series: Series = Series.NOBLE,
        suffix: str | None = None,
        workarounds=None,
    ) -> RockcraftFile:
        return RockPatcher().patch(
            _rock(),
            RockPatchOptions(
                ppa=ppa,
                release=release,
                series=series,
                suffix=suffix,
                workarounds=workarounds,
            ),
        )

    def test_sets_base_from_series(self):
        result = self._patch(
            ppa=None, release=Release.EPOXY, series=Series.NOBLE
        )
        assert result.yaml["base"] == "ubuntu@24.04"

    def test_ppa_added_when_specified(self):
        result = self._patch(
            ppa="foo/bar", release=Release.EPOXY, series=Series.NOBLE
        )
        repos = list(result.repositories())
        ppa_repos = [r for r in repos if isinstance(r, PpaPackageRepository)]
        assert len(ppa_repos) == 1
        assert ppa_repos[0].ppa == "foo/bar"

    def test_no_ppa_entry_when_not_specified(self):
        result = self._patch(
            ppa=None, release=Release.EPOXY, series=Series.NOBLE
        )
        repos = list(result.repositories())
        assert not any(isinstance(r, PpaPackageRepository) for r in repos)

    def test_version_suffix_appended(self):
        result = self._patch(
            ppa=None,
            release=Release.EPOXY,
            series=Series.NOBLE,
            suffix="heliostat",
        )
        assert result.yaml["version"] == "2024.1-heliostat"

    def test_cloud_repo_appears_before_ppa(self):
        # release patch runs before ppa patch — cloud repo must be index 0
        result = self._patch(
            ppa="foo/bar",
            release=Release.ANTELOPE,
            series=Series.NOBLE,
        )
        repos = list(result.repositories())
        assert isinstance(repos[0], CloudPackageRepository)
        assert isinstance(repos[1], PpaPackageRepository)

    def test_release_updates_cloud_repo_value(self):
        result = self._patch(
            ppa=None, release=Release.ANTELOPE, series=Series.NOBLE
        )
        repos = list(result.repositories())
        assert repos[0].cloud == "antelope"

    def test_workarounds_appended_last(self):
        from heliostat.workarounds.wsgi import WSGIShim

        shim = WSGIShim(module="nova.wsgi", script_name="nova-api")
        result = self._patch(
            ppa=None,
            release=Release.EPOXY,
            series=Series.NOBLE,
            workarounds=[shim],
        )
        assert "wsgi_shim" in result.yaml["parts"]

    def test_no_release_leaves_cloud_repo_unchanged(self):
        result = self._patch(ppa=None, release=None, series=Series.NOBLE)
        repos = list(result.repositories())
        assert repos[0].cloud == "epoxy"
