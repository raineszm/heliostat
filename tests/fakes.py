class FakePackageResolver:
    def __init__(self, packages_by_source: dict[str, list[str]]):
        self.packages_by_source = packages_by_source

    def binaries_for_source(self, src_packages, *, series, release):
        del series, release
        for src_package in src_packages:
            yield from self.packages_by_source.get(src_package, ())
