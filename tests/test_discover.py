import asyncio
import pytest
from pyzcc import Discover
from pyzcc.discover import _DiscoverProtocol, _ListenerProtocol
from pyzcc.zcc import ZccDevice
from pyzcc.exceptions import ZccException


# def test_discovery():
#     """This currently requires a real ZCC device on the network, as we are performing a real discovery."""
#     found_devices = asyncio.run(
#         Discover.discover(timeout=1, discovery_packets=2))
#     assert len(found_devices) > 0

def test_discover_send(mocker):
    """Test that we send the requested number of messages."""
    proto = _DiscoverProtocol()
    assert proto.discovery_packets == 5
    assert proto.target == ("255.255.255.255", 5001)
    transport = mocker.patch.object(proto, "transport")
    proto.do_discover()
    assert transport.sendto.call_count == 5


def test_discover_datagram_received(mocker):
    """Verify that datagram received fills discovered_devices."""
    proto = _ListenerProtocol()
    addr = "127.0.0.1"
    proto.datagram_received(
        b'{"brand":"zimi","product":"zcc","mac":"c4ffbc90a687","tcp":5003,"availableTcps":6}', (addr, 1234))

    # Check that device in discovered_devices is initialized correctly
    assert len(proto.discovered_devices) == 1
    dev = proto.discovered_devices[addr]
    assert issubclass(dev.__class__, ZccDevice)
    assert dev.host == addr


def test_invalid_response():
    """Test an invalid response from the discovery."""
    proto = _ListenerProtocol()
    proto.datagram_received(
        b'{"Error": "Some invalid response!"}', ("127.0.0.1", 1234))
    pytest.raises(ZccException)
