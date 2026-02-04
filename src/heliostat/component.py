import itertools
import subprocess
from collections.abc import Iterable


def package_list(src_package: str) -> Iterable[str]:
    showsrc = subprocess.check_output(["apt-cache", "showsrc", src_package], text=True)

    iter = showsrc.splitlines()
    iter = itertools.dropwhile(lambda x: not x.startswith("Package-List:"), iter)
    next(iter)
    iter = itertools.takewhile(lambda x: not x.startswith("Files:"), iter)
    return map(lambda line: line.split()[0].strip(), iter)
