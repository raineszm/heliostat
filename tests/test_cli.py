"""Smoke tests for the heliostat CLI."""

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from heliostat.cli import main
from heliostat.rocks import RockcraftFile, SunbeamRock

runner = CliRunner()

CINDER_CONSOLIDATED_YAML = {
    "name": "cinder-consolidated",
    "base": "ubuntu@24.04",
    "version": "2024.1",
    "parts": {
        "cinder": {
            "plugin": "nil",
            "overlay-packages": [
                "sudo",
                "sysfsutils",
                "cinder-volume",
                "tgt",
                "nfs-common",
                "cinder-scheduler",
                "ceph-common",
                "cinder-api",
            ],
        }
    },
    "package-repositories": [
        {
            "type": "apt",
            "cloud": "epoxy",
            "priority": "always",
        }
    ],
}

CINDER_API_YAML = {
    "name": "cinder-api",
    "base": "ubuntu@24.04",
    "version": "2024.1",
    "parts": {
        "cinder": {
            "plugin": "nil",
            "overlay-packages": ["sudo", "cinder-api"],
        }
    },
    "package-repositories": [
        {"type": "apt", "cloud": "epoxy", "priority": "always"}
    ],
}

# Binary packages that cinder source produces
CINDER_BINARY_PACKAGES = [
    "cinder-api",
    "cinder-backup",
    "cinder-common",
    "cinder-scheduler",
    "cinder-volume",
    "python3-cinder",
]


def make_mock_rock(name: str, yaml_data: dict) -> MagicMock:
    """Create a mock SunbeamRock with the given name and yaml data."""
    rock = MagicMock(spec=SunbeamRock)
    rock.name = name
    rock.rockcraft_yaml.return_value = RockcraftFile(yaml_data.copy())
    return rock


def make_mock_repo() -> MagicMock:
    """Create a configured SunbeamRockRepo mock instance."""
    mock_instance = MagicMock()

    mock_cinder_consolidated = make_mock_rock(
        "cinder-consolidated", CINDER_CONSOLIDATED_YAML
    )
    mock_cinder_api = make_mock_rock("cinder-api", CINDER_API_YAML)

    all_rocks = [mock_cinder_consolidated, mock_cinder_api]
    rocks_by_name = {r.name: r for r in all_rocks}

    def get_rocks(names=None):
        if names is None:
            return all_rocks
        return [r for r in all_rocks if r.name in names]

    mock_instance.rocks.side_effect = get_rocks

    def get_rock(name):
        if name in rocks_by_name:
            return rocks_by_name[name]
        raise ValueError(f"No rock found with name '{name}'")

    mock_instance.rock.side_effect = get_rock

    def rocks_for_packages(*sources, **kwargs):
        if sources:
            return all_rocks
        return []

    mock_instance.rocks_for_packages.side_effect = rocks_for_packages

    return mock_instance


# =============================================================================
# General CLI Tests
# =============================================================================


class TestMainCli:
    def test_help(self):
        """Main --help shows available subcommands."""
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "rock" in result.output
        assert "package" in result.output

    def test_no_args_shows_help(self):
        """Running with no args shows help."""
        result = runner.invoke(main, [])
        # typer returns exit code 2 for no_args_is_help
        assert result.exit_code == 2
        assert "Usage" in result.output


# =============================================================================
# Rock Command Tests
# =============================================================================


class TestRockCommands:
    def test_rock_no_args_shows_help(self):
        """rock (no args) shows help."""
        result = runner.invoke(main, ["rock"])
        # typer returns exit code 2 for no_args_is_help
        assert result.exit_code == 2
        assert "Usage" in result.output

    @patch("heliostat.cli.rock.SunbeamRockRepo")
    def test_rock_list(self, mock_repo_cls):
        """rock list shows available rocks."""
        mock_repo_cls.ensure.return_value = make_mock_repo()
        result = runner.invoke(main, ["rock", "list"])
        assert result.exit_code == 0
        assert "cinder-consolidated" in result.output

    @patch("heliostat.cli.rock.SunbeamRockRepo")
    def test_rock_list_with_release(self, mock_repo_cls):
        """rock list --release accepts release option."""
        mock_repo_cls.ensure.return_value = make_mock_repo()
        result = runner.invoke(main, ["rock", "list", "--release", "caracal"])
        assert result.exit_code == 0

    @patch("heliostat.cli.rock.SunbeamRockRepo")
    def test_rock_show(self, mock_repo_cls):
        """rock show displays rock info."""
        mock_repo_cls.ensure.return_value = make_mock_repo()
        result = runner.invoke(main, ["rock", "show", "cinder-consolidated"])
        assert result.exit_code == 0
        assert "CloudPackageRepository" in result.output

    @patch("heliostat.cli.rock.SunbeamRockRepo")
    def test_rock_show_nonexistent(self, mock_repo_cls):
        """rock show with invalid rock name returns error."""
        mock_repo_cls.ensure.return_value = make_mock_repo()
        result = runner.invoke(main, ["rock", "show", "nonexistent-rock"])
        assert result.exit_code == 1
        assert "no rock found" in result.output.lower()

    @patch("heliostat.cli.rock.SunbeamRockRepo")
    def test_rock_patch(self, mock_repo_cls):
        """rock patch returns YAML output."""
        mock_repo_cls.ensure.return_value = make_mock_repo()
        result = runner.invoke(main, ["rock", "patch", "cinder-consolidated"])
        assert result.exit_code == 0
        assert "name: cinder-consolidated" in result.output

    @patch("heliostat.cli.rock.SunbeamRockRepo")
    def test_rock_patch_with_ppa(self, mock_repo_cls):
        """rock patch --ppa adds the PPA to the emitted YAML."""
        mock_repo_cls.ensure.return_value = make_mock_repo()
        result = runner.invoke(
            main,
            [
                "rock",
                "patch",
                "cinder-consolidated",
                "--ppa",
                "ppa:myteam/myrepo",
            ],
        )
        assert result.exit_code == 0
        assert "myteam/myrepo" in result.output

    @patch("heliostat.cli.rock.do_build")
    @patch("heliostat.cli.rock.SunbeamRockRepo")
    def test_rock_build(self, mock_repo_cls, mock_do_build):
        """rock build invokes do_build."""
        mock_repo_cls.ensure.return_value = make_mock_repo()
        result = runner.invoke(
            main, ["rock", "build", "--rock", "cinder-consolidated"]
        )
        assert result.exit_code == 0
        mock_do_build.assert_called_once()


# =============================================================================
# Package Command Tests
# =============================================================================


class TestPackageCommands:
    def test_package_no_args_shows_help(self):
        """package (no args) shows help."""
        result = runner.invoke(main, ["package"])
        assert result.exit_code == 2
        assert "Usage" in result.output

    @patch("heliostat.cli.package.package_list")
    def test_package_show(self, mock_package_list):
        """package show displays binary packages."""
        mock_package_list.return_value = CINDER_BINARY_PACKAGES
        result = runner.invoke(main, ["package", "show", "cinder"])
        assert result.exit_code == 0
        assert "cinder-api" in result.output

    @patch("heliostat.cli.package.SunbeamRockRepo")
    def test_package_rocks(self, mock_repo_cls):
        """package rocks lists rocks containing packages."""
        mock_repo_cls.ensure.return_value = make_mock_repo()
        result = runner.invoke(main, ["package", "rocks", "cinder"])
        assert result.exit_code == 0
        assert "cinder-consolidated" in result.output
