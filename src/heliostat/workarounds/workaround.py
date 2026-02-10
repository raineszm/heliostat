from pathlib import Path

from heliostat.rocks import Patch


class Workaround(Patch):
    def pre_build(self, build_path: Path): ...
