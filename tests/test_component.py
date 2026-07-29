import functools
import gzip

import responses

from heliostat.component import (
    NetworkPackageResolver,
    rmadison_url,
    uca_sources_url,
)
from heliostat.types import Release, Series

# Debian Sources stanza for cinder from jammy-caracal, gzip-compressed
# ruff: disable[E501]
_SOURCES_GZ = gzip.compress(b"""\
Package: cinder
Binary: cinder-api, cinder-backup, cinder-common, cinder-scheduler, cinder-volume, python3-cinder
Version: 2:24.2.0-0ubuntu2~cloud0
Section: net
Maintainer: Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>
Build-Depends: apache2-dev, debhelper-compat (= 13), dh-apache2, dh-python, openstack-pkg-tools (>= 123ubuntu2~), python3-all, python3-pbr (>= 5.8.0), python3-setuptools, python3-sphinx (>= 3.5.1), python3-tabulate (>= 0.8.7), qemu-utils
Build-Depends-Indep: python3-barbicanclient (>= 5.0.1), python3-boto3 (>= 1.18.49), python3-botocore, python3-castellan (>= 3.7.0), python3-coverage, python3-cryptography (>= 3.1), python3-cursive (>= 0.2.2), python3-ddt (>= 1.4.4), python3-decorator (>= 4.4.2), python3-distro (>= 1.8.0), python3-doc8, python3-eventlet (>= 0.30.1), python3-fixtures (>= 3.0.0), python3-glanceclient (>= 1:3.2.2), python3-googleapi (>= 1.7.11), python3-greenlet (>= 0.4.16), python3-hacking, python3-httplib2 (>= 0.18.1), python3-importlib-metadata (>= 3.1.1), python3-iso8601 (>= 0.1.12), python3-jsonschema (>= 3.2.0), python3-keystoneauth1 (>= 4.2.1), python3-keystoneclient (>= 1:4.1.1), python3-keystonemiddleware (>= 9.1.0), python3-lxml (>= 4.5.2), python3-migrate (>= 0.13.0), python3-mock (>= 2.0.0), python3-mypy, python3-novaclient (>= 2:18.2.0), python3-oauth2client (>= 4.1.3), python3-openstackdocstheme (>= 2.2.7), python3-os-api-ref (>= 2.1.0), python3-os-brick (>= 6.0.0), python3-os-win (>= 5.5.0), python3-oslo.concurrency (>= 4.5.0), python3-oslo.config (>= 1:8.3.2), python3-oslo.context (>= 1:3.4.0), python3-oslo.db (>= 11.0.0), python3-oslo.i18n (>= 5.1.0), python3-oslo.log (>= 4.6.1), python3-oslo.messaging (>= 14.1.0), python3-oslo.middleware (>= 4.1.1), python3-oslo.policy (>= 3.8.1), python3-oslo.privsep (>= 2.6.2), python3-oslo.reports (>= 2.2.0), python3-oslo.rootwrap (>= 6.2.0), python3-oslo.serialization (>= 4.2.0), python3-oslo.service (>= 2.8.0), python3-oslo.upgradecheck (>= 1.1.1), python3-oslo.utils (>= 6.0.0), python3-oslo.versionedobjects (>= 2.4.0), python3-oslo.vmware (>= 3.10.0), python3-oslotest (>= 1:4.5.0), python3-osprofiler (>= 3.4.0), python3-packaging (>= 20.4), python3-paramiko (>= 2.7.2), python3-paste (>= 3.4.3), python3-pastedeploy (>= 2.1.0), python3-pep8, python3-prettytable (>= 0.7.1), python3-psutil (>= 5.7.2), python3-psycopg2 (>= 2.8.5), python3-pymysql (>= 0.10.0), python3-pyparsing (>= 2.4.7), python3-requests (>= 2.25.1), python3-retrying (>= 1.2.3), python3-routes (>= 2.4.1), python3-rtslib-fb (>= 2.1.74), python3-six (>= 1.15.0), python3-sphinx-feature-classification (>= 1.1.0), python3-sphinxcontrib.apidoc (>= 0.3.0), python3-sqlalchemy (>= 1.4.23), python3-sqlalchemy-utils (>= 0.37.8), python3-stestr (>= 3.2.1), python3-stevedore (>= 1:3.2.2), python3-suds (>= 0.6), python3-swiftclient (>= 1:3.10.1), python3-taskflow (>= 5.4.0-0ubuntu2~), python3-tempest (>= 1:17.1.0), python3-tenacity (>= 6.3.1), python3-testrepository (>= 0.0.18), python3-testresources (>= 2.0.0), python3-testscenarios (>= 0.4), python3-testtools (>= 2.4.0), python3-tooz (>= 2.8.0), python3-tz (>= 2020.1), python3-webob (>= 1:1.8.6), python3-zstd (>= 1.4.5.1)
Architecture: all
Standards-Version: 4.6.1
Format: 3.0 (quilt)
Directory: pool/main/c/cinder
Files:
    87ba315e70d8c641383b4be15c55a404 6316576 cinder_24.2.0.orig.tar.gz
    9744ce185caba4dc9fe8858b1affb880 23880 cinder_24.2.0-0ubuntu2~cloud0.debian.tar.xz
    415b231e0f4ed0fe81e308c0268609cd 5206 cinder_24.2.0-0ubuntu2~cloud0.dsc
Checksums-Sha1:
    976f4b5a38e3c0d4d80d0e20c3069c843559e4c9 6316576 cinder_24.2.0.orig.tar.gz
    d6a2f1f6d90495e14d4de1c1e04de2591598cf59 23880 cinder_24.2.0-0ubuntu2~cloud0.debian.tar.xz
    bd4a5e82b2ce3ae513c43505572a5ff5086877c5 5206 cinder_24.2.0-0ubuntu2~cloud0.dsc
Checksums-Sha256:
    170440a7ceedb74c27b28aadb76288d9cf886cef9fd7dc6f083f6268ad5d50a6 6316576 cinder_24.2.0.orig.tar.gz
    4650b82bef2e98893b592e9aa45b28ac99c1b3009bfe375f263f3c0838b65353 23880 cinder_24.2.0-0ubuntu2~cloud0.debian.tar.xz
    a6f7be71e64ef3f7dcf9df4458cb5c244a56909ed93c3a7fa16c54726d4666d1 5206 cinder_24.2.0-0ubuntu2~cloud0.dsc
Homepage: https://launchpad.net/cinder
Vcs-Git: https://git.launchpad.net/~ubuntu-openstack-dev/ubuntu/+source/cinder
Testsuite: autopkgtest, autopkgtest-pkg-python
Testsuite-Triggers: lvm2, mysql-server, rabbitmq-server
Package-List: cinder-api deb net extra arch=all
    cinder-backup deb net extra arch=all
    cinder-common deb net extra arch=all
    cinder-scheduler deb net extra arch=all
    cinder-volume deb net extra arch=all
    python3-cinder deb python extra arch=all
Original-Maintainer: Chuck Short <zulcss@ubuntu.com>

""")
# ruff: enable[E501]

