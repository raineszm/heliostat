import pytest

from heliostat.rocks import (
    CloudPackageRepository,
    PpaPackageRepository,
    RockcraftFile,
    SetVersionString,
)

BASE_YAML = {"name": "test", "parts": {}}

_PATCHABLE_YAML = {
    "name": "test",
    "base": "ubuntu@24.04",
    "version": "1.0",
    "parts": {},
}


@pytest.fixture
def patchable():
    return RockcraftFile(_PATCHABLE_YAML)


class TestRepositories:
    def test_parses_cloud_repo(self):
        yaml = {
            **BASE_YAML,
            "package-repositories": [
                {"type": "apt", "cloud": "epoxy", "priority": "always"}
            ],
        }
        repos = list(RockcraftFile(yaml).repositories())
        assert len(repos) == 1
        assert isinstance(repos[0], CloudPackageRepository)
        assert repos[0].cloud == "epoxy"

    def test_parses_ppa_repo(self):
        yaml = {
            **BASE_YAML,
            "package-repositories": [{"type": "apt", "ppa": "foo/bar"}],
        }
        repos = list(RockcraftFile(yaml).repositories())
        assert len(repos) == 1
        assert isinstance(repos[0], PpaPackageRepository)
        assert repos[0].ppa == "foo/bar"

    def test_empty_when_no_repos_key(self):
        assert list(RockcraftFile(BASE_YAML).repositories()) == []

    def test_multiple_repos(self):
        yaml = {
            **BASE_YAML,
            "package-repositories": [
                {"type": "apt", "cloud": "epoxy", "priority": "always"},
                {"type": "apt", "ppa": "foo/bar"},
            ],
        }
        repos = list(RockcraftFile(yaml).repositories())
        assert len(repos) == 2
        assert isinstance(repos[0], CloudPackageRepository)
        assert isinstance(repos[1], PpaPackageRepository)


class TestDeps:
    def test_collects_overlay_packages_across_parts(self):
        yaml = {
            "name": "test",
            "parts": {
                "part1": {
                    "plugin": "nil",
                    "overlay-packages": ["pkg-a", "pkg-b"],
                },
                "part2": {"plugin": "nil", "overlay-packages": ["pkg-c"]},
            },
        }
        assert RockcraftFile(yaml).deps() == {"pkg-a", "pkg-b", "pkg-c"}

    def test_parts_without_overlay_packages_ignored(self):
        yaml = {
            "name": "test",
            "parts": {"part1": {"plugin": "nil"}},
        }
        assert RockcraftFile(yaml).deps() == set()

    def test_deduplicates_packages(self):
        yaml = {
            "name": "test",
            "parts": {
                "part1": {"plugin": "nil", "overlay-packages": ["pkg-a"]},
                "part2": {"plugin": "nil", "overlay-packages": ["pkg-a"]},
            },
        }
        assert RockcraftFile(yaml).deps() == {"pkg-a"}


class TestPatch:
    def test_returns_new_instance(self, patchable):
        patched = patchable.patch([SetVersionString(suffix="x")])
        assert patched is not patchable

    def test_original_dict_unmodified(self, patchable):
        patchable.patch([SetVersionString(suffix="x")])
        assert patchable.yaml["version"] == "1.0"

    def test_patches_applied_in_order(self, patchable):
        patched = patchable.patch(
            [SetVersionString(suffix="a"), SetVersionString(suffix="b")]
        )
        assert patched.yaml["version"] == "1.0-a-b"

    def test_empty_patch_list_is_identity(self, patchable):
        patched = patchable.patch([])
        assert patched.yaml["version"] == "1.0"
