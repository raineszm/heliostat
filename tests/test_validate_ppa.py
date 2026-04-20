import pytest
import typer

from heliostat.cli.rock import validate_ppa


class TestValidatePpa:
    def test_none_returns_none(self):
        assert validate_ppa(None) is None

    def test_valid_ppa_with_prefix_strips_prefix(self):
        assert validate_ppa("ppa:myteam/myrepo") == "myteam/myrepo"

    def test_valid_ppa_without_prefix_unchanged(self):
        assert validate_ppa("myteam/myrepo") == "myteam/myrepo"

    def test_ppa_with_numbers_and_dots(self):
        assert validate_ppa("ppa:team1/repo.2") == "team1/repo.2"

    def test_invalid_no_slash(self):
        with pytest.raises(typer.BadParameter):
            validate_ppa("ppa:justonepart")

    def test_invalid_plain_string(self):
        with pytest.raises(typer.BadParameter):
            validate_ppa("not-a-ppa")

    def test_invalid_uppercase(self):
        with pytest.raises(typer.BadParameter):
            validate_ppa("ppa:MyTeam/MyRepo")
