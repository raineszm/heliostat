import copy

from heliostat.rocks import (
    AddPpa,
    RockPatcher,
    RockcraftFile,
    SetBase,
    SetUcaRelease,
    SetVersionString,
)
from heliostat.types import Release, Series

BASE_YAML = {
    "name": "test-rock",
    "base": "ubuntu@24.04",
    "version": "2024.1",
    "parts": {"part": {"plugin": "nil", "overlay-packages": ["pkg-a"]}},
    "package-repositories": [
        {"type": "apt", "cloud": "epoxy", "priority": "always"}
    ],
}


def rockcraft_file() -> RockcraftFile:
    return RockcraftFile(copy.deepcopy(BASE_YAML))


class TestRockPatcherBuildPatches:
    def build_patches(
        self,
        *,
        ppa: str | None = None,
        release: Release | None = Release.EPOXY,
        series: Series = Series.NOBLE,
        suffix: str | None = None,
        workarounds=None,
    ) -> list:
        return RockPatcher(
            ppa=ppa,
            release=release,
            series=series,
            suffix=suffix,
            workarounds=workarounds,
        ).build_patches()

    def test_order_release_then_ppa_then_base_then_suffix(self):
        patches = self.build_patches(
            ppa="foo/bar",
            release=Release.ANTELOPE,
            series=Series.NOBLE,
            suffix="heliostat",
        )
        assert isinstance(patches[0], SetUcaRelease)
        assert isinstance(patches[1], AddPpa)
        assert isinstance(patches[2], SetBase)
        assert isinstance(patches[3], SetVersionString)

    def test_no_ppa_patch_when_not_specified(self):
        patches = self.build_patches(
            ppa=None,
            release=Release.EPOXY,
            series=Series.NOBLE,
        )
        assert not any(isinstance(patch, AddPpa) for patch in patches)

    def test_no_release_patch_when_not_specified(self):
        patches = self.build_patches(
            ppa=None,
            release=None,
            series=Series.NOBLE,
        )
        assert not any(isinstance(patch, SetUcaRelease) for patch in patches)

    def test_workarounds_appended_last(self):
        from heliostat.workarounds.wsgi import WSGIShim

        shim = WSGIShim(module="nova.wsgi", script_name="nova-api")
        patches = self.build_patches(
            ppa=None,
            release=Release.EPOXY,
            series=Series.NOBLE,
            workarounds=[shim],
        )
        assert patches[-1] is shim


class TestRockPatcherPatch:
    def patch(
        self,
        *,
        ppa: str | None = None,
        release: Release | None = Release.EPOXY,
        series: Series = Series.NOBLE,
        suffix: str | None = None,
        workarounds=None,
    ) -> RockcraftFile:
        return RockPatcher(
            ppa=ppa,
            release=release,
            series=series,
            suffix=suffix,
            workarounds=workarounds,
        ).patch(rockcraft_file())

    def test_release_updates_cloud_repo_value(self):
        result = self.patch(
            ppa=None,
            release=Release.ANTELOPE,
            series=Series.NOBLE,
        )
        repos = list(result.repositories())
        assert repos[0].cloud == "antelope"

    def test_workaround_patch_is_applied(self):
        from heliostat.workarounds.wsgi import WSGIShim

        shim = WSGIShim(module="nova.wsgi", script_name="nova-api")
        result = self.patch(
            ppa=None,
            release=Release.EPOXY,
            series=Series.NOBLE,
            workarounds=[shim],
        )
        assert "wsgi_shim" in result.yaml["parts"]
