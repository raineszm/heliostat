# heliostat

`heliostat` is a proof-of-concept tool for building and deploying custom sunbeam images. The primary use case is reproducing bugs in openstack and executing test plans for package [SRUs](https://canonical-se-docs.readthedocs-hosted.com/en/latest/se-sponsorship/ubuntu-cloud-archive-sru/).

## Workflow

The general workflow consists of:

1. **Building** custom rocks
2. **Generating** and **deploying** a sunbeam manifest
3. **Attaching** custom rocks to the deployed charms

### Build

The build process works by taking the upstream rockcraft.yaml from [ubuntu-openstack-rocks](https://github.com/canonical/ubuntu-openstack-rocks), and modifying it to pull packages from the appropriate repos and ppas. This is done, by keeping a local clone of the upstream repo in `~/.cache/heliostat`, emitting a rockcraft.yaml to a temp directory, and building a rock to the specified output directory.

It is important to note that, just as one source package builds multiple binary packages, one upstream openstack component can generate multiple rocks. `heliostat` attempts to keep track of all the rocks that will need to be built for a requested openstack component.

### Generate

Once all of the rocks are built, we need a [manifest]() for the deployment which is compatible with the base openstack release of the image. For example, if we are building a patched version of the cinder package for caracal, we need to use a manifest that selects the caracal channel of the charms.

`heliostat` attempts to generate an appropriate manifest and optionally can pass it to `sunbeam`.

### Attach

Finally, we have to update the image being used by the charms using `juju attach-resources`. `heliostat` will attempt to do this attachment for all required charms.

## Supported Releases

Currently `heliostat` support the same versions as sunbeam, but the hope is also to eventually support interim versions and versions back to yoga.

- [ ] 2022.1 (Yoga)
- [ ] 2022.2 (Zed)
- [x] 2023.1 (Antelope)
- [ ] 2023.2 (Bobcat)
- [x] 2024.1 (Caracal)
- [ ] 2024.2 (Dalmation)
- [x] 2025.1 (Epoxy)
- [ ] 2025.2 (Flamingo)
- [ ] 2026.1 (Gazpacho)
