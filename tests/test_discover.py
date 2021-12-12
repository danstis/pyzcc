import asyncio
from pyzcc import Discover


# This currently requires a real ZCC device on the network, as we are performing a real discovery.
def test_discovery():
    found_devices = asyncio.run(
        Discover.discover(timeout=0.5, discovery_packets=2))
    assert len(found_devices) > 0
