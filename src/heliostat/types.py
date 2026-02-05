from __future__ import annotations

from enum import StrEnum


class Release(StrEnum):
    YOGA = "yoga"
    ZED = "zed"
    ANTELOPE = "antelope"
    BOBCAT = "bobcat"
    CARACAL = "caracal"
    DALMATIAN = "dalmatian"
    EPOXY = "epoxy"
    FLAMINGO = "flamingo"
    GAZPACHO = "gazpacho"

    @classmethod
    def default(cls) -> Release:
        return cls.EPOXY


class Series(StrEnum):
    JAMMY = "jammy"
    NOBLE = "noble"
    QUESTING = "questing"

    @classmethod
    def default(cls) -> Series:
        return cls.NOBLE

    def to_base(self) -> Base:
        match self:
            case Series.JAMMY:
                return Base.UBUNTU_22_04
            case Series.NOBLE:
                return Base.UBUNTU_24_04
            case Series.QUESTING:
                return Base.UBUNTU_25_10

    def default_release(self) -> Release:
        match self:
            case Series.JAMMY:
                return Release.YOGA
            case Series.NOBLE:
                return Release.CARACAL
            case Series.QUESTING:
                return Release.FLAMINGO


class Base(StrEnum):
    UBUNTU_22_04 = "ubuntu@22.04"
    UBUNTU_24_04 = "ubuntu@24.04"
    UBUNTU_25_10 = "ubuntu@25.10"


class Pocket(StrEnum):
    UPDATES = "updates"
    PROPOSED = "proposed"

    @classmethod
    def default(cls) -> Pocket:
        return cls.UPDATES
