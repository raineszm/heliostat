"""
Workaround for projects which have switched from a WSGI script to a WSGI
application module.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .workaround import Workaround


@dataclass
class WSGIShim(Workaround):
    module: str
    script_name: str

    def script(self) -> str:
        return f"""
        from {self.module} import application
        """

    def part(
        self,
    ) -> dict[str, Any]:
        return {
            "plugin": "dump",
            "source": ".",
            "source-type": "local",
            "organize": {f"{self.script_name}": "usr/bin/"},
            "stage": ["usr"],
        }

    def apply(self, rockcraft: dict[str, Any]):
        rockcraft["parts"]["wsgi_shim"] = self.part()

    def pre_build(self, build_path: Path):
        with open(build_path / self.script_name, "w") as f:
            f.write(self.script())
