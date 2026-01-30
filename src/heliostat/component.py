from dataclasses import dataclass


@dataclass
class Component:
    """A component of an openstack deployment.


    Roughly corresponds to a debian source package for an openstack project.
    This keeps track of which rockcraft files need to be touched, and which
    rocks will need to be built.
    """

    rocks: list[str]
