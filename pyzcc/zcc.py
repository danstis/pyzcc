"""Describes a ZCC device"""

import logging

_LOGGER = logging.getLogger(__name__)


class ZccDevice:
    """Describes a ZCC device

    Defines a ZCC hub device.

    """

    def __init__(self, host: str, brand: str, product: str, mac: str, port: int, available_tcps: int) -> None:
        """Create a new device."""
        self.host = host
        self.brand = brand or 'zimi'
        self.product = product or 'zcc'
        self.mac = mac
        self.port = port
        self.available_tcps = available_tcps

        _LOGGER.debug('ZccDevice: %s', self)

    def __str__(self) -> str:
        return f"{self.brand} {self.product} at {self.host}:{self.port}. Device MAC:{self.mac}"

    def __repr__(self):
        return f'ZccDevice(host:"{self.host}", brand:"{self.brand}", product:"{self.product}", mac:"{self.mac}", port:"{self.port}", available_tcps:"{self.available_tcps}")'