# rmadison output: pipe-delimited, lines ending with "source" are source pkgs
_CINDER_BINARY_PACKAGES = {
    "cinder-api",
    "cinder-backup",
    "cinder-common",
    "cinder-scheduler",
    "cinder-volume",
    "python3-cinder",
}

_MOCK_MADISON = """\
cinder           | 2:24.0.0-0ubuntu1 | noble | source
cinder-api       | 2:24.0.0-0ubuntu1 | noble | all
cinder-backup    | 2:24.0.0-0ubuntu1 | noble | all
cinder-common    | 2:24.0.0-0ubuntu1 | noble | all
cinder-scheduler | 2:24.0.0-0ubuntu1 | noble | all
cinder-volume    | 2:24.0.0-0ubuntu1 | noble | all
python3-cinder   | 2:24.0.0-0ubuntu1 | noble | all
"""


def stub_cinder_responses(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with responses.RequestsMock(
            assert_all_requests_are_fired=False
        ) as rsps:
            rsps.add(
                responses.GET,
                rmadison_url("cinder", Series.NOBLE),
                body=_MOCK_MADISON,
                status=200,
            )
            rsps.add(
                responses.GET,
                uca_sources_url(Series.NOBLE, Release.ANTELOPE),
                body=_SOURCES_GZ,
                status=200,
            )
            return func(*args, **kwargs)

    return wrapper


class TestNetworkPackageResolver:
    @stub_cinder_responses
    def test_yields_uca_binary_packages_for_requested_source(self):
        resolver = NetworkPackageResolver()
        result = list(
            resolver.binaries_for_source(
                ["cinder"],
                series=Series.NOBLE,
                release=Release.ANTELOPE,
            )
        )
        assert set(result) == _CINDER_BINARY_PACKAGES

    @stub_cinder_responses
    def test_ignores_unrequested_source_package(self):
        resolver = NetworkPackageResolver()
        result = list(
            resolver.binaries_for_source(
                ["nova"],
                series=Series.NOBLE,
                release=Release.ANTELOPE,
            )
        )
        assert result == []
