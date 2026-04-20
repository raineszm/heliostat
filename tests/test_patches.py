from heliostat.rocks import AddPpa, SetBase, SetUcaRelease, SetVersionString
from heliostat.types import Base, Release, Series


class TestAddPpa:
    def test_adds_ppa_to_empty_repos(self):
        yaml = {"name": "test", "parts": {}}
        AddPpa(ppa="foo/bar").apply(yaml)
        assert yaml["package-repositories"] == [
            {"type": "apt", "ppa": "foo/bar"}
        ]

    def test_appends_to_existing_repos(self):
        yaml = {
            "name": "test",
            "parts": {},
            "package-repositories": [
                {"type": "apt", "cloud": "epoxy", "priority": "always"}
            ],
        }
        AddPpa(ppa="foo/bar").apply(yaml)
        assert len(yaml["package-repositories"]) == 2
        assert yaml["package-repositories"][1] == {
            "type": "apt",
            "ppa": "foo/bar",
        }


class TestSetUcaRelease:
    def test_updates_cloud_field_in_existing_repo(self):
        yaml = {
            "name": "test",
            "parts": {},
            "package-repositories": [
                {"type": "apt", "cloud": "epoxy", "priority": "always"}
            ],
        }
        SetUcaRelease(release=Release.ANTELOPE, series=Series.NOBLE).apply(
            yaml
        )
        assert yaml["package-repositories"][0]["cloud"] == "antelope"

    def test_creates_cloud_repo_when_none_exists(self):
        yaml = {"name": "test", "parts": {}}
        SetUcaRelease(release=Release.ANTELOPE, series=Series.NOBLE).apply(
            yaml
        )
        assert yaml["package-repositories"][0]["cloud"] == "antelope"

    def test_removes_cloud_repo_for_default_series_release_pairing(self):
        # noble's default release is caracal — no UCA repo needed
        yaml = {
            "name": "test",
            "parts": {},
            "package-repositories": [
                {"type": "apt", "cloud": "epoxy", "priority": "always"}
            ],
        }
        SetUcaRelease(release=Release.CARACAL, series=Series.NOBLE).apply(yaml)
        assert yaml["package-repositories"] == []

    def test_default_pairing_with_no_existing_repos_is_noop(self):
        yaml = {"name": "test", "parts": {}}
        SetUcaRelease(release=Release.CARACAL, series=Series.NOBLE).apply(yaml)
        assert yaml.get("package-repositories") == []


class TestSetBase:
    def test_sets_base_from_series(self):
        yaml = {"name": "test", "base": "ubuntu@22.04", "parts": {}}
        SetBase(series_or_base=Series.NOBLE).apply(yaml)
        assert yaml["base"] == "ubuntu@24.04"

    def test_sets_base_from_base_enum(self):
        yaml = {"name": "test", "base": "ubuntu@22.04", "parts": {}}
        SetBase(series_or_base=Base.UBUNTU_24_04).apply(yaml)
        assert yaml["base"] == "ubuntu@24.04"

    def test_sets_jammy_base(self):
        yaml = {"name": "test", "base": "ubuntu@24.04", "parts": {}}
        SetBase(series_or_base=Series.JAMMY).apply(yaml)
        assert yaml["base"] == "ubuntu@22.04"


class TestSetVersionString:
    def test_appends_suffix_with_hyphen(self):
        yaml = {"name": "test", "version": "2024.1", "parts": {}}
        SetVersionString(suffix="heliostat").apply(yaml)
        assert yaml["version"] == "2024.1-heliostat"

    def test_appends_to_already_suffixed_version(self):
        yaml = {"name": "test", "version": "2024.1-foo", "parts": {}}
        SetVersionString(suffix="bar").apply(yaml)
        assert yaml["version"] == "2024.1-foo-bar"
