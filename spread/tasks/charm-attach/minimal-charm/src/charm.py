#!/usr/bin/env python3
"""Minimal test charm."""

import ops


class MinimalCharm(ops.CharmBase):
    """Charm the application."""

    def __init__(self, framework: ops.Framework):
        super().__init__(framework)
        framework.observe(
            self.on["test-container"].pebble_ready, self.on_pebble_ready
        )
        self.container = self.unit.get_container("test-container")

    def on_pebble_ready(self, _: ops.PebbleReadyEvent):
        """Handle pebble-ready event."""
        self.unit.status = ops.ActiveStatus()


if __name__ == "__main__":  # pragma: nocover
    ops.main(MinimalCharm)
