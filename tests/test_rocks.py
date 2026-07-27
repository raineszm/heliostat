from pathlib import Path

from heliostat.component import StaticPackageResolver
from heliostat.rocks import SunbeamRockRepo
from heliostat.types import Release, Series


def write_rock(tmp_path: Path, name: str, deps: list[str]) -> None:
    rock_dir = tmp_path / "rocks" / name
    rock_dir.mkdir(parents=True)
    overlay = "\n".join(f"      - {dep}" for dep in deps)
    (rock_dir / "rockcraft.yaml").write_text(
        f"""name: {name}
base: ubuntu@24.04
version: \"1.0\"
parts:
  app:
    plugin: nil
    overlay-packages:
{overlay}
"""
    )


def test_rocks_for_packages_filters_with_static_resolver(tmp_path):
    write_rock(tmp_path, "cinder-consolidated", ["cinder-api", "sudo"])
    write_rock(tmp_path, "nova-api", ["nova-api", "sudo"])
    resolver = StaticPackageResolver({"cinder": ["cinder-api"]})

    repo = SunbeamRockRepo(tmp_path)
    result = [
        rock.name
        for rock in repo.rocks_for_packages(
            "cinder",
            series=Series.NOBLE,
            release=Release.ANTELOPE,
            resolver=resolver,
        )
    ]

    assert result == ["cinder-consolidated"]


def test_rocks_for_packages_consolidates_family_when_requested(tmp_path):
    write_rock(tmp_path, "cinder-api", ["cinder-api"])
    write_rock(tmp_path, "cinder-consolidated", ["cinder-api"])
    resolver = StaticPackageResolver({"cinder": ["cinder-api"]})

    repo = SunbeamRockRepo(tmp_path)
    unconsolidated = [
        rock.name
        for rock in repo.rocks_for_packages(
            "cinder",
            series=Series.NOBLE,
            release=Release.ANTELOPE,
            consolidated=False,
            resolver=resolver,
        )
    ]
    consolidated = [
        rock.name
        for rock in repo.rocks_for_packages(
            "cinder",
            series=Series.NOBLE,
            release=Release.ANTELOPE,
            consolidated=True,
            resolver=resolver,
        )
    ]

    assert unconsolidated == ["cinder-api", "cinder-consolidated"]
    assert consolidated == ["cinder-consolidated"]
