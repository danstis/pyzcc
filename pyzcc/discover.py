"""Discovery module for ZCC devices."""

import asyncio
import logging
import socket
import json
from typing import Awaitable, Callable, Dict, Optional, cast

from pyzcc.zcc import ZccDevice

_LOGGER = logging.getLogger(__name__)

OnDiscoveredCallable = Callable[[ZccDevice], Awaitable[None]]
DeviceDict = Dict[str, ZccDevice]


class _DiscoverProtocol(asyncio.DatagramProtocol):
    """Implementation of the discovery protocol handler.

    This is internal class, use :func:`Discover.discover`: instead.
    """

    def __init__(
        self,
        *,
        target: str = "255.255.255.255",
        discovery_packets: int = 5,
        interface: Optional[str] = None,
    ):
        self.transport = None
        self.discovery_packets = discovery_packets
        self.interface = interface
        self.target = (target, Discover.DISCOVERY_PORT)

    def connection_made(self, transport) -> None:
        """Set socket options for broadcasting."""
        self.transport = transport
        sock = transport.get_extra_info("socket")
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if self.interface is not None:
            sock.setsockopt(
                socket.SOL_SOCKET, socket.SO_BINDTODEVICE, self.interface.encode()
            )

        self.do_discover()

    def do_discover(self) -> None:
        """Send number of discovery datagrams."""
        _LOGGER.debug("[DISCOVERY] %s >> %s", self.target,
                      Discover.DISCOVERY_MESSAGE)
        for _ in range(self.discovery_packets):
            self.transport.sendto(Discover.DISCOVERY_MESSAGE, self.target)

    def error_received(self, ex):
        """Handle asyncio.Protocol errors."""
        _LOGGER.error("Got error: %s", ex)

    def connection_lost(self, ex):
        """NOP implementation of connection lost."""


class _ListenerProtocol(asyncio.DatagramProtocol):
    """Implementation of the listener protocol handler.

    This is internal class, use :func:`Discover.discover`: instead.
    """

    discovered_devices: DeviceDict

    def __init__(
            self,
            *,
            on_discovered: OnDiscoveredCallable = None):
        super().__init__()
        self.discovered_devices = {}
        self.on_discovered = on_discovered

    def connection_made(self, transport) -> None:
        """Set socket options for broadcasting."""
        self.transport = transport

    def datagram_received(self, data, addr) -> None:
        """Handle discovery responses."""
        ip, port = addr
        if ip in self.discovered_devices:
            return

        _LOGGER.debug("[DISCOVERY] %s << %s", ip, data)

        devinfo = json.loads(data)
        device = ZccDevice(ip, devinfo["brand"], devinfo["product"],
                           devinfo["mac"], devinfo["tcp"], devinfo["availableTcps"])

        self.discovered_devices[ip] = device

        if self.on_discovered is not None:
            asyncio.ensure_future(self.on_discovered(device))

    def error_received(self, ex):
        """Handle asyncio.Protocol errors."""
        _LOGGER.error("Got error: %s", ex)

    def connection_lost(self, ex):
        """NOP implementation of connection lost."""


class Discover:
    """Discover ZCC devices.

    The discovery is done by scanning the network for ZCC devices via a UDP discovery message on port 5001.
    Any present ZCC hubs will respond with a UDP discovery message on port 5002.

    The main entrypoint Discover.discover() will return a dictionary of discovered ZCC devices, with the IP and a
    device object.

    """

    DISCOVERY_PORT = 5001
    DISCOVERY_RESPONSE_PORT = 5002
    DISCOVERY_TARGET = "255.255.255.255"
    DISCOVERY_MESSAGE = b'ZIMI'

    @staticmethod
    async def discover(
        *,
        target=DISCOVERY_TARGET,
        on_discovered=None,
        timeout=5,
        discovery_packets=3,
        interface=None,
    ) -> DeviceDict:
        """Discover supported devices.

        Sends discovery message to 255.255.255.255:5001 in order to detect available supported devices in the local
        network and waits for given timeout for answers from devices.
        If you have multiple interfaces, you can use target parameter to specify the network for discovery.

        If given, `on_discovered` coroutine will get awaited with a :class:`ZccDevice`-derived object as parameter.

        The results of the discovery are returned as a dict of :class:`ZccDevice`-derived objects keyed with IP
        addresses.

        :param target: The target address where to send the broadcast discovery queries if multi-homing (e.g. 192.168.xxx.255).
        :param on_discovered: coroutine to execute on discovery
        :param timeout: How long to wait for responses, defaults to 5
        :param discovery_packets: Number of discovery packets to broadcast
        :param interface: Bind to specific interface
        :return: dictionary with discovered devices
        """
        loop = asyncio.get_event_loop()
        listen_transport, listen_protocol = await loop.create_datagram_endpoint(
            lambda: _ListenerProtocol(on_discovered=on_discovered),
            local_addr=("0.0.0.0", Discover.DISCOVERY_RESPONSE_PORT),
        )
        protocol = cast(_ListenerProtocol, listen_protocol)
        transport, NULL = await loop.create_datagram_endpoint(
            lambda: _DiscoverProtocol(
                target=target,
                discovery_packets=discovery_packets,
                interface=interface,
            ),
            local_addr=("0.0.0.0", 0),
        )

        try:
            _LOGGER.debug("Waiting %s seconds for responses...", timeout)
            await asyncio.sleep(timeout)
        finally:
            transport.close()
            listen_transport.close()

        _LOGGER.debug("Discovered %s ZCC hubs",
                      len(protocol.discovered_devices))

        return protocol.discovered_devices
